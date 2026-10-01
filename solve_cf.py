import asyncio
import io
import sys
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        print("Sayfa açılıyor...")
        await page.goto("https://perchance.org/image-generator-professional")
        await page.wait_for_timeout(3000)

        # Cloudflare Turnstile Checkbox tıklama
        print("Cloudflare Turnstile aranıyor...")
        for frame in page.frames:
            try:
                cb = await frame.query_selector('input[type="checkbox"], .ctp-checkbox-label, #challenge-stage')
                if cb:
                    print("Turnstile checkbox bulundu, tıklanıyor...")
                    await cb.click()
                    break
            except:
                pass

        # Genel koordinat tıklaması (Turnstile kutusu ortalama sol üstte)
        try:
            # Checkbox genelde x: 168, y: 420 civarında
            await page.mouse.click(168, 420)
            print("Turnstile koordinatına tıklandı.")
        except Exception as e:
            print("Koordinat tıklama hatası:", e)

        print("Bekleniyor (10s)...")
        await page.wait_for_timeout(10000)

        await page.screenshot(path="after_turnstile.png")
        print("Ekran görüntüsü alındı: after_turnstile.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
