"""
Perchance Image Generator - Anti-bot Bypass
============================================
Playwright ile gercek tarayici davranisi taklit ederek
Perchance'in anti-bot korumasini asma denemesi.

Strateji:
1. Once ana sayfayi ziyaret edip cookie/session al
2. Gercekci user-agent ve viewport kullan  
3. Mouse hareketi ve bekleme ile insan davranisi taklit et
4. verifyUser endpoint'inden userKey'i yakala
5. generate endpoint'ine POST yap
"""

import asyncio
import json
import random
import time
import sys
import io
import base64
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

BASE_URL = "https://image-generation.perchance.org/api"
GENERATOR_URL = "https://perchance.org/ai-image-generator"


async def attempt_1_stealth_browser():
    """Yontem 1: Stealth browser ile verifyUser'dan key alma"""
    from playwright.async_api import async_playwright

    print("\n" + "=" * 60)
    print("[YONTEM 1] Stealth Browser + verifyUser")
    print("=" * 60)

    async with async_playwright() as pw:
        # Gercekci browser ayarlari
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
        )

        page = await context.new_page()

        # navigator.webdriver'i gizle
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
        """)

        # 1. Once ana sayfayi ziyaret et (cookie toplama)
        print(">> Ana sayfa ziyaret ediliyor...")
        try:
            await page.goto(GENERATOR_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(random.randint(2000, 4000))
            print("   Ana sayfa yuklendi")
        except Exception as e:
            print(f"   Ana sayfa hatasi (devam ediliyor): {e}")

        # 2. verifyUser endpoint'ine git
        print(">> verifyUser endpoint'ine gidiliyor...")
        cache_bust = random.random()
        verify_url = f"{BASE_URL}/verifyUser?thread=0&__cacheBust={cache_bust}"
        
        try:
            await page.goto(verify_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            print(f"   Sayfa icerigi uzunlugu: {len(content)} karakter")
            
            # userKey ara
            key_entry = content.find('"userKey":"')
            if key_entry != -1:
                start_idx = key_entry + len('"userKey":"')
                end_idx = content.find('"', start_idx)
                user_key = content[start_idx:end_idx]
                print(f"   [BULUNDU] userKey: {user_key[:20]}...")
                
                await browser.close()
                return user_key
            else:
                # Detayli debug
                print(f"   userKey bulunamadi!")
                # Sayfadaki JSON'u bul
                if "too_many_requests" in content:
                    print("   >> RATE LIMIT - cok fazla istek")
                elif "challenge" in content.lower():
                    print("   >> CHALLENGE/CAPTCHA tespit edildi")
                
                # Sayfanin ilk 500 karakterini goster
                body_start = content.find("<body")
                if body_start != -1:
                    snippet = content[body_start:body_start+500]
                    print(f"   Body snippet: {snippet[:200]}...")
                else:
                    print(f"   Raw snippet: {content[:300]}...")
                    
        except Exception as e:
            print(f"   verifyUser hatasi: {e}")

        await browser.close()
        return None


async def attempt_2_intercept_network():
    """Yontem 2: Gercek sayfayi ac, network isteklerini yakala"""
    from playwright.async_api import async_playwright

    print("\n" + "=" * 60)
    print("[YONTEM 2] Network Intercept - Gercek sayfa uzerinden")
    print("=" * 60)

    captured_key = {"value": None}
    captured_requests = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()

        # navigator.webdriver gizle
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)

        # Tum network isteklerini dinle
        async def on_response(response):
            url = response.url
            if "verifyUser" in url or "userKey" in url or "generate" in url:
                captured_requests.append({
                    "url": url,
                    "status": response.status,
                })
                try:
                    body = await response.text()
                    if "userKey" in body:
                        key_start = body.find('"userKey":"') + len('"userKey":"')
                        key_end = body.find('"', key_start)
                        captured_key["value"] = body[key_start:key_end]
                        print(f"   [YAKALANDI] userKey: {captured_key['value'][:20]}...")
                except:
                    pass

        page.on("response", on_response)

        # Ana sayfayi ac ve bekle
        print(">> AI Image Generator sayfasi aciliyor...")
        try:
            await page.goto(GENERATOR_URL, wait_until="domcontentloaded", timeout=60000)
            print("   Sayfa yuklendi, network istekleri dinleniyor...")
            
            # Sayfanin tam yuklenmesini bekle
            await page.wait_for_timeout(10000)
            
            print(f"   Yakalanan ilgili istekler: {len(captured_requests)}")
            for req in captured_requests:
                print(f"     - {req['status']} {req['url'][:80]}")
                
        except Exception as e:
            print(f"   Sayfa yukleme hatasi: {e}")

        if captured_key["value"]:
            print(f"\n   [BASARILI] userKey elde edildi!")
            await browser.close()
            return captured_key["value"]
        
        # Sayfadaki global degiskenleri kontrol et
        print("\n>> Sayfadaki global degiskenler kontrol ediliyor...")
        try:
            js_vars = await page.evaluate("""
                () => {
                    const result = {};
                    // Perchance'in kullandigi bilinen degiskenleri ara
                    if (window.userKey) result.userKey = window.userKey;
                    if (window.__perchance) result.__perchance = JSON.stringify(window.__perchance);
                    if (window.generatorData) result.generatorData = 'found';
                    
                    // localStorage kontrol
                    try {
                        const keys = Object.keys(localStorage);
                        result.localStorageKeys = keys;
                    } catch(e) {}
                    
                    return result;
                }
            """)
            print(f"   JS degiskenleri: {json.dumps(js_vars, indent=2)}")
        except Exception as e:
            print(f"   JS eval hatasi: {e}")

        await browser.close()
        return None


async def attempt_3_direct_api():
    """Yontem 3: Dogrudan HTTP ile API endpoint'lerine istek"""
    import aiohttp

    print("\n" + "=" * 60)
    print("[YONTEM 3] Dogrudan HTTP API istekleri")
    print("=" * 60)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": GENERATOR_URL,
        "Origin": "https://perchance.org",
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # 1. Ana sayfayi ziyaret et (cookie al)
        print(">> Ana sayfa cookie'leri aliniyor...")
        try:
            async with session.get(GENERATOR_URL) as resp:
                print(f"   Status: {resp.status}")
                cookies = session.cookie_jar.filter_cookies("https://perchance.org")
                print(f"   Cookie sayisi: {len(cookies)}")
                for name, cookie in cookies.items():
                    print(f"     - {name}: {str(cookie.value)[:30]}...")
        except Exception as e:
            print(f"   Hata: {e}")

        # 2. verifyUser endpoint'ine istek
        print("\n>> verifyUser endpoint'ine istek yapiliyor...")
        cache_bust = random.random()
        verify_url = f"{BASE_URL}/verifyUser?thread=0&__cacheBust={cache_bust}"
        
        try:
            async with session.get(verify_url) as resp:
                print(f"   Status: {resp.status}")
                text = await resp.text()
                print(f"   Yanit uzunlugu: {len(text)}")
                print(f"   Yanit (ilk 300): {text[:300]}")
                
                if '"userKey"' in text:
                    key_start = text.find('"userKey":"') + len('"userKey":"')
                    key_end = text.find('"', key_start)
                    user_key = text[key_start:key_end]
                    print(f"\n   [BASARILI] userKey: {user_key[:20]}...")
                    return user_key
                    
        except Exception as e:
            print(f"   Hata: {e}")

    return None


