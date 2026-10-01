"""
Unified Multi-Category AI Image Generation Core Engine
======================================================
Perchance, Stable Horde ve Pollinations motorlarını çoklu kategori (Anime, Gerçekçi, Cyberpunk, Fantastik, 3D, Pixel Art vb.) desteğiyle çalıştırır.
"""

import sys
import io
import time
import json
import base64
import random
import asyncio
import requests
from pathlib import Path
from playwright.async_api import async_playwright
from categories import enhance_prompt_with_category, CATEGORIES

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT_DIR = Path("gallery")
OUTPUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------
# 1. PERCHANCE MOTORU
# -------------------------------------------------------------
async def generate_perchance(
    prompt: str,
    shape: str = "landscape", # landscape, square, portrait
    art_style: str = "Painted Anime",
    output_filename: str = None,
    timeout: int = 90
) -> dict:
    start_t = time.time()
    filename = output_filename or f"perchance_{int(time.time())}_{random.randint(100,999)}.png"
    filepath = OUTPUT_DIR / filename
    downloaded_images = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--start-maximized"],
            slow_mo=50
        )
        context = await browser.new_context(viewport={"width": 1920, "height": 1080}, locale="en-US", no_viewport=True)
        page = await context.new_page()

        async def on_response(response):
            url = response.url
            if "downloadTemporary" in url and response.status == 200:
                try:
                    data = await response.body()
                    if len(data) > 10000:
                        downloaded_images.append(data)
                except: pass

        page.on("response", on_response)

        await page.goto("https://perchance.org/ai-text-to-image-generator", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(7000)

        # Frame bul
        target_frame = None
        for frame in page.frames:
            if "perchance.org/ai-text-to-image" in frame.url and frame.url != "https://perchance.org/ai-text-to-image-generator":
                target_frame = frame
                break
        if not target_frame:
            for frame in page.frames:
                try:
                    if await frame.query_selector("#generateButtonEl"):
                        target_frame = frame
                        break
                except: pass
        if not target_frame: target_frame = page.main_frame

        # Art style seç
        if art_style:
            try:
                selects = await target_frame.query_selector_all("select")
                for sel in selects:
                    opts = await sel.query_selector_all("option")
                    for opt in opts:
                        txt = (await opt.text_content()) or ""
                        if art_style.lower() in txt.lower():
                            val = await opt.get_attribute("value")
                            await sel.select_option(value=val)
                            break
            except: pass

        # Textarea bul & doldur
        textareas = await target_frame.query_selector_all('textarea')
        prompt_ta = None
        for ta in textareas:
            ph = (await ta.get_attribute("placeholder")) or ""
            if "store" not in ph.lower() and len(ph) > 0:
                prompt_ta = ta
                break
        if not prompt_ta and textareas: prompt_ta = textareas[-1] if len(textareas) > 1 else textareas[0]

        # How many = 1
        try:
            selects = await target_frame.query_selector_all('select')
            for sel in selects:
                opts = [await o.text_content() for o in await sel.query_selector_all('option')]
                if "1" in opts and "2" in opts:
                    await sel.select_option(value="1")
                    break
        except: pass

        # Prompt yaz
        await prompt_ta.click()
        await prompt_ta.fill(prompt)
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
        await page.wait_for_timeout(1000)

        # Generate tıkla
        gen_btn = await target_frame.query_selector("#generateButtonEl, button:has-text('generate')")
        if gen_btn:
            await gen_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)
            await gen_btn.click()

        # Bekle
        while time.time() - start_t < timeout:
            await page.wait_for_timeout(3000)
            if downloaded_images: break
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
                    downloaded_images.append(base64.b64decode(img_data))
                    break
            except: pass

        await browser.close()

        if downloaded_images:
            with open(filepath, "wb") as f:
                f.write(downloaded_images[-1])
            return {
                "success": True,
                "provider": "perchance",
                "filename": filename,
                "filepath": str(filepath),
                "url": f"/api/gallery/{filename}",
                "elapsed_seconds": round(time.time() - start_t, 2),
                "size_kb": round(len(downloaded_images[-1])/1024, 1)
            }
        else:
            raise TimeoutError("Perchance görsel üretimi zaman aşımına uğradı.")

