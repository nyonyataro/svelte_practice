# ---- Frontend build stage ----
FROM node:20-alpine AS fe
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
# どれか一つが存在すればOKなので、失敗しても無視しない方針で
RUN npm ci
COPY . .
# SvelteKit静的ビルド（adapter-static）
RUN npm run build

# ---- Backend runtime stage ----
FROM python:3.11-slim AS be
WORKDIR /app

# OSレベル最小限
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Python依存
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# FastAPIアプリ
COPY backend /app/backend

# フロントの静的ファイルをFastAPIの配信用ディレクトリへ
# （main.py で StaticFiles(directory="static") を想定）
COPY --from=fe /app/build /app/backend/static

# 環境変数（UVICORNポート）
ENV PORT=8080
EXPOSE 8080

# 本番サーバ（gunicorn+uvicorn workerでもOK。依存は適宜requirementsに）
# ここはuvicorn単体で十分
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
