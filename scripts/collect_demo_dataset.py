import asyncio
import glob
import os
import re
from playwright.async_api import async_playwright

PORTAIL_URL = "http://appels-offres.equipement.gov.ma/recherche/criteres.aspx"

# Note from screenshot: "date parution a filtrer entre 07/2025 et 07/2026"
DATE_DEBUT = "01/01/2025"
DATE_FIN = "31/12/2025"

# Try up to 50 AOs but we will stop after the first success
LIMITE_AO = 50

async def aller_vers_archives(page):
    """Note 1 (Screenshot 1) : choisir AO archivés."""
    await page.goto(PORTAIL_URL, timeout=60000)
    await page.wait_for_load_state("networkidle")
    async with page.expect_navigation(timeout=30000):
        await page.click("#LinkButton_Archives")


async def decouvrir_numeros_ordre(context):
    page = await context.new_page()
    numeros = []

    print("[Découverte] Navigation vers le portail...")
    await aller_vers_archives(page)

    print(f"[Découverte] Filtrage par dates (Note 2) {DATE_DEBUT} -> {DATE_FIN}...")
    await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
    await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
    await page.fill("input[name='date_parution1']", DATE_DEBUT)
    await page.fill("input[name='date_parution2']", DATE_FIN)

    async with page.expect_navigation(timeout=30000):
        await page.click("input[name='btn_rechercher']")

    print("[Découverte] Attente du tableau de résultats...")
    try:
        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        table_element = page.locator("table[id^='TabC']").first
        table_id = await table_element.get_attribute("id")
    except Exception:
        print("[Découverte] Aucun tableau trouvé pour cette plage de dates.")
        await page.close()
        return numeros

    async def extraire_numeros_du_tableau(table_id_actuel):
        numeros_page = []
        rows = await page.locator(f"#{table_id_actuel} tr").all()
        for row in rows:
            cells = await row.locator("td").all()
            if len(cells) < 3:
                continue
            texte_ligne = await row.inner_text()
            match = re.search(r"\b(\d{6,10})\b", texte_ligne)
            if match:
                numeros_page.append(match.group(1))
        return numeros_page

    page_num = 1
    while len(numeros) < LIMITE_AO:
        print(f"[Découverte] Extraction de la page {page_num}...")
        numeros_page = await extraire_numeros_du_tableau(table_id)
        
        for num in numeros_page:
            if num not in numeros:
                numeros.append(num)
                
        if len(numeros) >= LIMITE_AO or len(numeros_page) == 0:
            break
            
        page_num += 1
        print(f"[Découverte] Navigation vers la page {page_num}...")
        try:
            # Chercher le lien correspondant au numéro de la page suivante (ex: "2")
            next_page_link = page.get_by_role("link", name=str(page_num), exact=True).first
            
            if await next_page_link.count() > 0:
                await next_page_link.click()
                await page.wait_for_timeout(4000) # Attendre le PostBack AJAX
                await page.wait_for_selector("table[id^='TabC']", timeout=15000)
                table_element = page.locator("table[id^='TabC']").first
                table_id = await table_element.get_attribute("id")
            else:
                print(f"[Découverte] Lien pour la page {page_num} introuvable. Fin de pagination.")
                break
        except Exception as e:
            print(f"[Découverte] [WARN] Échec navigation vers page {page_num}: {e}")
            break

    print(f"[Découverte] {len(numeros)} numéro(s) d'ordre trouvé(s) au total.")
    await page.close()
    return numeros[:LIMITE_AO]


