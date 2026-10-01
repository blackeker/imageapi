"""
Pollinations.ai - Ücretsiz AI Image Generation API
====================================================
Perchance'a en iyi alternatif! Tamamen ücretsiz, resmi API.
API key gerektirmez, rate limit çok cömerttir.

Perchance'ın kendisi de bazen Pollinations'ı arka planda kullanır.

Kurulum: pip install requests Pillow
"""

import requests
from pathlib import Path
from urllib.parse import quote


def generate_image(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    seed: int = -1,
    model: str = "flux",
    output_path: str = "pollinations_output.png",
    enhance: bool = True,
) -> str:
    """
    Pollinations.ai API ile görsel üretir. Tamamen ücretsiz!

    Args:
        prompt: Görsel açıklaması
        width: Genişlik (px)
        height: Yükseklik (px)
        seed: Rastgele seed (-1 = rastgele)
        model: Model adı ('flux', 'turbo', vb.)
        output_path: Çıktı dosya yolu
        enhance: Prompt'u otomatik iyileştir

    Returns:
        Kaydedilen dosyanın yolu
    """
    encoded_prompt = quote(prompt)

    # Pollinations.ai URL-based API
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    params = {
        "width": width,
        "height": height,
        "model": model,
        "enhance": str(enhance).lower(),
        "nologo": "true",
    }
    if seed >= 0:
        params["seed"] = seed

    print(f"🎨 Görsel üretiliyor: '{prompt}'")
    print(f"   Model: {model} | Boyut: {width}x{height}")

    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"✅ Görsel kaydedildi: {output_path}")
    return output_path


def generate_batch(
    prompts: list[str],
    output_dir: str = "outputs",
    width: int = 1024,
    height: int = 1024,
    model: str = "flux",
) -> list[str]:
    """
    Birden fazla prompt için toplu görsel üretir.

    Args:
        prompts: Prompt listesi
        output_dir: Çıktı dizini
        width: Genişlik
        height: Yükseklik
        model: Kullanılacak model

    Returns:
        Kaydedilen dosya yolları
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    saved_files = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[{i}/{len(prompts)}] Üretiliyor: '{prompt}'")
        try:
            file_path = str(output_path / f"image_{i:03d}.png")
            generate_image(
                prompt=prompt,
                width=width,
                height=height,
                model=model,
                output_path=file_path,
            )
            saved_files.append(file_path)
        except Exception as e:
            print(f"  ❌ Hata: {e}")

    return saved_files


# ── Flask API Server (İsteğe Bağlı) ─────────────────────────────
def create_api_server():
    """
    Kendi API sunucunuzu oluşturur.
    Çalıştırmak için: pip install flask
    """
    try:
        from flask import Flask, request, send_file, jsonify
    except ImportError:
        print("Flask gerekli: pip install flask")
        return None

    app = Flask(__name__)

    @app.route("/api/generate", methods=["POST"])
    def api_generate():
        data = request.get_json()
        if not data or "prompt" not in data:
            return jsonify({"error": "prompt gerekli"}), 400

        prompt = data["prompt"]
        width = data.get("width", 1024)
        height = data.get("height", 1024)
        model = data.get("model", "flux")

        output_path = f"temp_output.png"
        try:
            generate_image(
                prompt=prompt,
                width=width,
                height=height,
                model=model,
                output_path=output_path,
            )
            return send_file(output_path, mimetype="image/png")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "AI Image Generator API"})

    return app


# ── Kullanım Örneği ──────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # API sunucusu modunda çalıştır
        print("🚀 API Sunucusu başlatılıyor...")
        print("   POST http://localhost:5000/api/generate")
        print('   Body: {"prompt": "your prompt", "width": 1024, "height": 1024}')
        app = create_api_server()
        if app:
            app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        # Tek görsel üretim
        generate_image(
            prompt="A beautiful sunset over a cyberpunk city, detailed, 4k",
            width=1024,
            height=768,
            model="flux",
            output_path="pollinations_output.png",
        )

        # Toplu üretim örneği (yorum kaldırarak kullanın)
        # prompts = [
        #     "A magical forest with glowing mushrooms",
        #     "A robot playing guitar in space",
        #     "An underwater castle with mermaids",
        # ]
        # generate_batch(prompts, output_dir="batch_outputs")
