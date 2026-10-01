"""
Perchance Çoklu Anime Jeneratör API'si
======================================
Desteklenen Perchance Anime Jeneratörleri:
1. 'ai-text-to-image-generator' (Stil: Anime / Painted Anime)
2. 'ai-anime-generator'
3. 'anime-character-generator'
4. 'image-generator-professional'

Kullanım:
  python perchance_anime_api.py --generator ai-anime-generator --prompt "..."
  python perchance_anime_api.py --server
"""

import sys
import io
import time
import json
import base64
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

AVAILABLE_GENERATORS = {
    "text-to-image": "https://perchance.org/ai-text-to-image-generator",
    "anime": "https://perchance.org/ai-anime-generator",
    "anime-character": "https://perchance.org/anime-character-generator",
    "professional": "https://perchance.org/image-generator-professional"
}

async def async_generate_anime(
    prompt: str,
    generator_name: str = "text-to-image",
    art_style: str = "Painted Anime", # 'Painted Anime', 'Anime', 'Anime Screen'
    output_path: str = "anime_perchance_result.png",
    timeout: int = 90
) -> str:
    """
    Seçilen Perchance anime jeneratörü üzerinden görsel üretir.
    """
    target_url = AVAILABLE_GENERATORS.get(generator_name, AVAILABLE_GENERATORS["text-to-image"])
    downloaded_images = []

    print("=" * 60)
    print(f"🎨 PERCHANCE ANIME GENERATOR: {generator_name.upper()}")
    print(f"URL: {target_url}")
    print("=" * 60)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--start-maximized"
            ],
            slow_mo=50
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            no_viewport=True
        )

        page = await context.new_page()

        async def on_response(response):
            url = response.url
            if ("downloadTemporary" in url or "image" in response.headers.get("content-type", "")) and response.status == 200:
                if "perchance.org" in url or "image-generation" in url:
                    try:
                        body = await response.body()
                        if len(body) > 10000:
                            downloaded_images.append(body)
                    except:
                        pass

        page.on("response", on_response)

        print("[1] Sayfa yükleniyor...")
        await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(6000)

        # 18+ veya Content Warning varsa tıkla
        try:
            await page.evaluate("""() => {
                if (typeof showPreferences === 'function') showPreferences();
                const s = document.getElementById('sensitiveContentVisibilityEl');
                if (s) { s.value = 'warn'; s.dispatchEvent(new Event('change', {bubbles: true})); }
                const c = document.getElementById('ageVerificationCheckboxEl');
                if (c) { c.checked = true; c.dispatchEvent(new Event('change', {bubbles: true})); }
                const saveBtns = Array.from(document.querySelectorAll('button')).filter(b => (b.innerText || '').toLowerCase().includes('save'));
                if (saveBtns[0]) saveBtns[0].click();
                
                // Show content tıkla
                const btns = Array.from(document.querySelectorAll('button, a'));
                const show = btns.find(b => (b.innerText || '').includes('Show Content') || (b.innerText || '').includes('18'));
                if (show) show.click();
            }""")
            await page.wait_for_timeout(2000)
        except:
            pass

        # Generator iframe'ini bul
        print("[2] Generator formu taranıyor...")
        target_frame = None
        for frame in page.frames:
            if "perchance.org" in frame.url and frame.url != target_url:
                tas = await frame.query_selector_all("textarea")
                if len(tas) > 0:
                    target_frame = frame
                    break

        if not target_frame:
            for frame in page.frames:
                tas = await frame.query_selector_all("textarea")
                if len(tas) > 0:
                    target_frame = frame
                    break

        if not target_frame:
            target_frame = page.main_frame

        # Art Style seçeneğini ayarla (Painted Anime / Anime)
        try:
            selects = await target_frame.query_selector_all("select")
            for sel in selects:
                options = await sel.query_selector_all("option")
                for opt in options:
                    opt_text = (await opt.text_content()) or ""
                    if art_style.lower() in opt_text.lower():
                        val = await opt.get_attribute("value")
                        await sel.select_option(value=val)
                        print(f"    Stil seçildi: {opt_text.strip()}")
                        break
        except:
            pass

        # Prompt gir
        print(f"[3] Prompt giriliyor ({len(prompt)} karakter)...")
        textareas = await target_frame.query_selector_all("textarea")
        prompt_ta = textareas[-1] if len(textareas) > 1 else textareas[0]

        await prompt_ta.click()
        await prompt_ta.fill("")
        await prompt_ta.fill(prompt)
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
        await page.wait_for_timeout(1000)

        # Generate tıkla
        print("[4] Generate butonuna tıklanıyor...")
        gen_btn = await target_frame.query_selector("#generateButtonEl, button:has-text('generate'), button:has-text('Generate'), button:has-text('✨')")
        if gen_btn:
            await gen_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)
            await gen_btn.click()
        else:
            await target_frame.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button, input[type="button"]'));
                const b = btns.find(btn => (btn.innerText || btn.value || '').toLowerCase().includes('generate'));
                if (b) b.click();
            }""")

        # Görseli bekle
        print(f"[5] Görsel üretimi bekleniyor (maks {timeout}s)...")
        start_t = time.time()
        while time.time() - start_t < timeout:
            await page.wait_for_timeout(4000)
            if downloaded_images:
                break

            # Canvas kontrolü
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
            print(f"\n🎉 GÖRSEL BAŞARIYLA KAYDEDİLDİ: {output_path} ({len(downloaded_images[-1])/1024:.1f} KB)")
            return output_path
        else:
            raise TimeoutError("Görsel üretilemedi veya zaman aşımı oluştu.")

def generate_anime(prompt: str, generator: str = "text-to-image", art_style: str = "Painted Anime", output_path: str = "anime_result.png") -> str:
    return asyncio.run(async_generate_anime(prompt, generator_name=generator, art_style=art_style, output_path=output_path))

def start_server(port: int = 5000):
    from flask import Flask, request, jsonify, send_file
    app = Flask(__name__)

    @app.route("/api/perchance/anime", methods=["POST"])
    def api_generate():
        data = request.get_json() or {}
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "prompt parametresi zorunludur"}), 400

        gen = data.get("generator", "text-to-image")
        style = data.get("style", "Painted Anime")
        out_fn = f"temp_anime_{int(time.time())}.png"

        try:
            fn = generate_anime(prompt, generator=gen, art_style=style, output_path=out_fn)
            return send_file(fn, mimetype="image/png")
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/generators", methods=["GET"])
    def list_generators():
        return jsonify({
            "available_generators": list(AVAILABLE_GENERATORS.keys()),
            "styles": ["Painted Anime", "Anime", "Anime Screen", "Fantasy Landscape", "Cyberpunk"]
        })

    print(f"🚀 Perchance Anime API Sunucusu: http://localhost:{port}")
    print("   Endpoint: POST http://localhost:5000/api/perchance/anime")
    print('   Body: {"prompt": "...", "generator": "text-to-image", "style": "Painted Anime"}')
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if "--server" in sys.argv:
        start_server()
    else:
        sample = '''16:9 dynamic anime desktop wallpaper, high-energy esports aesthetic. A confident anime rogue with spiky neon-lime hair highlights, piercing amber eyes, and a low-profile cyber visor pushed up. She wears an open dark charcoal techwear parka featuring bold "KEKE" graphic print on the inner lining, tactical belts, and fingerless gloves. She is poised in a low combat-ready stance, a crackling green plasma blade held reverse-grip, leaving sharp slash trails of light across the frame. The background is pitch-black with layered dynamic elements: sharp diagonal hazard cuts, subtle grunge spray-paint splatters, floating digital embers, and faint geometric grid lines receding into darkness. Crisp clean lines, dramatic cinematic contrast, 4k wallpaper quality.'''
        generate_anime(sample, generator="text-to-image", art_style="Painted Anime", output_path="perchance_anime_result.png")
