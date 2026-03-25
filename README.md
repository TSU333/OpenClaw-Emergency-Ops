# OpenClaw Emergency Ops

OpenClaw Emergency Ops 是一个面向量化交易、自动化任务、爬虫和小型基础设施场景的 AI 告警编排层。它不做完整 observability，也不做完整 on-call 排班，而是把事件理解、严重度分级、多渠道升级、second contact、建议动作和动作闭环串成一个最小可演示产品。

## 5 分钟你可以展示什么

这套 MVP 最适合对外展示 5 个点：

- `AI summary`: 事件发生后，自动生成 what happened / impact / risk / recommended actions / immediate stop loss 建议
- `escalation`: 根据严重度自动分流到 Apprise / SMS-like fallback / Voice Call
- `second contact`: 超时未响应后升级到第二联系人
- `acknowledge / snooze`: 人工介入可以立刻接管或延后处理
- `action execution`: 可以从事件上下文直接执行 `pause_strategy` / `close_positions` / `restart_service`

事件详情页接口 `GET /api/v1/events/{event_id}` 现在会直接返回：

- `ai_summary`
- `notifications`
- `action_runs`
- `timeline`

这四块已经足够支撑一版对外展示。

## 1. 启动本地演示环境

```bash
cd /Users/oscarxia/Documents/CODEX/openclaw-emergency-ops
cp .env.example .env
docker compose up --build
```

默认开发节奏已经调成快速验收模式：

```env
ESCALATION_FIRST_WAIT_SECONDS=10
ESCALATION_SECOND_WAIT_SECONDS=20
```

这样你不需要等 5 分钟 / 10 分钟，就能在本地看到 escalation 和 second contact。

启动后：

- API 文档: [http://localhost:8000/docs](http://localhost:8000/docs)
- 健康检查: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## 2. 一键跑闭环 Demo

仓库已经带了一个脚本：

```bash
cd /Users/oscarxia/Documents/CODEX/openclaw-emergency-ops
./scripts/demo_flow.sh
```

这个脚本会依次做以下事情：

1. 创建事件
2. 立刻 `acknowledge`
3. 立刻 `snooze`
4. 执行 `pause_strategy`
5. 查询 `event detail`
6. 查询 `timeline`
7. 打印 `worker` 日志

适合 1 分钟内展示：

- AI summary 已生成
- 人工接管已记录
- snooze 已记录
- action execution 已记录
- event detail 里能看到 `action_runs`
- timeline 里能看到 `action.requested` / `action.completed`

## 3. 20 秒 second contact 演示

如果你要突出 `escalation + second contact`，建议再单独做一遍不立即 ack 的演示：

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H 'Content-Type: application/json' \
  -d '{
    "source": "quant-engine",
    "event_type": "liquidation_risk",
    "title": "Demo: liquidation risk rising",
    "message": "All positions are close to maintenance margin.",
    "severity_hint": "p0",
    "metadata": {
      "strategy_id": "BTC_PERP_01",
      "exchange": "Binance"
    },
    "suggested_actions": ["pause_strategy", "close_positions"]
  }'
```

然后等待约 20 秒，再查：

```bash
curl http://localhost:8000/api/v1/events/<EVENT_ID> | python3 -m json.tool
curl http://localhost:8000/api/v1/events/<EVENT_ID>/timeline | python3 -m json.tool
docker compose logs worker --tail 80
```

预期你会看到：

- `escalation_level = 2`
- `notifications` 里出现 second contact 的通知
- `timeline` 里出现 `notification.dispatched`
- `timeline` 里出现 `escalation.second_triggered`

如果 second contact 因配置或路由不可用被跳过，timeline 会明确出现：

- `escalation.second_skipped`
- `details.reason`

## 4. Telegram 配置说明

普通通知走 Apprise，所以 Telegram 也是通过 Apprise URL 来配置。

把 Telegram URL 填到 `.env` 里的 `DEFAULT_PRIMARY_APPRISE_TARGETS` 或 `DEFAULT_SECONDARY_APPRISE_TARGETS` 即可，例如：

```env
DEFAULT_PRIMARY_APPRISE_TARGETS=tgram://bot123456789:AAExampleToken/-1001234567890/
```

如果你同时还想发 Slack，可以逗号分隔多个 Apprise target：

```env
DEFAULT_PRIMARY_APPRISE_TARGETS=tgram://bot123456789:AAExampleToken/-1001234567890/,slack://TokenA/TokenB/TokenC/TradingAlerts
```

Telegram 配置步骤：

1. 用 BotFather 创建机器人，拿到 bot token
2. 先给这个 bot 发一条消息
3. 通过 Telegram `getUpdates` 拿到 chat id
4. 组合成 Apprise URL

Apprise 官方 Telegram 语法参考：

- `tgram://{bot_token}/{chat_id}/`
- 多个 chat id 也可以继续追加路径段

参考文档：

- [Apprise Telegram docs](https://github.com/caronc/apprise/wiki/notify_telegram)

## 5. 对外展示时建议怎么讲

推荐直接按这个顺序讲：

1. 先打开 `event detail`，指出 `ai_summary` 已经把事故解释成可操作语言
2. 指出 `severity` 和 `notifications`，说明这是一个编排层，不是新造通知渠道
3. 打开 `timeline`，展示系统做过什么、人做过什么、动作执行了什么
4. 展示 `acknowledge / snooze`
5. 展示 `action_runs`
6. 最后补一遍 second contact 的 20 秒升级演示

最适合截图或录屏的字段：

- `ai_summary.what_happened`
- `ai_summary.current_risk`
- `ai_summary.recommended_actions`
- `notifications[].channel`
- `notifications[].escalation_step`
- `action_runs[].action_name`
- `action_runs[].status`
- `timeline[].action`

## 关键 API

- `POST /api/v1/events`
- `POST /api/v1/events/ingest`
- `GET /api/v1/events/{event_id}`
- `GET /api/v1/events/{event_id}/timeline`
- `POST /api/v1/events/{event_id}/acknowledge`
- `POST /api/v1/events/{event_id}/snooze`
- `POST /api/v1/events/{event_id}/actions/{action_name}`

## 测试

```bash
cd /Users/oscarxia/Documents/CODEX/openclaw-emergency-ops
./.venv/bin/pytest app/tests -q
```

## 开源前安全检查

在把仓库公开之前，建议先做这一轮人工确认：

- 不要提交 `.env` 或任何 `.env.*` 文件
- 不要提交真实 `bot token`、`webhook`、`API key`、语音调用 token 或第三方通知地址
- 如果任何 token、webhook 或 key 曾经出现在聊天、截图、终端或错误提交中，应立即 rotate
- 演示或发布前，检查终端历史、截图、录屏、剪贴板和草稿文档，确认没有残留真实凭据

## 当前交付边界

- 已完成：AI-style summary、severity、routing、escalation、second contact、acknowledge、snooze、action execution、timeline、audit log
- 已预留：OpenClaw Voice Call 真实 HTTP 适配、规则可配置化、简单 Web UI
- 不做：完整 on-call 排班、完整 observability、通知渠道重造
