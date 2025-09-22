# mailssh

一个由 AI 驱动的自动邮件回复机器人，支持多角色人设切换和远程邮件指令。

## 功能

- **自动轮询邮箱**：每 60 秒自动拉取未读邮件并解析内容。
- **AI回复**：邮件内容由 AI（deepseek-chat）生成，模拟真实角色人设。
- **多角色切换**：支持通过邮件指令切换不同角色（如凯尔希、阿米娅、黍、迷迭香等），可扩展自定义角色。
- **首次教程**：新用户首次收到回复时，会自动发送详细使用教程邮件。
- **远程指令**：通过邮件发送特殊命令（如 `change_to [角色名]`、`helpme`）实现远程控制和帮助。
- **安全连接**：支持 IMAP/SMTP 协议，自动重连和 SSL 加密。
- **邮件内容解析**：自动处理 MIME、编码、分割历史内容，支持带附件发送。
- **人设自定义**：通过修改同目录下的 *.txt 文件即可定制角色设定和回复风格。

## 快速开始

### 1. 环境准备

- Python 3.8+
- 依赖包：
  ```bash
  pip install imapclient yagmail openai
  ```
- 需要有可用的邮箱账号（推荐 126、163 等支持 IMAP/SMTP 的邮箱）。

### 2. 配置邮箱和 API 密钥

- 编辑 `password.py`，填写你的邮箱地址、IMAP/SMTP 信息和 base64 编码后的邮箱密码、OpenAI API 密钥等。

  ```python
  class pwd:
      def content(self):
          return b'你的邮箱密码的base64编码'
      def api(self):
          return b'你的deepseek/openai的API密钥base64编码'
      def imap(self):
          return "imap.126.com", 993, "你的邮箱地址"
      def smtp(self):
          return "smtp.126.com", 465, "你的邮箱地址"
      def id(self):
          return {'name': '', 'version': '1.0', 'vendor': ''}
      def console(self):
          return b'控制台模式密码的base64编码'
  ```

### 3. 运行机器人

```bash
python bot.py
```

机器人会自动轮询邮箱并进行智能回复。

## 人设说明与自定义

- 默认人设为凯尔希（kalts.txt）。
- 你可以通过邮件发送 `change_to 角色名` 切换人设。
- 角色文件（如 kalts.txt、amiya.txt、shu.txt 等）支持自定义内容，支持 `{users}` 占位符自动替换为发件人名称。
- 添加新角色：复制一份 txt 文件（如 kalts.txt），修改内容，命名为新角色名，如 `newrole.txt`。

## 邮件指令

- `change_to [角色名]`：切换智能体角色，下封邮件生效。
- `helpme`：重新发送使用教程邮件。
- （可以根据控制台密码实现远程特殊指令）
- ![指令]在服务器端执行指令

## 注意事项

- 请勿直接上传包含敏感信息的 password.py 文件到公开仓库。
- 使用时请遵循相应邮箱服务商的 API 使用规范，避免频繁轮询导致封禁。
- 本项目仅用于技术研究与个人娱乐，不建议商用。

## License

MIT
