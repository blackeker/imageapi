"""
Perchance Anti-bot Bypass v2 - Gelismis Yontemler
==================================================
Bulgular:
- verifyUser endpoint'i browserId parametresi kullaniyor
- Headless tarayici 403 aliyor (fingerprint tespiti)
- generatorData global degiskeni sayfada mevcut

Yeni strateji:
1. Yeni Chromium headless modunu kullan (tespiti zor)  
2. Sayfanin kendi JS'ini kullanarak API cagr
3. browserId olusturma mantgini anla
4. Sayfadaki iframe/embed yaklasimi
"""

import asyncio
import json
import random
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROMPT = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''

GENERATOR_URL = "https://perchance.org/ai-image-generator"
BASE_URL = "https://image-generation.perchance.org/api"


async def attempt_new_headless():
    """Yeni Chromium headless modu ile deneme (daha zor tespit edilir)"""
    from playwright.async_api import async_playwright

    print("\n" + "=" * 60)
    print("[YONTEM A] Yeni Headless + Sayfa JS Kullanimi")
    print("=" * 60)

    captured_data = {
        "user_key": None,
        "verify_responses": [],
        "all_api_calls": [],
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--window-size=1920,1080",
                "--start-maximized",
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="Europe/Istanbul",
            color_scheme="dark",
            has_touch=False,
            is_mobile=False,
            device_scale_factor=1,
        )

        page = await context.new_page()

        # Kapsamli anti-detection
        await page.add_init_script("""
            // webdriver gizle
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            
            // plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const arr = [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                        { name: 'Native Client', filename: 'internal-nacl-plugin' }
                    ];
                    arr.item = (i) => arr[i];
                    arr.namedItem = (n) => arr.find(p => p.name === n);
                    arr.refresh = () => {};
                    return arr;
                }
            });
            
            // languages
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en', 'tr'] });
            
            // platform  
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            
            // hardwareConcurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            
            // deviceMemory
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            
            // chrome runtime
            window.chrome = {
                runtime: {
                    onMessage: { addListener: () => {} },
                    sendMessage: () => {},
                    connect: () => ({ onMessage: { addListener: () => {} } })
                },
                loadTimes: () => ({}),
                csi: () => ({})
            };
            
            // permissions
            const originalQuery = window.navigator.permissions?.query;
            if (originalQuery) {
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            }
            
            // WebGL vendor
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };
        """)

        # Network isteklerini dinle
        async def on_response(response):
            url = response.url
            if "perchance.org" in url and ("verify" in url or "generate" in url or "userKey" in url or "image-generation" in url):
                status = response.status
                captured_data["all_api_calls"].append({"url": url[:120], "status": status})
                
                if status == 200:
                    try:
                        text = await response.text()
                        if "userKey" in text:
                            idx = text.find('"userKey":"')
                            if idx != -1:
                                start = idx + len('"userKey":"')
                                end = text.find('"', start)
                                captured_data["user_key"] = text[start:end]
                                print(f"   >> userKey YAKALANDI: {captured_data['user_key'][:30]}...")
                    except:
                        pass

        page.on("response", on_response)

        # Sayfayi ac
        print(">> Sayfa aciliyor...")
        try:
            await page.goto(GENERATOR_URL, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print(f"   Goto hatasi (devam): {type(e).__name__}")

        # Insansi bekleme
        print(">> Sayfa yukleniyor, bekleniyor...")
        await page.wait_for_timeout(5000)

        # Sayfada scroll ve mouse hareketi yap (insan taklidi)
        print(">> Insan davranisi taklit ediliyor...")
        try:
            await page.mouse.move(random.randint(100, 800), random.randint(100, 400))
            await page.wait_for_timeout(500)
            await page.mouse.move(random.randint(200, 700), random.randint(200, 500))
            await page.wait_for_timeout(300)
            await page.evaluate("window.scrollBy(0, 300)")
            await page.wait_for_timeout(1000)
            await page.evaluate("window.scrollBy(0, -100)")
        except:
            pass

        # Daha fazla bekle - sayfa arka planda API cagirlari yapiyor olabilir
        print(">> Arka plan istekleri bekleniyor (15s)...")
        await page.wait_for_timeout(15000)

        # Yakalanan istekleri goster
        print(f"\n>> Yakalanan API istekleri ({len(captured_data['all_api_calls'])}):")
        for call in captured_data["all_api_calls"]:
            status_icon = "[OK]" if call["status"] == 200 else f"[{call['status']}]"
            print(f"   {status_icon} {call['url']}")

        # userKey bulunduysa
        if captured_data["user_key"]:
            print(f"\n>> userKey basariyla elde edildi!")
            await browser.close()
            return captured_data["user_key"]

        # Sayfadaki JS'den bilgi cikar
        print("\n>> Sayfadaki JS ortamini inceliyoruz...")
        try:
            page_info = await page.evaluate("""
                () => {
                    const info = {};
                    
                    // browserId nasil uretiliyor?
                    if (window.browserId) info.browserId = window.browserId;
                    
                    // generator verisi
                    if (window.generatorData) {
                        info.hasGeneratorData = true;
                        try {
                            info.generatorKeys = Object.keys(window.generatorData).slice(0, 20);
                        } catch(e) {}
                    }
                    
                    // userKey direkt erisilebilir mi?
                    if (window.userKey) info.userKey = window.userKey;
                    if (window.__userKey) info.__userKey = window.__userKey;
                    
                    // Perchance framework
                    if (window.PerchanceGenerator) info.hasPerchanceGenerator = true;
                    if (window.generate) info.hasGenerateFunc = true;
                    
                    // iframe icindeki icerik
                    try {
                        const iframes = document.querySelectorAll('iframe');
                        info.iframeCount = iframes.length;
                        info.iframeSrcs = Array.from(iframes).map(f => f.src || f.getAttribute('data-src') || '').filter(s => s).slice(0, 5);
                    } catch(e) {}
                    
                    // Tum script etiketlerinin src'leri
                    try {
                        const scripts = document.querySelectorAll('script[src]');
                        info.scriptSrcs = Array.from(scripts).map(s => s.src).filter(s => s.includes('perchance')).slice(0, 10);
                    } catch(e) {}
                    
                    // localStorage detay
                    try {
                        const storage = {};
                        for (let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            const val = localStorage.getItem(key);
                            storage[key] = val ? val.substring(0, 200) : null;
                        }
                        info.localStorage = storage;
                    } catch(e) {}
                    
                    // Cookie
                    info.cookies = document.cookie || '(empty)';
                    
                    return info;
                }
            """)
            print(f"   Sayfa bilgileri:")
            print(json.dumps(page_info, indent=2, ensure_ascii=False))
            
            # Eger iframe varsa, iframe icerigini de kontrol et
            if page_info.get("iframeCount", 0) > 0:
                print(f"\n>> {page_info['iframeCount']} iframe bulundu, icerikler kontrol ediliyor...")
                for i, frame in enumerate(page.frames):
                    frame_url = frame.url
                    if "perchance" in frame_url:
                        print(f"   Frame {i}: {frame_url[:100]}")
                        try:
                            frame_info = await frame.evaluate("""
                                () => {
                                    const info = {};
                                    if (window.userKey) info.userKey = window.userKey;
                                    if (window.__userKey) info.__userKey = window.__userKey;
                                    if (window.browserId) info.browserId = window.browserId;
                                    if (window.generateImage) info.hasGenerateImage = true;
                                    
                                    // Global fonksiyonlari listele
                                    const funcs = [];
                                    for (let key in window) {
                                        if (typeof window[key] === 'function' && 
                                            !key.startsWith('on') && 
                                            key.length > 3 &&
                                            (key.toLowerCase().includes('generat') || 
                                             key.toLowerCase().includes('image') ||
                                             key.toLowerCase().includes('key') ||
                                             key.toLowerCase().includes('verify') ||
                                             key.toLowerCase().includes('user') ||
                                             key.toLowerCase().includes('browser'))) {
                                            funcs.push(key);
                                        }
                                    }
                                    info.relevantFunctions = funcs.slice(0, 20);
                                    
                                    // Relevant variables
                                    const vars = [];
                                    for (let key in window) {
                                        if (typeof window[key] === 'string' && 
                                            window[key].length > 5 && window[key].length < 200 &&
                                            (key.toLowerCase().includes('key') || 
                                             key.toLowerCase().includes('token') ||
                                             key.toLowerCase().includes('browser') ||
                                             key.toLowerCase().includes('user'))) {
                                            vars.push({name: key, value: window[key].substring(0, 50)});
                                        }
                                    }
                                    info.relevantVars = vars.slice(0, 20);
                                    
                                    return info;
                                }
                            """)
                            print(f"     Frame data: {json.dumps(frame_info, indent=2, ensure_ascii=False)}")
                            
                            if frame_info.get("userKey"):
                                captured_data["user_key"] = frame_info["userKey"]
                                print(f"     >> IFRAME'DE userKey BULUNDU!")
                                
                        except Exception as e:
                            print(f"     Frame eval hatasi: {e}")
                            
        except Exception as e:
            print(f"   JS eval hatasi: {e}")

        # Screenshot al (debug icin)
        try:
            await page.screenshot(path="perchance_debug_screenshot.png")
            print("\n>> Debug screenshot kaydedildi: perchance_debug_screenshot.png")
        except:
            pass

        await browser.close()
        return captured_data.get("user_key")


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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Referer": GENERATOR_URL,
        "Origin": "https://perchance.org",
    }

    print(f">> Gorsel uretiliyor...")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=body, headers=headers, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                elapsed = time.time() - start
                print(f"   Status: {resp.status}")

                if resp.status == 200:
                    data = await resp.json()
                    print(f"   [BASARILI] Sure: {elapsed:.1f}s")
                    print(f"   Image ID: {data.get('imageId', 'N/A')}")

                    image_id = data['imageId']
                    dl_url = f"{BASE_URL}/downloadTemporaryImage?imageId={image_id}"
                    async with session.get(dl_url, headers=headers) as dl_resp:
                        if dl_resp.status == 200:
                            img_data = await dl_resp.read()
                            with open("perchance_result.png", "wb") as f:
                                f.write(img_data)
                            print(f"   Dosya: perchance_result.png ({len(img_data)/1024:.1f} KB)")
                else:
                    text = await resp.text()
                    print(f"   Hata ({elapsed:.1f}s): {text[:300]}")
        except Exception as e:
            print(f"   Istek hatasi: {e}")


async def main():
    print("=" * 60)
    print("PERCHANCE ANTI-BOT BYPASS v2")
    print("=" * 60)

    user_key = await attempt_new_headless()

    print("\n" + "=" * 60)
    if user_key:
        print(f"[SONUC] userKey elde edildi: {user_key[:30]}...")
        await generate_with_key(user_key)
    else:
        print("[SONUC] userKey elde edilemedi")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
