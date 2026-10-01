"""
Top-Tier SDXL Anime Modelleri ile Yüksek Kaliteli Üretim
========================================================
Eski SD1.5 modelleri (Anything v5 vb.) devre dışı bırakıldı.
Yalnızca yeni nesil SDXL / Animagine XL / Pony modelleri kullanılıyor.
"""

import sys
import io
import time
import requests
import json
import base64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''masterpiece, best quality, (absurdres:1.2), cinematic anime wallpaper, 1girl, confident rogue, spiky neon-lime hair highlights, detailed amber eyes, cyber visor, open dark charcoal techwear parka, (bold "KEKE" print on inner lining:1.1), tactical gear, fingerless gloves, combat stance, glowing green energy plasma dagger, dynamic green light slash trails, pitch black background, diagonal hazard cuts, grunge splatters, floating digital embers, geometric grid lines, volumetric lighting, ray tracing, sharp focus, 8k wallpaper'''

NEGATIVE = '''(worst quality:1.4), (low quality:1.4), (normal quality:1.2), flat colors, 3d render, cartoon, deformed, bad anatomy, bad hands, extra limbs, extra blades, multiple swords, missing fingers, blurry, watermark, text, signature, lowres, ugly'''

MODELS_TO_TRY = [
    ("Animagine XL", "anime_animagine_xl.png"),
    ("CyberRealistic Pony", "anime_cyber_pony.png"),
    ("AlbedoBase XL 3.1", "anime_albedobase_xl.png")
]

def generate_with_specific_model(model_name: str, output_file: str):
    headers = {
        "apikey": "0000000000",
        "Content-Type": "application/json",
        "Client-Agent": "TopTierAnimeTest:1.0.0"
    }

    payload = {
        "prompt": f"{PROMPT} ### {NEGATIVE}",
        "params": {
            "sampler_name": "k_dpmpp_2m",
            "cfg_scale": 7.0,
            "width": 896,
            "height": 512, # 16:9
            "steps": 25,
            "n": 1
        },
        "models": [model_name],
        "nsfw": True,
        "censor_nsfw": False,
        "shared": True
    }

    print(f"\n>> Model başlatılıyor: {model_name}...")
    res = requests.post("https://aihorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=30)
    if res.status_code != 202:
        print(f"   İstek reddedildi: {res.status_code} - {res.text}")
        return False

    req_id = res.json()["id"]
    print(f"   Kuyruk ID: {req_id}")

    start_t = time.time()
    while True:
        time.sleep(3)
        elapsed = time.time() - start_t
        check = requests.get(f"https://aihorde.net/api/v2/generate/check/{req_id}", headers=headers, timeout=30)
        if check.status_code == 200:
            data = check.json()
            if data.get("done", False):
                break
            print(f"   [{elapsed:.0f}s] Sıra: {data.get('queue_position', 0)} | Kalan: {data.get('wait_time', 0)}s")
        if elapsed > 120:
            print("   Zaman aşımı.")
            return False

    status = requests.get(f"https://aihorde.net/api/v2/generate/status/{req_id}", headers=headers, timeout=30).json()
    gens = status.get("generations", [])
    if gens:
        img_b64 = gens[0].get("img")
        if img_b64.startswith("http"):
            raw = requests.get(img_b64).content
        else:
            raw = base64.b64decode(img_b64)
        with open(output_file, "wb") as f:
            f.write(raw)
        print(f"   🎉 {output_file} başarıyla kaydedildi! ({len(raw)/1024:.1f} KB)")
        return True
    return False

if __name__ == "__main__":
    for model, fn in MODELS_TO_TRY:
        try:
            success = generate_with_specific_model(model, fn)
            if success:
                break # En az bir kaliteli SDXL görseli aldığımızda durabiliriz
        except Exception as e:
            print(f"Hata ({model}): {e}")
