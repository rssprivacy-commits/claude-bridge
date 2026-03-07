# CB-KB-Operations — Claude Bridge 运维知识库

## 部署记录

### 2026-03-07 首次部署
- 环境：macOS Apple Silicon, M4 Max
- LaunchAgent: ai.claude-bridge（~/Library/LaunchAgents/ai.claude-bridge.plist）
- 验证：launchctl list ai.claude-bridge 返回 PID，日志出现 "Claude Bridge started"
- 端到端测试：Telegram /start → /p add openclaw → 发送消息 → 收到回复

## 运维 SOP

### Bot Token 轮换
1. @BotFather → /mybots → 选 bot → API Token → Revoke
2. 生成新 token
3. `security add-generic-password -s claude-bridge-bot-token -a claude-bridge -p "<NEW_TOKEN>"`（如已存在先 delete）
4. 确认 config.json botToken 字段为 `!security find-generic-password -s claude-bridge-bot-token -a claude-bridge -w`
5. `launchctl kickstart -k gui/$(id -u)/ai.claude-bridge`
6. 验证：tail -3 ~/.claude-bridge/logs/claude-bridge.log

### LaunchAgent 管理
```bash
launchctl list ai.claude-bridge          # 状态
launchctl kickstart -k gui/$(id -u)/ai.claude-bridge  # 重启
launchctl bootout gui/$(id -u)/ai.claude-bridge       # 停止
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.claude-bridge.plist  # 启动
```

## 成本监控

每周检查：
```bash
sqlite3 ~/.claude-bridge/data/sessions.db \
  "SELECT date(created_at), printf('$%.4f', SUM(cost_usd)), SUM(turns) FROM cost_log GROUP BY date(created_at) ORDER BY 1 DESC LIMIT 7;"
```
