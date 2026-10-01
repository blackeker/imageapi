"""
Dedicated Perchance AI Image Generation Engine
==============================================
Yalnızca Perchance AI Image Generator motorunu kullanarak
100+ stil ve tüm çözünürlüklerde (768x512, 512x512, 512x768)
yüksek kaliteli görsel üretimi sağlar.
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
from categories import enhance_prompt_with_category, CATEGORIES

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT_DIR = Path("gallery")
OUTPUT_DIR.mkdir(exist_ok=True)

async def _launch_browser(pw):
    """
    Linux (Xvfb / Headless) veya Windows pencereli moduna göre tarayıcıyı başlatır.
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

async def generate_perchance(
    prompt: str,
    shape: str = "768x512",
    art_style: str = "Painted Anime Plus",
    output_filename: str = None,
    timeout: int = 60
) -> dict:
    """
    Perchance üzerinden görsel üretir.
    """
    start_t = time.time()
    filename = output_filename or f"perchance_{int(time.time())}_{random.randint(100,999)}.png"
    filepath = OUTPUT_DIR / filename
    downloaded_images = []

    async with async_playwright() as pw:
        browser = await _launch_browser(pw)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US"
        )
        page = await context.new_page()

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

        # 1. Sayfayı aç
        await page.goto("https://perchance.org/ai-text-to-image-generator", wait_until="domcontentloaded", timeout=45000)
        
        # 2. Frame bul
        target_frame = None
        for _ in range(30):
            for frame in page.frames:
                if "perchance.org/ai-text-to-image" in frame.url and frame.url != "https://perchance.org/ai-text-to-image-generator":
                    target_frame = frame
                    break
                try:
                    if await frame.query_selector("#generateButtonEl"):
                        target_frame = frame
                        break
                except:
                    pass
            if target_frame:
                break
            await page.wait_for_timeout(200)

        if not target_frame:
            target_frame = page.main_frame

        # 3. Art style & Shape seçimi
        try:
            await target_frame.evaluate("""({ artStyle, shape }) => {
                // 1. Art Style
                const styleSel = document.querySelector('select[data-name="artStyle"]') ||
                                 Array.from(document.querySelectorAll('select')).find(s => s.innerHTML.includes('Painted Anime'));
                if (styleSel && artStyle) {
                    const target = artStyle.trim().toLowerCase();
                    for (let opt of styleSel.options) {
                        const txt = opt.text.trim().toLowerCase();
                        const val = opt.value.trim().toLowerCase();
                        if (txt === target || val.includes(target) || txt.includes(target)) {
                            styleSel.value = opt.value;
                            styleSel.dispatchEvent(new Event('change', { bubbles: true }));
                            break;
                        }
                    }
                }

                // 2. Shape
                const shapeSel = document.querySelector('select[data-name="shape"]') ||
                                 Array.from(document.querySelectorAll('select')).find(s => s.innerHTML.includes('512x768') || s.innerHTML.includes('768x512'));
                if (shapeSel && shape) {
                    const shapeMap = {
                        'landscape': '768x512',
                        'square': '512x512',
                        'portrait': '512x768',
                        '768x512': '768x512',
                        '512x512': '512x512',
                        '512x768': '512x768'
                    };
                    const targetShape = shapeMap[shape.trim().toLowerCase()] || shape;
                    for (let opt of shapeSel.options) {
                        if (opt.value === targetShape || opt.text.includes(targetShape)) {
                            shapeSel.value = opt.value;
                            shapeSel.dispatchEvent(new Event('change', { bubbles: true }));
                            break;
                        }
                    }
                }
            }""", {"artStyle": art_style or "Painted Anime Plus", "shape": shape or "768x512"})
        except Exception as e:
            print(f"[Perchance] ArtStyle / Shape seçim logu: {e}")

        # 4. Otomatik Yaş Doğrulama / Tercihler (18+ / Sensitive Unblock)
        try:
            await target_frame.evaluate("""() => {
                try {
                    if (typeof window.showPreferences === 'function') {
                        window.showPreferences();
                    }
                    const sensitiveSel = document.querySelector('#sensitiveContentVisibilityEl');
                    if (sensitiveSel) {
                        sensitiveSel.value = 'warn';
                        sensitiveSel.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    const ageCheckbox = document.querySelector('#ageVerificationCheckboxEl');
                    if (ageCheckbox) {
                        ageCheckbox.checked = true;
                        ageCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    const closeBtns = Array.from(document.querySelectorAll('button, span, a')).filter(b => {
                        const t = (b.innerText || '').toLowerCase();
                        return t.includes('save') || t.includes('close') || t.includes('done') || t.includes('tamam');
                    });
                    if (closeBtns.length > 0) closeBtns[0].click();
                } catch(e) {}
            }""")
        except Exception as e:
            print(f"[Perchance] Tercih logu: {e}")

        # 5. Textarea bul & doldur
        try:
            await target_frame.wait_for_selector('textarea', timeout=10000)
        except:
            pass

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
            raise Exception("Prompt textarea elementi bulunamadı.")

        # How many = 1
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
        await prompt_ta.click()
        await prompt_ta.fill(prompt)
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")
        await page.wait_for_timeout(400)

        # 6. Generate Butonuna Tıkla
        gen_btn = await target_frame.query_selector("#generateButtonEl, button:has-text('generate')")
        if gen_btn:
            await gen_btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(200)
            await gen_btn.click()

        # 7. Bekle & Görseli Çek
        while time.time() - start_t < timeout:
            await page.wait_for_timeout(2500)

            # Hassas içerik uyarısı / modal varsa tıkla
            try:
                await target_frame.evaluate("""() => {
                    const warnings = Array.from(document.querySelectorAll('*')).filter(el => {
                        const t = (el.innerText || '').toLowerCase();
                        return t.includes('show image') || t.includes('view sensitive') || t.includes('i understand') || t.includes('click to view');
                    });
                    for (let w of warnings) {
                        if (w.tagName === 'BUTTON' || w.tagName === 'A' || w.tagName === 'DIV' || w.tagName === 'SPAN') {
                            w.click();
                        }
                    }
                }""")
            except:
                pass

            if downloaded_images:
                break

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
# MERKEZİ ÜRETİM FONKSİYONU (YALNIZCA PERCHANCE)
# -------------------------------------------------------------
def generate(
    prompt: str,
    category: str = "anime",
    style: str = None,
    provider: str = "perchance",
    shape: str = "768x512",
    output_filename: str = None,
    **kwargs
) -> dict:
    """
    Yalnızca Perchance motoru üzerinden görsel üretir.
    """
    enhanced_prompt, negative_prompt, _ = enhance_prompt_with_category(
        user_prompt=prompt,
        category=category,
        style=style
    )

    art_style_to_use = style or "Painted Anime Plus"

    return asyncio.run(
        generate_perchance(
            prompt=enhanced_prompt,
            shape=shape,
            art_style=art_style_to_use,
            output_filename=output_filename,
            **kwargs
        )
    )
