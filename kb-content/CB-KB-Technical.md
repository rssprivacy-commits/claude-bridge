# CB-KB-Technical — Claude Bridge 技术知识库

## 架构决策记录

### AD-001: claude -p stdin 传消息（2026-03-07）
决策：消息通过 stdin pipe 传入，不作为命令行参数
原因：argparse 将 `-` 开头内容误解析为 flag
影响文件：claude-bridge.py invoke_claude()

### AD-002: subprocess unset CLAUDECODE（2026-03-07）
决策：invoke_claude() 环境变量移除 CLAUDECODE 和 CLAUDE_PROJECT_DIR
原因：Claude Code 检测到 CLAUDECODE 环境变量时报嵌套会话错误
影响文件：claude-bridge.py CLAUDE_ENV 常量

### AD-003: python-telegram-bot v22 frozen dataclass（2026-03-07）
决策：handle_photo 独立实现，不修改 update.message 属性
原因：ptb v22 的 Message 是 frozen dataclass，赋值抛 AttributeError
Bug 发现：图片消息静默无响应（无 error handler 导致异常被吞）
修复：独立 handle_photo + 全局 error_handler 注册

## 已知问题记录

见 CB-系统状态.md 已知问题清单（保持同步）

## 依赖版本锁定

| 依赖 | 版本 | 关键约束 |
|------|------|---------|
| python-telegram-bot | >= 22.6 | v22 frozen Message |
| Python | 3.14.3 (/opt/homebrew) | 不可用 /usr/bin/python3 (3.9) |
| Claude Code CLI | 最新 | ~/.local/bin/claude |
