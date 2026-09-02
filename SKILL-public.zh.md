---
name: ai-app-valuation
description: "Valuation scoring for AI application companies (non-model-layer, non-hardware). Four steps: tier → moat check → quality score → valuation range. Deterministic arithmetic via estimate.py. Triggers: 'value this AI company', 'how much is XX worth', 'score this AI app startup'."
version: 1.15.1
author: open-source contributors
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [investing, valuation, ai-app, scoring]
    related_skills: [investment-deep-dive, wind-mcp-skill, gzh-data-rigor]
---
*：早期投资人看 AI 应用公司的入场前 30 分钟快速估值工具（对齐公众号 X4 四维度：能力→收费→财务→死因）。输入公司名/BP/公开数据 → 输出「定档 + 生死关 + 质量分 + $估值区间」一页纸评分卡。
> **与 investment-deep-dive 分工**：本 skill 先跑（快速估值打分），分数高才进 deep-dive 完整尽调。
> **数据纪律继承**：信源分级 S/A/B/C/D、[N] 可溯源、效验流程——对齐 investment-deep-dive。
> **📖 查表**：语义定义 → `references/definitions.md`；锚点带源 → `references/comps-source.md`；报告模板 → `templates/evaluation-template.md`。

## When to Use

- 目标标的 = AI 应用公司（有收入、卖智能/功能/结果的软件公司）
- **Not for**：模型层（战略期权逻辑）、AI 硬件/机器人、无收入纯早期（走 investment-deep-dive）、**交易平台/人力外包/硬件转售/AI 驱动资产运营商**（四类框架外 → definitions.md §11）

## Examples（话术 → 流程，v1.7.0）

- 「给 Harvey 估值」→ Step 1 定档三档（后训练+法律数据飞轮+高切换成本）→ Step 2 生死关 ✅ → Step 3 质量分 8.5 → Step 4 `estimate.py --tier tier3 --growth 0.8 --quality 8.5` → $15.7-17.5B（vs 实际 $15.5B，误差 <2%）
- 「看看这个 AI 客服项目值不值」→ 定档二档·转售智能（无自研）→ 生死关 ⚠️ 价格战（行业红海）→ 质量分 5 → 转售档毛利锁死 6-10x → 增速再高过不了 10x（Liblib 实证）
- 「给极视角估值」→ 定档前先读招股书（自研率 9.8% → 平台聚合二档·转售智能，不是自研型）→ 框架 3-16 亿 vs 市场 105 亿 → 偏离分析：低流通盘泡沫（真实流通 10% + Pre-IPO 3.9 倍）

## 使用流程（四步 + 披露充分性前置）

```bash
python scripts/estimate.py --arr 100 --tier tier1 --growth 0.4 --quality 6.5
```

```
输入公司名/BP → Step 0.5 披露充分性（充分→四步 / 部分→标推断 / 不足→降级只给定档+生死）
→ Step 1 定档（收入单位实证 + 两维判据）
→ Step 2 查生死（五死因：1 致命=Pass / 2+黄灯=降档）
→ Step 3 质量分（七指标含爬升检验，每维必填 Key evidence/Main risk）
→ Step 4 estimate.py 估值（矩阵 + 增速插值 + 修正系数）
```

## Step 1 · 定档（收入在卖什么）

**判据**：两维——①价值来源（软件功能 vs 模型智能本身）②成本结构（COGS 是否随用量涨）。毛利只做交叉验证。**定档前先实证收入单位**（seat/token/outcome/项目，来源：官网定价页 > 业绩会原话 > 招股书分部 > 年报收入确认附注——细节 → references/definitions.md B 段）。

