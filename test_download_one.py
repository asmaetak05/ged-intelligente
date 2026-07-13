import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=InsecureDownloadWarnings',
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        context = await browser.new_context(
            ignore_https_errors=True, 
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        
        # On va tester les 10 premiers résultats
        for attempt in range(1, 11):
            print(f"\n--- Tentative sur la ligne {attempt} ---")
            await page.goto("http://appels-offres.equipement.gov.ma/recherche/criteres.aspx", timeout=60000)
            await page.click("#LinkButton_Archives")
            await page.wait_for_load_state("networkidle")
            
            # Filtre
            await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
            await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
            await page.fill("input[name='date_parution1']", "01/07/2025")
            await page.fill("input[name='date_parution2']", "31/07/2026")
            
            async with page.expect_navigation():
                await page.click("input[name='btn_rechercher']")
                
            await page.wait_for_selector("table[id^='TabC']", timeout=15000)
            
            rows = await page.locator("table[id^='TabC'] tr").all()
            if attempt >= len(rows):
                print("Plus de lignes à tester.")
                break
                
            row = rows[attempt]
            text = await row.inner_text()
            print(f"Objet : {text[:80].replace(chr(10), ' ')}...")
            
            await row.locator("input[type='checkbox']").check()
            await page.locator("input[value='Détails']").first.click()
            await page.wait_for_load_state("networkidle")
            
            links = await page.locator("a").all()
            dao_link = None
            for link in links:
                t = await link.inner_text()
                if 'D.A.O' in t.upper() or 'D A O' in t.upper() or 'D A  O' in t.upper():
                    dao_link = link
                    break
                    
            if dao_link:
                href = await dao_link.get_attribute("href")
                print(f"Lien D.A.O trouvé : {href}")
                
                os.makedirs("data/raw", exist_ok=True)
                # Extraire l'ID du lien pour le nom de fichier
                filename = href.split('/')[-1] if href else f"AO_TEST_{attempt}.zip"
                chemin = f"data/raw/{filename}"
                
                await dao_link.evaluate("el => el.removeAttribute('target')")
                
                try:
                    # Timeout très court (5 secondes). Si c'est un vrai fichier, le navigateur déclenche le téléchargement très vite.
                    # Si c'est un 404, ça navigue vers une page d'erreur et ne déclenche pas le téléchargement.
                    async with page.expect_download(timeout=10000) as download_info:
                        await dao_link.click(force=True)
                    download = await download_info.value
                    await download.save_as(chemin)
                    print(f"[SUCCES] Fichier valide téléchargé dans {chemin} !!")
                    break # On a réussi, on s'arrête !
                except Exception as e:
                    print(f"[ECHEC] Le fichier est introuvable (Erreur 404 ou blocage) : {e}")
            else:
                print("Aucun lien D.A.O.")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
