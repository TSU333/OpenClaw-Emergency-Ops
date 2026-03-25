# OpenClaw Emergency Ops

**AI-powered alert orchestration for trading systems, automation jobs, crawlers, and small infrastructure.**

**面向交易系统、自动化任务、爬虫和小型基础设施的 AI 告警编排系统。**

---

## Overview | 项目简介

OpenClaw Emergency Ops is a community/core edition backend for alert escalation and incident response workflows.

It is designed to help operators and developers handle critical events with:

- AI-generated human-readable summaries
- severity-based alert routing
- automatic escalation when no one responds
- secondary contact notifications
- acknowledge and snooze workflows
- dry-run response actions
- timeline and audit trail recording

OpenClaw Emergency Ops 是一个面向告警升级与应急响应流程的社区版 / 核心版后端系统。

它帮助开发者和操作人员在重大事件发生时完成以下工作：

- 自动生成可读的 AI 摘要
- 按严重程度分级通知
- 无人响应时自动升级
- 通知第二联系人
- 支持 acknowledge（确认）与 snooze（延后）
- 支持 dry-run 应急动作执行
- 记录完整 timeline 与审计轨迹

---

## Why this project exists | 为什么做这个项目

Most alerting tools stop at sending a message.

This project goes one step further:

- explain what happened
- highlight the impact
- assess urgency
- escalate automatically
- support operator response actions
- preserve a full response timeline

大多数告警工具停留在“发一条消息”。

这个项目希望进一步解决这些问题：

- 解释到底发生了什么
- 说明影响范围
- 判断紧急程度
- 自动执行升级通知
- 支持操作人员进行响应动作
- 保留完整处理时间线

---

## Use cases | 适用场景

This project is especially suitable for:

- quant and trading bots
- crawlers and scheduled jobs
- automation pipelines
- self-hosted services
- lightweight team incident workflows

这个项目特别适合以下场景：

- 量化交易与自动化交易机器人
- 爬虫与定时任务
- 自动化流水线
- 自托管服务
- 轻量级团队应急流程

---

## Current capabilities | 当前能力

### English

- FastAPI-based event ingestion
- severity-based routing
- AI-style event summarization
- initial alert dispatch
- first escalation
- secondary contact escalation
- acknowledge workflow
- snooze workflow
- dry-run action execution
- event detail aggregation
- timeline and audit trail
- Telegram notification support via Apprise
- Docker Compose local deployment
- demo flow script

### 中文

- 基于 FastAPI 的事件接入
- 按严重度分级路由
- AI 风格事件摘要
- 初始告警发送
- 一级升级通知
- 第二联系人升级通知
- acknowledge 确认流程
- snooze 延后流程
- dry-run 动作执行
- 事件详情聚合
- timeline 与审计记录
- 通过 Apprise 支持 Telegram 通知
- 基于 Docker Compose 的本地部署
- 演示脚本支持

---

## Full feature list | 完整功能列表

### Event ingestion | 事件接入
- `POST /api/v1/events` 接收外部系统事件
- 支持从量化系统、自动化任务、爬虫、服务监控等来源提交 JSON 事件
- 支持 `source`、`event_type`、`severity_hint`、`metadata`、`suggested_actions` 等字段

### AI summary | AI 摘要
- 自动把原始技术事件整理成可读摘要
- 输出：
  - what happened
  - impact scope
  - current risk
  - recommended actions
  - operator brief

### Severity routing | 严重度路由
- 支持不同严重度下的通知与升级行为
- 当前已验证 `critical` 和 `p0` 场景
- 支持事件级别的升级初始化与调度

### Multi-stage escalation | 多阶段升级
- initial alert
- first escalation
- second contact escalation
- 支持主联系人与第二联系人
- 当事件未被处理时，系统会自动推进升级链

### Operator controls | 操作员控制
- `acknowledge`：确认事件，阻断后续升级
- `snooze`：延后处理，重排升级时间
- 支持将操作写入 timeline

### Action execution | 动作执行
- `pause_strategy`
- `close_positions`
- `restart_service`（可扩展）
- 当前默认以 dry-run 形式执行
- 执行结果会写入 `action_runs` 与 timeline

### Timeline and audit | 时间线与审计
- 事件创建
- 初始通知
- 升级触发
- 第二联系人通知
- acknowledge
- snooze
- action requested / action completed
- 所有关键步骤都会记录到 timeline 中

### Notification delivery | 通知发送
- 通过 Apprise 统一发送通知
- 当前已验证 Telegram 集成
- 代码中预留了 Slack / Discord / voice call / SMS fallback 等能力
- 当前 voice call 为模拟实现，适合 demo 和后续扩展

---

## Example workflow | 示例流程

### English

1. A service posts an event to the API
2. The backend classifies and summarizes the event
3. Initial notification is sent to the primary contact
4. If unacknowledged, the system escalates automatically
5. If still unacknowledged, the secondary contact is notified
6. Operators can acknowledge, snooze, or execute actions
7. Every step is written to the event timeline

### 中文

1. 外部系统通过 API 提交事件
2. 后端对事件进行分级并生成摘要
3. 初始通知发送给主联系人
4. 如果无人确认，系统自动触发升级
5. 如果仍无人处理，系统通知第二联系人
6. 操作人员可以 acknowledge、snooze 或执行动作
7. 所有步骤都会记录到事件 timeline 中

---

## Architecture | 技术架构

### Core components | 核心组件

- **FastAPI** — API and event ingestion  
  **FastAPI** —— API 与事件接入

- **PostgreSQL** — persistent storage  
  **PostgreSQL** —— 持久化存储

