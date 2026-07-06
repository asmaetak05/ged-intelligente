import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        
        print("1. Navigation vers le portail...")
        await page.goto("http://appels-offres.equipement.gov.ma/recherche/criteres.aspx", timeout=60000)
        
        print("2. Passage à la section 'AO archivés'...")
        await page.click("#LinkButton_Archives")
        await page.wait_for_load_state("networkidle")
        
        print("3. Attente du tableau de résultats...")
        try:
            await page.wait_for_selector("table[id^='TabC']", timeout=15000)
            table_element = await page.locator("table[id^='TabC']").first
            table_id = await table_element.get_attribute("id")
            print(f"Tableau trouvé : {table_id}")
        except Exception as e:
            print("Tableau non trouvé. Fin du script.")
            await browser.close()
            return
            
        print("4. Clic sur la première ligne d'archive disponible...")
        # On prend la première ligne de données
        checkbox = page.locator(f"#{table_id} tr input[type='checkbox']").first
        await checkbox.check()
        print("Première checkbox cochée !")
            
        print("5. Clic sur Détails...")
        await page.locator("input[value='Détails']").first.click()
        
        print("6. Attente de la page Details.aspx...")
        await page.wait_for_load_state("networkidle")
        
        print("7. Recherche et téléchargement du ZIP...")
        links = await page.locator("a").all()
        downloaded = False
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            if href and ('zip' in href.lower() or 'rar' in href.lower() or 'dossier' in text.lower()):
                print(f"Lien de téléchargement trouvé : {text} -> {href}")
                async with page.expect_download(timeout=60000) as download_info:
                    await link.click()
                download = await download_info.value
                await download.save_as("data/raw/VRAI_AO_ARCHIVE.zip")
                print("Fichier sauvegardé : data/raw/VRAI_AO_ARCHIVE.zip")
                downloaded = True
                break
                
        if not downloaded:
            inputs = await page.locator("input[type='image']").all()
            for inp in inputs:
                src = await inp.get_attribute("src")
                if src and ('dossier' in src.lower() or 'down' in src.lower()):
                    print("Bouton image de téléchargement trouvé.")
                    async with page.expect_download(timeout=60000) as download_info:
                        await inp.click()
                    download = await download_info.value
                    await download.save_as("data/raw/VRAI_AO_ARCHIVE.zip")
                    print("Fichier sauvegardé : data/raw/VRAI_AO_ARCHIVE.zip")
                    downloaded = True
                    break
                    
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
