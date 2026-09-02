#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_validate.py — validate.py 自检（R5 评估集，v1.7.0 补齐 skill-scorecard 扣分）
用法: python scripts/test_validate.py

职责: 固化「合格报告通过 / 造假报告拦截」两个基准用例，
      防止 validate.py 未来改动时误放行造假或误杀合格。

用例:
  GOOD — v1.7 完整格式报告（真实 URL + S 级已读标注 + 置信度 + 推理标注）→ 应 0 硬错
  BAD  — 造假报告（编造 URL → R6 + 非白名单标 S → R7 + 无已读标注 → R8）→ 应 ≥1 硬错

输出: PASS/FAIL，exit 0/1（提交前自检 / 可进 CI）
"""
import importlib.util
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_validate():
    path = os.path.join(BASE, "scripts", "validate.py")
    spec = importlib.util.spec_from_file_location("validate_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
| 一档·订阅 | 3-5x | 6-10x | 15-25x | 30-50x |
"""

BAD_REPORT = """# 造假测试报告（R6+R7+R8 三查应全拦）

【Step 1 · 定档】一档·订阅
【Step 2 · 生死关】✅ 通过
【Step 3 · 质量分】6/10
【Step 4 · 估值】$150M（15x × $10M ARR；方法=矩阵锚；假设=增速 20%；输入=ARR 10M）

## 来源索引

| [1] | 假招股书 | PDF | S | https://fake-hkex-pdf.example.com/fake.pdf |
| [2] | 新浪报道 | 文章 | S | https://finance.sina.com.cn/xxx |
"""


def main():
    mod = load_validate()

    r_err, r_warn = mod.check_r(GOOD_REPORT)
    c_err, c_warn = mod.check_c(GOOD_REPORT)
    s_err, s_warn = mod.check_s(GOOD_REPORT)
    good_hard = len(r_err) + len(c_err) + len(s_err)

    r_err2, r_warn2 = mod.check_r(BAD_REPORT)
    c_err2, c_warn2 = mod.check_c(BAD_REPORT)
    s_err2, s_warn2 = mod.check_s(BAD_REPORT)
    bad_hard = len(r_err2) + len(c_err2) + len(s_err2)

    print("===== test_validate: R5 评估集 =====")
    ok = True
    if good_hard == 0:
        print("  ✅ GOOD 合格报告通过（0 硬错）")
    else:
        ok = False
        print(f"  🔴 GOOD 合格报告被误杀（{good_hard} 硬错）:")
        for e in r_err + c_err + s_err:
            print(f"      {e}")
    if bad_hard >= 1:
        print(f"  ✅ BAD 造假报告被拦截（{bad_hard} 硬错）")
        for e in r_err2 + c_err2 + s_err2:
            print(f"      {e}")
    else:
        ok = False
        print("  🔴 BAD 造假报告未被拦截（0 硬错）——R6/R7/R8 可能失效")
    print(f"结果: {'✅ 全部通过' if ok else '❌ 有失败'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