# -------------------------------------------------------------
# 2. STABLE HORDE MOTORU (Kategori Optimize)
# -------------------------------------------------------------
def generate_horde(
    prompt: str,
    negative_prompt: str = None,
    models: list = None,
    width: int = 896,
    height: int = 512,
    steps: int = 25,
    cfg_scale: float = 7.0,
    output_filename: str = None
) -> dict:
    start_t = time.time()
    filename = output_filename or f"horde_{int(time.time())}_{random.randint(100,999)}.png"
    filepath = OUTPUT_DIR / filename

    if models is None:
        models = ["AlbedoBase XL 3.1", "CyberRealistic Pony", "Animagine XL", "DreamShaper XL"]

    neg = negative_prompt or "lowres, bad anatomy, bad hands, cropped, worst quality, low quality, normal quality, artifacts, blurry, watermark"

    headers = {"apikey": "0000000000", "Content-Type": "application/json", "Client-Agent": "MultiCategoryEngine:1.0"}
    payload = {
        "prompt": f"{prompt} ### {neg}",
        "params": {"sampler_name": "k_euler_a", "cfg_scale": cfg_scale, "width": width, "height": height, "steps": steps, "n": 1},
        "models": models,
        "nsfw": True,
        "censor_nsfw": False,
        "shared": True
    }

    res = requests.post("https://aihorde.net/api/v2/generate/async", headers=headers, json=payload, timeout=30)
    if res.status_code != 202:
        raise Exception(f"Horde Hatası: {res.status_code} - {res.text}")

    req_id = res.json()["id"]

    while True:
        time.sleep(3)
        check = requests.get(f"https://aihorde.net/api/v2/generate/check/{req_id}", headers=headers, timeout=30).json()
        if check.get("done", False): break
        if time.time() - start_t > 150: raise TimeoutError("Horde işlemi zaman aşımına uğradı.")

    status = requests.get(f"https://aihorde.net/api/v2/generate/status/{req_id}", headers=headers, timeout=30).json()
    gens = status.get("generations", [])
    if not gens: raise Exception("Görsel oluşturulamadı.")

    img_data = gens[0].get("img")
    used_model = gens[0].get("model", "Bilinmiyor")

    if img_data.startswith("http"):
        raw = requests.get(img_data).content
    else:
        raw = base64.b64decode(img_data)

    with open(filepath, "wb") as f:
        f.write(raw)

    return {
        "success": True,
        "provider": "horde",
        "model": used_model,
        "filename": filename,
        "filepath": str(filepath),
        "url": f"/api/gallery/{filename}",
        "elapsed_seconds": round(time.time() - start_t, 2),
        "size_kb": round(len(raw)/1024, 1)
    }

# -------------------------------------------------------------
# 3. POLLINATIONS MOTORU
# -------------------------------------------------------------
def generate_pollinations(
    prompt: str,
    width: int = 1024,
    height: int = 576,
    model: str = "flux",
    output_filename: str = None
) -> dict:
    start_t = time.time()
    filename = output_filename or f"pollinations_{int(time.time())}_{random.randint(100,999)}.png"
    filepath = OUTPUT_DIR / filename

    from urllib.parse import quote
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}"
    params = {"width": width, "height": height, "model": model, "nologo": "true", "seed": random.randint(1, 999999)}

    r = requests.get(url, params=params, timeout=60)
    if r.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(r.content)
        return {
            "success": True,
            "provider": "pollinations",
            "model": model,
            "filename": filename,
            "filepath": str(filepath),
            "url": f"/api/gallery/{filename}",
            "elapsed_seconds": round(time.time() - start_t, 2),
            "size_kb": round(len(r.content)/1024, 1)
        }
    else:
        raise Exception(f"Pollinations Hatası: {r.status_code}")

# -------------------------------------------------------------
# MERKEZİ ÜRETİM FONKSİYONU (KATEGORİ VE STİL DESTEKLİ)
# -------------------------------------------------------------
def generate(
    prompt: str,
    category: str = "anime",
    style: str = None,
    provider: str = "auto",
    shape: str = "landscape",
    **kwargs
) -> dict:
    """
    Kategori ve stil zenginleştirmesi uygulayarak en uygun sağlayıcı üzerinden görsel üretir.
    """
    # 1. Kategori ve Stile Göre Prompt Zenginleştirme
    enhanced_prompt, negative_prompt, suggested_models = enhance_prompt_with_category(
        user_prompt=prompt,
        category=category,
        style=style
    )

    # 2. Şekil / Çözünürlük Hesapla
    if shape == "square":
        width, height = 768, 768
    elif shape == "portrait":
        width, height = 512, 896
    else: # landscape
        width, height = 896, 512

    # 3. Sağlayıcı Seçimi (auto ise kategoriye göre en iyi motor seçilir)
    if provider == "auto":
        if category == "anime":
            provider = "perchance"
        else:
            provider = "horde"

    provider = provider.lower()

    if provider == "perchance":
        # Perchance'ta doğrudan zenginleştirilmiş prompt kullanılır
        return asyncio.run(generate_perchance(enhanced_prompt, shape=shape, **kwargs))
    elif provider == "horde":
        return generate_horde(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            models=suggested_models,
            width=width,
            height=height,
            **kwargs
        )
    elif provider == "pollinations":
        polli_model = "flux-anime" if category == "anime" else "flux"
        return generate_pollinations(enhanced_prompt, width=width, height=height, model=polli_model, **kwargs)
    else:
        raise ValueError(f"Geçersiz sağlayıcı: {provider}")
