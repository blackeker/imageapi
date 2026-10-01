"""
Perchance Professional - Turnstile Bypass + Preference + Generator
==================================================================
"""

import asyncio
import io
import sys
import time
import re
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET_URL = "https://perchance.org/image-generator-professional"
PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => false });")

        downloaded_images = []
        async def on_response(response):
            url = response.url
            if ("downloadTemporary" in url or "image" in response.headers.get("content-type", "")) and response.status == 200:
                if "perchance.org" in url:
                    body = await response.body()
                    if len(body) > 10000:
                        downloaded_images.append(body)
                        print(f"\n>> GÖRSEL YAKALANDI: {len(body)/1024:.1f} KB")

        page.on("response", on_response)

        print("1. Sayfa açılıyor...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

        # Cloudflare Turnstile varsa tıkla
        print("2. Cloudflare Turnstile kontrolü...")
        for frame in page.frames:
            if "challenges.cloudflare.com" in frame.url:
                print("   Turnstile frame bulundu, tıklanıyor...")
                try:
                    await frame.click('input[type="checkbox"], .ctp-checkbox-label, body')
                    print("   Turnstile tıklandı!")
                    await page.wait_for_timeout(5000)
                except Exception as e:
                    print("   Turnstile tıklama hatası:", e)

        # Tercihleri ayarla
        print("3. Tercihler ayarlanıyor (warn + 18+ onay + save)...")
        await page.evaluate("""() => {
            if (typeof showPreferences === 'function') showPreferences();
            const s = document.getElementById('sensitiveContentVisibilityEl');
            if (s) { s.value = 'warn'; s.dispatchEvent(new Event('change', {bubbles: true})); }
            const c = document.getElementById('ageVerificationCheckboxEl');
            if (c) { c.checked = true; c.dispatchEvent(new Event('change', {bubbles: true})); }
            const saveBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').toLowerCase().includes('save'));
            if (saveBtns[0]) saveBtns[0].click();
        }""")
        await page.wait_for_timeout(2000)

        # Show Content tıkla
        print("4. Show Content tıklanıyor...")
        await page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const b = btns.find(btn => (btn.innerText || '').includes('Show Content') || (btn.innerText || '').includes('18'));
            if (b) b.click();
        }""")
        await page.wait_for_timeout(5000)

        # Tekrar Turnstile çıktıysa tıkla
        for frame in page.frames:
            if "challenges.cloudflare.com" in frame.url:
                print("   Yeniden Turnstile frame bulundu, tıklanıyor...")
                try:
                    await frame.click('input[type="checkbox"], .ctp-checkbox-label, body')
                    await page.wait_for_timeout(5000)
                except:
                    pass

        await page.screenshot(path="prof_status.png")
        print("5. Durum ekran görüntüsü: prof_status.png")

        # Generator frame'ini bul
        print("6. Generator frame taranıyor...")
        target_frame = None
        for frame in page.frames:
            tas = await frame.query_selector_all("textarea")
            if len(tas) > 0:
                target_frame = frame
                break

        if not target_frame:
            target_frame = page.main_frame

        # Prompt yaz
        print("7. Prompt yazılıyor...")
        await target_frame.evaluate("""(p) => {
            const tas = Array.from(document.querySelectorAll('textarea'));
            if (tas.length > 0) {
                const ta = tas.length > 1 ? tas[1] : tas[0];
                ta.value = p;
                ta.dispatchEvent(new Event('input', {bubbles: true}));
                ta.dispatchEvent(new Event('change', {bubbles: true}));
            }
        }""", PROMPT)

        # Generate tıkla
        print("8. Generate tıklanıyor...")
        await target_frame.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button, input[type="button"]'));
            const gen = btns.find(b => (b.innerText || b.value || b.id || '').toLowerCase().includes('generate'));
            if (gen) gen.click();
        }""")

        # Bekle
        print("9. Görsel üretimi bekleniyor (maks 90s)...")
        for _ in range(18):
            await page.wait_for_timeout(5000)
            if downloaded_images:
                break

        await page.screenshot(path="prof_result_final.png")
        print("10. Sonuç ekran görüntüsü: prof_result_final.png")

        if downloaded_images:
            with open("perchance_professional_result.png", "wb") as f:
                f.write(downloaded_images[-1])
            print(f"✅ GÖRSEL BAŞARIYLA KAYDEDİLDİ: perchance_professional_result.png ({len(downloaded_images[-1])/1024:.1f} KB)")
        else:
            print("Görsel yakalanamadı.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
