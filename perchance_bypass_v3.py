"""
Perchance Anti-bot Bypass v3 - UI Otomasyon Yaklasimi
=====================================================
Onceki yontemler API'yi dogrudan cagirmaya calisti ve 403 aldi.
Bu sefer farkli strateji: Gercek bir kullanici gibi sayfayi kullanacagiz.

Strateji:
1. Dogru sayfayi ac (ai-text-to-image-generator)
2. Prompt textarea'sina yaz
3. Generate butonuna tikla
4. Gorselin yuklenmesini bekle
5. Gorseli indir

Bu, anti-bot'u asmanin en dogal yolu - cunku gercekten
sayfayi kullaniyoruz, sadece otomatik yapiyoruz.
"""

import asyncio
import json
import random
import time
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

# Farkli URL'ler deneyelim
URLS_TO_TRY = [
    "https://perchance.org/ai-text-to-image-generator",
    "https://perchance.org/ai-image-generator",
    "https://perchance.org/image-generator-professional",
]


async def explore_page(url: str):
    """Sayfayi kesfet - ne var ne yok bul"""
    from playwright.async_api import async_playwright

    print(f"\n{'='*60}")
    print(f"[KESFET] {url}")
    print(f"{'='*60}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
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
        api_calls = []
        async def on_response(response):
            u = response.url
            if "image-generation" in u or "generate" in u or "verify" in u:
                api_calls.append({"url": u[:150], "status": response.status})
        page.on("response", on_response)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"   Yukleme: {type(e).__name__}")

        await page.wait_for_timeout(5000)

        # Sayfa basligini al
        title = await page.title()
        print(f"   Baslik: {title}")

        # Screenshot
        safe_name = url.split("/")[-1].replace("-", "_")
        screenshot_path = f"debug_{safe_name}.png"
        await page.screenshot(path=screenshot_path)
        print(f"   Screenshot: {screenshot_path}")

        # Iframe'leri listele
        frames = page.frames
        print(f"   Frame sayisi: {len(frames)}")
        for i, frame in enumerate(frames):
            print(f"     Frame {i}: {frame.url[:100]}")

        # Sayfa icerigini analiz et
        try:
            analysis = await page.evaluate("""
                () => {
                    const info = {};
                    
                    // Tum input/textarea elementleri
                    const inputs = document.querySelectorAll('input, textarea');
                    info.inputs = Array.from(inputs).map(el => ({
                        tag: el.tagName,
                        type: el.type || '',
                        id: el.id || '',
                        name: el.name || '',
                        placeholder: el.placeholder || '',
                        class: el.className || ''
                    })).slice(0, 10);
                    
                    // Tum butonlar
                    const buttons = document.querySelectorAll('button, [role="button"], input[type="submit"]');
                    info.buttons = Array.from(buttons).map(el => ({
                        tag: el.tagName,
                        text: el.textContent?.trim().substring(0, 50) || '',
                        id: el.id || '',
                        class: el.className?.substring(0, 50) || ''
                    })).slice(0, 10);
                    
                    // Iframe'ler
                    const iframes = document.querySelectorAll('iframe');
                    info.iframes = Array.from(iframes).map(f => ({
                        src: f.src?.substring(0, 120) || '',
                        id: f.id || '',
                        class: f.className || ''
                    }));
                    
                    return info;
                }
            """)
            print(f"\n   Input/Textarea'lar ({len(analysis.get('inputs', []))}):")
            for inp in analysis.get("inputs", []):
                print(f"     - <{inp['tag']}> type={inp['type']} id={inp['id']} placeholder='{inp['placeholder'][:40]}'")
            
            print(f"\n   Butonlar ({len(analysis.get('buttons', []))}):")
            for btn in analysis.get("buttons", []):
                print(f"     - <{btn['tag']}> text='{btn['text'][:40]}' id={btn['id']}")

        except Exception as e:
            print(f"   Analiz hatasi: {e}")

        # Her iframe icinde de ara
        for i, frame in enumerate(frames[1:], 1):
            try:
                frame_analysis = await frame.evaluate("""
                    () => {
                        const info = {};
                        
                        // Input/textarea
                        const inputs = document.querySelectorAll('input, textarea');
                        info.inputs = Array.from(inputs).map(el => ({
                            tag: el.tagName,
                            type: el.type || '',
                            id: el.id || '',
                            placeholder: el.placeholder || '',
                        })).slice(0, 10);
                        
                        // Butonlar
                        const buttons = document.querySelectorAll('button, [role="button"]');
                        info.buttons = Array.from(buttons).map(el => ({
                            text: el.textContent?.trim().substring(0, 50) || '',
                            id: el.id || '',
                            class: el.className?.substring(0, 80) || '',
                            onclick: el.getAttribute('onclick')?.substring(0, 80) || '',
                        })).slice(0, 15);

                        // Generate ile ilgili elementler
                        const genElements = document.querySelectorAll('[id*="generat" i], [class*="generat" i], [id*="prompt" i], [class*="prompt" i]');
                        info.generateElements = Array.from(genElements).map(el => ({
                            tag: el.tagName,
                            id: el.id || '',
                            class: el.className?.substring(0, 80) || '',
                            text: el.textContent?.trim().substring(0, 50) || '',
                        })).slice(0, 10);

                        return info;
                    }
                """)
                
                if frame_analysis.get("inputs") or frame_analysis.get("buttons") or frame_analysis.get("generateElements"):
                    print(f"\n   --- Frame {i} ({frame.url[:60]}) ---")
                    
                    if frame_analysis.get("inputs"):
                        print(f"   Inputs:")
                        for inp in frame_analysis["inputs"]:
                            print(f"     - <{inp['tag']}> id={inp['id']} placeholder='{inp['placeholder'][:40]}'")
                    
                    if frame_analysis.get("buttons"):
                        print(f"   Buttons:")
                        for btn in frame_analysis["buttons"]:
                            print(f"     - text='{btn['text'][:40]}' id={btn['id']} class={btn['class'][:40]}")
                    
                    if frame_analysis.get("generateElements"):
                        print(f"   Generate-related:")
                        for el in frame_analysis["generateElements"]:
                            print(f"     - <{el['tag']}> id={el['id']} class={el['class'][:40]} text='{el['text'][:30]}'")

            except Exception as e:
                if "Execution context was destroyed" not in str(e):
                    print(f"   Frame {i} eval hatasi: {type(e).__name__}")

        # API cagrilari
        if api_calls:
            print(f"\n   API cagrilari ({len(api_calls)}):")
            for call in api_calls:
                print(f"     [{call['status']}] {call['url']}")

        await browser.close()
        return screenshot_path


