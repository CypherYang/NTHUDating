# NTHUDating 架構文件

本文件說明 NTHUDating 目前的系統架構：各元件怎麼連接、程式碼怎麼分層、資料存在哪裡。內容依照專案現況整理，最後更新於 2026-11-15。

---

## 1. 專案概述

| 項目 | 說明 |
|------|------|
| 專案名稱 | NTHUDating |
| 類型 | 網頁版交友平台（MVP） |
| 執行方式 | 前後端直接跑在一台 Mac 上，資料庫等服務跑在 Docker |
| 使用方式 | 本機用 `http://localhost:5173`，同網路的其他裝置用 `http://<IP>:5173` |

---

## 2. 系統架構

### 2.1 整體架構圖

```
┌──────────────────────────────────────────────────────────────┐
│                          瀏覽器                               │
│            A 電腦本機，或同網路的 B 電腦／手機                  │
└──────────────────────────────┬───────────────────────────────┘
                               │ HTTP + WebSocket（只連 5173）
                               ▼
┌──────────────────────────────────────────────────────────────┐
│            前端 Vue 3 — Vite 開發伺服器 :5173                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ 頁面 Views   │  │ 狀態 Pinia   │  │ Vite 代理          │  │
│  │ 18 個路由    │  │ 7 個 store   │  │ /api /ws /uploads  │  │
│  └──────────────┘  └──────────────┘  └─────────┬──────────┘  │
└────────────────────────────────────────────────┼─────────────┘
                                                 │ 轉發到 localhost:8000
                                                 ▼
┌──────────────────────────────────────────────────────────────┐
│               後端 FastAPI — uvicorn :8000                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ 中介層       │  │ REST API     │  │ WebSocket          │  │
│  │ CORS、限流、 │  │ 9 組路由     │  │ /ws                │  │
│  │ 安全標頭     │  │ /api/...     │  │ 即時聊天、通知     │  │
│  └──────────────┘  └──────┬───────┘  └─────────┬──────────┘  │
│                           └─────────┬──────────┘             │
│  ┌──────────────┐  ┌────────────────▼─┐  ┌────────────────┐  │
│  │ 背景任務     │  │ Services         │  │ 資料模型       │  │
│  │ 清理、分數   │  │ 配對、信任分數、 │  │ SQLAlchemy     │  │
│  │ 恢復         │  │ 審核、寄信       │  │ 16 張資料表    │  │
│  └──────────────┘  └──────────────────┘  └────────────────┘  │
└───────┬────────────────┬────────────────┬──────────────┬─────┘
        ▼                ▼                ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐
│ PostgreSQL   │ │ Redis        │ │ 寄信 SMTP    │ │ uploads/   │
│ 17 + PostGIS │ │ 8            │ │ Gmail 或     │ │ 照片、     │
│ :5432        │ │ :6379        │ │ Mailpit      │ │ 聊天圖片   │
│ (Docker)     │ │ (Docker)     │ │              │ │ (本機)     │
└──────────────┘ └──────────────┘ └──────────────┘ └────────────┘
```

重點：

- **瀏覽器只連前端的 5173 埠。** `/api`、`/ws`、`/uploads` 由 Vite 代理轉給後端，其他裝置不需要直接連 8000 埠。
- **PostgreSQL 和 Redis 只綁定 `127.0.0.1`**，外部電腦無法直接連入資料庫。
- **寄信只走一條路**，由 `backend/.env` 的 SMTP 設定決定：Gmail（port 465、`SMTP_TLS=true`）或 Mailpit（port 1025，信件在 `http://localhost:8025` 查看）。

### 2.2 Docker 服務

定義在 `docker-compose.yml`：

| 容器 | 映像 | 埠 | 用途 |
|------|------|------|------|
| `nthu_postgres` | `postgis/postgis:17-3.5` | `127.0.0.1:5432` | 主資料庫（Apple Silicon 以 `linux/amd64` 執行） |
| `nthu_redis` | `redis:8-alpine` | `127.0.0.1:6379` | 快取、限流、驗證碼、Token 黑名單 |
| `nthu_mailpit` | `axllent/mailpit` | `1025`、`8025` | 開發用的信件攔截工具（使用 Gmail 時用不到） |

### 2.3 技術棧

#### 後端

