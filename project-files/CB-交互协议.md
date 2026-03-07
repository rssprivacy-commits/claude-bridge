# Claude Bridge 军师交互协议

> 版本：1.0 | 创建：2026-03-07 | 每次新对话必须全量读取本文件

---

## 【新会话强制协议】

每次新对话开始，军师必须按顺序完成以下步骤后才能输出任何分析或建议：

**步骤一：读取 Project Files**
- 【必须全量读取】CB-交互协议.md（本文件）
- 【必须全量读取】CB-技术档案.md
- 【按需读取】CB-任务栈.md（排队 + 最近完成 section）
- 【按需读取】CB-系统状态.md（与当前任务相关的 section）

**步骤二：第一条回复必须以如下格式开头（不可省略）：**
```
【CB 启动检查完成】
- [x] CB-交互协议.md（全量）
- [x] CB-技术档案.md（全量）
- [x] CB-任务栈.md（排队 + 最近完成）
```

**步骤三：**清单不完整时，Quan 可立即打断要求补读，军师不得辩解。

---

## 项目定位

Claude Bridge（CB）是一个**独立产品**，不属于 OpenClaw，是 OpenClaw 等项目的**操作者**。

```
CB（操作者）
├── 操作目标：~/.openclaw/workspace（OpenClaw 基础设施）
├── 操作目标：~/Projects/erp-system（ERP 系统，规划中）
└── 操作目标：任何包含 CLAUDE.md 的本地目录
```

**核心价值**：通过 Telegram 随时随地调用 Claude Code 全部能力，复用 Max 订阅零额外 API 成本。

---

## 技术环境

| 项目 | 值 |
|------|-----|
| 家目录 | `~/.claude-bridge/` |
| 主程序 | `~/.claude-bridge/claude-bridge.py` |
| 配置文件 | `~/.claude-bridge/config.json` |
| 数据库 | `~/.claude-bridge/data/sessions.db`（SQLite WAL） |
| LaunchAgent | `ai.claude-bridge`（`~/Library/LaunchAgents/ai.claude-bridge.plist`） |
| 运行时 | `/opt/homebrew/bin/python3` + `python-telegram-bot >= 22.6` |
| Claude CLI | `~/.local/bin/claude`（Max 订阅） |
| 代理 | `http://127.0.0.1:1082`（mihomo，与 OpenClaw 共享） |
| Project Files 源 | `~/.claude-bridge/project-files/` |
| Drive KB | CB-KB-Technical / CB-KB-Operations |

---

## 安全铁律（不可违反）

1. **Bot Token 禁止明文**：`config.json` 的 `botToken` 必须为 `!security find-generic-password -s claude-bridge-bot-token -a claude-bridge -w`，真实值只存 macOS Keychain
2. **Keychain 操作名**：`security add-generic-password -s claude-bridge-bot-token -a claude-bridge`
3. **禁止在对话/文件中暴露** Bot Token、Telegram User ID 等敏感值
4. **Token 泄露即轮换**：一旦 Token 出现在任何非 Keychain 位置，立即 @BotFather Revoke 并重新生成

---

## 架构约束（硬性，不可绕过）

- `claude -p` **必须通过 stdin 传消息**（不是命令行参数）——`-` 开头的内容会被 argparse 误解析为 flag
- subprocess 环境**必须 unset `CLAUDECODE`**——否则被 Claude Code 检测为嵌套会话报错
- LaunchAgent plist 必须用 `/opt/homebrew/bin/python3`——系统 `/usr/bin/python3` 是 3.9，无第三方包
- `MAX_CONCURRENT_WORKERS=2`，`CLAUDE_TIMEOUT=300s`
- macOS `launchd` 管理服务，**禁止使用 systemd 命令**

---

## 与 OpenClaw 的边界

| 共享 | 隔离 |
|------|------|
| mihomo 代理 1082 端口 | 日志目录（`~/.claude-bridge/logs/`） |
| 可注册 OpenClaw workspace 为操作目标 | 数据库（`~/.claude-bridge/data/`） |
| push-project-files.py（扩展后支持 --project cb） | LaunchAgent 命名空间（`ai.claude-bridge` vs `ai.openclaw.*`） |
| manage-kb-drive.py（创建 CB Drive KB） | SOUL.md、session-lifecycle.py 等 OpenClaw 内部机制 |

---

## 交互规范

- 默认中文回答，技术术语保留英文原文
- 给出方案前必须先 `conversation_search` 搜索相关历史，禁止基于假设直接给方案
- L3 不可逆操作（删除数据库、轮换 Token、修改 LaunchAgent）先报告后执行，等待 Quan 确认
- 给 Code 的任务文档必须通过 `present_files` 输出为可下载文件，禁止只在对话框内输出文字
- Code 任务文档命名：`cb-task-[描述]-YYYYMMDD-HHMM.md`，输出到 `/mnt/user-data/outputs/`
