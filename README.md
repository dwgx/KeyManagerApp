# KeyManagerApp

KeyManagerApp 是一个本地密钥与账号信息管理工具，基于 PySide6 开发。

核心思路很简单：
把敏感信息加密后只存在本地，平时通过主密钥解锁查看和编辑。

## 主要功能

- 主密钥登录
- 本地加密存储
- 条目增删改查
- 关键词搜索
- 主题/背景设置
- JSON 导入导出

## 环境要求

- Python 3.10+
- Windows（主要测试环境）

## 快速开始

```bash
git clone https://github.com/dwgx/KeyManagerApp.git
cd KeyManagerApp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 数据文件

程序会在本地生成并使用这些文件：

- `settings.dat`
- `data.dat`
- `salt.dat`

要迁移或备份数据，请把这三个文件一起备份。

## 常见问题

### 忘记主密钥

主密钥用于解密本地数据，忘记后无法恢复已加密内容。

### 启动时报缺依赖

确认已激活虚拟环境，并重新执行：

```bash
pip install -r requirements.txt
```
