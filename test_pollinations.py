"""
Pollinations.ai Test - Ayni prompt ile gorsel uretimi
"""

import requests
from urllib.parse import quote
import time
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''


def main():
    print("=" * 60)
    print("[POLLINATIONS.AI TEST]")
    print("=" * 60)
    print(f"Prompt: {PROMPT[:80]}...")
    print()

    encoded_prompt = quote(PROMPT)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    params = {
        "width": 1920,
        "height": 1080,
        "model": "flux",
        "enhance": "false",
        "nologo": "true",
    }

    print(">> Gorsel uretiliyor (30-90 saniye surebilir)...")
    start = time.time()

    try:
        response = requests.get(url, params=params, timeout=180)
        response.raise_for_status()
        elapsed = time.time() - start

        output_path = "pollinations_result.png"
        with open(output_path, "wb") as f:
            f.write(response.content)

        file_size = len(response.content) / 1024
        print(f"[OK] BASARILI!")
        print(f"   Sure: {elapsed:.1f} saniye")
        print(f"   Boyut: {file_size:.1f} KB")
        print(f"   Dosya: {output_path}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")

    except requests.exceptions.Timeout:
        print("[HATA] Istek zaman asimina ugradi (180s)")
    except requests.exceptions.RequestException as e:
        print(f"[HATA] {e}")

    print()


if __name__ == "__main__":
    main()
