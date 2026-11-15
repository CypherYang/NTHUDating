# NTHUDating 開發指南

> 詳細開發流程請使用 **Skill: nthu-quickstart**

---

## 專案資訊

- **專案名稱**: NTHUDating 交友平台
- **技術棧**: FastAPI + Vue 3 + PostgreSQL + PostGIS + Redis

---

## 快速開始（3 步驟）

```bash
# 1. 啟動基礎設施 (postgres / redis / mailpit)
docker compose up -d

# 2. 啟動後端 (http://localhost:8000/docs)
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 啟動前端 (http://localhost:5173)
cd frontend && npm run dev
```

---

## 可用的 Skills

| Skill | 用途 |
|-------|------|
| **api-routing-standards** | API 路由規則 - 強制「無尾隨斜線」以防止 404 錯誤 |
| **backend-dev-fastapi** | FastAPI + SQLAlchemy 2.0 Async 開發模式 |
| **frontend-dev-vue3** | Vue 3 Composition API + Pinia 開發模式 |
| **nthu-quickstart** | 完整開發流程、指令和故障排除 |
| **project-audit** | 專案健康檢查 - 功能完整性和一致性 |
| **ui-ux-pro-max** | UI/UX 設計智能 - 67 種樣式、96 種配色、字型配對與元件範例 |

### Skills 結構

```
.claude/skills/
├── api-routing-standards/
│   ├── SKILL.md
│   └── references/           # 尾隨斜線規則、RESTful 原則
├── backend-dev-fastapi/
│   └── SKILL.md
├── frontend-dev-vue3/
│   └── SKILL.md
├── nthu-quickstart/
│   ├── SKILL.md
│   └── references/           # 指令、工具、故障排除、工作流程
├── project-audit/
│   ├── SKILL.md
│   └── references/           # 功能狀態、前後端差異、E2E 測試指南
└── ui-ux-pro-max/
    ├── SKILL.md
    ├── data/
    └── scripts/
```

---

## 重要規則：禁止尾隨斜線

所有 API 端點必須不使用尾隨斜線。這是由 `redirect_slashes=False` 強制執行的。

```python
# 正確
@router.get("")                  # GET /api/profile
@router.put("/interests")        # PUT /api/profile/interests

# 錯誤（會導致 404）
@router.get("/")                 # 404
@router.put("/interests/")       # 404
```

```javascript
// 前端也必須沒有尾隨斜線
await axios.get('/api/profile')          // 正確
await axios.get('/api/profile/')         // 404
```

詳細資訊請使用 **Skill: api-routing-standards**

---

## 專案結構

> 詳見 [README.md](README.md#-專案結構)

---

## 常用指令

```bash
# 資料庫
docker exec -it nthu_postgres psql -U nthu -d nthu

# 測試
cd backend && pytest -v --cov=app

# 程式碼品質（commit 時自動執行）
pre-commit run --all-files            # 手動執行全部檢查
ruff check backend/ --fix             # 後端 lint + 自動修復
ruff format backend/                  # 後端格式化
cd frontend && npm run lint:fix       # 前端 lint + 自動修復
cd frontend && npm run format         # 前端格式化

# 重置
docker compose down -v && docker compose up -d
```

完整指令列表請使用 **Skill: nthu-quickstart**

---

## 相關文件

- **README.md** - 專案概述（含快速開始）
- **docs/ARCHITECTURE.md** - 技術架構

---

## 核心原則

1. **禁止尾隨斜線** - 所有 API 端點不使用 `/` 結尾
2. **非同步優先** - 後端使用 async/await
3. **Composition API** - 前端使用 `<script setup>`
4. **測試驅動** - TDD 開發流程
5. **使用 Skills** - 開發時參考 skills

---

## Design Context

### Users
- **目標用戶**: 台灣 18+ 年輕族群，尋找真誠交友關係
- **使用情境**: 通勤、休息時間瀏覽，晚間深度互動
- **核心需求**: 在安全可靠的環境中認識新朋友，不追求速食式配對



