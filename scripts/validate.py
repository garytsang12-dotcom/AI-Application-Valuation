#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate.py — 估值报告统一校验（三段：来源真实性 + 估值链一致性 + 置信度）
用法: python validate.py <报告.md> [--offline]
      --offline：跳过全部网络请求（沙箱/CI 环境），只做格式与路径校验（v1.15.1）

三段检查（v1.7 由 validate_valuation/validate_chain/validate_confidence 合并）:
  R 段 · 来源校验（HARD）:
    R1 每条 S 级数据带 [N] 引用（正文上标）
    R2 无裸数值（数字 30 字符内必须有 [N] 或标注推理/公司口径）
    R3 来源索引表存在且编号连续（| [N] | 来源 | 类型 | 链接 |）
    R4 关键数据点标注来源等级 S/A/B/C/D 或「单源待验证」
    R5 推理值标注（方法/假设/输入）——估值区间必须有
    R6 URL 可访问性：非白名单 URL 必须能访问（HEAD/GET 200），假 URL = 硬错；白名单官方域名不做访问验证（v1.14.3，反爬 403）
    R7 S 级来源白名单：S 级只允许 hkexnews.hk / sec.gov / wind.com.cn / 公司官网；其他域名标 S = 硬错
    R8 已读核查：S 级来源行必须写明读了什么（原文/中报/招股书/页码等，v1.15.0 起不要求「📖已读」标注）；描述空泛 = 硬错
    R6b hkexnews PDF 直链路径自洽（目录 YYYY/MMDD = 文件名前 8 位且不晚于今日）——不自洽 = 警告（v1.15.1）
  C 段 · 估值链一致性（HARD）:
    C1 定档与估值倍数匹配（v1.15.1 重写：档位取「定档结果」/【Step 1】/Step 1 段落；倍数只扫估值区间章节+附件一；
       「矩阵格」行严格落格，其余行按 0.5×下限～2×上限容差——对齐 estimate.py 超限阈值，插值/毛利/垂直/创始人修正在容差内；
       行内档位标签优先；市场对照行跳过；SOTP 只认「定档结果」行显式标注）
    C2 增速与倍数匹配（<15% 增速给 >25x = 可疑）
    C3 生死关 ❌ 却给出估值区间 = 错
    C4 ARR 口径标注存在（total/B2B/agentic）
    C5 修正系数有依据（垂直/创始人/AI叙事——不裸写）
  S 段 · 置信度（SOFT，仅供参考）:
    S1 报告含置信度标注（🟢/🟡/🔴）
    S2 估值区间带置信度（默认 🟡 中确信）
    S3 「单源」数据已标注（Perplexity/Legora 类）
    S4 无「绝对正确」式断言（「肯定值 20 亿」类）

