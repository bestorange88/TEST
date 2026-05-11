# 中央结算公司 - 交易平台

一个完整的金融交易平台，包含前端H5应用、后端API服务和管理后台。

## 项目结构

```
├── frontend/          # 前端H5应用 (Vue 3 + Vite)
├── server/            # 后端API服务 (Node.js + Express + SQLite)
└── admin/             # 管理后台 (Vue 3 + Element Plus)
```

## 功能特性

### 前端H5
- 用户登录/注册
- 首页（产品推荐、快捷操作、通知公告）
- 产品列表（实时价格行情）
- 产品详情（K线图、买涨/买跌/双向交易）
- 个人中心（资产总览、信用分）
- 实名认证
- 订单记录（持仓列表/平仓记录）
- 充值/提现
- 绑定银行卡
- 设置（修改密码、语言设置）

### 后端API
- JWT身份认证
- 用户管理（注册、登录、实名认证）
- 产品管理（CRUD、K线数据）
- 订单系统（下单、自动平仓）
- 资金管理（充值、提现、余额）
- 银行卡管理

### 管理后台
- 数据概览（Dashboard）
- 用户管理（查看、编辑、重置密码）
- 产品管理（增删改查）
- 订单管理（查看、强制平仓）
- 充值审核（通过/拒绝）
- 提现审核（通过/拒绝）
- 通知管理（增删改查）

## 快速开始

### 安装依赖

```bash
# 后端
cd server && npm install

# 前端
cd frontend && npm install

# 管理后台
cd admin && npm install
```

### 启动服务

```bash
# 启动后端 (端口 3000)
cd server && npm run dev

# 启动前端 (端口 5173)
cd frontend && npm run dev

# 启动管理后台 (端口 5174)
cd admin && npm run dev
```

### 默认账号

- **管理后台**: admin / admin123
- **前端注册**: 自行注册新用户

## 技术栈

- **前端**: Vue 3, Vite, Vue Router, Pinia, Axios
- **后端**: Node.js, Express, better-sqlite3, JWT, bcryptjs
- **管理后台**: Vue 3, Vite, Element Plus, Vue Router