| 档位 | 定义 | 判据 | 毛利交叉验证 |
|---|---|---|---|
| 第零档 | 项目制（卖交付/人天，含沉淀定性） | 按项目收费、交付制 | 服务~人力级 |
| 一档 | 租功能（订阅/seat） | 卖软件功能，COGS 不随用量涨 | 软件级 70-80% |
| 二档·转售智能 | 转售第三方模型（聚合/API 差价），无自研 AND 无强入口 | 价值=模型智能但无自研，赚差价 | 转售级 <30-40% |
| 三档·自研智能 | 自研模型 **OR 强分发入口**；档内双判据（飞轮闭环+高切换成本）定位上下沿 | 下沿=有自研/入口但飞轮不成立；上沿=飞轮闭环 且 高切换成本（≥2 来源） | 混合~软件级 60%+ |

**典型锚**：Liblib（无自研无入口）→ 二档 4-8x；Cursor（自研+入口但无飞轮）→ 三档下沿 15-25x；Harvey（法律数据飞轮+流程嵌入）→ 三档上沿 40-50x。

**四条必须先拆再估的红线**（详见 definitions.md §1）：
1. 毛利 <10% 大额收入段 = 流量代销 → 剔除（迈富时教训）
2. 毛利 15-25% 大额收入段先问 gross 还是 net → 净额法重估（汇量教训）
3. 混合型公司必须 SOTP → 整体毛利/增速是混合结果
4. 按效果付费 + 总额基准 + 采购过手 → 强制净额重估，禁止总额收入直接吃软件倍数（明略教训）

**自研率定档硬判据（极视角事故教训）**：「自研 vs 聚合」不能凭公司叙事猜——上市公司定档前必须实际读招股书/年报的算法构成与收入模式段（S 级）。自研率 <30% = 平台聚合 → 二档（毛利锁死）；>60% = 自研型；介于之间看后训练深度。

**第零档专项：项目制四步拆解**：①拆收入结构（重复 vs 一次性——只有重复部分上倍数）②重复部分按档位定价（席位 5-8x/用量 3-6x/结果 10-15x）③分部加总+转型折溢价 ④看沉淀（验收单/组件/垂直数据/know-how）。**有沉淀量化判据**：重复收入 >30% 或 复购 >50% 或 有产品资产。→ definitions.md §2。


**「公司自称的商业模式」≠「会计确认的收入结构」**——范式「Agentic RaaS 实为探索」、迅策「Token 第一股实为项目制向 Token 探索中」、海致「AI 公司实为 97.4% 验收制项目」都是没读原文被自称带偏的教训。**上市公司定档前必须读财报原文完成三查，转述只配当线索，不允许把定档证据丢进 DD Priority**：

1. **查收入确认时间分类**（年报/中报「收入确认」附注——项目制 vs 订阅的分水岭）：
   - 按**时间点确认**（验收/交付制）占比 >70% → 项目制（第零档），哪怕公司自称 SaaS/AI 平台
   - 按**随时间推移确认**（持续服务/订阅）占比 >50% → 订阅可上一档
   - 案例：海致 1H26 时间点确认 97.4%（第 32 页）→ 第零档坐实
2. **查分部收入拆分原文**（Token/订阅/智能体占比到底多少，不是管理层指引）：
   - 案例：迅策中报原文「Token 业务收入占比突破 10%」（第 17 页）≠ 盈喜暗示的 20-30%；管理层原文「从项目制、订阅制向探索按 Token 业务」（第 26 页）= 迁移早期
3. **查管理层对商业模式的自我表述**（是否说「探索中/推进中/早期」——是则按当期结构估值，新业务只作爬升检验期权）：
   - 新业务/自称平台占比 <15% → 不给独立档位估值，只作爬升检验信号（群核 AI 新应用 <4% 教训——基数太小增速无意义）

**配套（写入每份报告）**：
- 定档段必须写「收入单位实证（中报原文第 X 页，S 级已读）」+ 时间点/随时间拆分数字
- 报告必附「估值矩阵 + 档位定义」附件（读者能独立理解——见模板 v1.12.0 附件段）
- 质量分每指标给 Key evidence + Main risk（禁止只给分数无依据）
- **未上市（无财报）标的**：三查第 1 查做不了 → 改语言时态判别（「进入/将/更像」= 未来时态自称 = 期权非当期；访谈项目交付词 vs 订阅/按量词交叉）——详见 case-fabarta-2026-09

