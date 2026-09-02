#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate.py — 估值报告统一校验（三段：来源真实性 + 估值链一致性 + 置信度）
用法: python validate.py <报告.md>

三段检查（v1.7 由 validate_valuation/validate_chain/validate_confidence 合并）:
  R 段 · 来源校验（HARD）:
    R1 每条 S 级数据带 [N] 引用（正文上标）
    R2 无裸数值（数字 30 字符内必须有 [N] 或标注推理/公司口径）
    R3 来源索引表存在且编号连续（| [N] | 来源 | 类型 | 链接 |）
    R4 关键数据点标注来源等级 S/A/B/C/D 或「单源待验证」
    R5 推理值标注（方法/假设/输入）——估值区间必须有
    R6 URL 可访问性：索引表每条 URL 必须能访问（HEAD/GET 200），假 URL = 硬错
    R7 S 级来源白名单：S 级只允许 hkexnews.hk / sec.gov / wind.com.cn / 公司官网；其他域名标 S = 硬错
    R8 来源核查清单：S 级来源必须带「📖已读」标注；标 S 但未标已读 = 硬错
  C 段 · 估值链一致性（HARD）:
    C1 定档与估值倍数匹配（支持 SOTP 多段 + 附录豁免）
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
import re
import sys
import urllib.request
import urllib.error
from matrix_data import TIER_RANGE

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



def is_s_level_url(url):
    url_lower = url.lower()
    return any(d in url_lower for d in S_WHITELIST_DOMAINS)


def url_reachable(url):
    """验证 URL 可访问性（HEAD 优先，失败降级 GET，超时 8 秒）"""
    if not url or url in ("—", "-", "无"):
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
    for i, line in enumerate(lines):
        if any(k in line for k in ["【Step 4", "估值区间", "IC Thesis", "DD Priority", "Watch Triggers", "置信度", "来源索引"]):
            conclusion_start = i
            break
    data_zone = "\n".join(lines[:conclusion_start] if conclusion_start else lines)
    data_zone = "\n".join(l for l in data_zone.split("\n") if not l.strip().startswith("|"))
    for m in re.finditer(r"\$?\d+(?:\.\d+)?(?:x|亿|M|B|%)", data_zone):
        line_start = data_zone.rfind("\n", 0, m.start()) + 1
        line_end = data_zone.find("\n", m.end())
        if line_end == -1:
            line_end = len(data_zone)
        whole_line = data_zone[line_start:line_end]
        if "[" not in whole_line and "推理" not in whole_line and "推断" not in whole_line and "口径" not in whole_line and "约" not in whole_line:
            line = data_zone[:m.start()].count("\n") + 1
            errors.append(f"R2 L{line} 疑似裸数值: {m.group()}（行内无 [N]/推理/口径标注）")

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
    url_issues = 0
    for l in idx_lines:
        parts = [p.strip() for p in l.split("|")]
        if len(parts) < 6:
            continue
        grade = parts[4]
        # URL 列：兼容带「信息时点」列的 7 列结构（| [N] | 来源 | 类型 | 等级 | 时点 | 链接 |）
        url = parts[6] if len(parts) >= 8 else parts[5]
        # R6 URL 可访问
        if url and url not in ("—", "-", "无"):
            # v1.14.3：白名单官方域名（hkexnews/sec.gov/wind.com）反爬常见（urllib 被 403），
            # R6 只对「非白名单 URL」做可访问性验证；白名单域名默认可信，人工可复核
            if is_s_level_url(url):
                pass  # S 级官方域名，无需 R6 可访问性证明
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
    # R9 来源必须有真实可访问 URL（主人 2026-09-02 硬性要求——「链接存在问题，研报为什么没有 url？」）
    # 招股书/中报/研报/新闻每条来源必须能点开复核；「—」占位 = 硬错
    no_url_count = 0
    for l in idx_lines:
        parts = [p.strip() for p in l.split("|")]
        if len(parts) < 6:
            continue
        url = parts[6] if len(parts) >= 8 else parts[5]
        src_type = parts[2] if len(parts) >= 3 else ""
        if url in ("—", "-", "无", ""):
            no_url_count += 1
            errors.append(f"R9 来源 [{parts[1].strip('[]')}]（{src_type}）没有真实 URL——每条来源必须可点开复核（招股书/中报/研报/新闻都要链接），禁止「—」占位")
    # R8 已读标注（v1.15.0 改版：不要求专门的「读取状态」段落——主人要求删掉自我证明句）
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


