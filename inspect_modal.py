import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://perchance.org/image-generator-professional")
        await page.wait_for_timeout(3000)
        
        info = await page.evaluate("""() => {
            const warningEl = document.querySelector('.content-warning, #content-warning, [id*="warning"], [class*="warning"]');
            return {
                warningHtml: document.body.innerHTML.substring(0, 2000),
                localStorage: JSON.stringify(localStorage),
                links: Array.from(document.querySelectorAll('a, button')).map(el => ({text: el.innerText, href: el.href, id: el.id, class: el.className}))
            };
        }""")
        print("Links & Buttons:", info["links"])
        
        # Also check localStorage setting for mature/nsfw/warnings
        await browser.close()

asyncio.run(check())