async def try_ui_automation(url: str):
    """Sayfanin UI'ini kullanarak gorsel uret"""
    from playwright.async_api import async_playwright

    print(f"\n{'='*60}")
    print(f"[UI OTOMASYON] {url}")
    print(f"{'='*60}")

    generated_image_url = {"value": None}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            window.chrome = { runtime: {} };
        """)

        # Image response'larini yakala
        async def on_response(response):
            url = response.url
            ct = response.headers.get("content-type", "")
            if ("image" in ct or "downloadTemporary" in url) and response.status == 200:
                if "perchance" in url or "image-generation" in url:
                    generated_image_url["value"] = url
                    print(f"   >> Gorsel URL yakalandi: {url[:100]}")

        page.on("response", on_response)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except:
            pass

        await page.wait_for_timeout(8000)

        # Tum frame'lerde prompt alani ve generate butonu ara
        for frame in page.frames:
            try:
                # Prompt textarea bul
                prompt_el = await frame.query_selector('textarea[id*="prompt" i], textarea[placeholder*="prompt" i], textarea[placeholder*="describe" i], textarea')
                if prompt_el:
                    print(f">> Prompt alani bulundu! Frame: {frame.url[:60]}")
                    
                    # Temizle ve yaz
                    await prompt_el.click()
                    await prompt_el.fill("")
                    await page.wait_for_timeout(500)
                    
                    # Insan gibi yaz (her karakter arasinda kucuk gecikme)
                    await prompt_el.type(PROMPT, delay=10)
                    print(f"   Prompt yazildi ({len(PROMPT)} karakter)")
                    await page.wait_for_timeout(1000)

                    # Generate butonu bul
                    generate_btn = await frame.query_selector('button:has-text("generate"), button:has-text("Generate"), button:has-text("create"), [id*="generat" i]')
                    if generate_btn:
                        print(f">> Generate butonu bulundu! Tiklaniyor...")
                        await generate_btn.click()
                        
                        # Gorselin olusmasini bekle (60 saniye)
                        print(">> Gorsel uretimi bekleniyor (maks 60s)...")
                        for i in range(12):
                            await page.wait_for_timeout(5000)
                            if generated_image_url["value"]:
                                print(f"   Gorsel {(i+1)*5}s'de hazirlandi!")
                                break
                            print(f"   {(i+1)*5}s beklendi...")
                        
                        # Screenshot al
                        await page.screenshot(path="perchance_ui_result.png")
                        print(">> Sonuc screenshot: perchance_ui_result.png")
                    else:
                        print("   Generate butonu bulunamadi")
                        # Tum butonlari listele
                        buttons = await frame.query_selector_all('button')
                        for btn in buttons:
                            text = await btn.text_content()
                            if text and text.strip():
                                print(f"     Buton: '{text.strip()[:50]}'")
                    break
            except Exception as e:
                continue

        await browser.close()
        return generated_image_url.get("value")


async def main():
    print("=" * 60)
    print("PERCHANCE BYPASS v3 - KESFET + UI OTOMASYON")
    print("=" * 60)

    # Once dogru sayfayi bul
    for url in URLS_TO_TRY:
        await explore_page(url)

    # En umut vaat eden URL ile UI otomasyonu dene
    print("\n\n" + "#" * 60)
    print("# UI OTOMASYON DENEMESI")
    print("#" * 60)
    
    for url in URLS_TO_TRY:
        result = await try_ui_automation(url)
        if result:
            print(f"\n[BASARILI] Gorsel URL: {result}")
            break
    else:
        print("\n[SONUC] Hicbir URL'de UI otomasyonu basarili olamadi")


if __name__ == "__main__":
    asyncio.run(main())
