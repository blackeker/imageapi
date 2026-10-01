"""
DrissionPage Turnstile Çözücü + Perchance Professional Otomasyonu
=================================================================
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
    print("DRISSIONPAGE PERCHANCE PROFESSIONAL OTOMASYONU")
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

        # 1. Turnstile kontrolü ve tıklama
        print("[2] Turnstile kontrolü...")
        for frame in page.get_frames():
            if "cloudflare" in frame.url:
                print("    Turnstile frame bulundu, tıklanıyor...")
                try:
                    cb = frame('tag:input@@type=checkbox') or frame('.ctp-checkbox-label')
                    if cb:
                        cb.click()
                        print("    Turnstile checkbox tıklandı!")
                        time.sleep(5)
                except Exception as e:
                    print("    Turnstile frame tıklama hatası:", e)

        # Sayfa üzerinde koordinat tıklaması (Turnstile kutusu)
        try:
            cf_box = page('tag:iframe@@src*=challenges.cloudflare.com')
            if cf_box:
                cf_box.click()
                print("    Turnstile iframe tıklandı!")
                time.sleep(5)
        except:
            pass

        # 2. Tercihleri ayarla
        print("[3] Tercihler ayarlanıyor (warn + 18+ onay + save)...")
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

        # 3. Show Content tıkla
        print("[4] 'Show Content' tıklanıyor...")
        page.run_js("""
            const btns = Array.from(document.querySelectorAll('button, a, input[type="button"]'));
            const b = btns.find(btn => (btn.innerText || '').includes('Show Content') || (btn.innerText || '').includes('18'));
            if (b) b.click();
        """)
        time.sleep(5)

        page.get_screenshot(path="dp_after_show.png")
        print("    Screenshot: dp_after_show.png")

        # 4. Generator frame'ini bul
        print("[5] Generator arayüzü taranıyor...")
        target_frame = None
        for i, f in enumerate(page.get_frames()):
            has_tas = f.run_js("return document.querySelectorAll('textarea').length > 0;")
            if has_tas:
                target_frame = f
                print(f"    -> Hedef generator frame: Frame {i} ({f.url[:60]})")
                break

        if not target_frame:
            target_frame = page

        # 5. Prompt'u yaz
        print("[6] Prompt yazılıyor...")
        target_frame.run_js(f"""
            const tas = Array.from(document.querySelectorAll('textarea'));
            if (tas.length > 0) {{
                const target = tas.length > 1 ? tas[1] : tas[0];
                target.value = {repr(PROMPT)};
                target.dispatchEvent(new Event('input', {{bubbles: true}}));
                target.dispatchEvent(new Event('change', {{bubbles: true}}));
            }}
        """)
        time.sleep(1)

        # 6. Generate butonuna tıkla
        print("[7] Generate butonuna tıklanıyor...")
        target_frame.run_js("""
            const btns = Array.from(document.querySelectorAll('button, input[type="button"], a.button'));
            const genBtn = btns.find(b => {
                const t = (b.innerText || b.value || b.id || '').toLowerCase();
                return t.includes('generate') || t.includes('✨') || t.includes('create');
            });
            if (genBtn) genBtn.click();
        """)

        # 7. Görsel üretimini bekle
        print("[8] Görsel üretimi bekleniyor (maks 120s)...")
        output_file = "perchance_final_result.png"
        saved = False

        for s in range(1, 25):
            time.sleep(5)
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
                return null;
            """)

            print(f"    [{s*5}s] Bekleniyor... Görsel hazır mı: {bool(img_b64)}")
            if img_b64:
                raw = base64.b64decode(img_b64)
                with open(output_file, "wb") as f:
                    f.write(raw)
                print(f"\n🎉 BAŞARILI! Görsel üretildi ve kaydedildi: {output_file} ({len(raw)/1024:.1f} KB)")
                saved = True
                break

        page.get_screenshot(path="dp_status_final.png")
        print("    Son Screenshot: dp_status_final.png")

        if not saved:
            print("\nGörsel üretilemedi veya Turnstile bekleniyor.")

    finally:
        page.quit()

if __name__ == "__main__":
    main()
