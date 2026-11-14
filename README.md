# NTHUDating 交友平台

交友平台 MVP，後端使用 FastAPI，前端使用 Vue 3，資料庫使用 PostgreSQL + PostGIS，並以 Redis 做快取與限流。


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

## 技術

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

### 1.確認docker正常
```bash
docker info > /dev/null && echo "Docker 正常"
```
### 2.啟動docker(在專案目錄下)
```bash
docker compose up -d
docker compose ps
```
### 3.設定後端
```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -r requirements-dev.txt
pip install greenlet
pre-commit install
```
### 4.建立環境變數與資料表

```bash
cp .env.example .env          # 已存在 .env 時不要重複執行
```

編輯 `backend/.env`，至少確認以下設定：

```
DATABASE_URL=postgresql+asyncpg://nthu:nthu123@localhost:5432/nthu
REDIS_URL=redis://:nthu_redis123@localhost:6379/0
FRONTEND_URL=http://localhost:5173
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

設定好 `.env` 之後再建立資料表：

```bash
source venv/bin/activate
alembic upgrade head
python scripts/init_interest_tags.py
```

### 5.設定前端

```bash
cd ../frontend
npm install
```

### 6.啟動後端：

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 啟動前端

```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

### 8. 開啟網站
server 用 http://localhost:5173
ipconfig getifaddr en0：查看ip
client 用 http://<IP>:5173（例如 http://192.168.213.50:5173）


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


