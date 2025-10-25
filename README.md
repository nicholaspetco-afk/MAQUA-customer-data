# MAQUA 會員查詢 · Render 部署包

這個目錄整理了部署到 Render 所需的最小檔案，內容取自 `manus查詢用戶資料` 專案，方便上傳至 GitHub 後直接建立 Render Web Service。

## 目錄結構

- `app.py`：核心 Flask 應用程式，提供 `/api/profile` 會員查詢 API 與頁面邏輯。
- `manus_app.py`：Render/Gunicorn 入口，啟用 CORS 與健康檢查，並自動讀取平台提供的 `PORT`。
- `requirements.txt`：部署時會安裝的 Python 套件清單。
- `Procfile`：Render 會用來啟動 `gunicorn manus_app:app`。
- `render.yaml`：Render 自動化部署設定（單一 web service）。
- `services/`、`templates/`、`static/`：後端呼叫設定、Jinja2 樣板與前端靜態資源。

## 本地測試

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manus_app.py  # Render 上會改由 gunicorn 啟動
```

瀏覽 `http://127.0.0.1:5000/`，輸入密碼 `maqua28453792` 後進入查詢頁面。

## Render 部署流程

1. 將此目錄內容推送到 GitHub（建議保持目錄名稱 `render 查詢資料` 或自行調整引用路徑）。
2. Render 控制台新增 **Web Service** → 選取對應的 GitHub Repo。
3. 若 repo 根目錄即為此資料夾，Build/Start command 可直接沿用 `render.yaml` 的設定；否則請手動指定：
   - Build Command：`pip install -r requirements.txt`
   - Start Command：`gunicorn manus_app:app`
4. Deploy 後確認 Render logs 顯示 `Starting gunicorn...` 並監控 `/healthz`、`/` 行為是否正常。

> 若需要自訂允許來源，可在 Render 環境變數新增 `ALLOWED_ORIGINS`，多個來源以逗號分隔。