- **Redis** — task broker / backend  
  **Redis** —— 异步任务队列与结果后端

- **Celery** — delayed escalation tasks  
  **Celery** —— 延迟升级任务执行

- **Apprise** — notification delivery  
  **Apprise** —— 统一通知发送

- **Alembic** — database migrations  
  **Alembic** —— 数据库迁移管理

### Internal services | 内部服务模块

- `event_service` — event lifecycle management  
- `severity_engine` — severity evaluation  
- `summary_service` — AI-style summaries  
- `notification_service` — notification dispatch  
- `routing_engine` — contact/channel resolution  
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


⸻

Quick start | 快速开始

1. Clone the repository | 克隆仓库

git clone https://github.com/TSU333/openclaw-emergency-ops.git
cd openclaw-emergency-ops

2. Create local config | 创建本地配置

cp .env.example .env

3. Start the stack | 启动服务栈

docker compose up --build

4. Check health | 健康检查

curl http://localhost:8000/api/v1/health

5. Run the demo flow | 运行演示脚本

./scripts/demo_flow.sh


⸻

Telegram notifications | Telegram 通知配置

Telegram delivery is supported via Apprise.

Telegram 通知通过 Apprise 实现。

Example .env configuration | .env 示例配置

DEFAULT_PRIMARY_APPRISE_TARGETS=tgram://<BOT_TOKEN>/<CHAT_ID>/
DEFAULT_SECONDARY_APPRISE_TARGETS=tgram://<BOT_TOKEN>/<CHAT_ID>/

Setup steps | 配置步骤

English
	1.	Create a bot with BotFather
	2.	Send the bot a message such as /start
	3.	Get your Telegram chat_id
	4.	Update .env
	5.	Restart the stack
	6.	Send a test event and verify delivery

中文
	1.	通过 BotFather 创建 Telegram bot
	2.	先给 bot 发一条消息，例如 /start
	3.	获取你的 Telegram chat_id
	4.	更新 .env
	5.	重启服务
	6.	发送测试事件并确认是否收到通知

Why multiple Telegram notifications may appear | 为什么会连续收到多条 Telegram 通知

If both primary and secondary contacts are configured to the same Telegram chat, you may receive:
	•	initial alert
	•	first escalation
	•	second contact escalation

这不是重复 bug，而是系统按升级链正常工作。
如果主联系人和第二联系人都配置成同一个 Telegram 会话，你会在同一个聊天中连续看到：
	•	初始通知
	•	一级升级通知
	•	第二联系人通知

这在本地测试阶段是正常现象。

⸻

Example event payload | 示例事件载荷

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


⸻

Demo scenarios | 演示场景

English

This repository currently supports demonstrating:
	•	initial alert dispatch
	•	first escalation
	•	secondary contact escalation
	•	immediate acknowledge flow
	•	snooze and delayed escalation
	•	dry-run action execution
	•	event detail inspection
	•	timeline and audit inspection
	•	Telegram notification delivery

中文

当前仓库支持演示以下流程：
	•	初始告警发送
	•	一级升级通知
	•	第二联系人升级通知
	•	立即 acknowledge 的处理流程
	•	snooze 与延后升级流程
	•	dry-run 动作执行
	•	事件详情查看
	•	timeline 与审计轨迹查看
	•	Telegram 真实通知发送

⸻

Demo script | 演示脚本

The repository includes:

./scripts/demo_flow.sh

It demonstrates:
	•	create event
	•	acknowledge
	•	snooze
	•	execute pause_strategy
	•	query event detail
	•	query timeline
	•	print worker logs

仓库中包含：

./scripts/demo_flow.sh

它会演示：
	•	创建事件
	•	acknowledge
	•	snooze
	•	执行 pause_strategy
	•	查询 event detail
	•	查询 timeline
	•	打印 worker 日志

⸻

Development notes | 开发说明

Current implementation status | 当前实现状态

This is an actively evolving backend prototype focused on incident orchestration workflows.

The current implementation is best understood as a working community/core MVP rather than a finished production SaaS.

这是一个持续迭代中的后端原型，重点在于应急事件编排流程。

当前实现更适合理解为“可运行的社区版 / 核心版 MVP”，而不是一个已经完成的生产级 SaaS 产品。

Community/Core Edition | 社区版 / 核心版说明

This repository contains the community/core edition of OpenClaw Emergency Ops.

Possible future extensions may include:
	•	production-grade action executors
	•	voice/phone escalation integrations
	•	hosted multi-user control plane
	•	advanced industry-specific templates
	•	richer AI routing and summary logic

本仓库提供的是 OpenClaw Emergency Ops 的社区版 / 核心版。

未来可能扩展的方向包括：
	•	生产级动作执行器
	•	语音 / 电话升级集成
	•	托管式多用户控制台
	•	更强的行业模板
	•	更复杂的 AI 路由与摘要逻辑


Roadmap | 路线图

Near-term | 近期方向
	•	improve operator-facing UI
	•	support richer escalation policies
	•	add clearer deployment examples
	•	expand action executor coverage

Mid-term | 中期方向
	•	production-grade voice/phone integrations
	•	more reliable multi-contact routing
	•	team-oriented permission model
	•	richer incident dashboard

中文

近期方向：
	•	改进面向操作员的 UI
	•	支持更丰富的升级策略
	•	补充更清晰的部署示例
	•	扩展动作执行器能力

中期方向：
	•	生产级电话 / 语音集成
	•	更稳定的多联系人路由
	•	团队权限模型
	•	更完整的事件面板

⸻

License | 许可证

This project is licensed under the Apache License 2.0.

本项目使用 Apache License 2.0 许可证。