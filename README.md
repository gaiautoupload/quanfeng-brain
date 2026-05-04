# 🤖 智慧客服 (Smart Customer Service)

**RAG 智慧問答系統** — 基於道路救援、機場接送知識庫的 AI 問答平台

---

## 📋 功能特色

- **RAG 檢索增強生成**：整合 PDF + Excel 知識庫，共 702+ 筆資料
- **向量檢索**：ChromaDB + Ollama (nomic-embed-text) 語意搜尋
- **LLM 生成**：Qwen3.6-27B 生成專業回答
- **Web UI**：直觀的聊天介面
- **REST API**：供外部系統呼叫

---

## 🚀 快速開始

### 1. 環境需求

| 項目 | 版本 | 說明 |
|------|------|------|
| Python | >= 3.10 | 執行環境 |
| Ollama | 最新版 | 本地 LLM 推理引擎 |
| Git | - | 版本控制 |

### 2. 安裝 Ollama 並下載模型

```bash
# 安裝 Ollama (https://ollama.ai)
# 下載所需模型
ollama pull qwen3.6:27b
ollama pull nomic-embed-text
```

### 3. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 4. 準備知識庫資料

將您的 PDF 和 Excel 檔案放入 `data/` 資料夾：

```
smart-course-service/
├── data/
│   ├── *.pdf          # 知識庫 PDF 文件
│   └── *.xlsx         # 知識庫 Excel 文件
├── server.py
├── ingest.py
├── query.py
└── ...
```

### 5. 建立向量資料庫

```bash
python ingest.py
```

執行後會在 `vector_store/` 建立 ChromaDB 向量索引。

### 6. 啟動伺服器

```bash
python server.py
```

伺服器預設在 `http://localhost:8000` 啟動。

---

## 📡 API 文件

### 健康檢查

```bash
GET http://localhost:8000/health
```

**回應：**
```json
{
  "status": "healthy",
  "model": "qwen3.6:27b",
  "vector_store": "chromadb",
  "collection_count": 702
}
```

### 智慧問答

```bash
POST http://localhost:8000/query
Content-Type: application/json

{
  "query": "國道第二類特殊作業收費標準是什麼？"
}
```

**回應：**
```json
{
  "query": "國道第二類特殊作業收費標準是什麼？",
  "answer": "根據知識庫資料...",
  "sources": [
    {
      "source": "國泰金控 20260424.pdf",
      "similarity": 0.856,
      "content_preview": "..."
    }
  ]
}
```

---

## ⚙️ 參數設定

在 `server.py` 中可調整以下參數：

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `OLLAMA_MODEL` | `qwen3.6:27b` | LLM 模型名稱 |
| `EMBEDDING_MODEL` | `nomic-embed-text` | 嵌入模型名稱 |
| `TOP_K` | `10` | 檢索筆數 |
| `SIMILARITY_THRESHOLD` | `0.30` | 相似度門檻 (0~1) |
| `PORT` | `8000` | 伺服器埠號 |

---

## 📁 專案結構

```
smart-course-service/
├── server.py           # FastAPI 伺服器 (主程式)
├── ingest.py           # 資料匯入腳本 (PDF/Excel → 向量庫)
├── query.py            # 獨立問答腳本 (CLI 模式)
├── extract_pdf.py      # PDF 文字萃取工具
├── test_api.py         # API 測試腳本
├── static/             # Web UI 前端
│   └── index.html      # 聊天介面
├── data/               # 原始知識庫資料 (不上傳)
│   ├── *.pdf
│   └── *.xlsx
├── vector_store/       # ChromaDB 向量庫 (不上傳)
├── requirements.txt    # Python 依賴
├── .gitignore
└── README.md
```

---

## 🔑 機密資料 (不上傳)

以下資料**不會**包含在 GitHub 倉庫中，需自行準備：

| 資料類型 | 說明 | 取得方式 |
|----------|------|----------|
| `data/*.pdf` | 知識庫 PDF 文件 | 自行準備或向管理員索取 |
| `data/*.xlsx` | 知識庫 Excel 文件 | 自行準備或向管理員索取 |
| `vector_store/` | ChromaDB 向量索引 | 執行 `python ingest.py` 自動生成 |
| `.env` | 環境變數 (如需) | 複製 `.env.example` 並填寫 |

---

## 🛠️ 疑難排解

### Ollama 模型未找到

```bash
ollama list              # 檢查已安裝模型
ollama pull qwen3.6:27b  # 下載模型
```

### 向量資料庫為空

```bash
python ingest.py         # 重新匯入資料
```

### 埠號被佔用

```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# 或修改 server.py 中的 PORT 參數
```

### 相似度太低

降低 `SIMILARITY_THRESHOLD` 或增加 `TOP_K` 值。

---

## 📝 授權

Internal Use Only

---

**開發者：** gaiautoupload | **最後更新：** 2026-05-05
