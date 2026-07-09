import asyncio
from playwright.async_api import async_playwright

PORTAIL_URL = "http://appels-offres.equipement.gov.ma/recherche/criteres.aspx"
DATE_DEBUT = "01/01/2025"
DATE_FIN = "01/07/2026"

# Changez ce numéro pour tester un autre AO en échec
NUMERO_A_TESTER = "1027947"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        print(f"[{NUMERO_A_TESTER}] Navigation vers le portail...")
        await page.goto(PORTAIL_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")
        async with page.expect_navigation(timeout=30000):
            await page.click("#LinkButton_Archives")

        print(f"[{NUMERO_A_TESTER}] Filtrage par numéro d'ordre...")
        await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
        await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
        await page.fill("input[name='date_parution1']", DATE_DEBUT)
        await page.fill("input[name='date_parution2']", DATE_FIN)
        await page.fill("input[name='TXTNORDRE']", NUMERO_A_TESTER)

        async with page.expect_navigation(timeout=30000):
            await page.click("input[name='btn_rechercher']")

        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        table_element = page.locator("table[id^='TabC']").first
        table_id = await table_element.get_attribute("id")

        checkbox = page.locator(f"#{table_id} tr input[type='checkbox']").first
        await checkbox.check()
        print(f"[{NUMERO_A_TESTER}] Ligne cochée.")

        await page.locator("input[value='Détails']").first.click()
        await page.wait_for_load_state("networkidle")

        await page.screenshot(path="diagnostic_details.png", full_page=True)
        print(f"[{NUMERO_A_TESTER}] Screenshot sauvegardé : diagnostic_details.png")

        print(f"\n=== TOUS LES LIENS <a> DE LA PAGE DE DÉTAILS ===\n")
        liens = await page.locator("a").all()
        for i, lien in enumerate(liens):
            texte = (await lien.inner_text()).strip()
            href = await lien.get_attribute("href")
            print(f"[{i}] Texte={texte!r} | href={href!r}")

        print(f"\n=== TOUS LES BOUTONS <input type=button/submit> DE LA PAGE ===\n")
        boutons = await page.locator("input[type='button'], input[type='submit']").all()
        for i, bouton in enumerate(boutons):
            valeur = await bouton.get_attribute("value")
            nom = await bouton.get_attribute("name")
            print(f"[{i}] value={valeur!r} | name={nom!r}")

        print(f"\nURL actuelle de la page de détails : {page.url}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())