async def telecharger_un_ao(context, numero_ordre):
    page = await context.new_page()
    try:
        print(f"\n[{numero_ordre}] Navigation vers le portail...")
        await aller_vers_archives(page)

        print(f"[{numero_ordre}] Filtrage exact par numéro d'ordre...")
        await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
        await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
        await page.fill("input[name='date_parution1']", DATE_DEBUT)
        await page.fill("input[name='date_parution2']", DATE_FIN)
        await page.fill("input[name='TXTNORDRE']", numero_ordre)

        async with page.expect_navigation(timeout=30000):
            await page.click("input[name='btn_rechercher']")

        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        table_element = page.locator("table[id^='TabC']").first
        table_id = await table_element.get_attribute("id")

        rows = await page.locator(f"#{table_id} tr").all()
        ligne_cible = None
        for row in rows:
            cells = await row.locator("td").all()
            if len(cells) < 3:
                continue
            texte_ligne = await row.inner_text()
            if re.search(rf"\b{re.escape(numero_ordre)}\b", texte_ligne):
                ligne_cible = row
                break

        if ligne_cible is None:
            return False

        # Screenshot 2: "cocher une ligne et cliquer sur details"
        checkbox = ligne_cible.locator("input[type='checkbox']").first
        await checkbox.check()
        print(f"[{numero_ordre}] Ligne cochée.")

        await page.locator("input[value='Détails']").first.click()
        await page.wait_for_load_state("networkidle")

        # Screenshot 3: "ici est mentionné avec D.A.O le telechargement du zip"
        links = await page.locator("a").all()
        dao_link = None
        for link in links:
            text = await link.inner_text()
            if 'D.A.O' in text.upper() or 'D A O' in text.upper() or 'D A  O' in text.upper():
                dao_link = link
                break

        if not dao_link:
            print(f"[{numero_ordre}] [WARN] Lien D.A.O introuvable.")
            return False

        url_document = await dao_link.get_attribute("href")
        print(f"[{numero_ordre}] URL D.A.O trouvee: {url_document}")
        
        # S'assurer que c'est une URL absolue
        if url_document and url_document.startswith("/"):
            from urllib.parse import urljoin
            url_document = urljoin(page.url, url_document)
            print(f"[{numero_ordre}] URL absolue: {url_document}")

        if not url_document or numero_ordre not in url_document:
            print(f"[{numero_ordre}] [WARN] Le numero d'ordre n'est pas dans l'URL, ou URL vide.")
            return False

        extension = ".pdf" if url_document.lower().endswith(".pdf") else ".zip"
        os.makedirs("data/raw", exist_ok=True)
        chemin_fichier = f"data/raw/AO_{numero_ordre}{extension}"

        # Remplacer le clic navigateur qui pose problème par une requête directe
        try:
            print(f"[{numero_ordre}] Tentative de téléchargement direct via requête HTTP...")
            headers = {
                "Referer": page.url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            reponse = await context.request.get(url_document, headers=headers, timeout=60000)
            if reponse.ok:
                contenu = await reponse.body()
                with open(chemin_fichier, "wb") as f:
                    f.write(contenu)
                print(f"[{numero_ordre}] [OK] Téléchargé avec succès via requête HTTP : {chemin_fichier}")
                return True
            else:
                print(f"[{numero_ordre}] [WARN] Échec : Réponse HTTP {reponse.status} pour {url_document}")
                return False
        except Exception as e_fetch:
            print(f"[{numero_ordre}] [WARN] Échec téléchargement direct : {e_fetch}")
            return False

    except Exception as e:
        print(f"[{numero_ordre}] [ERROR] Erreur globale : {e}")
        return False
    finally:
        await page.close()


def numeros_deja_telecharges():
    deja_faits = set()
    for chemin in glob.glob("data/raw/AO_*.*"):
        nom_fichier = os.path.basename(chemin)
        sans_prefixe = nom_fichier[len("AO_"):]
        numero = sans_prefixe.rsplit(".", 1)[0]
        deja_faits.add(numero)
    return deja_faits


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=InsecureDownloadWarnings',
                '--no-sandbox'
            ]
        )
        # On ajoute un User-Agent classique pour éviter le blocage 404
        context = await browser.new_context(
            ignore_https_errors=True,
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )

        numeros = await decouvrir_numeros_ordre(context)

        if not numeros:
            print("Aucun appel d'offre trouvé.")
            await browser.close()
            return

        deja_faits = numeros_deja_telecharges()
        numeros_a_faire = [n for n in numeros if n not in deja_faits]
        print(f"\n{len(numeros) - len(numeros_a_faire)} AO déjà présents. {len(numeros_a_faire)} restants à tester.")

        reussis = 0
        for numero in numeros_a_faire:
            if await telecharger_un_ao(context, numero):
                reussis += 1
            await asyncio.sleep(2)

        print(f"\n=== Bilan : {reussis} téléchargé(s) ===")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

