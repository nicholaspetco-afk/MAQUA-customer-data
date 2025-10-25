# MAQUA 會員查詢（Flask）

此目錄可直接推上 GitHub，支援本地開發與雲端部署（Gunicorn / Docker）。

## 結構
- `app.py`：Flask 主程式與路由（首頁、`POST /api/profile`）
- `manus_app.py`：部署入口，啟用 CORS 與 `/healthz`，支援 `PORT` 環境變數
- `services/`：業務服務與 CRM 對接模組
- `templates/index.html`、`static/members.css`：前端頁面與樣式
- `requirements.txt`：依賴（含 `Flask`、`Flask-Cors`、`requests`）
- `Procfile`：Gunicorn 啟動宣告
- `Dockerfile`：容器部署

## 本地啟動
```bash
pip3 install -r requirements.txt
FLASK_APP=manus_app.py flask run --host 0.0.0.0 --port 4001
# 或
python manus_app.py  # 讀取 PORT/FLASK_PORT，預設 5000
```
瀏覽 `http://127.0.0.1:<port>/`，健康檢查 `GET /healthz` 應回 `OK`。

## 生產部署（無 Docker）
- Koyeb / Railway：Start Command 設 `gunicorn -b 0.0.0.0:$PORT manus_app:app`
- 設定（選用）：`ALLOWED_ORIGINS` 控制 CORS 允許來源（預設 `*`）

## 環境變數
- 必填：`APP_KEY`、`APP_SECRET`、`TENANT_ID`
- 選填：`ALLOWED_ORIGINS`、`TOKEN_URL`、`GATEWAY_URL`
- 本地測試可先用 `export` 設定：
```bash
export APP_KEY="你的APP_KEY"
export APP_SECRET="你的APP_SECRET"
export TENANT_ID="你的TENANT_ID"
```
- Koyeb 請在 Service > Settings > Environment 中設定以上變數。

## 生產部署（Docker）
使用 `Dockerfile`，平台會對外暴露 `PORT`（Cloud Run/Fly.io 預設 8080）。