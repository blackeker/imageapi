"""
Perchance Bypass v4 - Hedefli UI Otomasyon
==========================================
Bulgular:
- Dogru sayfa: ai-text-to-image-generator
- Generator Frame 2 icinde (cd282...perchance.org)  
- Prompt placeholder: 'girl, at a penthouse, watching the city,'
- Generate butonu: id=generateButtonEl, text='generate'
- Cloudflare challenge var ama sayfa icinden calisiyoruz

Strateji: Dogrudan Frame 2'yi hedefle, prompt yaz, generate tikla
"""

import asyncio
import json
import random
import time
import sys
import io
import base64

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

TARGET_URL = "https://perchance.org/ai-text-to-image-generator"


async def main():
    from playwright.async_api import async_playwright

    print("=" * 60)
    print("PERCHANCE BYPASS v4 - HEDEFLI UI OTOMASYON")
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
            timezone_id="Europe/Istanbul",
        )

        page = await context.new_page()

        # Anti-detection
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'tr'] });
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            window.chrome = { runtime: {} };
        """)

        # Image download'larini yakala
        async def on_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            status = response.status
            
            # verifyUser sonuclarini logla
            if "verifyUser" in url:
                print(f"   [verifyUser] status={status} url={url[:100]}")
                if status == 200:
                    try:
                        text = await response.text()
                        if "userKey" in text:
                            print(f"   >> userKey YAKALANDI!")
                    except:
                        pass
            
            # Uretilen gorsel
            if "downloadTemporary" in url and status == 200:
                try:
                    data = await response.body()
                    downloaded_images.append(data)
                    print(f"   >> GORSEL INDIRILDI! ({len(data)/1024:.1f} KB)")
                except:
                    pass

        page.on("response", on_response)

        # ========================================
        # 1. SAYFAYI AC
        # ========================================
        print("\n[1/5] Sayfa aciliyor...")
        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
            print("   Sayfa yuklendi")
        except Exception as e:
            print(f"   Yukleme hatasi (devam): {type(e).__name__}")

        # Sayfanin tamamen yuklenmesini bekle
        print("[2/5] Sayfa iceriginin yuklenmesi bekleniyor (10s)...")
        await page.wait_for_timeout(10000)

        # ========================================
        # 2. DOGRU FRAME'I BUL
        # ========================================
        print("\n[3/5] Generator frame'i araniyor...")
        
        target_frame = None
        for i, frame in enumerate(page.frames):
            url = frame.url
            # Generator iframe'ini bul (hash subdomain)
            if "perchance.org/ai-text-to-image" in url and url != TARGET_URL:
                target_frame = frame
                print(f"   Generator frame bulundu: Frame {i}")
                print(f"   URL: {url[:80]}")
                break

        if not target_frame:
            print("   Generator frame bulunamadi! Tum frame'ler:")
            for i, frame in enumerate(page.frames):
                print(f"     Frame {i}: {frame.url[:100]}")
            
            # Fallback: generateButtonEl iceren frame'i bul
            for i, frame in enumerate(page.frames):
                try:
                    btn = await frame.query_selector("#generateButtonEl")
                    if btn:
                        target_frame = frame
                        print(f"   generateButtonEl Frame {i}'de bulundu!")
                        break
                except:
                    continue

        if not target_frame:
            print("   HATA: Hedef frame bulunamadi!")
            await page.screenshot(path="v4_error.png")
            await browser.close()
            return

        # ========================================
        # 3. PROMPT TEXTAREA'SINI BUL VE YAZ
        # ========================================
        print("\n[3/5] Prompt alani araniyor...")
        
        # Prompt textarea'sini bul (placeholder'a gore)
        prompt_textarea = await target_frame.query_selector('textarea[placeholder*="girl"]')
        if not prompt_textarea:
            prompt_textarea = await target_frame.query_selector('textarea[placeholder*="penthouse"]')
        if not prompt_textarea:
            # Tum textarea'lari dene
            textareas = await target_frame.query_selector_all('textarea')
            print(f"   {len(textareas)} textarea bulundu")
            for j, ta in enumerate(textareas):
                ph = await ta.get_attribute("placeholder") or ""
                print(f"     textarea[{j}] placeholder='{ph[:50]}'")
                # 2. textarea genellikle prompt alani (1. notlar icin)
                if j == 1 or "girl" in ph.lower() or "describe" in ph.lower():
                    prompt_textarea = ta
                    break
            if not prompt_textarea and textareas:
                prompt_textarea = textareas[-1] if len(textareas) == 1 else textareas[1]

        if not prompt_textarea:
            print("   HATA: Prompt textarea bulunamadi!")
            await page.screenshot(path="v4_no_textarea.png")
            await browser.close()
            return

        print("   Prompt textarea bulundu!")
        
        # Temizle
        await prompt_textarea.click()
        await page.wait_for_timeout(300)
        await prompt_textarea.evaluate("el => el.value = ''")
        await prompt_textarea.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await page.wait_for_timeout(300)

        # Prompt'u yaz
        print("   Prompt yaziliyor...")
        await prompt_textarea.fill(PROMPT)
        await prompt_textarea.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await page.wait_for_timeout(1000)
        
        # Dogrulama
        current_val = await prompt_textarea.evaluate("el => el.value")
        print(f"   Yazilan: {current_val[:60]}... ({len(current_val)} karakter)")

        # ========================================
        # 4. GENERATE BUTONUNA TIKLA
        # ========================================
        print("\n[4/5] Generate butonuna tiklaniyor...")
        
        generate_btn = await target_frame.query_selector("#generateButtonEl")
        if not generate_btn:
            generate_btn = await target_frame.query_selector('button:has-text("generate")')
        
        if not generate_btn:
            print("   HATA: Generate butonu bulunamadi!")
            await page.screenshot(path="v4_no_button.png")
            await browser.close()
            return

        btn_text = await generate_btn.text_content()
        print(f"   Buton bulundu: '{btn_text.strip()}'")
        
        # Mouse ile tikla (daha dogal)
        box = await generate_btn.bounding_box()
        if box:
            await page.mouse.click(
                box["x"] + box["width"] / 2,
                box["y"] + box["height"] / 2
            )
        else:
            await generate_btn.click()
        
        print("   Generate butonuna tiklandi!")

        # ========================================
        # 5. SONUCU BEKLE
        # ========================================
        print("\n[5/5] Gorsel uretimi bekleniyor...")
        start_time = time.time()
        max_wait = 90  # max 90 saniye

        for tick in range(max_wait // 5):
            await page.wait_for_timeout(5000)
            elapsed = time.time() - start_time
            
            # Indirilen gorsel var mi?
            if downloaded_images:
                print(f"\n   [BASARILI] Gorsel {elapsed:.0f}s'de uretildi!")
                break

            # Sayfadaki durumu kontrol et
            try:
                status_text = await target_frame.evaluate("""
                    () => {
                        // Yukleme durumu
                        const statusEl = document.querySelector('[class*="status"], [class*="progress"], [id*="status"]');
                        const loadingEl = document.querySelector('[class*="loading"], [class*="spinner"]');
                        const errorEl = document.querySelector('[class*="error"]');
                        const imgEl = document.querySelector('img[src*="image-generation"], img[src*="blob:"]');
                        
                        let info = '';
                        if (statusEl) info += 'Status: ' + statusEl.textContent.trim().substring(0, 50) + ' | ';
                        if (loadingEl) info += 'Loading: visible | ';
                        if (errorEl) info += 'Error: ' + errorEl.textContent.trim().substring(0, 50) + ' | ';
                        if (imgEl) info += 'Image found: ' + imgEl.src.substring(0, 60) + ' | ';
                        
                        // Canvas kontrol
                        const canvases = document.querySelectorAll('canvas');
                        if (canvases.length > 0) info += `Canvas: ${canvases.length} | `;
                        
                        return info || 'Bekleniyor...';
                    }
                """)
                print(f"   [{elapsed:.0f}s] {status_text}")
            except:
                print(f"   [{elapsed:.0f}s] Kontrol edilemiyor...")

            if elapsed > max_wait:
                break

        # Son screenshot
        screenshot_path = "perchance_v4_result.png"
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"\n>> Screenshot: {screenshot_path}")

        # Indirilen gorseli kaydet
        if downloaded_images:
            output_path = "perchance_result.png"
            with open(output_path, "wb") as f:
                f.write(downloaded_images[0])
            print(f">> Gorsel kaydedildi: {output_path} ({len(downloaded_images[0])/1024:.1f} KB)")
        else:
            print("\n>> Gorsel indirilemedi. Sayfadan gorsel cikarma deneniyor...")
            
            # Sayfadaki img/canvas'tan gorsel al
            try:
                img_data = await target_frame.evaluate("""
                    () => {
                        // blob/data URL'li img bul
                        const imgs = document.querySelectorAll('img');
                        for (const img of imgs) {
                            if (img.src && (img.src.startsWith('blob:') || img.src.startsWith('data:')) && img.naturalWidth > 100) {
                                // Canvas'a ciz ve data URL al
                                const canvas = document.createElement('canvas');
                                canvas.width = img.naturalWidth;
                                canvas.height = img.naturalHeight;
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(img, 0, 0);
                                return canvas.toDataURL('image/png').split(',')[1];
                            }
                        }
                        
                        // Canvas bul
                        const canvases = document.querySelectorAll('canvas');
                        for (const canvas of canvases) {
                            if (canvas.width > 100 && canvas.height > 100) {
                                return canvas.toDataURL('image/png').split(',')[1];
                            }
                        }
                        
                        return null;
                    }
                """)
                
                if img_data:
                    raw = base64.b64decode(img_data)
                    with open("perchance_result.png", "wb") as f:
                        f.write(raw)
                    print(f"   Gorsel sayfadan cikarildi! ({len(raw)/1024:.1f} KB)")
                else:
                    print("   Sayfada gorsel bulunamadi.")
            except Exception as e:
                print(f"   Gorsel cikarma hatasi: {e}")

        await browser.close()

    # Sonuc
    print("\n" + "=" * 60)
    if downloaded_images:
        print("[SONUC] BASARILI - Gorsel perchance_result.png olarak kaydedildi!")
    else:
        print("[SONUC] Gorsel uretilemedi")
        print("   Perchance Cloudflare challenge korumasi bypass edilemedi.")
        print("   Screenshot'u kontrol edin: perchance_v4_result.png")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