| 技術 | 版本 | 用途 |
|------|------|------|
| Python | 3.13+ | 開發語言 |
| FastAPI | 0.137 | Web 框架 |
| uvicorn | 0.49 | ASGI 伺服器 |
| SQLAlchemy | 2.0（async） | ORM |
| asyncpg | 0.31 | PostgreSQL 驅動 |
| Alembic | 1.18 | 資料庫遷移 |
| GeoAlchemy2 | 0.20 | PostGIS 整合 |
| Pydantic / pydantic-settings | 2.13 / 2.14 | 資料驗證、讀取 `.env` |
| redis | 8.0 | Redis 客戶端 |
| slowapi | 0.1.10 | 速率限制 |
| PyJWT、bcrypt | 2.13、5.0 | 登入憑證、密碼雜湊 |
| aiosmtplib | 5.1 | 寄信 |
| Pillow | 12.2 | 圖片處理與縮圖 |
| pytest | 9.1 | 測試 |
| Ruff、pre-commit | 見 `.pre-commit-config.yaml` | 程式碼檢查與格式化 |

#### 前端

| 技術 | 版本 | 用途 |
|------|------|------|
| Vue | 3.x（Composition API） | 前端框架 |
| Vite | 8.x | 開發伺服器與建置 |
| Pinia | 3.x | 狀態管理 |
| Vue Router | 5.x | 路由 |
| Naive UI | 2.x | UI 元件（使用深色主題） |
| Axios | 1.x | HTTP 客戶端 |
| WebSocket | 瀏覽器原生 | 即時通訊 |
| Vitest | 4.x | 測試 |
| ESLint、Prettier | 10.x、3.x | 程式碼檢查與格式化 |

---

## 3. 後端架構

程式碼在 `backend/app/`，進入點是 `main.py`。

### 3.1 中介層

每個請求都會經過，設定在 `main.py`：

| 中介層 | 做什麼 |
|------|------|
| 安全標頭（`middleware/security_headers.py`） | 在回應加上 HSTS、`X-Frame-Options`、`X-Content-Type-Options`、`Referrer-Policy`、CSP；`/docs` 與 `/redoc` 不套用 CSP |
| 最後上線時間（`middleware/last_active.py`） | 已登入使用者請求成功後更新 `Profile.last_active`，同一人 5 分鐘內只寫一次資料庫（Redis 節流） |
| CORS | 只允許 `BACKEND_CORS_ORIGINS` 列出的來源，允許帶 Cookie |
| 速率限制（slowapi） | 每個 IP 每分鐘 60 次（`RATE_LIMIT_GLOBAL`）；登入／註冊另有 5 分鐘 10 次的限制 |

### 3.2 API 路由

REST 路由都在 `/api` 底下，WebSocket 在 `/ws`。完整的互動式文件在 `http://localhost:8000/docs`。

| 路由前綴 | 檔案 | 端點數 | 負責 |
|------|------|------|------|
| `/api/auth` | `api/auth.py` | 12 | 註冊、登入、Email 驗證、密碼重置、Token 更新 |
| `/api/profile` | `api/profile.py` | 10 | 個人檔案、照片、興趣標籤、位置 |
| `/api/discovery` | `api/discovery.py` | 8 | 探索候選人、喜歡、跳過、配對 |
| `/api/messages` | `api/messages.py` | 7 | 對話列表、聊天記錄、已讀、刪除訊息、上傳圖片、破冰題目 |
| `/api/safety` | `api/safety.py` | 5 | 封鎖、檢舉 |
| `/api/notifications` | `api/notifications.py` | 6 | 通知列表、未讀數、標記已讀 |
| `/api/moderation` | `api/moderation.py` | 11 | 敏感詞、內容申訴 |
| `/api/admin` | `api/admin.py` | 7 | 管理後台統計、檢舉處理、用戶管理 |
| `/api/admin/photos` | `api/photo_moderation.py` | 5 | 照片審核 |
| `/ws` | `api/websocket.py` | 1 | WebSocket 連線 |

### 3.3 Services

業務邏輯在 `services/`：

| 檔案 | 負責 |
|------|------|
| `matching_service.py` | 配對演算法與候選人查詢 |
| `trust_score.py`、`trust_score_recovery.py` | 信任分數調整、每日恢復 |
| `content_moderation.py`、`photo_moderation.py` | 敏感詞過濾、照片審核 |
| `email.py`、`email_rate_limiter.py` | 寄信、寄信頻率限制 |
| `verification_code.py`、`verification_limiter.py` | Email 驗證碼、驗證次數限制 |
| `login_limiter.py` | 登入失敗次數限制 |
| `token_blacklist.py`、`token_invalidator.py` | 登出與改密碼後讓舊 Token 失效 |
| `file_storage.py` | 照片與聊天圖片的儲存、縮圖 |
| `account_cleanup.py`、`pass_cleanup.py` | 清理已刪除帳號、過期的跳過記錄 |
| `redis_client.py` | Redis 連線管理 |

