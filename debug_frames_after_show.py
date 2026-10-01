import asyncio
import io
import sys
import json
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(headless=True)
        p = await b.new_page(viewport={"width": 1920, "height": 1080})
        await p.goto("https://perchance.org/image-generator-professional")
        await p.wait_for_timeout(3000)

        # 1. Preferences ayarla
        await p.evaluate("""() => {
            if (typeof showPreferences === 'function') showPreferences();
            const s = document.getElementById('sensitiveContentVisibilityEl');
            if (s) { s.value = 'warn'; s.dispatchEvent(new Event('change', {bubbles: true})); }
            const c = document.getElementById('ageVerificationCheckboxEl');
            if (c) { c.checked = true; c.dispatchEvent(new Event('change', {bubbles: true})); }
            const saveBtns = Array.from(document.querySelectorAll('button')).filter(b => b.innerText.toLowerCase().includes('save'));
            if (saveBtns[0]) saveBtns[0].click();
        }""")
        await p.wait_for_timeout(2000)

        # 2. Show Content tıkla
        await p.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const btn = btns.find(b => b.innerText.includes('Show Content') || b.innerText.includes('18'));
            if (btn) btn.click();
        }""")
        await p.wait_for_timeout(8000)

        # 3. Tüm frame'leri detaylı listele
        print(f"Toplam Frame Sayısı: {len(p.frames)}")
        for idx, f in enumerate(p.frames):
            print(f"\n--- Frame {idx}: {f.url[:80]} ---")
            frame_info = await f.evaluate("""() => {
                const textareas = Array.from(document.querySelectorAll('textarea')).map(t => ({
                    id: t.id,
                    placeholder: t.placeholder,
                    value: t.value.substring(0, 30)
                }));
                const buttons = Array.from(document.querySelectorAll('button, input[type="button"], a.button')).map(b => ({
                    id: b.id,
                    text: b.innerText.trim().substring(0, 30),
                    className: b.className
                }));
                const inputs = Array.from(document.querySelectorAll('input:not([type="button"])')).map(i => ({
                    id: i.id,
                    type: i.type,
                    placeholder: i.placeholder
                }));
                return { textareas, buttons, inputs };
            }""")
            print("Textareas:", json.dumps(frame_info["textareas"], ensure_ascii=False))
            print("Buttons:", json.dumps(frame_info["buttons"][:10], ensure_ascii=False))

        await p.screenshot(path="after_show_content_debug.png")
        print("\nScreenshot kaydedildi: after_show_content_debug.png")
        await b.close()

asyncio.run(main())