## Step 2 · 查生死（五死因，先判生死再看质量）

1. **概念热（需求真伪）**：真实付费需求 or 概念热度？
2. **无存量预算（预算来源）**：客户原本有预算科目吗？（替换=有存量；新创=慢死）
3. **单点功能**：三条件必须同时满足才算致命（价值无沉淀 + 零切换成本 + 闭源依赖）——**开源基座 ≠ 单点功能风险**；留存率 <30% 是量化证据 → definitions.md §5
4. **价格战三型**：行业红海→致命 / 主动降价获客→观察 / **毛利下滑≠价格战（先归因再判定）**
5. **责任链两要件**：可归责 + 可补救。缺一 = 断裂（医疗/法律/金融高危）

**处理**：命中 1 条致命 → 直接 Pass；命中 2+ 条黄灯 → 降一档估值。
**NDR 拆解纪律（X4）**：NDR 涨先问哪部分涨（客户数留存涨=真好；单客户用量涨=看毛利扛不扛得住）。披露不可得 → 写「未披露，需 IR」，不编数。
**壳层≠必死修正（X2）**：死的是「停在第一层」的公司不是套壳本身——判断生死看是否在**加厚**，不是看今天是不是壳。

## Step 3 · 质量分（七指标，0-10 分）

| 指标 | 一句话口径 | 高分 | 低分 |
|---|---|---|---|
| 智慧自有率 | 后训练级以上自有模型承担的推理占比 | 六成+ | 三成- |
| 单位结果成本趋势 | 结果单元成本环比（先定义结果单元） | 持续降 | 持平/升 |
| IER（推理成本÷收入） | 推理支出 ÷ 收入（inference API+GPU 折旧+训练摊销）——越小越好 | <20% 且降 | >33% |
| 数据回流 | 产品设计成「数据→训练→增强」闭环 | 设计回流 | 用完即走 |
| 归因资产化 | eval/独占数据/可导出权重 ≥2 | 三者至少二 | 全无 |
| 护城河层数 | 品牌/数据/规模/网络效应/切换成本/独占资源 | 4 层+ | 1-2 层 |
| **爬升检验** | 收入结构是否向高档迁移（token→outcome）——动态斜率 | 真爬（有证据） | 嘴爬（BP 写满十年不动） |

**打分纪律**：每维必须填「Key evidence / Main risk」再打分——禁止只填分数。MECE 整合（v1.15.0）：账本三核查（IER/训练推理配比/现金流质量，判断刻度）+ 质量七指标（0-10 分），两组正交无重复——先扫「在不在资产化」再评「好不好」。
**⚠️ 已知缺口（case-dipu 反馈）**：①盈利拐点未进七指标（Q2 单季盈利对生死关/估值修正力强）②「有沉淀第零档」与「二档纯转售」之间缺中间档——待办，详见 case-dipu。

## Step 4 · 估值（estimate.py，确定性计算）

**估值矩阵（档位 × 增速，v1.12 修正版）**：

| 档位 \ 增速 | <15% | 15-30% | 30-60% | >60% |
|---|---|---|---|---|
| 第零档·项目制（含沉淀定性） | 0.5-1.5x | 1.5-2x | 1.5-2.5x（硬锚） | 2.5-3.5x ⚠️推断格（增速期权≈0） |
| 一档·订阅 | 美股 3-5x | 美股 6-10x | 15-25x | 15-25x（海外推断）/ **4-6x（港股锚带 g4，v1.7.12 实测）** |
| 二档·转售智能（无自研/弱自研） | 3-5x | 5-8x | **5-8x** | **5-8x**（铁锚——增速期权≈0；v1.12 修正倒挂：g3/g4 对齐） |
| 三档·自研智能（自研 OR 强入口，档内飞轮/切换成本插值） | 5-8x | 8-15x | 15-25x（硬锚） | 15-50x（质量<7 下沿 15-25x / 7-8 中带 25-40x / ≥8 上沿 40-50x——estimate.py 档内双锚独立分层，v1.13.4） |
| 算力/Infra（--tier infra） | 5-10x | 5-10x | 5-10x | 5-10x（轻资产 --corr asset_light 15-25x） |

