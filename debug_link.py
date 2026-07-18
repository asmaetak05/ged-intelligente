import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        print('Navigating...')
        await page.goto('http://appels-offres.equipement.gov.ma/recherche/criteres.aspx', timeout=60000)
        async with page.expect_navigation(timeout=30000):
            await page.click('#LinkButton_Archives')
            
        await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
        await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
        await page.fill("input[name='date_parution1']", '01/07/2025')
        await page.fill("input[name='date_parution2']", '31/07/2026')
        
        async with page.expect_navigation(timeout=30000):
            await page.click("input[name='btn_rechercher']")
            
        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        table_id = await page.locator("table[id^='TabC']").first.get_attribute('id')
        
        rows = await page.locator(f'#{table_id} tr').all()
        # Find row with 1005675
        for row in rows:
            text = await row.inner_text()
            if '1005675' in text:
                print('Found row!')
                await row.locator("input[type='checkbox']").first.check()
                # Use networkidle instead of expect_navigation for details click
                await page.locator("input[value='Détails']").first.click()
                await page.wait_for_load_state("networkidle")
                break
                
        print("--- All Links ---")
        links = await page.locator('a').all()
        for link in links:
            html = await link.evaluate('el => el.outerHTML')
            print(f'Link: {html}')
            
        print("--- All Inputs ---")
        inputs = await page.locator('input').all()
        for inp in inputs:
            html = await inp.evaluate('el => el.outerHTML')
            if 'hidden' not in html.lower():
                print(f'Input: {html}')
                
        await browser.close()

asyncio.run(run())