async def generate_with_key(user_key: str):
    """Elde edilen key ile gorsel uret"""
    import aiohttp

    print("\n" + "=" * 60)
    print("[GORSEL URETIMI]")
    print("=" * 60)

    url = (
        f"{BASE_URL}/generate"
        f"?userKey={user_key}"
        f"&requestId=aiImageCompletion{random.randint(0, 2**30)}"
        f"&__cacheBust={random.random()}"
    )

    body = {
        "generatorName": "ai-image-generator",
        "channel": "ai-text-to-image-generator",
        "subChannel": "public",
        "prompt": PROMPT,
        "negativePrompt": "blurry, low quality, watermark, text",
        "seed": -1,
        "resolution": "768x512",
        "guidanceScale": 7.0,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": GENERATOR_URL,
        "Origin": "https://perchance.org",
    }

    print(f">> Gorsel uretiliyor...")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=body, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as resp:
            elapsed = time.time() - start
            print(f"   Status: {resp.status}")
            
            if resp.status == 200:
                data = await resp.json()
                print(f"   [BASARILI] Sure: {elapsed:.1f}s")
                print(f"   Image ID: {data.get('imageId', 'N/A')}")
                
                # Gorseli indir
                image_id = data['imageId']
                dl_url = f"{BASE_URL}/downloadTemporaryImage?imageId={image_id}"
                async with session.get(dl_url, headers=headers) as dl_resp:
                    if dl_resp.status == 200:
                        img_data = await dl_resp.read()
                        output_path = "perchance_result.png"
                        with open(output_path, "wb") as f:
                            f.write(img_data)
                        print(f"   Dosya: {output_path} ({len(img_data)/1024:.1f} KB)")
                    else:
                        print(f"   Indirme hatasi: {dl_resp.status}")
            else:
                text = await resp.text()
                print(f"   Hata ({elapsed:.1f}s): {text[:300]}")


async def main():
    print("=" * 60)
    print("PERCHANCE ANTI-BOT BYPASS DENEMESI")
    print("=" * 60)

    user_key = None

    # Yontem 3: Dogrudan HTTP (en hizli)
    user_key = await attempt_3_direct_api()
    
    # Yontem 1: Stealth browser
    if not user_key:
        user_key = await attempt_1_stealth_browser()

    # Yontem 2: Network intercept (en yavas ama en gercekci)
    if not user_key:
        user_key = await attempt_2_intercept_network()

    # Sonuc
    print("\n" + "=" * 60)
    if user_key:
        print(f"[SONUC] userKey basariyla elde edildi!")
        await generate_with_key(user_key)
    else:
        print("[SONUC] Hicbir yontem calismadi :(")
        print("   Perchance'in anti-bot korumasi bu yontemlerle asilamadi.")
        print("   Oneriler:")
        print("   - Pollinations.ai kullanin (ucretsiz, guvenilir)")
        print("   - HuggingFace Inference API deneyin")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