> ⚠️ = 推断格。锚点明细 → `references/comps-source.md`（SKILL 不内嵌时点数据）。增速插值 estimate.py 自动。毛利调节（必叠）：<40% ×0.7 / 40-55% ×1.0 / 55%+ ×1.3。市场锚带：默认港股；明确美股公司用 `--market us`。
>
> 一档美股带 Wind 校准勿动（3-5x/6-10x/15-25x）；口径教训 → definitions.md §10。
>
> ⚠️ 矩阵单调性纪律：同档 g1→g4 倍数必须单调不减（tier2 倒挂教训）——「高增速格比低增速格便宜」= 视觉倒挂。改矩阵后逐档查单调再 commit；增速不可信用 ⚠️ 标注，不用数字倒挂。

**修正系数**：
- **同赛道对照法（X4）**：同赛道跨公司对照 > 同公司 SOTP 拆解（Sierra ~100x vs Freshworks 3.95x）。**⚠️ 对照倍数差必须先排除增速变量**（Sierra ARR 一年 5 倍 vs Freshworks +16%——增速差本身解释了大半倍数差；正确归因链：先承认增速差 → 再论证增速差源于商业模式 → 最后才归因商业模式）
- 垂直赛道溢价 ×1.5-2：**三条件判据**——高客单价 + 高切换成本 + 强合规壁垒（法律/金融/搜索/医疗 ✅；客服/办公 ❌）
- 创始人/战略溢价：上沿 80x（Sierra 级）——顶级创始人 + 战略买家托底，缺一不可
- 模型层单列（一级 P/ARR → comps-source.md §模型层单列，不混入应用矩阵）；**模型层期权纪律**：有自研模型 ≠ 给模型层倍数——需三档迁移可验证证据，否则期权=0 → definitions.md §12
- 混合型公司（MiniMax 型/金山型）：按收入结构拆段估值

**使用纪律 12 条（标题速查，查 definitions.md）**：
1. 档位决定天花板：二档纯转售增速期权≈0（Liblib +3000% 也只 6.7x）
2. 增速决定同档内位置：一档最敏感（12%→4x vs 33%→21x）
3. 质量分调节：≥8 上沿 / 6-8 中带 / <6 下沿
4. 锚点校准问句（同档内）：禁止跨档比较
5. 超限告警：超出矩阵上限 → 脚本提醒
6. 第零档×增速>60% 无样本：按 g3 上限或转下沿，标注边界
7. 负增长 SaaS：g1 下沿再打折（×0.5-0.7）或转利润 PE；**近零增长（增速 <5%）按负增长边缘 ×0.65 打折（v1.13.7 群核裁决——1.5% 增速给 2.5-4x 下沿再 ×0.65 → 1.6-2.4x；报告 C1 需有折扣上下文豁免词「折扣/负增长/近零」避免误报估值链断裂）**
8. **框架边界（X4）**：矩阵给的是**定位，不是定价**——框架价值在看偏离，报告必须附「偏离分析」段
9. 锚带校准三元验证：每家公司核对 PS+增速+商业模式三要素，剔除异常值，标注 ✅实证/⚠️推断/❌反例
10. **Forward 估值纪律**：估值输入必须用 2026E 预测收入（市场 consensus，禁止自造），执行前显式标注 `--period 1h26|2026e`
11. **倒算市场隐含 PS**：高增速公司定档前先倒算（市值 ÷ 各口径收入，必须用 forward 口径）；市场隐含价≈框架下沿时不能轻易喊低估
12. 港股/美股双轨锚带：港股 SaaS 的 PS 与增速几乎不挂钩（确定性定价），市值 <50 亿剔除样本

