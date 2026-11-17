# NTHUDating 交友平台

交友平台 MVP，後端使用 FastAPI，前端使用 Vue 3，資料庫使用 PostgreSQL + PostGIS，並以 Redis 做快取與限流。


## 功能

| 模組 | 說明 |
|------|------|
| 認證系統 | 註冊、登入、Email 驗證碼、密碼重置、JWT |
| 個人檔案 | 資料編輯、照片上傳、興趣標籤、地理位置 |
| 探索配對 | 滑動卡片、5 維度加權配對演算法、誰喜歡我、撤銷跳過 |
| 即時聊天 | WebSocket、圖片訊息、已讀回條、打字指示器、破冰辯論題（隨機抽題） |
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

以下步驟以 macOS 為例，會在你自己的電腦上架起一套獨立的網站（資料庫是空的，需要自己註冊帳號）。

### 前置需求

先安裝好這三樣，並把 Docker Desktop 打開：

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.13+
- Node.js 24+

### 1.下載專案

```bash
git clone https://github.com/CypherYang/NTHUDating.git
cd NTHUDating
```

### 2.確認docker正常
```bash
docker info > /dev/null && echo "Docker 正常"
```
### 3.啟動docker(在專案目錄下)
```bash
docker compose up -d
docker compose ps
```
要看到 `nthu_postgres`、`nthu_redis`、`nthu_mailpit` 三個容器都在執行。

### 4.設定後端
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
只想把網站跑起來、不打算改程式的話，`requirements-test.txt`、`requirements-dev.txt` 和 `pre-commit install` 這三行可以略過。

### 5.建立環境變數與資料表

```bash
[ -f .env ] || cp .env.example .env     # 只有還沒有 .env 時才會建立，不會蓋掉已經改好的設定
alembic upgrade head
python scripts/init_interest_tags.py
```

`.env` 用預設值就能在本機執行，不需要修改。`alembic upgrade head` 會建立所有資料表與 100 題破冰題庫，第三行會建立興趣標籤。

### 6.設定前端

```bash
cd ../frontend
npm install
```

### 7.啟動後端（這個終端機視窗保持開著）

```bash
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8.啟動前端（開新的終端機視窗）

新視窗要先進到專案的 `frontend` 資料夾：

```bash
cd NTHUDating/frontend
npm run dev -- --host 0.0.0.0
```

### 9.開啟網站

瀏覽器開 http://localhost:5173 ，註冊一個帳號。

註冊後需要輸入 Email 驗證碼。預設設定下驗證信不會真的寄出，而是被 Mailpit 攔下來，到 http://localhost:8025 就能看到驗證碼。

## 之後每次啟動

第一次設定完成後，之後只需要在專案目錄下執行：

```bash
docker compose up -d
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

另開一個終端機視窗，同樣在專案目錄下：

```bash
cd frontend && npm run dev -- --host 0.0.0.0
```

## 進階設定

修改 `backend/.env` 之後，都要重新啟動後端才會生效。

### 讓同一個網路的其他裝置連進來

1. 在執行服務的電腦上查看 IP：`ipconfig getifaddr en0`
2. 把 `backend/.env` 的這兩行改成你的 IP（以 `192.168.1.10` 為例）：

```
FRONTEND_URL=http://192.168.1.10:5173
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://192.168.1.10:5173"]
```

3. 重新啟動後端，其他裝置用 `http://192.168.1.10:5173` 開啟。

### 把驗證信寄到真實信箱（Gmail）

1. Google 帳號開啟兩步驟驗證，到 https://myaccount.google.com/apppasswords 產生一組 16 碼的應用程式密碼。
2. 把 `backend/.env` 的 SMTP 設定改成：

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=你的帳號@gmail.com
SMTP_PASSWORD=16碼應用程式密碼
SMTP_FROM_EMAIL=你的帳號@gmail.com
SMTP_FROM_NAME=NTHUDating
SMTP_TLS=true
```

port 必須是 465。`.env` 不會上傳到 GitHub，密碼請勿寫進其他檔案。

## 關閉伺服器

```bash
docker compose down           # 停止，資料保留
docker compose down -v        # 停止並清空資料庫（帳號和訊息都會不見）
docker rm -f $(docker ps -aq) # 清空container
docker volume rm -f $(docker volume ls -q) #清空volume
docker rmi -f $(docker images -aq)#清空image
```

## 常見問題

| 狀況 | 處理方式 |
|------|------|
| `docker compose up` 出現 `no matching manifest for linux/arm64` | 確認 `docker-compose.yml` 的 postgres 服務有 `platform: linux/amd64` |
| 註冊或登入失敗，後端出現 `Connection refused` | Docker 容器沒有啟動，執行 `docker compose up -d` |
| 執行 `init_interest_tags.py` 出現 `greenlet library is required` | 執行 `pip install greenlet` |
| 收不到驗證信 | 預設是寄到 Mailpit，到 http://localhost:8025 查看；使用 Gmail 時檢查應用程式密碼與 port 465 |
| 其他裝置開得了網頁但無法註冊登入 | `backend/.env` 的 `FRONTEND_URL`、`BACKEND_CORS_ORIGINS` 沒有改成實際 IP，或改完沒有重啟後端 |
| 改了 `.env` 沒有效果 | `.env` 只在後端啟動時讀取，需要重新啟動後端 |

Windows 使用者：啟用虛擬環境的指令是 `venv\Scripts\activate`，查看 IP 用 `ipconfig`，其餘步驟相同。這份專案只在 macOS 上實際執行過。

預設的資料庫與 Redis 密碼是公開的開發用密碼，僅適合在自己的電腦上執行，不要直接用來架設對外的正式網站。


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
└── docker-compose.yml    # 基礎服務設定
```
