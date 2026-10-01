"""
Perchancy ile Perchance Professional Görsel Üretimi (DrissionPage Tabanlı)
==========================================================================
"""

import sys
import io
import time
import json
import base64
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import perchancy

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

def main():
    print("=" * 60)
    print("PERCHANCY - IMAGE GENERATOR PROFESSIONAL (DrissionPage)")
    print("=" * 60)

    client = perchancy.Client(headless=True)

    print(f"\nPrompt: {PROMPT[:80]}...")
    print("Model: image-generator-professional")
    print("Görsel üretimi başlatılıyor...")

    start_t = time.time()
    try:
        response = client.images.generate(
            model="image-generator-professional",
            prompt=PROMPT,
            num_images=1,
            image_format="png",
            time_for_image=120,
            disable_safety_settings=True
        )
        elapsed = time.time() - start_t
        print(f"\nİşlem süresi: {elapsed:.1f} saniye")
        print("Yanıt:", json.dumps(response, indent=2, ensure_ascii=False))

        if response.get("data"):
            for i, item in enumerate(response["data"]):
                url_or_data = item.get("url")
                if url_or_data:
                    output_file = f"perchancy_professional_result.png"
                    if url_or_data.startswith("data:image"):
                        base64_data = url_or_data.split(",")[1]
                        with open(output_file, "wb") as f:
                            f.write(base64.b64decode(base64_data))
                    elif url_or_data.startswith("http"):
                        import requests
                        r = requests.get(url_or_data)
                        with open(output_file, "wb") as f:
                            f.write(r.content)
                    print(f"\n🎉 BAŞARILI! Görsel kaydedildi: {output_file}")
        elif response.get("error"):
            print("\n❌ Hata:", response["error"])

    except Exception as e:
        print("\nİstisna:", e)
    finally:
        try:
            client.close()
        except:
            pass

if __name__ == "__main__":
    main()