**按用量（token/API）定价规则 → definitions.md §3**：先问 gross/net → 低毛利转售（<30% 模型差价，Liblib 6.7x 锚）/ 高毛利转售（60-70% 路由抽成）/ 中间态+高增速（Cursor 早期 54-100x 生态溢价）→ 自研模型（15-22x）→ 模型层单列。**推理平台（Baseten/Together/Fal）不入应用层锚**（卖算力是基础设施层）。
**算力/Infra 段 → definitions.md §9**：自持/纳管算力 + Token 按量 + 异构调度技术（范式 API = 无问芯穹型）——SOTP 单列，重资产 5-10x / 轻资产 15-25x（国内校准：优刻得 7.57x）。

### SOTP 分段纪律（多业务公司必做）

混合型（订阅+项目+Agentic 等）必须 SOTP 分段估值——整体毛利/增速是混合结果会骗人（第四范式教训：API+860% 只占 12.3%，Agentic「RaaS」自称订阅实为探索）。各段独立定档 × 独立倍数 → 加总。**自称商业模式 ≠ 会计确认结构**——定档前先做三查（见 Step 1）。

## 数据纪律（红线清单，细节 → references/definitions.md）

### 披露充分性（Step 0.5）
进估值前先评估披露充分性，决定四步走到哪（→ definitions.md §7）：充分→正常四步 / 部分→标注推断 / 不足→**降级输出**（只给定档+生死关，不给估值或宽区间）。
**三态标注铁律（防 AI 脑补）**：每个判断标「已披露可证 / 推断 / 缺失」；缺失维度**禁止给具体数字**，只能写「未披露，需 DD/调研」；推断必须带依据。

**① 招股书 + 年报（S 级）——必须直接读原文** → **② 券商研报（B 级）** → **③ 财经新闻（C/B 级）**（只做交叉验证，不能作为关键数据唯一来源）。
- 审计财务数据（净资产/流动比率/负债/毛利率/留存率）必须标招股书 S 级，媒体转述只做交叉验证（海致教训）
- 招股书下载本地全文检索（pymupdf 读 PDF），关键数字标页码


**索引表每条来源必须有真实可访问 URL**——招股书/中报/研报/新闻全部可点开复核，禁止「—」占位。S 级来源给官方链接（hkexnews PDF / Wind / sec.gov）；B 级研报给公开转载链接（证券时报/新浪/发现报告等可访问页）或报告原文。**「来源是转述」不是「不给链接」的理由**——转述也要指向转述来源的页面。validate R9 检查，缺 URL = 硬错。

****次新股（上市 <12 个月）市场估值含流通盘稀缺溢价，非均衡价——禁止作锚**（definitions.md §8）；收购价 ≠ 公允倍数（控制权溢价）。**可用锚 = 已解禁**（判据：锁定窗口已过，非上市时长：普通主板 Rule 10.07 六个月 vs 18C 十二个月）——范式/金蝶/中软 + 一级 Harvey/ElevenLabs/Liblib；聚水潭 2026-04-21 解禁 ✅。完整锚点清单 + 港股解禁四要素分析 → `references/comps-source.md` + `references/listing-float-analysis.md`（8.05(1)/8.05(3) vs 18C 判定、基石解禁日、自由流通 <15%）。

### 次新股中报重估触发点（v1.9.1）
次新股（上市 <12 个月）的首份中报/年报 = 估值重置时点：①增速口径必须更新（招股书数据 → 1H26 实际 + 全年指引）②AI 业务占比是重估第一变量（爬升检验从嘴爬变真爬）③盈利拐点普遍出现 → 生死关缓解 ④但倍数上限硬锚没动（自研率/流通盘/AI 含量）⑤市场已重新定价——偏离分析前必须先拉最新市值。名单见数据纪律段

### 关键数据门禁 / 口径坑（细节 → references/definitions.md）

