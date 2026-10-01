import requests
from urllib.parse import quote
import time

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

models = ["flux-anime", "any-dark", "flux"]

for m in models:
    url = f"https://image.pollinations.ai/prompt/{quote(PROMPT)}"
    params = {
        "width": 1920,
        "height": 1080,
        "model": m,
        "enhance": "true",
        "nologo": "true",
        "seed": 42
    }
    print(f"Model deneniyor: {m}...")
    try:
        r = requests.get(url, params=params, timeout=120)
        if r.status_code == 200:
            fn = f"pollinations_{m.replace('-', '_')}.png"
            with open(fn, "wb") as f:
                f.write(r.content)
            print(f"  Kaydedildi: {fn} ({len(r.content)/1024:.1f} KB)")
    except Exception as e:
        print(f"  Hata: {e}")
