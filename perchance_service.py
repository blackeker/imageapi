"""
Perchance AI Image Generator - Nihai API Modülü ve Sunucusu
============================================================
Bu modül, Perchance AI Image Generator'ı programatik olarak çalıştırıp
istediğiniz prompt ile yüksek kaliteli anime/sanat görselleri üretir.

Kullanım:
1. Python Modülü Olarak:
   from perchance_service import generate_perchance_image
   img_path = generate_perchance_image("your prompt here", shape="landscape")

2. Komut Satırından:
   python perchance_service.py --prompt "anime rogue with neon lime hair, cyber visor"

3. API Sunucusu Olarak (Port 5000):
   python perchance_service.py --server
"""

import os
import sys
import io
import time
import json
import base64
import random
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TARGET_URL = "https://perchance.org/ai-text-to-image-generator"

async def _launch_browser(pw):
    """
    Linux / Sunucu veya Masaüstü ortamına göre tarayıcıyı en uygun modda başlatır.
    XServer / DISPLAY yoksa otomatik headless moduna geçer.
    """
    is_server_env = os.environ.get("HEADLESS", "").lower() in ("true", "1") or (
        sys.platform != "win32" and not os.environ.get("DISPLAY")
    )

    base_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu"
    ]

    if not is_server_env:
        try:
            return await pw.chromium.launch(
                headless=False,
                args=base_args + ["--start-maximized"],
                slow_mo=50
            )
        except Exception as e:
            print(f"[SmartLauncher] Headed mod başlatılamadı ({e}), Headless moda geçiliyor...")

    return await pw.chromium.launch(
        headless=True,
        args=base_args
    )

async def async_generate_perchance_image(
    prompt: str,
    shape: str = "landscape", # 'portrait', 'square', 'landscape'
    art_style: str = "Painted Anime",
    output_path: str = "perchance_output.png",
    timeout: int = 90
) -> str:
    """
    Perchance üzerinden görsel üretip belirtilen yola kaydeder.
    """
    downloaded_images = []

    async with async_playwright() as pw:
        browser = await _launch_browser(pw)

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )

        page = await context.new_page()

        # Network dinleyicisi
        async def on_response(response):
            url = response.url
            if "downloadTemporary" in url and response.status == 200:
                try:
                    data = await response.body()
                    if len(data) > 10000:
                        downloaded_images.append(data)
                except:
                    pass

        page.on("response", on_response)

        print(">> Perchance sayfası açılıyor...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(8000)

        # Generator iframe'ini bul
        target_frame = None
        for frame in page.frames:
            if "perchance.org/ai-text-to-image" in frame.url and frame.url != TARGET_URL:
                target_frame = frame
                break

        if not target_frame:
            for frame in page.frames:
                try:
                    btn = await frame.query_selector("#generateButtonEl")
                    if btn:
                        target_frame = frame
                        break
                except:
                    pass

        if not target_frame:
            target_frame = page.main_frame

        # Textarea'yı bul
        textareas = await target_frame.query_selector_all('textarea')
        prompt_ta = None
        for ta in textareas:
            ph = (await ta.get_attribute("placeholder")) or ""
            if "store" not in ph.lower() and len(ph) > 0:
                prompt_ta = ta
                break

        if not prompt_ta and textareas:
            prompt_ta = textareas[-1] if len(textareas) > 1 else textareas[0]

        if not prompt_ta:
            await browser.close()
            raise Exception("Prompt textarea bulunamadı.")

        # How many = 1 yap (hızlı üretim için)
        try:
            selects = await target_frame.query_selector_all('select')
            for sel in selects:
                opts = [await o.text_content() for o in await sel.query_selector_all('option')]
                if "1" in opts and "2" in opts:
                    await sel.select_option(value="1")
                    break
        except:
            pass

        # Prompt yaz
        print(f">> Prompt giriliyor ({len(prompt)} karakter)...")
        await prompt_ta.click()
        await prompt_ta.fill("")
        await prompt_ta.fill(prompt)
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
        await page.wait_for_timeout(1000)

        # Generate butonuna tıkla
        print(">> Generate butonuna tıklanıyor...")
        gen_btn = await target_frame.query_selector("#generateButtonEl, button:has-text('generate')")
        if gen_btn:
            await gen_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)
            await gen_btn.click()
        else:
            await target_frame.evaluate("() => { const b = document.querySelector('#generateButtonEl'); if(b) b.click(); }")

        # Görseli bekle
        print(f">> Görsel üretimi bekleniyor (maks {timeout}s)...")
        start_t = time.time()
        while time.time() - start_t < timeout:
            await page.wait_for_timeout(4000)
            if downloaded_images:
                break

            # DOM Canvas/IMG kontrolü
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
            except:
                pass

        await browser.close()

        if downloaded_images:
            with open(output_path, "wb") as f:
                f.write(downloaded_images[-1])
            print(f"🎉 Görsel başarıyla kaydedildi: {output_path} ({len(downloaded_images[-1])/1024:.1f} KB)")
            return output_path
        else:
            raise TimeoutError("Görsel üretimi zaman aşımına uğradı.")

def generate_perchance_image(prompt: str, shape: str = "landscape", output_path: str = "perchance_output.png") -> str:
    return asyncio.run(async_generate_perchance_image(prompt, shape=shape, output_path=output_path))

def start_api_server(port: int = 5000):
    from flask import Flask, request, jsonify, send_file
    app = Flask(__name__)

    @app.route("/api/perchance/generate", methods=["POST"])
    def api_gen():
        data = request.get_json() or {}
        p = data.get("prompt")
        if not p:
            return jsonify({"error": "prompt alanı zorunludur"}), 400
        
        shape = data.get("shape", "landscape")
        out_fn = f"temp_{int(time.time())}.png"
        try:
            fn = generate_perchance_image(p, shape=shape, output_path=out_fn)
            return send_file(fn, mimetype="image/png")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "Perchance AI Generator API"})

    print(f"🚀 Perchance API Sunucusu başlatıldı: http://localhost:{port}")
    print("   Endpoint: POST http://localhost:5000/api/perchance/generate")
    print('   Body: {"prompt": "...", "shape": "landscape"}')
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if "--server" in sys.argv:
        start_api_server()
    else:
        sample_prompt = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''
        generate_perchance_image(sample_prompt, output_path="perchance_result.png")
