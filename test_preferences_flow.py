"""
Perchance Professional - Change Preferences ve İçerik Açma
===========================================================
1. image-generator-professional sayfasını aç
2. "change preferences" butonuna / linkine tıkla
3. Açılan ayarlar modalında mature/sensitive content iznini aç
4. Generator arayüzüne gir, prompt'u yaz ve generate et!
"""

import asyncio
import io
import json
import sys
import time
import base64
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET_URL = "https://perchance.org/image-generator-professional"
PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

async def main():
    print("=" * 60)
    print("PERCHANCE: CHANGE PREFERENCES & IMAGE GENERATION")
    print("=" * 60)

    downloaded_images = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )

        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)

        # Network dinle
        async def on_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            status = response.status
            if ("downloadTemporary" in url or "image" in ct) and status == 200:
                if "perchance.org" in url or "image-generation" in url:
                    try:
                        body = await response.body()
                        if len(body) > 15000:
                            downloaded_images.append(body)
                            print(f"\n>> GORSEL YAKALANDI: {len(body)/1024:.1f} KB - {url[:80]}")
                    except:
                        pass

        page.on("response", on_response)

        print("[1] Sayfa yükleniyor...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

        # 1. "change preferences" linkini / butonunu ara ve tıkla
        print("[2] 'change preferences' aranıyor ve tıklanıyor...")
        try:
            # Hem ana sayfada hem de olası frame'lerde ara
            clicked = False
            for frame in page.frames:
                pref_el = await frame.query_selector('text="change preferences", a:has-text("change preferences"), span:has-text("change preferences"), [class*="pref"], [id*="pref"]')
                if pref_el:
                    print(f"    'change preferences' bulundu! Frame: {frame.url[:50]}")
                    await pref_el.click()
                    clicked = True
                    await page.wait_for_timeout(2000)
                    break
            
            if not clicked:
                # evaluate ile doğrudan JS tıklaması
                print("    Doğrudan JS ile 'change preferences' aranıyor...")
                res = await page.evaluate("""() => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    for (const el of elements) {
                        if (el.innerText && el.innerText.trim().toLowerCase() === 'change preferences') {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                }""")
                print(f"    JS tıklama sonucu: {res}")
                await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"    Tıklama hatası: {e}")

        await page.screenshot(path="step2_preferences_clicked.png")
        print("    Screenshot: step2_preferences_clicked.png")

        # 2. Açılan tercihler ekranında hassas içerik / NSFW / yaş onayını aktif et
        print("[3] Tercihler ayarlanıyor (Mature / NSFW / Show Content)...")
        try:
            # Checkbox'ları veya onay butonlarını işaretle
            await page.evaluate("""() => {
                // Tüm checkbox'ları işaretle veya 'show' / 'allow' içerenleri seç
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(cb => {
                    if (!cb.checked) {
                        cb.checked = true;
                        cb.dispatchEvent(new Event('change', {bubbles: true}));
                    }
                });

                // 'save', 'allow', 'show', 'confirm', 'agree' butonları
                const buttons = document.querySelectorAll('button, input[type="button"], a');
                buttons.forEach(btn => {
                    const txt = (btn.innerText || '').toLowerCase();
                    if (txt.includes('save') || txt.includes('allow') || txt.includes('show content') || txt.includes('i understand') || txt.includes('continue')) {
                        btn.click();
                    }
                });
            }""")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"    Tercih ayarlama hatası: {e}")

        await page.screenshot(path="step3_after_settings.png")
        print("    Screenshot: step3_after_settings.png")

        # 3. Generator iframe ve formunu bul
        print("\n[4] Generator Formu ve Prompt Alanı Aranıyor...")
        target_frame = None
        for frame in page.frames:
            if "image-generator-professional" in frame.url and frame.url != TARGET_URL:
                target_frame = frame
                break
        
        if not target_frame:
            for frame in page.frames:
                ta = await frame.query_selector("textarea")
                if ta:
                    target_frame = frame
                    break

        if not target_frame:
            target_frame = page.main_frame

        print(f"    Kullanılan Frame: {target_frame.url[:70]}")

        # Textarea'ya prompt yaz
        textareas = await target_frame.query_selector_all("textarea")
        print(f"    Bulunan textarea sayısı: {len(textareas)}")
        
        target_ta = None
        if len(textareas) > 1:
            target_ta = textareas[1]
        elif len(textareas) == 1:
            target_ta = textareas[0]

        if target_ta:
            print("    Prompt yazılıyor...")
            await target_ta.click()
            await target_ta.fill("")
            await target_ta.fill(PROMPT)
            await target_ta.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
            await target_ta.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
            print("    Prompt yazıldı!")
        else:
            print("    UYARI: Textarea bulunamadı!")

        # Generate butonuna tıkla
        print("\n[5] Generate butonuna tıklanıyor...")
        gen_btn = await target_frame.query_selector('button:has-text("generate"), button:has-text("Generate"), #generateButtonEl, button:has-text("✨")')
        if gen_btn:
            await gen_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await gen_btn.click()
            print("    Generate tıklandı!")
        else:
            # evaluate ile buton tıklaması
            await target_frame.evaluate("""() => {
                const btns = document.querySelectorAll('button');
                for (const b of btns) {
                    if ((b.innerText || '').toLowerCase().includes('generate')) {
                        b.click();
                        return true;
                    }
                }
                return false;
            }""")
            print("    JS ile generate arandı ve tıklandı.")

        # Bekle
        print("\n[6] Görsel üretimi bekleniyor (maks 90s)...")
        for i in range(1, 19):
            await page.wait_for_timeout(5000)
            print(f"    [{(i*5)}s] Bekleniyor... (İndirilen: {len(downloaded_images)})")
            if downloaded_images:
                break

        await page.screenshot(path="step4_final.png")
        print("    Son Screenshot: step4_final.png")

        if downloaded_images:
            with open("perchance_professional_result.png", "wb") as f:
                f.write(downloaded_images[-1])
            print(f"\n✅ BAŞARILI! Görsel kaydedildi: perchance_professional_result.png ({len(downloaded_images[-1])/1024:.1f} KB)")
        else:
            # Canvas / img kontrolü
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
                    with open("perchance_professional_result.png", "wb") as f:
                        f.write(raw)
                    print(f"\n✅ Sayfadan görsel çıkarıldı: perchance_professional_result.png ({len(raw)/1024:.1f} KB)")
                else:
                    print("\n❌ Görsel henüz sayfaya yüklenmedi.")
            except Exception as e:
                print(f"Görsel alma hatası: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