- 估值/ARR/增速/倍数 ≥2 个 A/B 级独立来源，否则「单源待验证」
- 4 要素口径（时间/单位/计算/市场）；ARR 必须写口径（total/B2B/agentic）
- **时点错配双向坑**：新估值÷旧 ARR=假贵（Sierra）；旧估值÷新 ARR=假便宜（Glean）
- 留存率/获客成本标口径+时点（客户数留存≠NDR；销售费÷新增客户≠CAC）
- AI 转述数字先搜再降级；查不到相对化不挂 [N]

### 置信度标注
高确信（A/B 双源）/ 中确信（单源外推）/ 低确信（推算/单源）；估值区间默认中确信

### 效验流程（产出报告后必跑——v1.14.0 升级）

1. **validate.py 三段校验**（必跑，硬错 = 未通过）：R6 URL 真实性 / R7 S 级白名单 / R8 已读标注（查来源行描述指明读了什么，不再要求专门「读取状态」段）/ R9 来源必带真实 URL / C1 估值链一致 / D0 附件零必含 / D0b 收入确认拆分 / **S5 元解释句禁词硬错（MECE/正交/读取状态/免责声明等）+ S6 装饰性 emoji 硬错（🔴⚠️✅❌☑ 语义/表单符号豁免，📖🚀🎨 等装饰禁）+ S7 金额两位小数提示（财报原文可保留，估值判断值须 1 位小数）**
2. **D0 附件零硬性要求（v1.14.0）**：报告必附「估值矩阵 + 档位定义」附件（读者独立理解）；定档段必须写「收入单位实证（财报原文第 X 页）」+ 时间点/随时间拆分数字
3. **自检**：`python scripts/test_estimate.py`（引擎 43 用例）+ `python scripts/test_validate.py`（校验器基准）——全过 = 安装完好

### 数据与隐私边界
- BP/招股书仅本地处理，不上传外部服务


## 输出格式（详见 templates/evaluation-template.md v1.12.0）

**报告十章节 + 附件体系**（完整模板在 templates/，这里只列骨架）：
执行摘要 → 一速览 → 二业绩（拆分+迁移）→ 三定档（时点法+档位表）→ 四能力栈（六层定性）→ 五财务核查+质量七指标 → 六五死因 → 七估值区间 → 八偏离（港股含解禁）→ 九 IC Thesis → 十 DD+Watch
**报告纪律**：禁装饰性 emoji / 数据只出现一次 / 金额 1 位小数 / 公司汇报货币 / 去元解释句（禁 MECE 分工/读取状态/免责声明——R8 改版查来源行描述）。





## Files

- `scripts/estimate.py` — deterministic valuation engine (matrix + growth interpolation + corrections + over-limit warning)
- `scripts/validate.py` — three-pass report validation (source authenticity / valuation chain / confidence)
- `references/definitions.md` — semantic definitions (tier / death causes / quality metrics / anchoring rules / **data-desensitization checklist**)
- `references/comps-source.md` — anchor company detail (every multiple traceable to a real transaction)
- `references/anchor-calibration.md` — anchor band calibration methodology
- `templates/evaluation-template.md` — report template (chapters 1-10 + appendix matrix + appendix anchors)
- `assets/valuation-matrix.png` — matrix chart

## Data & Privacy (data-desensitization checklist)

When analyzing companies with non-public data (BP, prospectus PDFs, internal notes):

1. **Keep local**: BP/prospectus files are processed locally, never uploaded to external services
2. **De-identify customer names**: report client names only when already public (annual report/10-K); otherwise use 'Customer A in {industry}'
3. **Mark non-public numbers**: unpublished financials must be marked 'internal, not for distribution'
4. **No raw sensitive data in reports**: exclude unreleased revenue, internal costs, or personnel data from any published report
5. **Source state disclosure**: every [N] source states its read-state in words (read original / via citation / unopened) — validate S6 rejects 📖-style emoji in reports
