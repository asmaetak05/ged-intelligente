import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        await page.goto("http://appels-offres.equipement.gov.ma/recherche/criteres.aspx", timeout=60000)
        await page.click("#LinkButton_Archives")
        await page.wait_for_load_state("networkidle")
        
        print("INPUTS:")
        inputs = await page.locator("input").all()
        for i in inputs:
            name = await i.get_attribute("name")
            id_ = await i.get_attribute("id")
            type_ = await i.get_attribute("type")
            print(f"Input name={name} id={id_} type={type_}")
            
        print("\nSELECTS:")
        selects = await page.locator("select").all()
        for s in selects:
            name = await s.get_attribute("name")
            id_ = await s.get_attribute("id")
            print(f"Select name={name} id={id_}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