输出: 🔴 硬错 / 🟡 警告 / ✅ 通过（exit 0）
"""
import datetime
import re
import sys
import urllib.request
import urllib.error
from urllib.parse import urlparse
from matrix_data import TIER_RANGE, MATRIX, HK_MATRIX_TIER1

OFFLINE = False  # --offline：跳过网络请求（test_validate 与沙箱环境置 True）

# ── S 级来源白名单 ──────────────────────────────
S_WHITELIST_DOMAINS = [
    "hkexnews.hk",       # 港交所披露易
    "www.hkex.com.hk",   # 港交所
    "sec.gov",           # 美国证监会
    "wind.com.cn",       # Wind
    "windsun.com",       # Wind 金融终端
    "kingdee.com",       # 金蝶官网（公司官网按需加入白名单——R7 防「报道标官方」，不防真实官网）
    "fourthparadigm.com",  # 范式智能官网
    "marketingforce.com",  # 迈富时官网（投资者关系页）
    "designkit.cn",        # 美图设计室官网（美图子公司官方定价页）
    "sensetime.com",      # 商汤官网（U1 发布页/NEO-Unify 自研架构确认）
]



def extract_url(cell):
    """索引表链接列取 URL：兼容 markdown 链接 [文字](url) 与裸 URL（v1.15.1——原实现把整个 [x](url) 当 URL 访问，必判不可达）"""
    if not cell:
        return cell
    m = re.search(r"\((https?://[^)\s]+)\)", cell) or re.search(r"(https?://[^\s|>]+)", cell)
    return m.group(1) if m else cell.strip()


def is_s_level_url(url):
    """S 级白名单按主机名后缀匹配（v1.15.1——原实现子串匹配，hkexnews.hk.evil.example 可冒充）"""
    u = url.strip()
    if "://" not in u:
        u = "https://" + u  # 无 scheme 的官网写法（www.kingdee.com/ir）
    try:
        host = (urlparse(u).hostname or "").lower()
    except Exception:
        return False
    return any(host == d or host.endswith("." + d) for d in S_WHITELIST_DOMAINS)


HKEX_PDF_RE = re.compile(
    r"^https?://www\d?\.hkexnews\.hk/listedco/listconews/(?:sehk|gem)/(\d{4})/(\d{4})/(?:ltn|gln)?(\d{8})\d+(?:_[a-z]+)?\.pdf$",
    re.I)


def hkex_path_consistent(url):
    """hkexnews 公告/招股书 PDF 直链路径自洽校验（v1.15.1）：目录 YYYY/MMDD 必须等于文件名前 8 位，且日期不晚于今日。
    返回 True 自洽 / False 不自洽（疑似编造） / None 非该形态（/app/ 聆讯后资料集、搜索页等，不校验）。
    边界：日期自洽的编造路径仍会通过；官方域名不做自动访问验证（反爬 403，见 v1.14.3）。"""
    m = HKEX_PDF_RE.match(url.strip())
    if not m:
        return None
    yyyy, mmdd, prefix = m.groups()
    if prefix != yyyy + mmdd:
        return False
    try:
        d = datetime.date(int(prefix[:4]), int(prefix[4:6]), int(prefix[6:]))
    except ValueError:
        return False
    return d <= datetime.date.today()


def url_reachable(url):
    """验证 URL 可访问性（HEAD 优先，失败降级 GET，超时 8 秒）"""
    if not url or url in ("—", "-", "无"):
        return None
    if OFFLINE:
        return None
    for method in ["HEAD", "GET"]:
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,*/*;q=0.8", "Accept-Language": "zh-CN,zh;q=0.9"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except urllib.error.HTTPError as e:
            if e.code in (403, 405):
                return None  # 反爬，需人工确认
            return False
        except Exception:
            continue
    return False


def read_file(path):
    try:
        raw = open(path, "rb").read()
        return raw.decode("utf-8", errors="replace")
    except Exception as e:
        print(f"❌ 无法读取文件: {e}")
        return None


def check_r(txt):
    """R 段：来源格式 + 来源真实性"""
    errors, warns = [], []
    refs_in_text = re.findall(r"\[(\d+)\]", txt)
    if not refs_in_text:
        warns.append("R1 正文没有 [N] 引用——纯定性报告可接受，有数据必须有引用")

    # R2: 裸数值检查（只查数据区，跳过结论区/表格行）
    lines = txt.split("\n")
    conclusion_start = None
    # v1.15.1：截断点只认 # 标题行与【Step 4 行——原实现任何含「估值区间」「置信度」的行都截断，
    #   模板第 2-3 行（框架说明、报告日期行）即命中，导致模板报告的 R2 实际只检查前两行；
    #   ** 开头的行也不作截断点（模板第一章「**未披露清单**：→ 见第十章 DD Priority」会把二至六章跳过）
    for i, line in enumerate(lines):
        s = line.strip()
        if not (s.startswith("#") or s.startswith("【Step 4")):
            continue
        if any(k in s for k in ["【Step 4", "Step 4", "估值区间", "IC Thesis", "DD Priority", "Watch Triggers", "置信度", "来源索引"]):
            conclusion_start = i
            break
    zone = list(enumerate(lines[:conclusion_start] if conclusion_start else lines, start=1))
    # v1.15.1：逐原文行检查（原实现对剔除表格后的文本计数，报出的行号与原文错位）；
    #   比较式阈值（<15%、>70%、≥5 亿）是规则文字不是数据点，不算裸数值（模板第三章样板句与既有报告大量出现）
    for lineno, whole_line in zone:
        if whole_line.strip().startswith("|"):
            continue
        if "[" in whole_line or any(k in whole_line for k in ("推理", "推断", "口径", "约")):
            continue
        for m in re.finditer(r"\$?\d+(?:\.\d+)?(?:x|亿|M|B|%)", whole_line):
            if re.search(r"[<>≤≥＜＞]\s*$", whole_line[max(0, m.start() - 2):m.start()]):
                continue
            errors.append(f"R2 L{lineno} 疑似裸数值: {m.group()}（行内无 [N]/推理/口径标注）")

    # R3: 来源索引表（只查「来源索引」标题后的表格）
    idx_section = txt[txt.rfind("来源索引"):] if "来源索引" in txt else txt
    idx_entries = re.findall(r"\| \[(\d+)\] \|", idx_section)
    if idx_entries:
        nums = [int(n) for n in idx_entries]
        if nums != list(range(1, len(nums) + 1)):
            errors.append(f"R3 索引编号不连续: {nums}")
    else:
        if "来源索引" not in txt and "数据来源" not in txt:
            warns.append("R3 未找到来源索引表（报告有 [N] 引用时必须存在）")

    # R4: 来源等级标注
    if re.search(r"[SABCD]级|[SABCD] 级|等级[:：]?\s*[SABCD]", txt) is None:
        warns.append("R4 未找到来源等级标注（S/A/B/C/D）——关键数据点必须标等级")

    # R5: 估值区间推理标注
    if "估值区间" in txt or "估值" in txt:
        if not re.search(r"方法|假设|输入|矩阵锚|推理值", txt):
            warns.append("R5 估值区间缺少推理标注（方法/假设/输入）——禁止裸估值")

    # R6/R7/R8: 来源真实性三查
    idx_lines = [l for l in lines if re.match(r"\| \[\d+\] \|", l)]
    if OFFLINE and idx_lines:
        warns.append("R6 离线模式：跳过 URL 可访问性检查，只做格式/白名单/路径校验")
    url_issues = 0
    for l in idx_lines:
        parts = [p.strip() for p in l.split("|")]
        if len(parts) < 6:
            continue
        grade = parts[4]
        # URL 列：兼容带「信息时点」列的 7 列结构（| [N] | 来源 | 类型 | 等级 | 时点 | 链接 |）
        url = extract_url(parts[6] if len(parts) >= 8 else parts[5])
        # R6 URL 可访问
        if url and url not in ("—", "-", "无"):
            # v1.14.3：白名单官方域名（hkexnews/sec.gov/wind.com）反爬常见（urllib 被 403），
            # R6 只对「非白名单 URL」做可访问性验证；白名单域名默认可信，人工可复核
            if is_s_level_url(url):
                # S 级官方域名不做自动访问验证（反爬 403），但 hkexnews PDF 直链做路径自洽校验（v1.15.1）
                if hkex_path_consistent(url) is False:
                    warns.append(f"R6 hkexnews PDF 路径不自洽（目录 YYYY/MMDD 须等于文件名前 8 位且不晚于今日）——疑似编造路径，请人工核对: {parts[1]} {url[:80]}")
            else:
                reachable = url_reachable(url)
                if reachable is False:
                    url_issues += 1
                    errors.append(f"R6 索引表 URL 不可访问: {url}（来源 {parts[1]}）——可能是编造链接")
                elif reachable is None:
                    warns.append(f"R6 URL 需人工确认（403/反爬或无链接）: {parts[1]} {url[:60]}")
        # R7 S 级白名单
        if "S" in grade and url and url not in ("—", "-", "无"):
            if not is_s_level_url(url):
                errors.append(f"R7 S 级来源不在白名单: {parts[1]} {url[:70]}（S 级只允许港交所/sec.gov/Wind/公司官网）——把报道标官方 = 硬错")
    # R9 来源必须有真实可访问 URL（2026-09-02 框架硬性要求——「链接存在问题，研报为什么没有 url？」）
    # 招股书/中报/研报/新闻每条来源必须能点开复核；「—」占位 = 硬错
    no_url_count = 0
    for l in idx_lines:
        parts = [p.strip() for p in l.split("|")]
        if len(parts) < 6:
            continue
        url = extract_url(parts[6] if len(parts) >= 8 else parts[5])
        src_type = parts[2] if len(parts) >= 3 else ""
        if url in ("—", "-", "无", ""):
            no_url_count += 1
            errors.append(f"R9 来源 [{parts[1].strip('[]')}]（{src_type}）没有真实 URL——每条来源必须可点开复核（招股书/中报/研报/新闻都要链接），禁止「—」占位")
    # R8 已读标注（v1.15.0 改版：不要求专门的「读取状态」段落——框架要求删掉自我证明句）
    # 判断逻辑改为：S 级来源行本身描述含「原文/中报/年报/招股书/公告/第N页/官网新闻」任一 = 已指明读了什么 → 通过
    # 只有 S 级来源描述空泛（如「某券商」）且无任何已读痕迹才报错
    s_entries = [l for l in idx_lines if len([p.strip() for p in l.split("|")]) >= 5 and "S" in [p.strip() for p in l.split("|")][4]]
    vague_s = []
    read_markers = ["原文", "中报", "年报", "招股书", "公告", "第", "页", "官网", "已读", "PDF", "Wind", "wind.com", "sec.gov", "hkexnews"]
    for l in s_entries:
        parts = [p.strip() for p in l.split("|")]
        desc = parts[1] + parts[2]
        if not any(m in desc for m in read_markers):
            vague_s.append(parts[1][:40])
    if vague_s:
        errors.append(f"R8 S 级来源描述空泛（{'; '.join(vague_s[:3])}）——S 级必须指明读了什么（原文/中报/招股书/公告等），防没读标官方")
    return errors, warns


# ── C1 辅助（v1.15.1）──────────────────────────────
MULT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*x(?![A-Za-z0-9])")  # 数字+x，后不接字母数字（兼容「| 30x |」「45x × ARR」）
SKIP_LINE_RE = re.compile(r"市场对照|市场口径|非框架估值|市场 PS|隐含 PS|市值\s*[:：]|TTM PS|Forward PS")  # 市场对照行（市场口径倍数不是框架倍数）；不按裸「TTM」「市值」跳过，防「30x（TTM 收入口径）」绕过
DISCOUNT_RE = re.compile(r"折扣|负增长|近零|×\s*0\.\d|增速打折")
# 档位标签模式（按优先级；先命中的区段被屏蔽，「二档·自研型」只算三档）
#   裸「一档/二档/三档」前不得是构成复合词的字（同一档位/上一档/降一档/每一档/唯一档案/统一档期/这一档/两档之间…）
_B = r"(?<![同上下降升每任统唯这那哪该此前后高低跨越邻差整各单多两几])"
_TIER_PATTERNS = [
    ("三档", r"二档\s*[·・]?\s*自研型|自研型|\btier2[bs]\b|\btier3\b|第\s*[三3]\s*档|" + _B + r"三档"),  # tier2s/自研型 v1.9.0 并入三档
    ("第零档", r"第\s*[零0]\s*档|\btier0s?\b"),
    ("一档", r"第\s*[一1]\s*档|\btier1\b|" + _B + r"一档"),
    ("二档", r"第\s*[二2]\s*档|\btier2a?\b|" + _B + r"二档"),
    ("算力/Infra 段", r"算力\s*/?\s*Infra\s*段|算力段|Infra\s*段|\binfra\b"),
]


def find_tier_labels(text):
    """按出现顺序返回文本中的正式档位标签（去重）。认 第零档/一档/二档/三档/算力段、数字形态「第 3 档」、英文键 tier0-3/infra。"""
    taken, hits = [], []
    for canon, pat in _TIER_PATTERNS:
        for m in re.finditer(pat, text, flags=re.I):
            if any(m.start() < e and m.end() > s for s, e in taken):
                continue
            taken.append((m.start(), m.end()))
            hits.append((m.start(), canon))
    out = []
    for _, c in sorted(hits):
        if c not in out:
            out.append(c)
    return out


def detect_tier(body):
    """定档识别，按优先级：①「定档结果」行 ②【Step 1 · 定档】行 ③ '# Step 1' 标题后 5 行 ④ 执行摘要「| 定档 |」行。返回 (标签, 来源)。"""
    for line in body.split("\n"):
        if "定档结果" in line:
            labels = find_tier_labels(line.split("定档结果", 1)[1])
            if labels:
                return labels[0], "定档结果行"
    m = re.search(r"【Step 1[^\n】]*】([^\n]*)", body)
    if m:
        labels = find_tier_labels(m.group(1))
        if labels:
            return labels[0], "【Step 1】行"
    m = re.search(r"^#+\s*Step 1[^\n]*\n((?:[^\n]*\n?){0,5})", body, flags=re.M)
    if m:
        labels = find_tier_labels(m.group(1))
        if labels:
            return labels[0], "Step 1 段落"
    m = re.search(r"^\|\s*\**\s*定档\s*\**\s*\|([^\n]*)", body, flags=re.M)
    if m:
        labels = find_tier_labels(m.group(1))
        if labels:
            return labels[0], "执行摘要定档行"
    return None, None


def detect_sotp(body):
    """SOTP 只认「定档结果」行显式标注（剔除模板样板句「混合形态标 SOTP 需拆分」）；
    无「定档结果」行的旧格式报告沿用关键词/①②③ 启发式（同样剔除模板样板句）。"""
    for line in body.split("\n"):
        if "定档结果" in line:
            clean = line.replace("混合形态标 SOTP 需拆分", "")
            return _sotp_positive(clean, r"SOTP|分段估值|拆段")
    clean = re.sub(r"SOTP 的依据|SOTP 需拆分|SOTP 单列", "", body)
    return _sotp_positive(clean, r"SOTP|拆段|分段估值|多业务") or bool(re.search(r"^[*\s]*[①②③④⑤]", clean, flags=re.M))


def _sotp_positive(text, pat):
    """SOTP 关键词出现且非否定语境（「无需 SOTP」「不做 SOTP」「SOTP 不适用」不算）"""
    for m in re.finditer(pat, text):
        before = text[max(0, m.start() - 4):m.start()]
        after = text[m.end():m.end() + 4]
        if re.search(r"无需|不需|不做|不用|不属|不是|不适|非|无\s*$", before) or re.search(r"^\s*(?:不适用|无需|不需)", after):
            continue
        return True
    return False


def c1_scope(txt):
    """C1/C2 扫描范围：估值区间章节（标题含 估值区间/Step 4/七、估值，或【Step 4 行）+ 附件一落位表；都没有返回 None（回退全文）。"""
    lines = txt.split("\n")
    n = len(lines)
    secs = []
    i = 0
    while i < n:
        s = lines[i].strip()
        if (s.startswith("#") and re.search(r"估值区间|Step 4|第七章|七、估值|估值结论|估值结果|附件一", s)) or s.startswith("【Step 4"):
            j = i + 1
            while j < n and not lines[j].lstrip().startswith("#") and not lines[j].startswith("【Step"):
                j += 1
            secs.append("\n".join(lines[i:j]))
            i = j
            continue
        i += 1
    return "\n".join(secs) if secs else None


_TIER_KEY = {"第零档": "tier0", "一档": "tier1", "二档": "tier2", "三档": "tier3", "算力/Infra 段": "infra"}


def detect_market(scope):
    """市场锚带：估值区间「市场 hk/us」或「港股锚带」字样；识别不到返回 None（取档位并集）"""
    if re.search(r"市场\s*[:：]?\s*hk\b|--market\s+hk|港股(?:锚)?带|港股一档", scope, flags=re.I):
        return "hk"
    if re.search(r"市场\s*[:：]?\s*us\b|--market\s+us|美股(?:锚)?带", scope, flags=re.I):
        return "us"
    return None


def detect_band(scope):
    """增速档：估值区间「（g3）」「增速档 g3」字样；识别不到返回 None"""
    m = re.search(r"增速档\s*(g[1-4])|[（(]\s*(g[1-4])\s*[)）]", scope, flags=re.I)
    return (m.group(1) or m.group(2)).lower() if m else None


def tier_bounds(label, market=None, band=None):
    """C1 核对基准 (下限, 上限, 说明)：识别到市场+增速档取矩阵格，否则取档位并集；一档 hk 取港股带；算力段恒取并集（轻资产 15-25x 是修正项）"""
    key = _TIER_KEY.get(label)
    if key == "tier1" and market == "hk":
        if band in HK_MATRIX_TIER1:
            lo, hi = HK_MATRIX_TIER1[band]
            return lo, hi, f"港股带 {band}"
        return min(c[0] for c in HK_MATRIX_TIER1.values()), max(c[1] for c in HK_MATRIX_TIER1.values()), "港股带并集"
    if key and key != "infra" and band in MATRIX.get(key, {}):
        lo, hi = MATRIX[key][band]
        return lo, hi, f"矩阵格 {band}"
    lo, hi = TIER_RANGE[label]
    return lo, hi, "档位并集"


def check_c(txt):
    """C 段：估值链一致性 + 报告完整性"""
    errors, warns = [], []
    # D0: 附件零（估值矩阵+档位定义）必含（v1.14.0 框架硬性要求——读者独立理解）
    if "估值矩阵" not in txt or "档位定义" not in txt:
        errors.append("D0 报告缺「附件零：估值矩阵 + 档位定义」——每份报告必附最新矩阵和档位定义（框架硬性要求）")
    # D0b: 收入确认三查必填（时间点/随时间拆分）
    if ("时间点" not in txt and "時點" not in txt) or ("随时间" not in txt and "隨時間" not in txt):
        warns.append("D0b 未找到「时间点/随时间」收入确认拆分——定档三查第一查缺失（项目制 vs 订阅分水岭）")
    # ── C1（v1.15.1 重写）────────────────────────────────────────────
    # 原实现三处失效：①倍数正则只认「x」后接 倍/→/,/）/换行，表格单元格「| 30x |」和「45x × ARR」全部漏捕；
    # ②档位识别在前 2000 字按字典序匹配「订阅」「项目制」等通用词，三档报告摘要提到「订阅收入」即判为一档；
    # ③SOTP 分支靠正文出现「SOTP」触发，模板正文自带三处「SOTP」，模板报告一律走 SOTP 分支，单档检查成死代码。
    # 新实现：档位只从「定档结果」行 / 【Step 1】行 / Step 1 段落 / 执行摘要「定档」行取正式标签；
    #   倍数只扫估值区间章节 + 附件一落位表；行内自带档位标签的按该行标签核对（情景表/SOTP 分段行）；
    #   核对基准 = 矩阵格（识别到增速档 gN 与市场 hk/us 时取该格，否则取档位并集）：
    #     「矩阵格」行严格落格；其余行按 0.5×下限～2×上限容差——estimate.py 的档内插值（±25% 跨度）、
    #     毛利 ×1.3、垂直 ×1.5-2、founder80 封顶都在容差内，上限×2 与引擎超限告警阈值一致；
    #   市场对照行跳过；折扣豁免沿用原实现（正文出现折扣关键词即豁免下行，v1.13.5）。
    # 附件/附录是参考表，不参与估值链检查（v1.14.0 起含附件零）；附件一落位表由 c1_scope 从全文单独取
    body = txt.split("【附录")[0]
    body = re.split(r"## 附件[零一二三]|## 附录", body)[0]
    tier_found, tier_src = detect_tier(body)
    is_sotp = detect_sotp(body)
    scope = c1_scope(txt) or body
    has_discount_ctx = bool(DISCOUNT_RE.search(body))
    market, band = detect_market(scope), detect_band(scope)
    labelled_rows = 0
    for line in scope.split("\n"):
        if SKIP_LINE_RE.search(line):
            continue
        mults = [float(m.group(1)) for m in MULT_RE.finditer(line)]
        if not mults:
            continue
        labels = find_tier_labels(line)
        if len(labels) == 1:
            src = labels[0]
            labelled_rows += 1
        elif len(labels) >= 2:
            continue  # 多档同行（对照表）无法归属
        elif is_sotp or not tier_found:
            continue  # SOTP 无标签行 / 未识别档位：无法归属
        else:
            src = tier_found
        lo, hi, basis = tier_bounds(src, market, band if src == tier_found else None)
        strict = "矩阵格" in line
        tol_lo, tol_hi = (lo, hi) if strict else (lo * 0.5, hi * 2.0)
        for val in mults:
            if tol_lo <= val <= tol_hi:
                continue
            if val < tol_lo and has_discount_ctx:
                continue  # 负增长/近零折扣后低于下限是设计内（v1.13.5）
            how = "矩阵格行严格落格" if strict else "容差 0.5×-2×"
            errors.append(f"C1 档位 {src}（{basis} {lo:g}-{hi:g}x，{how}）但出现 {val:g}x——估值链断裂：{line.strip()[:60]}")
    if not tier_found and not is_sotp:
        warns.append("C1 未识别档位标注（需要「定档结果」行、【Step 1 · 定档】行或 Step 1 段落写明 第零档/一档/二档/三档/算力段）")
    if is_sotp and labelled_rows == 0:
        warns.append("C1 [SOTP] 估值区间/附件一中未见「档位 + 倍数」同行的分段行——SOTP 报告请每段一行标注档位与倍数")

    # C2: 增速 ↔ 倍数（单档位模式；SOTP 跳过）——v1.15.1：支持小数增速（原「12.0%」被解析为 0%）
    if not is_sotp:
        growth_m = re.search(r"增速[^%\n]{0,30}?(-?\d+(?:\.\d+)?)\s*%", body)
        if growth_m:
            g = float(growth_m.group(1))
            for line in scope.split("\n"):
                if SKIP_LINE_RE.search(line):
                    continue
                for m in MULT_RE.finditer(line):
                    val = float(m.group(1))
                    if g < 15 and val > 25:
                        warns.append(f"C2 增速 {g:g}% 却出现 {val}x——低增速高倍数，检查增速是否虚报或修正是否过度")
                    if g > 60 and val < 3:
                        warns.append(f"C2 增速 {g:g}% 却出现 {val}x——超高增速极低倍数，检查档位是否过低")

    # C3: 生死关 ❌ 却估值
    if re.search(r"【Step 2[^\n]*生死关[^\n]*❌|一票否决[^\n]*❌", txt) and "估值区间" in txt:
        errors.append("C3 生死关 ❌（一票否决）却给出估值区间——禁止对已否决项目估值")

    # C4: ARR 口径
    if "估值区间" in txt and not re.search(r"total|B2B|agentic|口径", txt):
        warns.append("C4 估值未标注 ARR 口径（total/B2B/agentic）——倍数必须带口径")

    # C5: 修正系数有依据
    if re.search(r"修正|溢价", txt):
        if not re.search(r"垂直|创始人|战略|中国|AI 叙事|AI叙事", txt):
            warns.append("C5 出现修正/溢价但未说明类型（垂直/创始人/中国/AI叙事）")
    return errors, warns


def check_s(txt):
    """S 段：置信度（SOFT）"""
    errors, warns = [], []
    if not re.search(r"🟢|🟡|🔴|置信度", txt):
        warns.append("S1 报告无置信度标注（🟢 高确信 / 🟡 中确信 / 🔴 低确信）")
    if "估值区间" in txt and not re.search(r"🟢|🟡|🔴", txt):
        warns.append("S2 估值区间未带置信度——估值默认 🟡 中确信（矩阵是时点数据）")
    if re.search(r"单源|Sacra|待验证", txt):
        if not re.search(r"单源|待验证", txt):
            warns.append("S3 出现单源数据（Sacra 类）但未标注")
    if re.search(r"肯定|绝对|必然|一定值|确定值", txt):
        warns.append("S4 出现绝对断言词（肯定/绝对/必然）——估值是区间不是断言")
    # S5 元解释句/自我证明句禁词（v1.15.0 框架校准连续裁决：报告直接给判断，不解释框架设计/不自我证明/不加免责套话）
    # 注意：置信度行的「S 级已读原文」是可信度依据（保留）；专门的读取状态段/免责声明/框架自述是元语句（禁）
    meta_phrases = [
        "MECE", "正交", "不重复打分", "不重复论证", "不重复推导",
        "读取状态", "来源核查清单", "📖已读",
        "框架推演", "不构成投资建议", "仅供参考",
        "两组", "分工", "扫账本", "评质量",
    ]
    for phrase in meta_phrases:
        if phrase in txt:
            # 定位上下文辅助删改
            idx = txt.find(phrase)
            start = max(0, txt.rfind("\n", 0, idx) - 30)
            end = min(len(txt), txt.find("\n", idx) + 60)
            ctx = txt[start:end].replace("\n", " ")
            errors.append(f"S5 元解释/自我证明句禁词「{phrase}」——报告直接给判断不解释框架设计（删掉或改写），上下文: …{ctx}…")
    # S6 装饰性 emoji 禁（v1.15.0 框架校准：🔴⚠️ 语义符号保留；装饰性全禁）
    # ✅❌☑ 用于「数据状态」列 + 「修正系数勾选」表单（已披露/缺失/已勾选语义，同 🔴⚠️ 属表格符号）→ 不禁；真正装饰性的 📖🚀🎨🔥💡⭐✨📌🎯 等禁
    decorative_emojis = ["📖", "🚀", "🎨", "🔥", "💡", "⭐", "✨", "📌", "🎯", "💪", "👏", "🎉", "🧠", "🤖", "💼", "📊", "💰", "🤑", "😊", "👍"]  # v1.15.1：🟢 移出——S1/S2 与 estimate.py 用 🟢🟡🔴 三色标置信度
    for ch in decorative_emojis:
        if ch in txt:
            errors.append(f"S6 装饰性 emoji「{ch}」——语义符号（🔴⚠️✅❌数据状态）可用，装饰性 emoji 全禁（v1.15.0 框架校准）")
    # S7 金额小数位（v1.15.0：金额 1 位小数——但仅针对报告产出的估值/判断，财报原文引用必须保留原值）
    # 处理：命中「亿/万」后两位小数 → 警告（按数字去重，避免同一财报数字刷屏）；区分财报引用 vs 报告估值难自动化，降级提示
    seen_amounts = set()
    for m in re.finditer(r"\d+\.\d{2}(?=\s*亿|\s*万)", txt):
        num = m.group()
        if num not in seen_amounts:
            seen_amounts.add(num)
            warns.append(f"S7 金额两位小数「{num}」——若为报告估值/判断值请改 1 位小数（假精确）；若为财报原文引用可保留（2.84 亿中报数据原样）")
    return errors, warns


def main():
    global OFFLINE
    OFFLINE = "--offline" in sys.argv[1:]
    argv = [a for a in sys.argv[1:] if a != "--offline"]
    if len(argv) < 1:
        print("用法: python validate.py <报告.md> [--offline]")
        sys.exit(1)
    path = argv[0]
    txt = read_file(path)
    if txt is None:
        sys.exit(1)

    r_errors, r_warns = check_r(txt)
    c_errors, c_warns = check_c(txt)
    s_errors, s_warns = check_s(txt)

    all_errors = r_errors + c_errors + s_errors
    all_warns = r_warns + c_warns + s_warns

    print(f"===== validate: {path} =====")
    for e in all_errors:
        print(f"  🔴 {e}")
    for w in all_warns:
        print(f"  🟡 {w}")
    ok = len(all_errors) == 0
    print(f"结果: {'✅ 通过' if ok else '❌ 未通过（有硬错）'} | 硬错 {len(all_errors)} | 警告 {len(all_warns)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
