"""
Perchance Professional Generator - Tam Otomasyon ve Görsel Üretimi
==================================================================
1. Tercihleri ayarla: 'warn' + 18+ onay + save
2. "✅ I am over 18 - Show Content" butonuna tıkla
3. Generator arayüzüne girip prompt'u doldur
4. Generate butonuna tıkla
5. Üretilen görseli indir ve kaydet
"""

import asyncio
import io
import sys
import time
import base64
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET_URL = "https://perchance.org/image-generator-professional"
PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

async def main():
    print("=" * 60)
    print("PERCHANCE PROFESSIONAL GENERATOR OTOMASYONU")
    print("=" * 60)

    downloaded_images = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )

        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        # Network dinleyicisi
        async def on_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            status = response.status
            if ("downloadTemporary" in url or "image" in ct) and status == 200:
                if "perchance.org" in url or "image-generation" in url:
                    try:
                        body = await response.body()
                        if len(body) > 10000:
                            downloaded_images.append(body)
                            print(f"\n>> [GÖRSEL YAKALANDI]: {len(body)/1024:.1f} KB - {url[:70]}")
                    except:
                        pass

        page.on("response", on_response)

        print("[1] Sayfa yükleniyor...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

        # 1. Tercihleri ayarla
        print("[2] Tercihler ayarlanıyor (change preferences -> warn -> over 18 -> save)...")
        pref_result = await page.evaluate("""() => {
            try {
                if (typeof showPreferences === 'function') {
                    showPreferences();
                } else {
                    const link = document.getElementById('changePreferencesLinkEl');
                    if (link) link.click();
                }

                const selectEl = document.getElementById('sensitiveContentVisibilityEl');
                if (selectEl) {
                    selectEl.value = 'warn';
                    selectEl.dispatchEvent(new Event('change', {bubbles: true}));
                }

                const ageCheckbox = document.getElementById('ageVerificationCheckboxEl');
                if (ageCheckbox) {
                    ageCheckbox.checked = true;
                    ageCheckbox.dispatchEvent(new Event('change', {bubbles: true}));
                }

                const saveBtns = Array.from(document.querySelectorAll('button, input[type="button"], a')).filter(el => {
                    const t = (el.innerText || el.value || '').toLowerCase();
                    return t.includes('save') || t.includes('close') || t.includes('done') || t.includes('confirm');
                });
                if (saveBtns.length > 0) {
                    saveBtns[0].click();
                }

                return { success: true };
            } catch(e) {
                return { success: false, error: e.toString() };
            }
        }""")
        print("    Tercihler ayarlandı:", pref_result)
        await page.wait_for_timeout(3000)

        # 2. "✅ I am over 18 - Show Content" butonuna tıkla
        print("[3] '✅ I am over 18 - Show Content' butonuna tıklanıyor...")
        show_btn_clicked = await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, a, input[type="button"]'));
            const btn = btns.find(b => {
                const t = (b.innerText || b.value || '').toLowerCase();
                return t.includes('show content') || t.includes('18') || t.includes('continue');
            });
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        }""")
        print(f"    Show Content tıklandı: {show_btn_clicked}")

        # Generator arayüzünün gelmesini bekle
        print("[4] Generator arayüzünün yüklenmesi bekleniyor (15s)...")
        await page.wait_for_timeout(15000)

        await page.screenshot(path="prof_generator_unlocked.png")
        print("    Screenshot: prof_generator_unlocked.png")

        # 3. Tüm frame'leri tara ve aktif generator frame'ini bul
        print("\n[5] Generator Frame'i taranıyor...")
        target_frame = None
        for i, frame in enumerate(page.frames):
            try:
                tas = await frame.query_selector_all("textarea")
                btns = await frame.query_selector_all("button")
                print(f"    Frame {i} ({frame.url[:60]}): {len(tas)} textarea, {len(btns)} buton")
                if len(tas) > 0 and len(btns) > 0:
                    target_frame = frame
                    print(f"    -> HEDEF GENERATOR FRAME: Frame {i}")
                    break
            except:
                pass

        if not target_frame:
            target_frame = page.main_frame
            print("    -> Ana sayfa frame'i kullanılıyor.")

        # 4. Prompt'u yaz
        print("\n[6] Prompt dolduruluyor...")
        prompt_filled = await target_frame.evaluate("""(promptText) => {
            const tas = Array.from(document.querySelectorAll('textarea'));
            if (tas.length === 0) return false;

            let targetTa = tas.find(ta => {
                const ph = (ta.placeholder || '').toLowerCase();
                return ph.includes('girl') || ph.includes('describe') || ph.includes('prompt') || ph.includes('picnic');
            });
            if (!targetTa && tas.length > 1) targetTa = tas[1];
            if (!targetTa) targetTa = tas[0];

            targetTa.value = promptText;
            targetTa.dispatchEvent(new Event('input', {bubbles: true}));
            targetTa.dispatchEvent(new Event('change', {bubbles: true}));
            return true;
        }""", PROMPT)

        print(f"    Prompt dolduruldu: {prompt_filled}")
        await page.wait_for_timeout(1000)

        # 5. Generate butonuna tıkla
        print("\n[7] Generate butonuna tıklanıyor...")
        btn_clicked = await target_frame.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, input[type="button"], a.button'));
            const genBtn = btns.find(b => {
                const t = (b.innerText || b.value || '').toLowerCase();
                const id = (b.id || '').toLowerCase();
                return id.includes('generate') || t.includes('generate') || t.includes('✨') || t.includes('create');
            });
            if (genBtn) {
                genBtn.click();
                return (genBtn.innerText || genBtn.id || 'clicked');
            }
            return null;
        }""")
        print(f"    Generate butonu tetiklendi: {btn_clicked}")

        # 6. Görsel üretimini bekle
        print("\n[8] Görsel üretimi bekleniyor (maks 120s)...")
        start_t = time.time()
        for s in range(1, 25):
            await page.wait_for_timeout(5000)
            elapsed = time.time() - start_t
            print(f"    [{elapsed:.0f}s] Bekleniyor... (Yakalanan görsel: {len(downloaded_images)})")
            if downloaded_images:
                print(f"    >> GÖRSEL BAŞARIYLA ÜRETİLDİ! ({elapsed:.0f} saniye)")
                break

        # Son ekran görüntüsü
        await page.screenshot(path="prof_final_result.png")
        print("\n[9] Son ekran görüntüsü kaydedildi: prof_final_result.png")

        # Dosyayı kaydet
        output_file = "perchance_professional_result.png"
        if downloaded_images:
            with open(output_file, "wb") as f:
                f.write(downloaded_images[-1])
            print(f"\n🎉 TEBRİKLER! Görsel başarıyla kaydedildi: {output_file} ({len(downloaded_images[-1])/1024:.1f} KB)")
        else:
            try:
                img_data = await target_frame.evaluate("""() => {
                    const imgs = document.querySelectorAll('img');
                    for (const img of imgs) {
                        if (img.naturalWidth > 200 && img.naturalHeight > 200) {
                            const c = document.createElement('canvas');
                            c.width = img.naturalWidth;
                            c.height = img.naturalHeight;
                            const ctx = c.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            return c.toDataURL('image/png').split(',')[1];
                        }
                    }
                    return null;
                }""")
                if img_data:
                    raw = base64.b64decode(img_data)
                    with open(output_file, "wb") as f:
                        f.write(raw)
                    print(f"\n🎉 TEBRİKLER! Görsel DOM Canvas'tan kaydedildi: {output_file} ({len(raw)/1024:.1f} KB)")
                else:
                    print("\n❌ Görsel bekleniyor / oluşmadı.")
            except Exception as e:
                print(f"DOM görsel çıkarma hatası: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
