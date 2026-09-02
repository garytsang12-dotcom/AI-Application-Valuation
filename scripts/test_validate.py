#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_validate.py — validate.py 自检（R5 评估集；v1.15.1 扩为用例表 + estimate→报告→validate 回路）
用法: python scripts/test_validate.py

职责: 固化「合格报告通过 / 造假报告拦截」两个基准，加 v1.15.1 各修复项的回归用例，
      防止 validate.py 改动时误放行造假或误杀合格。全部用例走离线模式，不发网络请求。

输出: 每条用例 ✅/🔴，exit 0/1（提交前自检 / 可进 CI）
"""
import importlib.util
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
from matrix_data import MATRIX, HK_MATRIX_TIER1  # noqa: E402

SCRIPT = os.path.join(BASE, "scripts", "estimate.py")


def load_validate():
    path = os.path.join(BASE, "scripts", "validate.py")
    spec = importlib.util.spec_from_file_location("validate_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OFFLINE = True  # 用例不依赖网络
    return mod


def fmt(cell):
    return f"{cell[0]:g}-{cell[1]:g}x"


# 附录矩阵行从 matrix_data 生成（原夹具手写「30-50x」是 v1.7.10 已废弃值——夹具漂移）
MATRIX_ROW_TIER1 = "| 一档·订阅 | " + " | ".join(fmt(MATRIX["tier1"][g]) for g in ("g1", "g2", "g3", "g4")) + " |"

GOOD_REPORT = """# 测试报告 · 金蝶国际（0268.HK）· v1.7 格式验证

> 本文件仅用于 validate.py 自检（R5 评估集），非正式报告。

## 项目信息

| 字段 | 值 | 三态 |
|---|---|---|
| 公司名称 | 金蝶国际 | ✅ 披露可证 |
| 2025 收入 | 70.06 亿元（+12.0%） | ✅ 披露可证 [1] |
| 毛利率 | 67.1% | ✅ 披露可证 [1] |
| PS(TTM) | 3.9x | ✅ 披露可证 [1] |

## Step 0 · 公司 Profile

- 一句话定位：老牌 ERP 云转型（苍穹/星瀚），国产替代受益 [1]
- 业务结构：云订阅 + 传统许可 + 服务
- 客户画像：中大型企业，客户黏性高

## Step 0.5 · 披露充分性

✅ 披露充分（上市 20+ 年，年报分部数据全）

## Step 1 · 定档

**档位**：一档·订阅（卖软件功能，COGS 不随用量涨，毛利 67.1% 软件级交叉验证 [1]）

## Step 2 · 生死关

✅ 通过（五死因全部绿灯：概念热✅真实付费 / 无存量预算✅ERP 替换预算 / 单点功能✅客户黏性高 / 价格战✅国产替代红利 / 责任链✅）

## Step 3 · 质量分

6.5/10（护城河 3 层：品牌+规模+切换成本；爬升检验半爬——云订阅占比提升中）

## Step 4 · 估值

**估值区间**：$290M-$340M（total 口径；3.5-4.2x × $81M 收入；方法=矩阵锚一档 g1；假设=增速 12% 低速、毛利 67% 软件级；输入=2025 年报收入）

## 偏离分析

市场 3.9x vs 框架 3-5x——带内，合理。可解释：老牌 SaaS 增速低但客户黏性高。

## 置信度

🟡 中确信（矩阵 2026-08 时点数据）

## 附件零：估值矩阵 + 档位定义

估值矩阵：一档·订阅 港股带 g1 2.5-4x（档位定义见 SKILL.md Step 1 表；读者理解档位=租功能/订阅，COGS 不随用量涨）

---

## 来源索引

| [1] | Wind 行情/财务 | 行情 | S | https://www.wind.com.cn |


## 附录：估值矩阵参考表

### 表 1：矩阵

| 档位 \\ 增速 | <15% | 15-30% | 30-60% | >60% |
|---|---|---|---|---|
""" + MATRIX_ROW_TIER1 + "\n"

BAD_REPORT = """# 造假测试报告（R6+R7+R8 三查应全拦）

