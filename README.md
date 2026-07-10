# KeyManagerApp

> 像档案柜一样的本地加密密钥管理器，基于 PySide6。
> A local encrypted credential manager with a desktop GUI, built on PySide6.

## Overview / 概述

KeyManagerApp is a desktop credential vault that keeps everything local. Your accounts, passwords, and notes are encrypted with a master key and stored in local files only — no cloud, no network sync, no third-party storage. Unlock with your master key, view/copy/edit entries, lock when done.

KeyManagerApp 是一个桌面端的本地密钥与账号管理工具。所有敏感数据用主密钥加密后只存在本地文件里，不联网、不同步、不依赖任何云端。输入主密钥解锁，查看/复制/编辑条目，关掉就锁上。适合在自己机器上离线保管账号密码的个人用户。

## Features / 功能

- **Master key login** — Scrypt-derived encryption key unlocks the app
- **Local-only encrypted storage** — settings and data written as ciphertext to local files
- **Entry management** — add/delete entries; each holds a note, account, password, and creation time
- **Custom metadata** — attach arbitrary key-value pairs to any entry
- **View & copy** — inspect entry details, one-click copy account/password/metadata to clipboard
- **Visibility toggle** — show/hide account and password in the detail view
- **Optional re-authentication** — require master key input before viewing details (`require_master_key`)
- **Change master key** — re-encrypts all data and settings with a new key and salt
- **Privacy switches** — independently hide account, password, or extra info display
- **Themes** — light, dark, Windows native, PySide/Qt6 stock
- **Background** — random online images, solid black, or local image; configurable auto-change interval
- **Nuke button** — one-click wipe of data, settings, and salt files (irreversible)
- **Attempt limit** — configurable max failed attempts; exceeded limit triggers data destruction

---

- **主密钥登录** — Scrypt 派生加密密钥，解锁应用
- **本地加密存储** — 设置和数据以密文写入本地文件
- **条目管理** — 新增/删除条目；每条包含备注、账号、密码、创建时间
- **自定义附加信息** — 每个条目可添加任意数量的键值对
- **查看与复制** — 查看条目详情，一键复制账号/密码/附加信息到剪贴板
- **可见性切换** — 详情页临时显示或隐藏账号与密码
- **二次验证（可选）** — 查看详情前要求再次输入主密钥
- **更改主密钥** — 用新密钥和新盐重新加密全部数据与设置
- **隐私开关** — 分别控制账号、密码、附加信息的显示
- **主题切换** — 亮色 / 暗色 / Windows 原生 / PySide/Qt6 原版
- **背景设置** — 随机在线图片、纯黑、本地图片；可设置自动更换频率
- **一键清除** — 删除数据、设置和盐文件（不可撤销）
- **错误尝试上限** — 可配置最大错误次数，超限触发数据销毁

<!-- TODO: confirm whether search / JSON import-export are planned or were removed -->

## Tech Stack / 技术栈

| Layer | Choice |
|-------|--------|
| Language | Python >= 3.10 |
| GUI | PySide6 >= 6.11.1 |
| Crypto | `cryptography` >= 49.0.0 — Scrypt (n=2^14, r=8, p=1, 16-byte salt) + Fernet (AES authenticated encryption) |
| Randomness | `secrets` |
| Network | `QtNetwork` (only for fetching random background images) |

<!-- TODO: confirm which version floor is authoritative — requirements.txt vs setup.py -->

## Project Structure / 项目结构

```
KeyManagerApp/
├── main.py                 # All app logic: login, main UI, settings, crypto
├── requirements.txt        # Runtime dependencies
├── setup.py                # Package metadata (key-manager-app 0.1.0)
├── installcommand          # Install/run/package command cheatsheet
├── icon/
│   └── icon.ico            # App icon (for PyInstaller)
├── .github/workflows/
│   └── ci.yml              # CI: compileall syntax check
├── LICENSE                 # MIT
└── .gitignore              # Ignores settings.dat / data.dat / salt.dat
```

<!-- TODO: confirm whether an icons/ directory is expected — main.py references QIcon("icons/...") but the directory is not in the repo -->

## Getting Started / 快速开始

### Prerequisites / 环境要求

- Python 3.10+
- Windows (primary test environment; other platforms untested for network features)

### Install & Run / 安装与运行

```bash
git clone https://github.com/dwgx/KeyManagerApp.git
cd KeyManagerApp

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux (not officially tested)
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Package as Executable (optional) / 打包为可执行文件（可选）

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon/icon.ico main.py
```

## Usage / 使用方法

1. Launch and enter your master key. First run auto-generates a random salt (`salt.dat`).
2. Use the toolbar "Add Password" to create entries: fill in note, account, password, and optional metadata.
3. Click an entry in the list to view details (if re-auth is enabled, enter master key again).
4. Toggle account/password visibility in the detail view; one-click copy to clipboard.
5. In Settings: change theme, background, verification, hidden fields, max attempts, or master key.
6. Use "Nuke Data" in the toolbar to irreversibly wipe everything.

---

1. 启动后输入主密钥登录，首次运行自动生成随机盐（`salt.dat`）。
2. 工具栏"添加密码"创建条目：填写备注、账号、密码及附加信息。
3. 点击列表条目查看详情；如开启了主密钥验证会要求再次输入。
4. 详情页可切换账号/密码可见性，一键复制到剪贴板。
5. 在"设置"中调整主题、背景、验证要求、隐藏项、最大错误次数，或更改主密钥。
6. 需要彻底清空时使用工具栏"一键清除数据"。

## Data Files / 数据文件

The app reads/writes these files in its working directory (all in `.gitignore`):

| File | Purpose |
|------|---------|
| `salt.dat` | Random salt for Scrypt |
| `settings.dat` | Encrypted app settings |
| `data.dat` | Encrypted credential entries (path overridable via `data_file_location` setting) |

Back up all three together when migrating. Losing the master key means permanent data loss.

备份或迁移时三个文件必须一起处理。主密钥丢失则数据不可恢复。

## Configuration / 配置

Settings are stored encrypted in `settings.dat`, editable within the app:

| Key | Description |
|-----|-------------|
| `theme` | Light / Dark / Windows Native / PySide/Qt6 Stock |
| `background_option` | Random / Black / Local image |
| `background_image` | Path to local background image |
| `background_change_frequency` | Auto-change interval (minutes) |
| `require_master_key` | Re-auth before viewing details |
| `max_attempts` | Max wrong attempts before data destruction |
| `data_file_location` | Custom data file path |
| `hide_account` / `hide_password` / `hide_more_info` | Hide respective fields |

## Status / 状态

Personal tool, version 0.1.0. CI runs `python -m compileall` syntax check only; no automated tests yet.

个人工具，版本 0.1.0。CI 仅做语法检查，暂无自动化测试。

## License / 许可证

MIT License, Copyright (c) 2024 dwgx. See [`LICENSE`](LICENSE).
