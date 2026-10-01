"""
DrissionPage ile Perchance Professional Görsel Üretimi
======================================================
DrissionPage (CDP tabanlı, webdriver kullanmaz) ile:
1. https://perchance.org/image-generator-professional aç
2. showPreferences() -> warn -> 18+ -> save
3. 'Show Content' tıkla
4. Generator iframe'inde prompt yaz ve generate et!
"""

import sys
import io
import time
import base64
from DrissionPage import ChromiumPage, ChromiumOptions

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''
TARGET_URL = "https://perchance.org/image-generator-professional"

def main():
    print("=" * 60)
    print("DRISSIONPAGE PERCHANCE PROFESSIONAL TESTİ")
    print("=" * 60)

    options = ChromiumOptions()
    options.headless(True)
    options.set_argument("--no-sandbox")
    options.set_argument("--disable-dev-shm-usage")
    options.set_argument("--window-size=1920,1080")

    page = ChromiumPage(options)

    try:
        print("[1] Sayfa açılıyor...")
        page.get(TARGET_URL)
        time.sleep(3)

        # 1. Tercihleri ayarla
        print("[2] Tercihler ayarlanıyor (warn + 18+ onay + save)...")
        page.run_js("""
            if (typeof showPreferences === 'function') showPreferences();
            const s = document.getElementById('sensitiveContentVisibilityEl');
            if (s) { s.value = 'warn'; s.dispatchEvent(new Event('change', {bubbles: true})); }
            const c = document.getElementById('ageVerificationCheckboxEl');
            if (c) { c.checked = true; c.dispatchEvent(new Event('change', {bubbles: true})); }
            const saveBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').toLowerCase().includes('save'));
            if (saveBtns[0]) saveBtns[0].click();
        """)
        time.sleep(2)

        # 2. Show Content tıkla
        print("[3] 'Show Content' tıklanıyor...")
        page.run_js("""
            const btns = Array.from(document.querySelectorAll('button, a, input[type="button"]'));
            const b = btns.find(btn => (btn.innerText || '').includes('Show Content') || (btn.innerText || '').includes('18'));
            if (b) b.click();
        """)
        time.sleep(10)

        # Screenshot al
        page.get_screenshot(path="dp_loaded.png")
        print("    Screenshot kaydedildi: dp_loaded.png")

        # 3. Tüm frame'leri listele ve generator iframe'ini bul
        print("\n[4] Generator frame'i aranıyor...")
        target_frame = None
        for i, f in enumerate(page.get_frames()):
            print(f"    Frame {i}: {f.url[:80]}")
            has_input = f.run_js("return document.querySelectorAll('textarea').length > 0;")
            if has_input:
                target_frame = f
                print(f"    -> Hedef generator frame: Frame {i}")
                break

        if not target_frame:
            target_frame = page
            print("    -> Ana sayfa frame'i kullanılıyor.")

        # 4. Prompt'u yaz
        print("\n[5] Prompt yazılıyor...")
        typed = target_frame.run_js(f"""
            const tas = Array.from(document.querySelectorAll('textarea'));
            if (tas.length > 0) {{
                const target = tas.length > 1 ? tas[1] : tas[0];
                target.value = {repr(PROMPT)};
                target.dispatchEvent(new Event('input', {{bubbles: true}}));
                target.dispatchEvent(new Event('change', {{bubbles: true}}));
                return true;
            }}
            return false;
        """)
        print(f"    Prompt yazıldı: {typed}")
        time.sleep(1)

        # 5. Generate butonuna tıkla
        print("\n[6] Generate butonuna tıklanıyor...")
        clicked = target_frame.run_js("""
            const btns = Array.from(document.querySelectorAll('button, input[type="button"], a.button'));
            const genBtn = btns.find(b => {
                const t = (b.innerText || b.value || b.id || '').toLowerCase();
                return t.includes('generate') || t.includes('✨') || t.includes('create');
            });
            if (genBtn) {
                genBtn.click();
                return genBtn.innerText || 'clicked';
            }
            return null;
        """)
        print(f"    Generate butonu: {clicked}")

        # 6. Görsel üretimini bekle
        print("\n[7] Görsel üretimi bekleniyor (maks 120s)...")
        output_file = "perchance_drission_result.png"
        saved = False

        start_t = time.time()
        for s in range(1, 25):
            time.sleep(5)
            elapsed = time.time() - start_t
            
            # Sayfadaki büyük görsel veya canvas kontrolü
            img_b64 = target_frame.run_js("""
                const imgs = document.querySelectorAll('img');
                for (const img of imgs) {
                    if (img.naturalWidth > 200 && img.naturalHeight > 200) {
                        try {
                            const c = document.createElement('canvas');
                            c.width = img.naturalWidth;
                            c.height = img.naturalHeight;
                            const ctx = c.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            return c.toDataURL('image/png').split(',')[1];
                        } catch(e) {}
                    }
                }
                const canvases = document.querySelectorAll('canvas');
                for (const c of canvases) {
                    if (c.width > 200 && c.height > 200) {
                        try { return c.toDataURL('image/png').split(',')[1]; } catch(e) {}
                    }
                }
                return null;
            """)

            print(f"    [{elapsed:.0f}s] Kontrol ediliyor... (Görsel var mı: {bool(img_b64)})")

            if img_b64:
                raw = base64.b64decode(img_b64)
                with open(output_file, "wb") as f:
                    f.write(raw)
                print(f"\n🎉 BAŞARILI! Görsel DrissionPage ile başarıyla üretildi: {output_file} ({len(raw)/1024:.1f} KB)")
                saved = True
                break

        page.get_screenshot(path="dp_final_result.png")
        print("\n[8] Son ekran görüntüsü: dp_final_result.png")

        if not saved:
            print("\n❌ Görsel henüz sayfaya yansımadı.")

    finally:
        page.quit()

if __name__ == "__main__":
    main()
