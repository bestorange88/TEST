# TRON 助记词缺词补全工具（约束式枚举）

## 免责声明

**本工具仅用于找回用户自有钱包的助记词。**

- 用户**必须提供候选词集合**，工具仅在候选词范围内进行枚举，**禁止从 BIP39 全量 2048 词库枚举**。
- 所有正确性判定均**离线完成**（通过派生 TRON 地址与用户提供的已知地址匹配）。
- 严禁将本工具用于任何未授权用途，包括但不限于碰撞、撞库、扫链等。
- 助记词、私钥、种子等敏感信息**不会写入任何日志文件**，仅在 GUI 界面显示。

---

## 功能特性

- **12 格助记词输入**：支持逐格输入或粘贴整串自动拆分
- **候选词约束枚举**：全局候选池或按位置单独候选
- **组合数估算与上限门禁**：默认上限 200,000，超限自动拒绝
- **BIP39 校验和快速过滤**：大幅减少无效组合的派生计算
- **TRON 地址派生**：标准 BIP44 路径 `m/44'/195'/0'/0/i`
- **多地址匹配**：支持全等匹配、前缀匹配、后缀匹配
- **后台线程运行**：不阻塞 GUI，可随时停止
- **安全设计**：敏感信息不写日志，默认不联网

---

## 使用步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行工具

```bash
python app.py
```

### 3. 操作流程

1. **填写助记词**：在 12 格中输入已知的助记词，留空未知词位
2. **配置候选词**：为未知词位提供候选词集合（全局或按位置）
3. **填写已知地址**：输入要匹配的 TRON 地址（以 T 开头）
4. **调整派生设置**（可选）：修改派生路径、Index 范围、Passphrase
5. **点击开始**：工具将在候选词范围内枚举，通过 BIP39 校验和过滤后派生地址并匹配

---

## 性能提示

- **组合数估算**：总组合数 = 各未知位候选词数量的乘积
  - 例如：3 个未知位，每位 10 个候选词 → 10 × 10 × 10 = 1,000 组合
- **BIP39 校验和**：约 1/16 的组合能通过校验（12 词助记词有 4 位校验）
- **上限门禁**：默认 200,000 组合上限，可在 GUI 中调整
- **建议**：尽量缩小候选词范围以加速搜索

---

## 打包为 Windows 可执行文件

### 使用 PowerShell 脚本（推荐）

```powershell
.\packaging\build.ps1
```

### 手动打包

```bash
pyinstaller packaging/recovery_tron.spec --distpath dist --workpath build --clean -y
```

输出文件：`dist/RecoveryTron.exe`

---

## 项目结构

```
recovery_tron/
  app.py                        # 程序入口
  ui/
    main_window.py              # 主窗体
    mnemonic_grid.py            # 12 格助记词输入
    candidates_panel.py         # 候选词配置面板
    results_table.py            # 结果展示表格
  core/
    bip39_words.py              # BIP39 词库加载与校验
    checksum.py                 # BIP39 校验和验证
    constraints.py              # 未知位检测与组合生成
    tron_derive.py              # TRON 地址派生
    matcher.py                  # 地址匹配逻辑
    worker.py                   # 后台枚举 Worker
  packaging/
    build.ps1                   # PowerShell 打包脚本
    recovery_tron.spec          # PyInstaller 配置
  tests/
    test_checksum.py            # 校验和测试
    test_constraints.py         # 约束逻辑测试
    test_tron_derive_smoke.py   # TRON 派生冒烟测试
  requirements.txt              # Python 依赖
  README.md                     # 本文件
```

---

## 技术规格

| 项目 | 说明 |
|------|------|
| Python 版本 | 3.11+ |
| GUI 框架 | PySide6 |
| BIP39/BIP44 | bip_utils |
| 派生路径 | m/44'/195'/0'/0/i |
| 默认 Index 范围 | 0-20 |
| 地址格式 | TRON Base58Check (T 开头) |
| 组合上限 | 200,000 (可配置) |

---

## 安全设计

1. **离线优先**：所有校验与派生均在本地完成，默认不联网
2. **无日志泄露**：助记词、私钥、种子不写入任何文件
3. **候选词约束**：禁止全量 BIP39 词库枚举，必须用户提供候选集合
4. **导出安全**：导出结果文件仅包含地址信息，不含助记词
