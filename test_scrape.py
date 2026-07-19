import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=InsecureDownloadWarnings'
            ]
        )
        context = await browser.new_context(ignore_https_errors=True, accept_downloads=True)
        page = await context.new_page()
        await page.goto("http://appels-offres.equipement.gov.ma/recherche/criteres.aspx", timeout=60000)
        await page.click("#LinkButton_Archives")
        await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
        await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
        await page.fill("input[name='date_parution1']", "01/07/2025")
        await page.fill("input[name='date_parution2']", "31/07/2026")
        await page.click("input[name='btn_rechercher']")
        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        
        # Click details of the first row
        await page.locator("table[id^='TabC'] tr").nth(1).locator("input[type='checkbox']").check()
        await page.locator("input[value='Détails']").first.click()
        await page.wait_for_load_state("networkidle")
        
        # Check D.A.O link
        links = await page.locator("a").all()
        for i, link in enumerate(links):
            text = await link.inner_text()
            if 'D.A.O' in text.upper() or 'D A O' in text.upper() or 'D A  O' in text.upper():
                href = await link.get_attribute("href")
                target = await link.get_attribute("target")
                onclick = await link.get_attribute("onclick")
                print(f"Link {i}: text='{text}', href='{href}', target='{target}', onclick='{onclick}'")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