【Step 1 · 定档】一档·订阅
【Step 2 · 生死关】✅ 通过
【Step 3 · 质量分】6/10
【Step 4 · 估值】$150M（15x × $10M ARR；方法=矩阵锚；假设=增速 20%；输入=ARR 10M）

## 来源索引

| [1] | 假招股书 | PDF | S | https://fake-hkex-pdf.example.com/fake.pdf |
| [2] | 新浪报道 | 文章 | S | https://finance.sina.com.cn/xxx |
"""

# ── 迷你夹具公共尾部 ──
CONF = "\n## 置信度\n\n🟡 中确信\n"
APPX = """
## 附件零：估值矩阵 + 档位定义

估值矩阵与档位定义略。

## 来源索引

| [1] | Wind 行情/财务 | 行情 | S | https://www.wind.com.cn |
"""


def idx(desc, url):
    """自定义来源索引（替换 APPX 里的默认行）"""
    return APPX.replace("| [1] | Wind 行情/财务 | 行情 | S | https://www.wind.com.cn |", f"| [1] | {desc} | PDF | S | {url} |")


CASES = [
    # (名称, 文本, 必含硬错前缀, 不得含硬错前缀, 必含警告前缀, 不得含警告前缀)
    ("GOOD 合格报告 0 硬错", GOOD_REPORT, [], ["R", "C", "S", "D"], [], []),
    ("BAD 造假报告被拦截（R7 非白名单标 S）", BAD_REPORT, ["R7"], [], [], []),
    ("S6：🟢 高确信不是装饰 emoji（v1.15.1）",
     "# 报告\n\n## Step 1 · 定档\n\n**档位**：一档·订阅\n\n## 估值区间\n\n倍数 3.5x（total 口径；方法=矩阵锚）\n\n## 置信度\n\n🟢 高确信（A/B 双源）\n" + APPX,
     [], ["S6"], [], []),
    ("C1 真阳性：二档写 30x（total 口径）——原正则漏捕",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能（无自研无入口）\n\n## 七、估值区间\n\n| 情景 | 档位 | 倍数 | 估值 |\n|---|---|---|---|\n| 中性（主） | 二档 | 30x（total 口径） | 30 亿 |\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 真阳性：附件一表格单元格「| 30x |」——原正则失明",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能\n\n## 七、估值区间\n\n有效区间 30 亿（total 口径）。\n\n## 附件一：本报告落位示意\n\n| 项 | 值 |\n|---|---|\n| 最终倍数 | 30x |\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 假阳性：三档报告摘要含「订阅收入」、定档写「第 3 档」——原判为一档",
     "# 报告\n\n## 执行摘要\n\n| 维度 | 结论 |\n|---|---|\n| 一句话定位 | 自研法律大模型，按结果计费为主，另有少量订阅收入 |\n| 定档 | 第 3 档·自研智能 |\n\n## 三、商业模式定档\n\n**定档结果**：第 3 档（自研法律模型 + 数据飞轮 + 流程嵌入）\n\n## 七、估值区间\n\n| 情景 | 倍数 | 估值 |\n|---|---|---|\n| 中性（主） | 45x（total 口径） | 45 亿 |\n" + CONF + APPX,
     [], ["C1"], [], []),
    ("C1 假阳性：第七章市场口径倍数行不参与核对",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：第零档·项目制（时间点确认 97.4%）\n\n## 七、估值区间\n\n倍数 1.2x（total 口径；方法=矩阵锚）\n\n**市场对照**：市值 200 亿，TTM PS 32.7x（市场口径，非框架估值）\n" + CONF + APPX,
     [], ["C1"], [], []),
    ("C1 假阳性：情景表异档行按该行档位核对",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅（随时间确认 90%）\n\n## 七、估值区间\n\n| 情景 | 档位 | 倍数 | 估值 |\n|---|---|---|---|\n| 悲观 | 第零档 | 1.2x（total 口径） | 12 亿 |\n| 中性（主） | 一档 | 3.5x（total 口径） | 35 亿 |\n| 乐观 | 一档 | 5.5x（total 口径） | 55 亿 |\n" + CONF + APPX,
     [], ["C1"], [], []),
    ("C1 折扣豁免：勾选近零增长折扣后低于下限放行",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 2.4x（total 口径）\n\n## 附件一：本报告落位示意\n\n| 修正系数逐项 | ☑ 近零增长折扣 ×0.65（1.6-2.4x） ☐ 无 |\n| 最终倍数 | 2.4x |\n" + CONF + APPX,
     [], ["C1"], [], []),
    ("C1 折扣豁免不恒真：模板未勾选折扣项不算上下文",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 1.0x（total 口径）\n\n## 附件一：本报告落位示意\n\n| 修正系数逐项 | ☐ 垂直赛道溢价 ×1.5-2（___）☐ 近零增长折扣 ×0.65（___）☐ 无 |\n| 最终倍数 | 1.0x |\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 SOTP：定档结果显式分段，各段行按自身档位核对",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：SOTP 分段——AI Platform 段三档 + 项目交付段第零档\n\n## 七、估值区间\n\n| 板块 | 档位 | 倍数 | 估值 |\n|---|---|---|---|\n| AI Platform | 三档 | 20x（agentic 口径） | 40 亿 |\n| 项目交付 | 第零档 | 1.5x（total 口径） | 3 亿 |\n" + CONF + APPX,
     [], ["C1"], [], []),
    ("C1 SOTP：分段行越档仍拦截（10x 超第零档 2× 容差）",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：SOTP 分段——AI Platform 段三档 + 项目交付段第零档\n\n## 七、估值区间\n\n| 板块 | 档位 | 倍数 | 估值 |\n|---|---|---|---|\n| AI Platform | 三档 | 20x（agentic 口径） | 40 亿 |\n| 项目交付 | 第零档 | 10x（total 口径） | 20 亿 |\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 模板样板句「混合形态标 SOTP 需拆分」不触发 SOTP 分支",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能（一句话依据；混合形态标 SOTP 需拆分；框架外情形：交易平台→不入本框架）\n\n## 七、估值区间\n\n| 情景 | 倍数 | 估值 |\n|---|---|---|\n| 中性（主） | 30x（total 口径） | 30 亿 |\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("R2：模板头部含「估值区间」不再截断数据区（原对模板报告只查前两行）",
     "# 测试公司估值报告\n\n*框架：四步：定档 → 查生死 → 质量分 → 估值区间*\n\n> **报告日期**：2026-09-02 ｜ **置信度**：中确信\n\n## 一、公司速览\n\n2025 年收入 12 亿元，毛利率 70%，客户 300 家。\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 3.5x（total 口径）\n" + CONF + APPX,
     ["R2"], [], [], []),
    ("C2：小数增速「65.0%」不再解析为 0%",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：三档·自研智能\n\n## 七、估值区间\n\n输入：增速 65.0%（g4）｜ 质量分 8.5\n\n倍数 40x（total 口径）\n" + CONF + APPX,
     [], [], [], ["C2"]),
    ("R6/R7：索引表 markdown 链接写法可解析",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 3.5x（total 口径）\n" + CONF + idx("2026 中报原文（第 32 页）", "[中报](https://www.hkexnews.hk/listedco/listconews/sehk/2026/0825/2026082500845_c.pdf)"),
     [], ["R6", "R7", "R9"], [], ["R6 hkexnews"]),
    ("R7：白名单按主机名后缀匹配，hkexnews.hk.evil.example 不得冒充",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 3.5x（total 口径）\n" + CONF + idx("2026 中报原文", "https://hkexnews.hk.evil.example/2026082500845_c.pdf"),
     ["R7"], [], [], []),
    ("R6：hkexnews 路径目录日期与文件名不一致 → 警告",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 3.5x（total 口径）\n" + CONF + idx("2026 中报原文", "https://www.hkexnews.hk/listedco/listconews/sehk/2026/0825/2026090100845_c.pdf"),
     [], [], ["R6 hkexnews"], []),
    # ── v1.15.1 第二轮对抗审查补充 ──
    ("C1 「同一档位」不算一档标签、「即三档」可识别",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：与 Harvey 同一档位，即三档·自研智能\n\n## 七、估值区间\n\n倍数 45x（total 口径）\n" + CONF + APPX,
     [], ["C1"], [], ["C1 未识别"]),
    ("C1 「降一档，定为二档」识别为二档",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：黄灯两条降一档，定为二档\n\n## 七、估值区间\n\n倍数 20x（total 口径）\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 「无需 SOTP」否定语境不进 SOTP 分支",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能（单一业务，无需 SOTP）\n\n## 七、估值区间\n\n倍数 30x（total 口径）\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 英文键 tier2 识别",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：tier2\n\n## 七、估值区间\n\n倍数 30x（total 口径）\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 旧标签「二档·自研型」按三档核对（v1.9.0 并档）",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·自研型（Cursor 类）\n\n## 七、估值区间\n\n倍数 20x（total 口径）\n" + CONF + APPX,
     [], ["C1"], [], []),
    ("C1 「30x（TTM 收入口径）」不再借 TTM 字样绕过",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能\n\n## 七、估值区间\n\n| 情景 | 倍数 |\n|---|---|\n| 中性 | 30x（TTM 收入口径） |\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 标题写法「## 第七章 估值」落入扫描范围",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能\n\n## 第七章 估值\n\n倍数 30x（total 口径）\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 标题写法「### 估值区间」落入扫描范围",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：二档·转售智能\n\n### 估值区间\n\n倍数 30x（total 口径）\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("C1 港股一档 g4 写 45x 拦截（识别市场+增速档取矩阵格）",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n**输入**：收入 10 亿（total 口径）｜ 档位 一档 ｜ 增速 80%（g4）｜ 质量分 7 ｜ 市场 hk\n\n倍数 45x（total 口径）\n" + CONF + APPX,
     ["C1"], [], [], []),
    ("R7：无 scheme 的官网 URL 仍按白名单放行",
     "# 报告\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 3.5x（total 口径）\n" + CONF + idx("金蝶官网投资者关系页（2025 年报 PDF）", "www.kingdee.com/ir"),
     [], ["R7", "R6"], [], []),
    ("R2：「**未披露清单**：→ 见第十章 DD Priority」行不再截断数据区",
     "# 报告\n\n## 一、公司速览\n\n**未披露清单**：→ **见第十章 DD Priority（逐条映射）**\n\n## 二、业绩表现\n\n毛利率 70%，客户 300 家。\n\n## 三、商业模式定档\n\n**定档结果**：一档·订阅\n\n## 七、估值区间\n\n倍数 3.5x（total 口径）\n" + CONF + APPX,
     ["R2"], [], [], []),
]

# ── estimate → 报告 → validate 回路：引擎合法输出不得被 C1 判硬错（第二轮审查案例 A-I）──
LABEL = {"tier0": "第零档·项目制", "tier1": "一档·订阅", "tier2": "二档·转售智能", "tier3": "三档·自研智能", "infra": "算力/Infra 段"}
ROUNDTRIP = [
    ("A 一档美股 g3 + 毛利 ×1.3", "tier1", 0.45, 6.5, "us", ["margin_high"]),
    ("B 一档美股增速 59% 档内插值上行", "tier1", 0.59, 6.5, "us", []),
    ("C 二档 g4 增速 90% 插值", "tier2", 0.9, 6.5, "hk", []),
    ("D 三档 g4 + 垂直 ×1.5", "tier3", 0.8, 8.5, "hk", ["vertical1.5"]),
    ("E 三档 g3 无修正", "tier3", 0.45, 6.5, "hk", []),
    ("F 第零档 g4 增速 100%", "tier0", 1.0, 6.5, "hk", []),
    ("G 三档 g4 + founder80", "tier3", 0.8, 8.5, "hk", ["founder80"]),
    ("H 算力段轻资产", "infra", 0.45, 6.5, "hk", ["asset_light"]),
    ("I 一档港股 g4", "tier1", 0.8, 6.5, "hk", []),
]


def engine(tier, growth, quality, market, corr):
    cmd = [sys.executable, SCRIPT, "--arr", "100", "--tier", tier, "--quality", str(quality), "--market", market, "--json"]
    if growth is not None:
        cmd += ["--growth", str(growth)]
    for c in corr:
        cmd += ["--corr", c]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout) if r.returncode == 0 else None


def band_of(g):  # 与 estimate.growth_band 同阈值
    return "g1" if g is None or g < 0.15 else "g2" if g < 0.30 else "g3" if g < 0.60 else "g4"


def roundtrip_report(tier, growth, quality, market, corr):
    out = engine(tier, growth, quality, market, corr)
    band = band_of(growth)
    cell = HK_MATRIX_TIER1[band] if (tier == "tier1" and market == "hk") else MATRIX[tier][band]
    m, label = out["倍数"], LABEL[tier]
    return ("# 回路测试\n\n## 三、商业模式定档\n\n**定档结果**：" + label + "\n\n## 七、估值区间\n\n"
            f"**输入**：收入 100（total 口径）｜ 档位 {label} ｜ 增速 {(growth or 0)*100:.0f}%（{band}）｜ 质量分 {quality} ｜ 市场 {market}\n\n"
            f"| 情景 | 档位 | 倍数 | 估值 |\n|---|---|---|---|\n| 中性（主） | {label} | {m['中位']}x（total 口径） | {m['中位']*100:.0f} |\n\n"
            f"## 附件一：本报告落位示意\n\n| 项 | 值 |\n|---|---|\n| 矩阵格 | {cell[0]:g}-{cell[1]:g}x |\n| 最终倍数 | {m['低']}-{m['高']}x |\n"
            + CONF + APPX), out


def run_all(mod, txt):
    r_e, r_w = mod.check_r(txt)
    c_e, c_w = mod.check_c(txt)
    s_e, s_w = mod.check_s(txt)
    return r_e + c_e + s_e, r_w + c_w + s_w


def has(msgs, prefix):
    return any(m.startswith(prefix) for m in msgs)


def main():
    mod = load_validate()
    print("===== test_validate: R5 评估集 + v1.15.1 回归用例 =====")
    ok_all = True
    for name, txt, must_err, no_err, must_warn, no_warn in CASES:
        errs, warns = run_all(mod, txt)
        problems = []
        for p in must_err:
            if not has(errs, p):
                problems.append(f"缺少硬错 {p}")
        for p in no_err:
            if has(errs, p):
                problems.append(f"误报硬错 {p}: " + "; ".join(e[:70] for e in errs if e.startswith(p)))
        for p in must_warn:
            if not has(warns, p):
                problems.append(f"缺少警告 {p}")
        for p in no_warn:
            if has(warns, p):
                problems.append(f"误报警告 {p}: " + "; ".join(w[:70] for w in warns if w.startswith(p)))
        if problems:
            ok_all = False
            print(f"  🔴 {name}")
            for p in problems:
                print(f"      {p}")
        else:
            print(f"  ✅ {name}")

    for name, tier, growth, quality, market, corr in ROUNDTRIP:
        txt, out = roundtrip_report(tier, growth, quality, market, corr)
        errs, warns = run_all(mod, txt)
        c1 = [e for e in errs if e.startswith("C1")] + [w for w in warns if w.startswith("C1 未识别")]
        if c1:
            ok_all = False
            print(f"  🔴 回路 {name}：引擎输出 {out['倍数']} 被 C1 误判")
            for e in c1:
                print(f"      {e[:90]}")
        else:
            print(f"  ✅ 回路 {name}：引擎输出 {out['倍数']} 通过 C1")

    # 模板自检：模板本身过 S 段必须 0 硬错（v1.15.0 模板自带 4 个 S5 禁词）；R2 对模板样板行不得报裸数值
    tpl = os.path.join(BASE, "templates", "evaluation-template.md")
    with open(tpl, encoding="utf-8-sig") as f:
        tpl_txt = f.read()
    s_e, _ = mod.check_s(tpl_txt)
    r_e, _ = mod.check_r(tpl_txt)
    r2 = [e for e in r_e if e.startswith("R2")]
    if s_e or r2:
        ok_all = False
        print("  🔴 模板 evaluation-template.md 自检有硬错：")
        for e in s_e + r2:
            print(f"      {e[:90]}")
    else:
        print("  ✅ 模板 evaluation-template.md 过 S 段 0 硬错、R2 对样板行 0 硬错")

    print(f"结果: {'✅ 全部通过' if ok_all else '❌ 有失败'}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
