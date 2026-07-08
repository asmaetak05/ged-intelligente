import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        print("1. Navigation vers le portail...")
        await page.goto("http://appels-offres.equipement.gov.ma/recherche/criteres.aspx", timeout=60000)
        await page.wait_for_load_state("networkidle")

        print("2. Passage à la section 'AO archivés'...")
        async with page.expect_navigation(timeout=30000):
            await page.click("#LinkButton_Archives")

        print("3. Remplissage des filtres exacts demandés...")
        await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
        await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
        await page.fill("input[name='date_parution1']", "01/07/2025")
        await page.fill("input[name='date_parution2']", "01/07/2026")
        await page.fill("input[name='TXTNORDRE']", "65058757")

        print("3b. Clic sur le bouton Rechercher...")
        async with page.expect_navigation(timeout=30000):
            await page.click("input[name='btn_rechercher']")

        print("4. Attente du chargement du tableau...")
        table_id = None
        try:
            await page.wait_for_selector("table[id^='TabC']", timeout=15000)
            table_element = page.locator("table[id^='TabC']").first
            table_id = await table_element.get_attribute("id")
            print(f"Tableau trouvé : {table_id}")
        except Exception:
            print("Tableau non trouvé avec le sélecteur TabC. Diagnostic en cours...")
            all_tables = await page.locator("table").all()
            print(f"Nombre total de tableaux sur la page : {len(all_tables)}")
            for i, t in enumerate(all_tables):
                tid = await t.get_attribute("id")
                tclass = await t.get_attribute("class")
                text_preview = (await t.inner_text())[:80].replace("\n", " ")
                print(f"  Tableau {i} -> id='{tid}' class='{tclass}' apercu='{text_preview}'")
            await page.screenshot(path="data/raw/screenshot_exact.png", full_page=True)
            await browser.close()
            return

        print("5. Coche de la case de la ligne correspondante...")
        try:
            text_content = await page.locator(f"#{table_id}").inner_text()
            print("Contenu du tableau trouvé :")
            print(text_content[:200])

            checkbox = page.locator(f"#{table_id} tr input[type='checkbox']").first
            await checkbox.check()
            print("Checkbox cochée.")
        except Exception as e:
            print("Erreur lors de la coche de la case :", e)
            await browser.close()
            return

        print("6. Clic sur le bouton Détails...")
        await page.locator("input[value='Détails']").first.click()

        print("7. Attente de la page Details.aspx...")
        await page.wait_for_load_state("networkidle")

        print("8. Clic sur le lien 'D A O' et téléchargement...")
        try:
            links = await page.locator("a").all()
            dao_link = None
            for link in links:
                text = await link.inner_text()
                if 'D A O' in text.upper() or 'D.A.O' in text.upper() or 'D A  O' in text.upper():
                    dao_link = link
                    print(f"Lien D A O trouvé : '{text}'")
                    break

            if dao_link:
                async with page.expect_download(timeout=60000) as download_info:
                    await dao_link.click()
                download = await download_info.value
                await download.save_as("data/raw/AO_65058757_REEL.zip")
                print("Le vrai fichier ZIP a été sauvegardé : data/raw/AO_65058757_REEL.zip")
            else:
                print("Lien 'D A O' introuvable sur la page. Voici tous les liens :")
                for link in links:
                    print(await link.inner_text())
                await page.screenshot(path="data/raw/screenshot_details_dao.png", full_page=True)
        except Exception as e:
            print("Erreur lors du téléchargement :", e)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())