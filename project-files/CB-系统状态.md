# Claude Bridge 系统状态档案

> 最后更新：2026-03-07 | 维护：Code 在复盘时更新，军师审核

---

## 部署状态

| 项目 | 状态 | 备注 |
|------|------|------|
| LaunchAgent ai.claude-bridge | ✅ 运行中 | KeepAlive，开机自启 |
| 主程序版本 | 1.0.0（880行） | 2026-03-07 架构独立后 |
| Bot Token 存储 | ⚠️ 待迁移 | 当前明文在 config.json，需迁入 Keychain |
| 代理 | ✅ http://127.0.0.1:1082 | mihomo，与 OpenClaw 共享 |
| 数据库 | ✅ WAL 模式 | ~/.claude-bridge/data/sessions.db |
| Project Files 自动推送 | ⚠️ 待配置 | 需扩展 push-project-files.py |
| Drive KB | ⚠️ 待创建 | CB-KB-Technical / CB-KB-Operations |

---

## 已注册项目

> 由 Code 通过以下命令更新：
> `sqlite3 ~/.claude-bridge/data/sessions.db "SELECT name, path, description FROM projects;"`

| 名称 | 路径 | 描述 |
|------|------|------|
| openclaw | /Users/chenmingzhong/.openclaw/workspace | OpenClaw infrastructure |
| erp | /Users/chenmingzhong/Projects/erp-system | ERP system |

---

## 版本历史

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-07 | 1.0.0 | 首版开发 + 部署验证通过 |
| 2026-03-07 | 1.0.0 | Bug Fix: frozen Message → 独立 handle_photo |
| 2026-03-07 | 1.0.0 | Bug Fix: `-` 开头消息报错 → stdin pipe |
| 2026-03-07 | 1.0.0 | 架构独立：从 ~/.openclaw/scripts/ 迁移到 ~/.claude-bridge/ |

---

## 已知问题清单

| 优先级 | 问题 | 状态 |
|--------|------|------|
| P0 | botToken 明文存储在 config.json | ⚠️ 待修复 |
| P2 | Forward 消息未处理（filters.FORWARDED 未测试） | 🔜 排队 |
| P3 | 成本统计时区用 UTC，用户在 UTC+8 有 8h 偏差 | 🔜 排队 |
| P3 | Document 类型消息（PDF/代码文件）未处理 | 🔜 排队 |
| P3 | Markdown 渲染失败时 fallback 为纯文本（非 MarkdownV2） | 🔜 排队 |

---

## 关键路径

```
LaunchAgent 启动
  └─ /opt/homebrew/bin/python3 ~/.claude-bridge/claude-bridge.py
       ├─ 读取 config.json（含 botToken）
       ├─ init SQLite WAL
       ├─ 建立 Telegram polling（via proxy 1082）
       └─ 收到消息 → invoke_claude()
            └─ subprocess: claude -p --output-format json
                 ├─ stdin: 用户消息
                 ├─ cwd: 项目目录（读取该目录 CLAUDE.md）
                 └─ env: unset CLAUDECODE
```

---

## 运维快查

```bash
# 状态检查
launchctl list ai.claude-bridge

# 重启
launchctl kickstart -k gui/$(id -u)/ai.claude-bridge

# 实时日志
tail -f ~/.claude-bridge/logs/claude-bridge.log

# 成本查询
sqlite3 ~/.claude-bridge/data/sessions.db \
  "SELECT date(created_at), SUM(cost_usd), SUM(turns) FROM cost_log GROUP BY date(created_at) ORDER BY 1 DESC LIMIT 7;"

# 项目列表
sqlite3 ~/.claude-bridge/data/sessions.db "SELECT * FROM projects;"
```