### 3.4 背景任務

後端啟動時（`main.py` 的 `lifespan`）會啟動這些定期任務，關閉時一併停止：

- Token 黑名單清理
- WebSocket 心跳與失效連線清理
- 已刪除帳號清理
- 信任分數恢復
- 跳過記錄清理

### 3.5 認證

- 支援兩種方式：HttpOnly Cookie 搭配 CSRF Token（主要），以及 Bearer Token（備用）。
- Access Token 有效 30 分鐘，Refresh Token 有效 30 天。
- 密碼以 bcrypt 雜湊儲存。
- WebSocket 連線後的第一則訊息必須是認證訊息，Token 不放在網址上。

### 3.6 即時聊天

聊天分成兩條路：

| 走 REST API | 走 WebSocket |
|------|------|
| 對話列表、歷史訊息（游標分頁） | 傳送與接收新訊息 |
| 上傳聊天圖片 | 打字中指示 |
| 刪除訊息 | 已讀回條 |
| 抽破冰辯論題 | 加入／離開聊天室、心跳 |

訊息類型有 `TEXT`、`IMAGE`、`GIF`。對方不在聊天室時，後端會寫入一筆通知並透過 WebSocket 推送。

**破冰辯論題**：聊天室的「破冰」按鈕呼叫 `POST /api/messages/matches/{match_id}/debate-topic`，後端從 `debate_topics` 隨機抽一題，存成一則 `TEXT` 訊息（開頭固定為「🎲 破冰辯論題：」）並廣播給雙方。同一個配對 5 秒內只能抽一次。

---

## 4. 前端架構

程式碼在 `frontend/src/`：

| 目錄 | 說明 |
|------|------|
| `views/` | 頁面：首頁、登入、註冊、Email 驗證、忘記／重設密碼、個人檔案、設定、探索、喜歡你、配對、訊息列表、聊天室、通知、封鎖名單、我的檢舉；`views/admin/` 是管理後台 |
| `components/` | 共用元件；`chat/` 是聊天相關，`layout/` 是導覽列，`ui/` 是基礎元件 |
| `stores/` | Pinia：`user`、`profile`、`discovery`、`chat`、`websocket`、`notification`、`safety` |
| `api/` | Axios 客戶端與認證 API |
| `router/` | 路由設定（18 個路由） |
| `composables/` | 可重用的組合式函式 |
| `utils/` | 工具函式（日期、距離、JWT、logger 等） |
| `assets/styles/tokens.css` | 色彩與樣式變數（深色主題的顏色在這裡調整） |

Vite 代理設定在 `frontend/vite.config.js`，把 `/api`、`/ws`、`/uploads` 轉給 `localhost:8000`。

---

## 5. 資料庫

共 16 張資料表，由 Alembic 遷移建立（`backend/alembic/versions/`）。

### 5.1 資料表關係

```
┌─────────┐ 1:1 ┌──────────┐ 1:N ┌────────┐
│  users  ├────▶│ profiles ├────▶│ photos │
└────┬────┘     └────┬─────┘     └────────┘
     │               │ N:M（profile_interests）
     │               ▼
     │          ┌───────────────┐
     │          │ interest_tags │
     │          └───────────────┘
     │
     │  喜歡／跳過／配對
     ├────▶ likes ──┐
     ├────▶ passes  ├─ 互相喜歡時建立 ─▶ matches ──1:N──▶ messages
     │              ┘
     │  安全與審核
     ├────▶ blocked_users
     ├────▶ reports
     ├────▶ content_appeals
     ├────▶ moderation_logs
     ├────▶ trust_score_logs
     │
     │  通知
     └────▶ notifications

獨立的資料表（不關聯到使用者）：
  sensitive_words   敏感詞清單
  debate_topics     破冰辯論題庫
```

### 5.2 資料表欄位

