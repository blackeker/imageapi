import asyncio
import io
import sys
import json
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        page = await context.new_page()

        print("1. image-generator-professional açılıyor...")
        await page.goto("https://perchance.org/image-generator-professional")
        await page.wait_for_timeout(3000)

        # Tüm frame'lerde "change preferences" ara ve koordinatını bul
        print("2. 'change preferences' aranıyor...")
        target_info = None
        for i, frame in enumerate(page.frames):
            info = await frame.evaluate("""() => {
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    if (node.nodeValue && node.nodeValue.toLowerCase().includes('change preferences')) {
                        const el = node.parentElement;
                        const rect = el.getBoundingClientRect();
                        return {
                            text: node.nodeValue,
                            tag: el.tagName,
                            html: el.outerHTML,
                            parentHtml: el.parentElement.outerHTML,
                            x: rect.x + rect.width / 2,
                            y: rect.y + rect.height / 2
                        };
                    }
                }
                return null;
            }""")
            if info:
                print(f"   Frame {i}'de bulundu: {info}")
                target_info = (frame, info)
                break

        if target_info:
            frame, info = target_info
            print(f"3. 'change preferences' öğesine tıklanıyor (x={info['x']}, y={info['y']})...")
            # Tıkla
            await page.mouse.click(info['x'], info['y'])
            await page.wait_for_timeout(2000)
        else:
            print("   'change preferences' bulunamadı, selector ile deneniyor...")
            el = await page.query_selector('text="change preferences"')
            if el:
                await el.click()
                await page.wait_for_timeout(2000)

        # Screenshot al
        await page.screenshot(path="preferences_modal_opened.png")
        print("4. Tercihler modalı ekran görüntüsü alındı: preferences_modal_opened.png")

        # Açılan ekrandaki tüm öğeleri analiz et
        modal_content = await page.evaluate("""() => {
            const data = {
                title: document.title,
                visibleText: document.body.innerText,
                checkboxes: Array.from(document.querySelectorAll('input[type="checkbox"]')).map(cb => ({
                    id: cb.id,
                    name: cb.name,
                    checked: cb.checked,
                    label: cb.parentElement ? cb.parentElement.innerText.trim() : ''
                })),
                radios: Array.from(document.querySelectorAll('input[type="radio"]')).map(r => ({
                    id: r.id,
                    name: r.name,
                    value: r.value,
                    checked: r.checked,
                    label: r.parentElement ? r.parentElement.innerText.trim() : ''
                })),
                buttons: Array.from(document.querySelectorAll('button, input[type="button"], a.button')).map(b => ({
                    id: b.id,
                    text: b.innerText.trim(),
                    tag: b.tagName
                }))
            };
            return data;
        }""")

        print("\n--- AÇILAN EKRAN İÇERİĞİ VE TERCİHLER ---")
        print("Metin Özeti:\n", modal_content['visibleText'][:1000])
        print("\nCheckbox'lar:", json.dumps(modal_content['checkboxes'], indent=2, ensure_ascii=False))
        print("\nRadio'lar:", json.dumps(modal_content['radios'], indent=2, ensure_ascii=False))
        print("\nButonlar:", json.dumps(modal_content['buttons'], indent=2, ensure_ascii=False))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
