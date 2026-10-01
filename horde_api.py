"""
Stable Horde Anime Image Generator API & Sunucusu
=================================================
Perchance'ın kullandığı gerçek anime modellerini (Animagine XL, Anything v5, Pony)
içeren tamamen ücretsiz, filigransız ve bot engelsiz REST API çözümü.

Kullanım:
1. Python Scripti Olarak:
   python horde_api.py

2. API Sunucusu Olarak (Port 5000):
   python horde_api.py --server
"""

import sys
import io
import time
import requests
import json
import base64
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HORDE_API_URL = "https://aihorde.net/api/v2"
ANON_API_KEY = "0000000000"

DEFAULT_NEGATIVE = '''lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name'''

def generate_anime_image(
    prompt: str,
    negative_prompt: str = DEFAULT_NEGATIVE,
    models: list = None,
    width: int = 1024,
    height: int = 576, # 16:9 Wallpaper
    steps: int = 30,
    cfg_scale: float = 7.0,
    api_key: str = ANON_API_KEY,
    output_path: str = "anime_wallpaper.png"
) -> dict:
    """
    Stable Horde API üzerinden yüksek kaliteli anime görseli üretir.
    """
    if models is None:
        models = ["Animagine XL", "AMPonyXL", "Anything v5", "CyberRealistic Pony", "AlbedoBase XL 3.1"]

    headers = {
        "apikey": api_key,
        "Content-Type": "application/json",
        "Client-Agent": "AnimeApiServer:1.0.0"
    }

    payload = {
        "prompt": f"{prompt} ### {negative_prompt}",
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "steps": steps,
            "n": 1
        },
        "models": models,
        "nsfw": True,
        "censor_nsfw": False,
        "shared": True
    }

    print(f">> Üretim isteği gönderiliyor (Modeller: {models})...")
    res = requests.post(f"{HORDE_API_URL}/generate/async", headers=headers, json=payload, timeout=30)
    if res.status_code != 202:
        raise Exception(f"Horde API Hatası: {res.status_code} - {res.text}")

    req_id = res.json()["id"]
    print(f"✅ Görev kuyruğa alındı (ID: {req_id})")

    start_t = time.time()
    while True:
        time.sleep(3)
        elapsed = time.time() - start_t
        check_res = requests.get(f"{HORDE_API_URL}/generate/check/{req_id}", headers=headers, timeout=30)
        if check_res.status_code != 200:
            continue

        status_data = check_res.json()
        if status_data.get("done", False):
            break

        if elapsed > 180:
            raise TimeoutError("İşlem zaman aşımına uğradı (180s).")

    # Sonuçları al
    final_res = requests.get(f"{HORDE_API_URL}/generate/status/{req_id}", headers=headers, timeout=30)
    final_data = final_res.json()
    generations = final_data.get("generations", [])

    if not generations:
        raise Exception("Görsel oluşturulamadı.")

    img_info = generations[0]
    img_data_b64 = img_info.get("img")
    used_model = img_info.get("model", "Bilinmiyor")

    if img_data_b64.startswith("http"):
        raw_bytes = requests.get(img_data_b64).content
    else:
        raw_bytes = base64.b64decode(img_data_b64)

    if output_path:
        with open(output_path, "wb") as f:
            f.write(raw_bytes)
        print(f"🎉 Görsel kaydedildi: {output_path} ({len(raw_bytes)/1024:.1f} KB)")

    return {
        "status": "success",
        "model": used_model,
        "elapsed_seconds": round(time.time() - start_t, 1),
        "image_path": output_path,
        "base64_preview": img_data_b64[:100] + "..."
    }

def start_server(port=5000):
    """
    Yerel Flask API Sunucusunu Başlatır
    """
    try:
        from flask import Flask, request, jsonify, send_file
    except ImportError:
        print("Flask gerekli: pip install flask")
        return

    app = Flask(__name__)

    @app.route("/api/anime/generate", methods=["POST"])
    def api_generate():
        data = request.get_json() or {}
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "prompt parametresi zorunludur"}), 400

        width = data.get("width", 1024)
        height = data.get("height", 576)
        models = data.get("models", ["Animagine XL", "AMPonyXL", "Anything v5", "CyberRealistic Pony"])
        output_file = "temp_generated.png"

        try:
            res = generate_anime_image(
                prompt=prompt,
                models=models,
                width=width,
                height=height,
                output_path=output_file
            )
            return send_file(output_file, mimetype="image/png")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "Stable Horde Anime Generator API"})

    print(f"🚀 Anime API Sunucusu çalışıyor: http://localhost:{port}")
    print("   Endpoint: POST http://localhost:5000/api/anime/generate")
    print('   Body: {"prompt": "1girl, cyberpunk anime, neon highlights...", "width": 1024, "height": 576}')
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        start_server()
    else:
        PROMPT_EXAMPLE = '''masterpiece, best quality, ultra-detailed, 16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic, 1girl, confident anime rogue, spiky neon-lime hair highlights, piercing amber eyes, low-profile cyber visor pushed up, open dark charcoal techwear parka, bold "KEKE" graphic print on inner lining, tactical belts, fingerless gloves, low combat-ready stance, crackling green plasma blade held reverse-grip, sharp slash trails of light, pitch-black background, sharp diagonal hazard cuts, grunge spray-paint splatters, floating digital embers, geometric grid lines receding into darkness, crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality'''
        generate_anime_image(
            prompt=PROMPT_EXAMPLE,
            width=1024,
            height=576,
            output_path="horde_anime_result.png"
        )
