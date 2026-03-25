# OpenClaw Emergency Ops

**AI-powered alert orchestration for trading systems, automation jobs, crawlers, and small infrastructure.**

**面向交易系统、自动化任务、爬虫和小型基础设施的 AI 告警编排系统。**

---

## Overview | 项目简介

OpenClaw Emergency Ops is a lightweight incident orchestration backend focused on alert understanding, severity routing, escalation, operator response, and auditability.

OpenClaw Emergency Ops 是一个轻量级应急编排后端，重点解决：

- 事件理解
- 严重度分级
- 多渠道升级通知
- 第二联系人升级
- 操作员确认与延后处理
- 动作执行闭环
- 时间线与审计记录

This repository is the community edition MVP. It is designed for operators and developers who need a simple, self-hosted alert orchestration layer without adopting a full on-call or observability platform.

本仓库提供的是社区版 MVP，适合希望自托管一个“告警编排层”的开发者和运维人员，而不是引入完整 on-call 或 observability 平台的团队。

---

## Why this project exists | 为什么做这个项目

Most alerting tools stop at sending a message.

OpenClaw Emergency Ops goes one step further:

- explain what happened
- highlight the impact
- assess urgency
- escalate automatically
- involve a secondary contact when needed
- support operator actions
- preserve a full response timeline

大多数告警工具停留在“发一条消息”。

OpenClaw Emergency Ops 更关注告警后的响应闭环：

- 解释发生了什么
- 说明影响范围
- 判断紧急程度
- 无人响应时自动升级
- 必要时通知第二联系人
- 支持操作动作执行
- 保留完整处理时间线

---

## What this project is | 项目定位

OpenClaw Emergency Ops is an orchestration layer for vertical scenarios such as:

- quant and trading bots
- crawlers and scheduled jobs
- automation pipelines
- self-hosted services
- lightweight internal incident workflows

OpenClaw Emergency Ops 面向以下垂直场景：

- 量化交易与自动化交易机器人
- 爬虫与定时任务
- 自动化流水线
- 自托管服务
- 轻量级团队应急流程

### Non-goals | 非目标

This project is not:

- a full PagerDuty replacement
- a full observability platform
- a full on-call scheduling system
- a general-purpose metrics/logs/traces product

本项目不是：

- PagerDuty 替代品
- 完整 observability 平台
- 完整 on-call 排班系统
- 通用指标 / 日志 / 链路追踪平台

---

## Current MVP capabilities | 当前 MVP 能力

- FastAPI-based event ingestion
- severity-based routing
- AI-style incident summaries
- initial alert dispatch
- first escalation
- second contact escalation
- acknowledge workflow
- snooze workflow
- action execution with dry-run-by-default handlers
- event detail aggregation
- timeline and audit trail
- Apprise-based notification delivery
- Telegram-validated notification setup
- Docker Compose local deployment
- demo flow script

当前 MVP 已实现：

- 基于 FastAPI 的事件接入
- 按严重度分级路由
- AI 风格事件摘要
- 初始告警发送
- 一级升级通知
- 第二联系人升级通知
- acknowledge 确认流程
- snooze 延后流程
- 默认 dry-run 的动作执行器
- 事件详情聚合
- timeline 与审计记录
- 基于 Apprise 的通知发送
- 已验证 Telegram 通知配置
- Docker Compose 本地部署
- 演示脚本

### Important note on AI summaries | 关于 AI 摘要的说明

The current community edition uses a local summary engine to generate structured, human-readable incident summaries. The summary layer is intentionally designed so it can later be replaced with an LLM-backed implementation.

当前社区版使用本地摘要引擎生成结构化、可读的事件摘要；这一层已经抽象好，后续可以替换为真正的 LLM 总结服务。

### Important note on actions and voice calls | 关于动作执行与电话通知的说明

- Action execution is webhook-based and runs in dry-run mode unless real action endpoints are configured.
- Voice-call delivery is currently exposed through an adapter layer and behaves as a simulated path unless a real OpenClaw Voice Call endpoint is configured.

- 动作执行基于 webhook 适配器；如果没有配置真实动作端点，默认以 dry-run 模式运行。
- 电话通知当前通过适配层暴露；如果没有配置真实 OpenClaw Voice Call 端点，则默认以模拟方式演示。

---

## Architecture | 技术架构

### Core components | 核心组件

- **FastAPI** — API and event ingestion
- **PostgreSQL** — persistent storage
- **Redis** — task broker / backend
- **Celery** — delayed escalation tasks
- **Apprise** — notification delivery
- **Alembic** — database migrations

### Internal services | 内部服务模块

- `event_service` — event lifecycle management
- `severity_engine` — severity evaluation
- `summary_service` — incident summarization
- `notification_service` — notification dispatch
- `routing_engine` — contact and channel resolution
- `escalation_engine` — delayed escalation logic
- `action_executor` — action execution pipeline
- `timeline_service` — timeline aggregation
- `audit_service` — audit log generation

---

## Key API endpoints | 主要接口

```text
POST /api/v1/events
POST /api/v1/events/{event_id}/acknowledge
POST /api/v1/events/{event_id}/snooze
POST /api/v1/events/{event_id}/actions/{action_name}
GET  /api/v1/events
GET  /api/v1/events/{event_id}
GET  /api/v1/events/{event_id}/timeline
GET  /api/v1/health
```

---

## 5-Minute Demo | 5 分钟演示

### 1. Clone the repository | 克隆仓库

```bash
git clone https://github.com/<your-org>/openclaw-emergency-ops.git
cd openclaw-emergency-ops
```

### 2. Create local config | 创建本地配置


cp .env.example .env


For fast local verification, set:


