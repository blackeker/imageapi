import asyncio
import time
from playwright.async_api import async_playwright

async def run_gen():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--start-maximized',
                '--window-size=1920,1080'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            locale='en-US'
        )
        page = await context.new_page()

        downloaded = []
        async def on_resp(r):
            if 'downloadTemporary' in r.url and r.status == 200:
                try:
                    d = await r.body()
                    if len(d) > 10000:
                        downloaded.append(d)
                        print('CAUGHT IMAGE VIA NETWORK:', len(d), 'bytes')
                except:
                    pass
        page.on('response', on_resp)

        print('1. Navigating to Perchance...')
        await page.goto('https://perchance.org/ai-text-to-image-generator', wait_until='domcontentloaded')
        await page.wait_for_timeout(6000)

        # Target frame bul
        target_frame = None
        for f in page.frames:
            if f != page.main_frame and 'perchance.org' in f.url:
                try:
                    btn = await f.query_selector('#generateButtonEl')
                    if btn:
                        target_frame = f
                        print('Found target frame with #generateButtonEl:', f.url)
                        break
                except:
                    pass

        if not target_frame:
            for f in page.frames:
                if f != page.main_frame:
                    target_frame = f
                    break

        print('Target frame selected:', target_frame.url)

        # Textarea bul
        tas = await target_frame.query_selector_all('textarea')
        prompt_ta = None
        for ta in tas:
            ph = (await ta.get_attribute('placeholder')) or ''
            if 'store' not in ph.lower() and len(ph) > 0:
                prompt_ta = ta
                break
        if not prompt_ta and tas:
            prompt_ta = tas[-1] if len(tas) > 1 else tas[0]

        print('Filling prompt...')
        await prompt_ta.click()
        await prompt_ta.fill('cute anime girl with pink hair and amber eyes, masterpiece 4k')
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('input', {bubbles: true}))")
        await prompt_ta.evaluate("el => el.dispatchEvent(new Event('change', {bubbles: true}))")

        print('Clicking Generate...')
        gen_btn = await target_frame.query_selector("#generateButtonEl, button:has-text('generate')")
        await gen_btn.click()

        print('Waiting for image...')
        start_t = time.time()
        while time.time() - start_t < 60:
            await page.wait_for_timeout(3000)
            if downloaded:
                print('SUCCESS! Image downloaded in', round(time.time() - start_t, 2), 's')
                with open('/tmp/perchance_vds_result.png', 'wb') as f:
                    f.write(downloaded[-1])
                break
            try:
                img_src = await target_frame.evaluate("""() => {
                    const imgs = document.querySelectorAll('img');
                    for (const img of imgs) {
                        if (img.naturalWidth > 200 && img.naturalHeight > 200) {
                            return img.src;
                        }
                    }
                    return null;
                }""")
                if img_src:
                    print('Image found in DOM:', img_src[:80])
                    break
            except:
                pass
            print(f'Waiting... ({round(time.time() - start_t, 1)}s)')

        await page.screenshot(path='/tmp/vds_screenshot_after_gen.png')
        await browser.close()

asyncio.run(run_gen())