| 資料表 | 用途 | 主要欄位 |
|------|------|------|
| `users` | 帳號 | email、password_hash、email_verified、date_of_birth、trust_score、warning_count、is_active、is_admin、ban_reason、banned_until、deleted_at |
| `profiles` | 個人檔案 | user_id、display_name、gender、bio、location（PostGIS）、location_name、年齡／距離／性別偏好、is_complete、is_visible、last_active |
| `photos` | 照片 | profile_id、url、thumbnail_url、display_order、is_profile_picture、moderation_status、rejection_reason |
| `interest_tags` | 興趣標籤 | name、category、icon、is_active |
| `profile_interests` | 個人檔案與興趣的對應 | 多對多關聯表，連接 profiles 與 interest_tags |
| `likes` | 喜歡 | from_user_id、to_user_id |
| `passes` | 跳過 | from_user_id、to_user_id、passed_at（24 小時後可再次出現） |
| `matches` | 配對 | user1_id、user2_id、status、matched_at、unmatched_at、unmatched_by |
| `messages` | 聊天訊息 | match_id、sender_id、content、message_type、is_read（讀取時間）、deleted_at（軟刪除）、sent_at |
| `blocked_users` | 封鎖 | blocker_id、blocked_id、reason |
| `reports` | 檢舉 | reporter_id、reported_user_id、report_type、reason、evidence、status、admin_notes |
| `notifications` | 通知 | user_id、type、title、content、data（JSON）、is_read |
| `sensitive_words` | 敏感詞 | word、category、severity、action、is_regex、is_active |
| `content_appeals` | 內容申訴 | user_id、appeal_type、rejected_content、reason、status、admin_response |
| `moderation_logs` | 審核記錄 | user_id、content_type、original_content、is_approved、violations、action_taken |
| `trust_score_logs` | 信任分數變更記錄 | user_id、action、adjustment、new_score、reason |
| `debate_topics` | 破冰辯論題庫 | content、is_active（預設 100 題） |

### 5.3 PostGIS 地理位置

配對需要計算使用者之間的距離，所以資料庫使用 PostGIS。

- `profiles.location` 是 `Geography(POINT, 4326)`，以球面計算，距離單位是公尺。
- 用到的函式：

| 函式 | 用途 | 位置 |
|------|------|------|
| `ST_MakePoint`、`ST_SetSRID` | 由經緯度建立位置點（經度在前） | `api/profile.py` |
| `ST_DWithin` | 篩選指定距離內的候選人，可使用空間索引 | `services/matching_service.py` |
| `ST_Distance` | 計算實際距離，用於距離評分 | `services/matching_service.py` |

### 5.4 Redis 的用途

Redis 不存主要資料，只存短期狀態：速率限制計數、登入失敗次數、Email 驗證碼、Token 黑名單、最後上線時間的節流、抽題冷卻、敏感詞與興趣標籤快取。

---

## 6. 設定檔

| 檔案 | 用途 | 是否進版本控制 |
|------|------|------|
| `backend/.env` | 資料庫與 Redis 連線、SMTP、`FRONTEND_URL`、`BACKEND_CORS_ORIGINS` | 否，每台電腦各自建立 |
| `backend/.env.example` | `.env` 的範本 | 是 |
| `backend/app/core/config.py` | 所有設定項目與預設值 | 是 |
| `docker-compose.yml` | Docker 服務 | 是 |
| `frontend/vite.config.js` | 開發伺服器與代理 | 是 |

`.env` 只在後端啟動時讀取一次，修改後要重啟後端才會生效。

---

## 7. 測試

| 項目 | 說明 |
|------|------|
| 後端 | `backend/tests/`，pytest + pytest-asyncio，執行 `pytest -v` |
| 前端 | Vitest，執行 `npm run test` |
| 說明文件 | [testing/TESTING_GUIDE.md](testing/TESTING_GUIDE.md)、[testing/MUTATION_TESTING.md](testing/MUTATION_TESTING.md) |

破冰辯論題功能目前沒有自動化測試。

---

## 8. 相關文件

| 文件 | 說明 |
|------|------|
| [FEATURES.md](FEATURES.md) | 功能清單 |
| [MATCHING_ALGORITHM.md](MATCHING_ALGORITHM.md) | 配對演算法 |
| [TRUST_SCORE_SYSTEM.md](TRUST_SCORE_SYSTEM.md) | 信任分數機制 |
| [CURSOR_PAGINATION.md](CURSOR_PAGINATION.md) | 聊天記錄的游標分頁 |
| [ROADMAP.md](ROADMAP.md) | 開發規劃 |
| [管理員設置指南.md](管理員設置指南.md) | 建立管理員帳號 |
