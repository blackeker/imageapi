"""
Perchance Test - Ayni prompt ile gorsel uretimi (Resmi Olmayan)
"""

import asyncio
import time
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''


async def main():
    print("=" * 60)
    print("[PERCHANCE TEST] (Resmi Olmayan API)")
    print("=" * 60)
    print(f"Prompt: {PROMPT[:80]}...")
    print()

    try:
        from perchance import ImageGenerator
        from PIL import Image
    except ImportError as e:
        print(f"[HATA] Import hatasi: {e}")
        print("   pip install perchance Pillow")
        return

    print(">> Gorsel uretiliyor...")
    start = time.time()

    try:
        async with ImageGenerator() as gen:
            result = await gen.image(
                prompt=PROMPT,
                negative_prompt="blurry, low quality, watermark, text",
                shape="landscape",
            )
            binary = await result.download()
            elapsed = time.time() - start

            image = Image.open(binary)
            output_path = "perchance_result.png"
            image.save(output_path)

            print(f"[OK] BASARILI!")
            print(f"   Sure: {elapsed:.1f} saniye")
            print(f"   Cozunurluk: {image.size[0]}x{image.size[1]}")
            print(f"   Dosya: {output_path}")

    except Exception as e:
        elapsed = time.time() - start
        print(f"[HATA] ({elapsed:.1f}s): {e}")
        print(f"   Tip: {type(e).__name__}")
        import traceback
        traceback.print_exc()

    print()


if __name__ == "__main__":
    asyncio.run(main())
