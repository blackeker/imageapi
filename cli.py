"""
Multi-Category AI Image Studio - CLI Aracı
==========================================
"""

import sys
import argparse
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from core_engine import generate, OUTPUT_DIR
from categories import CATEGORIES

def main():
    parser = argparse.ArgumentParser(description="Multi-Category AI Image Studio CLI")
    parser.add_argument("--prompt", "-p", type=str, help="Görsel açıklaması")
    parser.add_argument("--category", "-c", type=str, default="anime", choices=list(CATEGORIES.keys()), help="Kategori")
    parser.add_argument("--style", type=str, default=None, help="Alt stil (örn: studio_portrait, ghibli, dark_fantasy)")
    parser.add_argument("--provider", "-m", type=str, default="auto", choices=["auto", "perchance", "horde", "pollinations"], help="AI Motoru")
    parser.add_argument("--shape", "-s", type=str, default="768x512", choices=["768x512", "512x512", "512x768", "landscape", "square", "portrait"], help="Format / Oran")
    parser.add_argument("--output", "-o", type=str, default=None, help="Çıktı dosya adı")
    parser.add_argument("--categories", action="store_true", help="Tüm kategorileri ve stilleri listele")
    parser.add_argument("--gallery", "-g", action="store_true", help="Galerideki görselleri listele")

    args = parser.parse_args()

    if args.categories:
        print("\n" + "=" * 60)
        print("DESTEKLENEN KATEGORİLER VE STİLLER")
        print("=" * 60)
        for cat_id, cat_info in CATEGORIES.items():
            print(f"\n[{cat_id.upper()}] - {cat_info['name']} {cat_info.get('icon', '')}")
            st_keys = list(cat_info['styles'].keys())
            print(f"   Stiller:  {', '.join(st_keys)}")
        return

    if args.gallery:
        files = list(OUTPUT_DIR.glob("*.png"))
        print(f"\nGaleride {len(files)} adet görsel bulundu:")
        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:15]:
            print(f"  - {f.name} ({f.stat().st_size/1024:.1f} KB)")
        return

    if not args.prompt:
        parser.print_help()
        return

    print("=" * 60)
    print(f"GÖRSEL ÜRETİMİ [{args.category.upper()}]")
    print("=" * 60)
    print(f"Prompt:   {args.prompt[:80]}...")
    print(f"Kategori: {args.category}")
    print(f"Stil:     {args.style or 'Varsayılan'}")
    print(f"Format:   {args.shape}")

    try:
        res = generate(
            prompt=args.prompt,
            category=args.category,
            style=args.style,
            provider=args.provider,
            shape=args.shape,
            output_filename=args.output
        )
        print("\nÜRETİM BAŞARILI!")
        print(f"Dosya:    {res['filepath']} ({res['size_kb']} KB)")
        print(f"Motor:    {res['provider'].upper()} {res.get('model', '')}")
        print(f"Süre:     {res['elapsed_seconds']} saniye")
    except Exception as e:
        print(f"\nHata oluştu: {e}")

if __name__ == "__main__":
    main()