ESCALATION_FIRST_WAIT_SECONDS=10
ESCALATION_SECOND_WAIT_SECONDS=20


如需本地快速验证升级链，建议设置：


ESCALATION_FIRST_WAIT_SECONDS=10
ESCALATION_SECOND_WAIT_SECONDS=20


### 3. Start the stack | 启动服务栈


docker compose up --build


### 4. Check health | 健康检查


curl http://localhost:8000/api/v1/health


### 5. Run the demo flow | 运行演示脚本


./scripts/demo_flow.sh


The demo script will:

- create an event
- acknowledge it
- snooze it
- execute `pause_strategy`
- query event detail
- query timeline
- print worker logs

演示脚本会：

- 创建事件
- acknowledge
- snooze
- 执行 `pause_strategy`
- 查询 event detail
- 查询 timeline
- 打印 worker 日志

---

## Telegram setup | Telegram 通知配置

Notification delivery is handled through Apprise. Telegram has been validated in local demo flows, and other Apprise targets can also be configured.

通知发送通过 Apprise 实现。Telegram 已在本地演示流程中验证，其它 Apprise 目标也可以通过配置接入。

### Example .env configuration | .env 示例配置


DEFAULT_PRIMARY_APPRISE_TARGETS=tgram://<BOT_TOKEN>/<CHAT_ID>/
DEFAULT_SECONDARY_APPRISE_TARGETS=tgram://<BOT_TOKEN>/<CHAT_ID>/


### Setup steps 

1. Create a bot with BotFather
2. Send the bot a message such as `/start`
3. Obtain your Telegram `chat_id`
4. Update `.env`
5. Restart the stack
6. Send a test event and verify delivery

### 配置步骤

1. 通过 BotFather 创建 Telegram bot
2. 先给 bot 发一条消息，例如 `/start`
3. 获取 Telegram `chat_id`
4. 更新 `.env`
5. 重启服务
6. 发送测试事件并确认消息送达

### Why multiple Telegram messages may appear | 为什么会收到多条 Telegram 通知

If the primary and secondary contacts point to the same Telegram chat, you may receive:

- initial alert
- first escalation
- second contact escalation

This is expected during local testing and usually means the escalation chain is working as designed.

如果主联系人和第二联系人配置到了同一个 Telegram chat，你可能会连续收到：

- 初始通知
- 一级升级通知
- 第二联系人通知

这在本地测试阶段是正常现象，通常说明升级链正在按预期工作。

---

## Example event payload | 示例事件载荷

{
  "source": "quant-engine",
  "event_type": "max_drawdown_breach",
  "title": "Max drawdown exceeded threshold",
  "message": "Strategy BTC_PERP_01 breached max drawdown limit",
  "severity_hint": "critical",
  "metadata": {
    "strategy_id": "BTC_PERP_01",
    "exchange": "Binance",
    "drawdown_pct": 8.7,
    "pnl": -1240.55
  },
  "suggested_actions": [
    "pause_strategy",
    "close_positions"
  ]
}


---

## Example workflow

1. A service posts an event to the API
2. The backend classifies the event severity
3. The summary layer generates a human-readable incident brief
4. The primary contact receives the initial notification
5. If unacknowledged, the first escalation is triggered
6. If still unresolved, the secondary contact is notified
7. Operators can acknowledge, snooze, or execute actions
8. Every important step is recorded in the event timeline

### 示例流程

1. 外部系统通过 API 提交事件
2. 后端判断事件严重度
3. 摘要层生成可读的事件简报
4. 初始通知发送给主联系人
5. 如果无人确认，触发一级升级
6. 如果仍未处理，通知第二联系人
7. 操作人员可以 acknowledge、snooze 或执行动作
8. 所有关键步骤都会写入事件 timeline

---

## Demo scenarios | 演示场景

This repository is currently suitable for demonstrating:

- initial alert dispatch
- first escalation
- second contact escalation
- immediate acknowledge flow
- snooze and delayed escalation
- action execution
- event detail inspection
- timeline and audit inspection
- Telegram notification delivery

当前仓库适合演示：

- 初始告警发送
- 一级升级通知
- 第二联系人升级通知
- 立即 acknowledge 的处理流程
- snooze 与延后升级流程
- 动作执行
- 事件详情查看
- timeline 与审计轨迹查看
- Telegram 通知送达

---

## Development status | 开发状态

This is a working open-source MVP focused on incident orchestration workflows.

It should be understood as a practical community edition backend rather than a finished production SaaS platform.

这是一个围绕应急编排流程构建的开源可运行 MVP。

它更适合被理解为一个实用的社区版后端，而不是已经完成的生产级 SaaS 平台。

### Possible future extensions | 后续扩展方向

- production-grade action executors
- real voice / phone escalation integrations
- richer escalation policy models
- configurable rule management
- operator-facing web UI
- richer AI routing and summary logic

- 生产级动作执行器
- 真实电话 / 语音升级集成
- 更丰富的升级策略模型
- 可配置规则管理
- 面向操作员的 Web UI
- 更强的 AI 路由与摘要逻辑

---

## Open-source safety checklist | 开源前安全检查

Before publishing or demoing this project:

- do not commit `.env` or `.env.*`
- do not commit real bot tokens, webhooks, or API keys
- if any token was exposed, rotate it immediately
- check terminal history, screenshots, recordings, and clipboard contents before demos

在公开发布或演示前，请确认：

- 不要提交 `.env` 或 `.env.*`
- 不要提交真实 bot token、webhook 或 API key
- 如果凭据曾泄露，应立即 rotate
- 演示前检查终端历史、截图、录屏和剪贴板内容

---

## License | 许可证

This repository is licensed under the Apache License 2.0.

本仓库使用 Apache License 2.0 许可证。
