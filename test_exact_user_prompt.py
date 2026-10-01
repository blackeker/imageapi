"""
Kullanıcının Birebir Gönderdiği Prompt ile Görsel Üretimi (Bütçe Uyumlu)
========================================================================
"""

import sys
import io
import time
import requests
import json
import base64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

EXACT_PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

NEGATIVE_PROMPT = '''lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, blurry, deformed, disfigured, mecha armor, robot face'''

def main():
    print("=" * 60)
    print("🎨 KULLANICININ BİREBİR PROMPT'U İLE ÜRETİM")
    print("=" * 60)

    headers = {
        "apikey": "0000000000",
        "Content-Type": "application/json",
        "Client-Agent": "DirectUserPromptTest:1.0.0"
    }

    # Popüler ve hızlı çalışan anime modelleri
    models = ["Animagine XL", "AMPonyXL", "Anything v5", "CyberRealistic Pony", "AAM XL", "AlbedoBase XL 3.1"]

    payload = {
        "prompt": f"{EXACT_PROMPT} ### {NEGATIVE_PROMPT}",
        "params": {
            "sampler_name": "k_euler_a",
            "cfg_scale": 7.0,
            "width": 896,
            "height": 512, # 16:9 Widescreen
            "steps": 20,
            "n": 1
        },
        "models": models,
        "nsfw": True,
        "censor_nsfw": False,
        "shared": True
    }

    print(">> İstek gönderiliyor...")
    res = requests.post("https://aihorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=30)
    if res.status_code != 202:
        print(f"Hata: {res.status_code} - {res.text}")
        return

    req_id = res.json()["id"]
    print(f"✅ Kuyruğa alındı (ID: {req_id})")

    start_t = time.time()
    while True:
        time.sleep(3)
        elapsed = time.time() - start_t
        check = requests.get(f"https://aihorde.net/api/v2/generate/check/{req_id}", headers=headers, timeout=30)
        if check.status_code == 200:
            data = check.json()
            if data.get("done", False):
                break
            print(f"  [{elapsed:.0f}s] Sıra: {data.get('queue_position', 0)} | Kalan: {data.get('wait_time', 0)}s")
        if elapsed > 180:
            print("Zaman aşımı!")
            return

    # İndir
    status = requests.get(f"https://aihorde.net/api/v2/generate/status/{req_id}", headers=headers, timeout=30).json()
    gens = status.get("generations", [])
    if gens:
        img_info = gens[0]
        used_model = img_info.get("model", "Bilinmiyor")
        img_b64 = img_info.get("img")
        
        output_file = "user_exact_prompt_result.png"
        raw_bytes = base64.b64decode(img_b64)
        with open(output_file, "wb") as f:
            f.write(raw_bytes)
            
        print(f"\n🎉 BAŞARILI! Kullanılan Model: {used_model}")
        print(f"📁 Dosya: {output_file} ({len(raw_bytes)/1024:.1f} KB)")

if __name__ == "__main__":
    main()
