# Wind 数据访问配方（锚带刷新 / 行情核实）

> 2026-09-02 实测可用。wind-mcp-skill（hub 安装）在本 profile 直接可用——**API key 全局共享，无需 per-profile 配置**。排查「WIND_API_KEY 未配置」时先查全局 config，不要只看环境变量。

## key 位置（三层查找，cli.mjs getApiKey 逻辑）
1. **用户全局**：`~/.wind-aifinmarket/config`（内容 `WIND_API_KEY=...`）——本机 2026-07 已配，**所有 profile 共享**（tuanzi/writer/maliang 共用）
2. skill 本地：`<wind-mcp-skill>/config.json`（`{"wind_api_key": ...}`）
3. 环境变量 `WIND_API_KEY`

`node cli.mjs setup-key <KEY> --scope global|skill` 可写；全局 scope 写 `~/.wind-aifinmarket/config`。

## CLI 形态
```bash
node <wind-mcp-skill>/scripts/cli.mjs call <server_type> <tool_name> '<json>'
node <wind-mcp-skill>/scripts/cli.mjs list-tools <server_type>
```
- server_type：`stock_data`（行情/财务/股本/事件——锚带刷新主力）
- 常用工具：
  - `get_stock_price_indicators`：参数 `windcode`（逗号串）+ `indexes`（**必须是英文逗号分隔字符串，不是数组**；`总市值` 不在指标清单里——要市值走 fundamentals）
  - `get_stock_fundamentals`：参数 `question`（自然语言，required）+ `windcode`（逗号串）——返回 `最新总市值(亿元)`、`最新收盘价`、`最新营业收入_TTM` 等
- 输出为 JSON envelope：`d['content'][0]['text']` 内层再 json.loads → `data.data[0].rows/columns`

## 锚带 PS 计算（Wind S 级口径纪律）
PS = 最新总市值 ÷ 最新营业收入_TTM，**币种对齐**：
- 港股：市值 HKD ÷ TTM 收入（按公司记账本位币 CNY/HKD/USD）——换算 HKD×0.92≈CNY、USD×7.15≈CNY（2026-09 汇率，发布前重核）
- 美股：市值 USD ÷ TTM 收入 USD 直接除
- **锚点校准一律 Wind TTM PS；web 二手站（financecharts/companiesmarketcap/TIKR）NTM/EV/forward 口径混用可差 20-50%，只作方向参考不作数值**（2026-09-02 实证事故：Atlassian web 报 5.9x 实为 7.2x、Datadog web 报 11.4x 实为 21.9x、Workday web 报 5.28x 实为 4.7x——误判「SaaS 压缩年」被 Wind 推翻回滚，详见 definitions.md §10）

## 实例（已验证，2026-09-02）
拉港股锚带市值+收盘：
```
node cli.mjs call stock_data get_stock_fundamentals '{"question":"金蝶国际00268.HK 金山软件03888.HK 当前总市值和最新收盘价？","windcode":"00268.HK,03888.HK"}'
```
拉 TTM 收入：question 用「最近报告期营业收入（TTM）是多少？」→ 列 `最新营业收入_TTM`（附报告截止时间列）。

## refresh_comps.py 衔接
`scripts/refresh_comps.py` 内置 Wind 拉数 + 失败保留旧快照容错；cron 每月 1 日自动跑。手动跑前确认 key 可达（本配方第一节）。