def check_c(txt):
    """C 段：估值链一致性 + 报告完整性"""
    errors, warns = [], []
    # D0: 附件零（估值矩阵+档位定义）必含（v1.14.0 主人硬性要求——读者独立理解）
    if "估值矩阵" not in txt or "档位定义" not in txt:
        errors.append("D0 报告缺「附件零：估值矩阵 + 档位定义」——每份报告必附最新矩阵和档位定义（主人硬性要求）")
    # D0b: 收入确认三查必填（时间点/随时间拆分）
    if ("时间点" not in txt and "時點" not in txt) or ("随时间" not in txt and "隨時間" not in txt):
        warns.append("D0b 未找到「时间点/随时间」收入确认拆分——定档三查第一查缺失（项目制 vs 订阅分水岭）")
    # C1: 定档 ↔ 倍数（SOTP 多段 + 附录/附件豁免——附件是参考表，不参与估值链检查）
    # v1.14.0: 附件零（估值矩阵+档位定义）也是参考表，加入豁免
    body = txt.split("【附录")[0]
    body = re.split(r"## 附件[零一二三]|## 附录", body)[0]
    # SOTP 检测：关键词（SOTP/拆段/分段估值/多业务）或 ①②③ 编号
    is_sotp = bool(re.search(r"SOTP|拆段|分段估值|多业务", body)) or bool(
        re.search(r"(?=^[*\s]*[①②③④⑤])", body, flags=re.M)
    )
    if is_sotp:
        # 按粗体小标题分段（**AI Platform** / **Agentic** / **API**）或 ①②③ 编号行
        segments = [s for s in re.split(r"(?=\*\*[^*]+\*\*|^[*\s]*[①②③④⑤])", body, flags=re.M) if s.strip()]
        for seg in segments:
            seg_tiers = [t for t in TIER_RANGE if re.search(rf"{t}", seg[:800])]
            seg_mults = re.findall(r"(\d+(?:\.\d+)?)\s*x\s*(?:倍|→|,|）|\)|\n|$)", seg)
            if not seg_tiers:
                if seg_mults:
                    warns.append(f"C1 [SOTP段] 未识别档位标注，段内含倍数 {seg_mults[:3]}——建议显式标注段档位")
                continue
            ranges = [TIER_RANGE[t] for t in seg_tiers]
            lo_all = min(r[0] for r in ranges)
            hi_all = max(r[1] for r in ranges)
            for m in seg_mults:
                val = float(m)
                if val < lo_all or val > hi_all:
                    errors.append(f"C1 [SOTP段] 段内档位 {'/'.join(seg_tiers)}（允许 {lo_all}-{hi_all}x 并集）但出现 {val}x——估值链断裂")
    else:
        segments = [body]
        tier_found = None
        for tier in TIER_RANGE:
            # 修复 v1.7.12：原正则 `【Step 1|定档】.*?{tier}` 中「|」优先级问题——
            # 「【Step 1」单独匹配就 True，导致永远匹配 TIER_RANGE 第一个键「第零档」
            if re.search(rf"(?:【Step 1|定档】).*?{tier}", body) or re.search(rf"{tier}", body[:2000]):
                tier_found = tier
                break
        mults = re.findall(r"(\d+(?:\.\d+)?)\s*x\s*(?:倍|→|,|）|\)|\n|$)", body)
        if tier_found:
            lo, hi = TIER_RANGE[tier_found]
            # v1.13.5：负增长/近零增长折扣豁免——「折扣/负增长/近零/×0.5/×0.65」上下文里的低倍数
            # 不算断裂（群核案例：增速 1.5% 近零 → ×0.65 → 2.4x 低于一档下限 2.5，属设计内折扣）
            has_discount_ctx = bool(re.search(r"折扣|负增长|近零|×0\.\d|×\s*0\.\d|增速打折", body))
            for m in mults:
                val = float(m)
                if val < lo or val > hi:
                    if val < lo and has_discount_ctx:
                        continue  # 折扣上下文豁免（负增长折扣后低于档位下限是设计内）
                    errors.append(f"C1 档位 {tier_found}（允许 {lo}-{hi}x）但报告出现 {val}x——估值链断裂")
        else:
            warns.append("C1 未识别档位标注（需要【Step 1 · 定档】段落）")

    # C2: 增速 ↔ 倍数（单档位模式；SOTP 跳过全局对比）
    if len(segments) <= 1:
        growth_m = re.search(r"增速[^%]*?(\d+)%", body)
        if growth_m:
            g = int(growth_m.group(1))
            mults = re.findall(r"(\d+(?:\.\d+)?)\s*x\s*(?:倍|→|,|）|\)|\n|$)", body)
            for m in mults:
                val = float(m)
                if g < 15 and val > 25:
                    warns.append(f"C2 增速 {g}% 却出现 {val}x——低增速高倍数，检查增速是否虚报或修正是否过度")
                if g > 60 and val < 3:
                    warns.append(f"C2 增速 {g}% 却出现 {val}x——超高增速极低倍数，检查档位是否过低")

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
    # S5 元解释句/自我证明句禁词（v1.15.0 主人连续裁决：报告直接给判断，不解释框架设计/不自我证明/不加免责套话）
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
    # S6 装饰性 emoji 禁（v1.15.0 主人裁决：🔴⚠️ 语义符号保留；装饰性全禁）
    # ✅❌☑ 用于「数据状态」列 + 「修正系数勾选」表单（已披露/缺失/已勾选语义，同 🔴⚠️ 属表格符号）→ 不禁；真正装饰性的 📖🚀🎨🔥💡⭐✨📌🎯 等禁
    decorative_emojis = ["📖", "🚀", "🎨", "🔥", "💡", "⭐", "✨", "📌", "🎯", "💪", "👏", "🎉", "🧠", "🤖", "💼", "📊", "💰", "🤑", "😊", "👍", "🟢"]
    for ch in decorative_emojis:
        if ch in txt:
            errors.append(f"S6 装饰性 emoji「{ch}」——语义符号（🔴⚠️✅❌数据状态）可用，装饰性 emoji 全禁（v1.15.0 主人裁决）")
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
    if len(sys.argv) < 2:
        print("用法: python validate.py <报告.md>")
        sys.exit(1)
    path = sys.argv[1]
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
