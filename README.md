README
概要
このリポジトリは SvelteKit + Tailwind CSS を用いたフロントエンドと、FastAPI ベースのバックエンドからなるシンプルな画像編集アプリです。ユーザーがアップロードした画像に対し、Gemini 生成 API を利用して指定のプロンプトに沿った加工画像を返します。

frontend (SvelteKit) ── fetch ──> /generate (FastAPI) ──> Gemini API
主な特徴
画像ファイルをブラウザからアップロードし、編集条件（プロンプト）を指定

Google Gemini の image generation 機能を用いたサーバサイド処理

Tailwind CSS v4 によるスタイル適用

SvelteKit の static adapter を使った SPA ビルド（build/ 出力）

バックエンドはビルド済み静的ファイルを配信可能

ディレクトリ構成
svelte_practice/
├─ src/                 # SvelteKit フロントエンド
│  ├─ routes/           # ルーティング (+page.svelte など)
│  └─ app.css           # Tailwind CSS 読み込み
├─ backend/             # FastAPI バックエンド
│  ├─ main.py
│  └─ requirements.txt
├─ static/              # 開発中の静的アセット (favicon 等)
├─ svelte.config.js     # Static adapter 設定
├─ vite.config.ts       # Vite + Tailwind プラグイン設定
└─ tailwind.config.ts   # Tailwind v4 設定
セットアップ
1. フロントエンド依存関係
npm install
2. バックエンド依存関係
cd backend
pip install -r requirements.txt
3. 環境変数
バックエンドで Google Gemini API キーを使用するため、.env などで GEMINI_API_KEY を設定してください。

# backend/.env 例
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
フロントエンドからバックエンドのベース URL を切り替える場合は PUBLIC_API_BASE を設定します（未設定時は相対パス /generate に POST）。

# .env (プロジェクトルート)
PUBLIC_API_BASE=https://your-api-host.example.com
開発モードで起動
別ターミナルでフロントエンドとバックエンドをそれぞれ立ち上げます。

# ターミナル1 - フロントエンド
npm run dev    # http://localhost:5173

# ターミナル2 - バックエンド
cd backend
uvicorn main:app --reload --port 8000
ブラウザで http://localhost:5173 を開き、画像をアップロードしてプロンプトを入力すると、バックエンド経由で Gemini API が呼ばれます。

本番ビルド & 配信
フロントエンドをビルド

npm run build   # build/ 配下に出力
バックエンドで静的ファイルを配信
backend/main.py の STATIC_DIR にビルド出力パス（デフォルトで backend/static/）を指定し、成果物をコピーしてから FastAPI を起動します。

# 例: build を backend/static にコピー
cp -r build backend/static

# バックエンド起動
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
これで / で Svelte アプリが配信され、/generate で画像生成 API が動作します。

API エンドポイント
POST /generate

フォームフィールド:

file: アップロード画像 (multipart/form-data)

prompt: 指示テキスト

レスポンス（成功時）:

{ "image_url": "data:image/png;base64,..." }
GET /healthz : ヘルスチェック
