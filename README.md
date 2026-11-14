# NTHUDating 交友平台

交友平台 MVP，後端使用 FastAPI，前端使用 Vue 3，資料庫使用 PostgreSQL + PostGIS，並以 Redis 做快取與限流。

> 本專案為學習與開發用途，改寫自 [twtrubiks/MergeMeet](https://github.com/twtrubiks/MergeMeet)（Apache-2.0）。

## 功能

| 模組 | 說明 |
|------|------|
| 認證系統 | 註冊、登入、Email 驗證碼、密碼重置、JWT |
| 個人檔案 | 資料編輯、照片上傳、興趣標籤、地理位置 |
| 探索配對 | 滑動卡片、5 維度加權配對演算法、誰喜歡我、撤銷跳過 |
| 即時聊天 | WebSocket、圖片訊息、已讀回條、打字指示器 |
| 安全功能 | 封鎖、檢舉、內容審核、信任分數機制 |
| 管理後台 | 統計儀表板、檢舉處理、用戶管理 |
| 通知系統 | 通知中心、未讀計數、即時推送 |

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 | Python 3.13+、FastAPI、SQLAlchemy 2.0（async）、Alembic |
| 前端 | Vue 3（Composition API）、Vue Router、Pinia、Vite、Naive UI |
| 資料庫 | PostgreSQL 17 + PostGIS 3.5 |
| 快取 | Redis 8 |
| 開發基礎設施 | Docker Compose（PostgreSQL、Redis、Mailpit） |

### 配對演算法

以五個維度加權評分：

| 維度 | 權重 | 說明 |
|------|------|------|
| 興趣匹配 | 50% | 每個共同興趣 10 分，最高 50 分 |
| 地理距離 | 20% | 使用 PostGIS 計算，越近分數越高 |
| 活躍度 | 20% | 依最後上線時間評分 |
| 檔案完整度 | 5% | 照片數量與自我介紹 |
| 信任分數 | 5% | 用戶信譽評分 |

## 快速開始

### 前置需求

- Docker Desktop
- Python 3.13+
- Node.js 24+

### 1. 啟動基礎服務

```bash
docker compose up -d
docker compose ps
```

會啟動 PostgreSQL、Redis 和 Mailpit。PostgreSQL 與 Redis 只綁定 `127.0.0.1`，外部無法直接連線。

### 2. 設定後端

```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -r requirements-dev.txt
pip install greenlet          # SQLAlchemy 非同步模式需要，目前 requirements 未列出
pre-commit install

cp .env.example .env          # 已存在 .env 時不要重複執行
```

編輯 `backend/.env`，至少確認以下設定：

```
DATABASE_URL=postgresql+asyncpg://nthu:nthu123@localhost:5432/nthu
REDIS_URL=redis://:nthu_redis123@localhost:6379/0
FRONTEND_URL=http://localhost:5173
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

寄信設定見下方〈寄信設定〉。

建立資料表並初始化興趣標籤（首次執行）：

```bash
alembic upgrade head
python scripts/init_interest_tags.py
```

啟動後端：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 設定前端

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

### 4. 開啟網站

| 服務 | 網址 |
|------|------|
| 網站 | http://localhost:5173 |
| API 文件 | http://localhost:8000/docs |
| 驗證信箱（Mailpit，僅開發用） | http://localhost:8025 |
| 管理後台 | http://localhost:5173/admin/login（設定方式見[管理員設置指南](./docs/管理員設置指南.md)） |

## 寄信設定

註冊、重設密碼等功能需要寄信。`backend/.env` 有兩種模式：

**開發模式（預設）**：信件由 Mailpit 攔截，顯示在 http://localhost:8025，不會真的寄出。

```
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_TLS=false
```

**Gmail 模式**：信件會寄到收件人的信箱，適合 demo 或正式測試。

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=你的寄件Gmail
SMTP_PASSWORD=你的16碼應用程式密碼
SMTP_FROM_EMAIL=你的寄件Gmail
SMTP_FROM_NAME=NTHUDating
SMTP_TLS=true
```

- 應用程式密碼需要先開啟 Google 帳號的兩步驟驗證，再到「應用程式密碼」頁面建立，**不是 Gmail 登入密碼**。
- 目前程式使用直接加密連線（`use_tls`），Gmail 必須用 465 埠，不支援 587 + STARTTLS。
- 寄件人只有一組（即 `SMTP_USER`），收件人可以是任何信箱，包括觀眾自己的 Gmail。

## 讓其他裝置連線

後端和前端都要用 `--host 0.0.0.0` 啟動。依照連線方式，修改 `backend/.env`：

| 情境 | `FRONTEND_URL` 與 `BACKEND_CORS_ORIGINS` 設定為 |
|------|------|
| 同一個 Wi-Fi | `http://<電腦的區網IP>:5173` |
| Tailscale 跨網路 | `http://<Tailscale 位址>:5173` |
| 公開通道（demo） | `https://xxxx.trycloudflare.com`，並在 `frontend/vite.config.js` 的 `server` 加上 `allowedHosts: ['.trycloudflare.com']` |

修改後要重啟後端。`FRONTEND_URL` 會寫進信件連結，要填觀眾實際會打開的網址。

查詢區網 IP：

```bash
ipconfig getifaddr en0
```

> 公開通道與區網開放僅適合 demo。開發環境使用預設密碼，不要在公用網路長時間開放。

## 測試

```bash
cd backend && pytest -v --cov=app    # 後端測試
cd frontend && npm run test          # 前端測試（Vitest）
```

提交時 pre-commit 會自動執行 Ruff、ESLint、Prettier 等檢查。手動執行：

```bash
pre-commit run --all-files
```

## 專案結構

```text
NTHUDating/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 設定、資料庫、安全、Cookie、限流
│   │   ├── middleware/   # 安全標頭、最後上線時間
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 驗證格式
│   │   ├── services/     # 業務邏輯（配對、信任分數、寄信、照片審核）
│   │   ├── websocket/    # WebSocket 連線管理
│   │   └── main.py       # 應用程式入口
│   ├── alembic/          # 資料庫遷移
│   ├── scripts/          # 初始化腳本
│   ├── tests/            # pytest 測試
│   └── uploads/          # 上傳的照片與檔案（執行時產生，不納入版本控制）
├── frontend/
│   └── src/
│       ├── views/        # 頁面
│       ├── components/   # 共用元件
│       ├── stores/       # Pinia 狀態
│       ├── router/       # 路由
│       ├── api/          # API 客戶端
│       └── assets/styles/tokens.css  # 色彩與樣式變數
├── docs/                 # 專案文件
└── docker-compose.yml    # 基礎服務設定
```

## 文件

| 文件 | 說明 |
|------|------|
| [技術架構](./docs/ARCHITECTURE.md) | 系統架構、資料庫設計、API 設計 |
| [安全機制](./docs/SECURITY.md) | 認證授權、資料保護、安全措施 |
| [功能清單](./docs/FEATURES.md) | 完整功能說明 |
| [配對演算法](./docs/MATCHING_ALGORITHM.md) | 配對評分細節 |
| [信任分數系統](./docs/TRUST_SCORE_SYSTEM.md) | 信任分數規則 |
| [測試指南](./docs/testing/TESTING_GUIDE.md) | 測試策略與執行方式 |

## 常見問題

- **`relation "users" does not exist`**：還沒執行 `alembic upgrade head`。
- **`Connection refused` 到 5432**：PostgreSQL 容器沒有啟動，執行 `docker compose ps` 檢查。
- **Apple Silicon 無法拉取 PostgreSQL 映像**：`docker-compose.yml` 的 postgres 服務需要加上 `platform: linux/amd64`。
- **收不到驗證信**：確認寄信設定，後端終端機會顯示 `Email sent successfully` 或 `Failed to send email`。
- **別的裝置打不開網站**：確認 IP 正確、防火牆允許連入、前後端都使用 `--host 0.0.0.0`。

## 授權

Apache-2.0。原始專案版權屬於 [twtrubiks](https://github.com/twtrubiks)，改寫部分的版權聲明請依你的需求補充。
