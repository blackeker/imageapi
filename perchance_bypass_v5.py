"""
Perchance Bypass v5 - Cookie Capture Yaklasimi
===============================================
Cloudflare, headless tarayiciyi tespit edip engelliyor.
Bu yontem farkli: Gercek tarayicini (Chrome) aciyor,
kullanici olarak sayfayi yukluyoruz, Cloudflare challenge
otomatik cozuluyor ve cookie'leri yakaliyoruz.

Anahtar fark: headless=False (gercek tarayici penceresi)
Cloudflare, gercek tarayici penceresini engelleyemez!
"""

import asyncio
import json
import random
import time
import sys
import io
import base64
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

TARGET_URL = "https://perchance.org/ai-text-to-image-generator"


async def main():
    from playwright.async_api import async_playwright

    print("=" * 60)
    print("PERCHANCE BYPASS v5 - GERCEK TARAYICI")
    print("=" * 60)
    print()
    print(">> ONEMLI: Bu yontem gercek bir Chrome penceresi acar.")
    print(">> Cloudflare, gercek tarayici penceresini engelleyemez.")
    print()

    downloaded_images = []
    user_key_found = {"value": None}

    async with async_playwright() as pw:
        # *** ANAHTAR FARK: headless=False ***
        # Gercek tarayici penceresi acilir
        browser = await pw.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized",
            ],
            slow_mo=100,  # Islemleri biraz yavaslatarak daha dogal yap
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            no_viewport=True,
        )

        page = await context.new_page()

        # Minimal anti-detection (gercek tarayicide fazla gerekmiyor)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
        """)

        # Network dinle
        async def on_response(response):
            url = response.url
            status = response.status

            if "verifyUser" in url:
                print(f"   [verifyUser] status={status}")
                if status == 200:
                    try:
                        text = await response.text()
                        if "userKey" in text:
                            idx = text.find('"userKey":"')
                            start = idx + len('"userKey":"')
                            end = text.find('"', start)
                            key = text[start:end]
                            user_key_found["value"] = key
                            print(f"   >> userKey YAKALANDI: {key[:30]}...")
                            
                            # Key'i dosyaya kaydet (gelecek kullanim icin)
                            with open("perchance_session.json", "w") as f:
                                json.dump({
                                    "userKey": key,
                                    "timestamp": time.time(),
                                }, f)
                            print(f"   >> Session kaydedildi: perchance_session.json")
                    except:
                        pass
                        
            if "downloadTemporary" in url and status == 200:
                try:
                    data = await response.body()
                    downloaded_images.append(data)
                    print(f"   >> GORSEL INDIRILDI ({len(data)/1024:.1f} KB)")
                except:
                    pass

        page.on("response", on_response)

        # ========================================
        # 1. SAYFAYI AC
        # ========================================
        print("[1/5] Sayfa aciliyor (gercek tarayici)...")
        try:
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            print("   Sayfa yuklendi")
        except Exception as e:
            print(f"   Yukleme: {type(e).__name__} (devam)")

        # Cloudflare challenge'in cozulmesini bekle
        print("[2/5] Cloudflare challenge bekleniyor (15s)...")
        await page.wait_for_timeout(15000)

        # ========================================
        # 2. DOGRU FRAME'I BUL
        # ========================================
        print("\n[3/5] Generator frame'i araniyor...")
        
        target_frame = None
        for i, frame in enumerate(page.frames):
            url = frame.url
            if "perchance.org/ai-text-to-image" in url and url != TARGET_URL:
                target_frame = frame
                print(f"   Frame {i}: {url[:80]}")
                break

        if not target_frame:
            # Fallback
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
            print("   HATA: Frame bulunamadi!")
            for i, frame in enumerate(page.frames):
                print(f"     Frame {i}: {frame.url[:100]}")
            await page.screenshot(path="v5_error.png")
            await browser.close()
            return

        # ========================================
        # 3. PROMPT YAZ
        # ========================================
        print("\n[3/5] Prompt yaziliyor...")
        
        # Textarea bul (2. textarea = prompt)
        textareas = await target_frame.query_selector_all('textarea')
        prompt_textarea = None
        for ta in textareas:
            ph = await ta.get_attribute("placeholder") or ""
            if "girl" in ph or "picnic" in ph or "describe" in ph or "monster" in ph:
                prompt_textarea = ta
                break
        
        if not prompt_textarea and len(textareas) >= 2:
            prompt_textarea = textareas[1]
        elif not prompt_textarea and textareas:
            prompt_textarea = textareas[0]

        if not prompt_textarea:
            print("   HATA: Prompt textarea bulunamadi!")
            await browser.close()
            return

        # Shape'i Landscape yap (16:9 icin)
        try:
            shape_select = await target_frame.query_selector('select')
            selects = await target_frame.query_selector_all('select')
            for sel in selects:
                # Shape select'ini bul
                options = await sel.query_selector_all('option')
                for opt in options:
                    text = await opt.text_content()
                    if "landscape" in text.lower() or "wide" in text.lower():
                        val = await opt.get_attribute("value")
                        await sel.select_option(value=val)
                        print(f"   Shape: Landscape secildi")
                        break
        except:
            pass

        # How many? 1 yap (daha hizli)
        try:
            selects = await target_frame.query_selector_all('select')
            for sel in selects:
                options = await sel.query_selector_all('option')
                option_texts = []
                for opt in options:
                    text = (await opt.text_content()).strip()
                    option_texts.append(text)
                # "1" secenegi olan select = "How many?"
                if "1" in option_texts and "2" in option_texts:
                    await sel.select_option(value="1")
                    print(f"   How many: 1 secildi")
                    break
        except:
            pass

        # Prompt yaz
        await prompt_textarea.click()
        await page.wait_for_timeout(500)
        
        # Triple-click ile tum metni sec, sonra sil
        await prompt_textarea.click(click_count=3)
        await page.keyboard.press("Backspace")
        await page.wait_for_timeout(300)
        
        # Yeni prompt'u yaz
        await prompt_textarea.fill(PROMPT)
        await page.wait_for_timeout(500)
        
        # Input event tetikle
        await prompt_textarea.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await prompt_textarea.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
        
        current_val = await prompt_textarea.evaluate("el => el.value")
        print(f"   Yazildi: {current_val[:60]}... ({len(current_val)} chr)")

        # ========================================
        # 4. GENERATE TIKLA
        # ========================================
        print("\n[4/5] Generate butonuna tiklaniyor...")
        await page.wait_for_timeout(2000)

        generate_btn = await target_frame.query_selector("#generateButtonEl")
        if generate_btn:
            # Butona scroll et
            await generate_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            
            # Tikla
            await generate_btn.click()
            print("   Generate tiklandi!")
        else:
            print("   HATA: Generate butonu bulunamadi!")
            await browser.close()
            return

        # ========================================
        # 5. SONUCU BEKLE
        # ========================================
        print("\n[5/5] Gorsel uretimi bekleniyor (maks 120s)...")
        start_time = time.time()
        max_wait = 120

        for tick in range(max_wait // 5):
            await page.wait_for_timeout(5000)
            elapsed = time.time() - start_time

            if downloaded_images:
                print(f"\n   >> BASARILI! Gorsel {elapsed:.0f}s'de indirildi!")
                break

            # Sayfadaki gorsel varligini kontrol et
            try:
                img_check = await target_frame.evaluate("""
                    () => {
                        const imgs = document.querySelectorAll('img');
                        const found = [];
                        for (const img of imgs) {
                            if (img.src && img.naturalWidth > 200) {
                                found.push({src: img.src.substring(0, 80), w: img.naturalWidth, h: img.naturalHeight});
                            }
                        }
                        // Loading/progress kontrol
                        const all = document.body.innerText;
                        const hasLoading = all.includes('loading') || all.includes('generating') || all.includes('Generating');
                        const hasError = all.includes('error') || all.includes('Error') || all.includes('limit');
                        
                        return {images: found.slice(0, 3), loading: hasLoading, error: hasError};
                    }
                """)
                
                status = f"imgs={len(img_check.get('images', []))}"
                if img_check.get("loading"):
                    status += " LOADING"
                if img_check.get("error"):
                    status += " ERROR!"
                for img in img_check.get("images", []):
                    status += f" [{img['w']}x{img['h']}]"
                
                print(f"   [{elapsed:.0f}s] {status}")
                
                # Gorsel bulduysa indir
                if img_check.get("images"):
                    for img_info in img_check["images"]:
                        if img_info["w"] > 300:
                            print(f"   >> Sayfada gorsel bulundu! Indiriliyor...")
                            img_data_b64 = await target_frame.evaluate("""
                                (src) => {
                                    const img = document.querySelector(`img[src="${src}"]`) || 
                                                document.querySelector('img[src^="blob:"]');
                                    if (!img) return null;
                                    const canvas = document.createElement('canvas');
                                    canvas.width = img.naturalWidth;
                                    canvas.height = img.naturalHeight;
                                    const ctx = canvas.getContext('2d');
                                    ctx.drawImage(img, 0, 0);
                                    return canvas.toDataURL('image/png').split(',')[1];
                                }
                            """, img_info["src"])
                            
                            if img_data_b64:
                                raw = base64.b64decode(img_data_b64)
                                downloaded_images.append(raw)
                                print(f"   >> Gorsel yakalandi ({len(raw)/1024:.1f} KB)")
                            break
            except:
                print(f"   [{elapsed:.0f}s] ...")

            if elapsed > max_wait:
                break

        # Screenshot
        await page.screenshot(path="perchance_v5_result.png")
        print(f"\n>> Screenshot: perchance_v5_result.png")

        # Kaydet
        if downloaded_images:
            with open("perchance_result.png", "wb") as f:
                f.write(downloaded_images[0])
            print(f">> GORSEL KAYDEDILDI: perchance_result.png ({len(downloaded_images[0])/1024:.1f} KB)")

        # userKey kaydet
        if user_key_found["value"]:
            print(f"\n>> userKey da kaydedildi! Gelecekte dogrudan API ile kullanilabilir.")

        await browser.close()

    # Sonuc
    print("\n" + "=" * 60)
    if downloaded_images:
        print("[SONUC] BASARILI!")
        print(f"   Gorsel: perchance_result.png")
        if user_key_found["value"]:
            print(f"   userKey: {user_key_found['value'][:30]}...")
            print(f"   Session: perchance_session.json")
    else:
        print("[SONUC] Gorsel uretilemedi")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
