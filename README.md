# KeyManagerApp

一个基于 PySide6 的本地密钥管理工具，用于加密保存账号密码和常用密钥信息。

## 功能

- 主密钥登录与本地加密存储
- 条目增删改查与关键词检索
- 主题与背景设置
- 数据导入/导出（JSON）

## 运行环境

- Python 3.10+
- Windows（项目默认针对 Windows 使用场景）

## 快速开始

1. 克隆仓库

```bash
git clone https://github.com/dwgx/KeyManagerApp.git
cd KeyManagerApp
```

2. 创建并激活虚拟环境（推荐）

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 启动程序

```bash
python main.py
```

## 依赖说明

- `PySide6`：桌面 GUI
- `cryptography`：主密钥派生与数据加密

`pyinstaller` 仅用于打包发布，不属于运行时依赖。

## 打包（可选）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon/icon.ico main.py
```

## 数据文件位置

程序会在项目目录下创建和读取以下文件：

- `settings.dat`
- `data.dat`
- `salt.dat`

备份应用数据时请同时备份这三个文件。

## 常见问题

### 1) 启动时报依赖缺失

请确认已经激活虚拟环境，并执行过：

```bash
pip install -r requirements.txt
```

### 2) 忘记主密钥怎么办

主密钥用于解密本地数据，忘记后无法恢复已有加密内容。请务必妥善保存。
