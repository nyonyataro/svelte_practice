import base64
import logging
import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# .env 読み込み
load_dotenv()

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて絞る
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("環境変数 GEMINI_API_KEY が設定されていません")

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-preview-image-generation:generateContent"
    f"?key={GEMINI_API_KEY}"
)


@app.post("/generate")
async def generate_image(file: UploadFile, prompt: str = Form(...)):
    logger.info(
        f"受信: prompt='{prompt}', file='{file.filename}' ({file.content_type})"
    )

    # 画像Base64化
    img_data = base64.b64encode(await file.read()).decode()

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inlineData": {"mimeType": file.content_type, "data": img_data}},
                ],
            }
        ],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }

    logger.debug(f"送信ペイロード: {payload}")

    # API呼び出し
    r = requests.post(API_URL, json=payload)
    logger.info(f"Gemini API ステータス: {r.status_code}")

    if r.status_code != 200:
        logger.error(f"Gemini API エラー: {r.text}")
        return {"error": r.json()}

    data = r.json()

    # partsから画像抽出
    parts = data.get("candidates", [])[0].get("content", {}).get("parts", [])
    image_part = next((p for p in parts if "inlineData" in p), None)

    if image_part:
        mime = image_part["inlineData"].get("mimeType", "image/png")
        image_base64 = image_part["inlineData"]["data"]
        logger.info("画像生成成功")
        return {"image_url": f"data:{mime};base64,{image_base64}"}
    else:
        logger.warning("画像が生成されなかった")
        return {"error": "画像が生成されませんでした", "raw_response": data}
