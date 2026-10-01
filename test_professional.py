"""
Perchance Professional Generator (image-generator-professional) Otomasyonu
========================================================================
Hedef URL: https://perchance.org/image-generator-professional
"""

import asyncio
import io
import json
import sys
import time
import base64
from pathlib import Path
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET_URL = "https://perchance.org/image-generator-professional"
PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

async def main():
    print("=" * 60)
    print(f"HEDEF: {TARGET_URL}")
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
            timezone_id="Europe/Istanbul"
        )

        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        # Network isteklerini dinle
        async def on_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            status = response.status
            if ("downloadTemporary" in url or "image" in ct) and status == 200:
                if "perchance.org" in url:
                    try:
                        body = await response.body()
                        if len(body) > 10000: # En az 10KB
                            downloaded_images.append(body)
                            print(f"\n[NETWORK] Gorsel yakalandi! Boyut: {len(body)/1024:.1f} KB - URL: {url[:80]}")
                    except Exception as e:
                        pass

        page.on("response", on_response)

        print("[1] Sayfa aciliyor...")
        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
            print("    Sayfa yuklendi.")
        except Exception as e:
            print(f"    Yukleme uyarisi: {e}")

        await page.wait_for_timeout(4000)

        # 18+ butonunu kontrol et
        print("[2] 18+ Onay ekrani kontrol ediliyor...")
        try:
            over18_btn = await page.query_selector('#showContentBtn, button:has-text("18"), button:has-text("Show Content")')
            if over18_btn:
                print("    18+ Butonu bulundu, tiklaniyor...")
                await over18_btn.click()
                await page.wait_for_timeout(3000)
            else:
                print("    18+ Butonu gorunmuyor veya gerek yok.")
        except Exception as e:
            print(f"    18+ buton hatasi: {e}")

        await page.screenshot(path="prof_step1.png")
        print("    Screenshot kaydedildi: prof_step1.png")

        # Frame'leri listele ve generator frame'ini bul
        print("\n[3] Generator Frame'i araniyor...")
        target_frame = None
        for i, frame in enumerate(page.frames):
            print(f"    Frame {i}: {frame.url[:80]}")
            if "image-generator-professional" in frame.url and frame.url != TARGET_URL:
                target_frame = frame
                print(f"    -> Hedef generator frame: Frame {i}")
                break

        if not target_frame:
            # Fallback: icinde textarea veya generate olan herhangi bir iframe
            for i, frame in enumerate(page.frames):
                try:
                    ta = await frame.query_selector("textarea")
                    btn = await frame.query_selector("button")
                    if ta and btn:
                        target_frame = frame
                        print(f"    -> Fallback hedef frame: Frame {i} ({frame.url[:60]})")
                        break
                except:
                    pass

        if not target_frame:
            target_frame = page.main_frame
            print("    -> Ana sayfa frame'i kullaniliyor.")

        # Textarea ve Generate butonunu bul
        print("\n[4] Prompt alani ve Generate butonu ayarlaniyor...")
        textareas = await target_frame.query_selector_all("textarea")
        print(f"    Bulunan textarea sayisi: {len(textareas)}")

        prompt_box = None
        for idx, ta in enumerate(textareas):
            ph = (await ta.get_attribute("placeholder")) or ""
            print(f"    Textarea {idx}: placeholder='{ph[:50]}'")
            # genellikle aciklama / prompt iceren
            if "prompt" in ph.lower() or "girl" in ph.lower() or "describe" in ph.lower() or idx == 1 or len(textareas) == 1:
                prompt_box = ta

        if not prompt_box and textareas:
            prompt_box = textareas[0]

        if prompt_box:
            print("    Prompt textarea secildi. Metin yaziliyor...")
            await prompt_box.click()
            await prompt_box.fill("")
            await prompt_box.fill(PROMPT)
            await prompt_box.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
            await prompt_box.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
            print("    Prompt basariyla dolduruldu.")
        else:
            print("    UYARI: Prompt kutusu bulunamadi!")

        # Generate butonunu bul
        buttons = await target_frame.query_selector_all("button")
        gen_btn = None
        for btn in buttons:
            txt = (await btn.text_content()) or ""
            btn_id = (await btn.get_attribute("id")) or ""
            if "generate" in txt.lower() or "generate" in btn_id.lower() or "✨" in txt:
                gen_btn = btn
                print(f"    Generate butonu bulundu: '{txt.strip()}' (id={btn_id})")
                break

        if gen_btn:
            print("[5] Generate butonuna tiklaniyor...")
            await gen_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            await gen_btn.click()
            print("    Tıklandı! Görsel üretimi bekleniyor...")
        else:
            print("    Generate butonu bulunamadi, sayfadaki butonlar:")
            for btn in buttons[:10]:
                t = (await btn.text_content()) or ""
                print(f"      - '{t.strip()}'")

        # Görsel oluşmasını bekle
        start_t = time.time()
        for s in range(1, 19): # 90 saniye kadar bekle
            await page.wait_for_timeout(5000)
            print(f"    [{(s*5)}s] Bekleniyor... (Yakalanan gorsel: {len(downloaded_images)})")
            if downloaded_images:
                print("    >> Gorsel basariyla yakalandi!")
                break

        # Son screenshot
        await page.screenshot(path="prof_result.png")
        print("\n[6] Son screenshot: prof_result.png")

        # Görselleri kaydet
        if downloaded_images:
            output_file = "perchance_prof_result.png"
            with open(output_file, "wb") as f:
                f.write(downloaded_images[-1])
            print(f"✅ GORSEL KAYDEDILDI: {output_file} ({len(downloaded_images[-1])/1024:.1f} KB)")
        else:
            # Sayfa DOM'undaki resim elementlerinden yakalama dene
            try:
                img_data = await target_frame.evaluate("""
                    () => {
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
                    }
                """)
                if img_data:
                    raw = base64.b64decode(img_data)
                    with open("perchance_prof_result.png", "wb") as f:
                        f.write(raw)
                    print(f"✅ Sayfadaki canvas/img'den gorsel alindi: perchance_prof_result.png ({len(raw)/1024:.1f} KB)")
                else:
                    print("❌ Sayfada buyuk boyutlu gorsel henuz gorunmedi.")
            except Exception as e:
                print(f"DOM gorsel alma hatasi: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
