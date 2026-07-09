import asyncio
import glob
import os
import re
from playwright.async_api import async_playwright

PORTAIL_URL = "http://appels-offres.equipement.gov.ma/recherche/criteres.aspx"

# Plage de dates à explorer pour la découverte des AO (à ajuster selon vos besoins)
DATE_DEBUT = "01/04/2025"
DATE_FIN = "01/07/2026"

# Nombre maximum d'AO à traiter dans cette exécution (le site plafonne à 50 par page de résultats)
LIMITE_AO = 50


async def aller_vers_archives(page):
    """Navigue vers le portail et bascule sur la section AO archivés."""
    await page.goto(PORTAIL_URL, timeout=60000)
    await page.wait_for_load_state("networkidle")
    async with page.expect_navigation(timeout=30000):
        await page.click("#LinkButton_Archives")


async def decouvrir_numeros_ordre(context):
    """
    PHASE A : recherche large par dates (sans filtre de numéro),
    puis extrait tous les numéros d'ordre trouvés dans le tableau.
    """
    page = await context.new_page()
    numeros = []

    print("[Découverte] Navigation vers le portail...")
    await aller_vers_archives(page)

    print(f"[Découverte] Filtrage par dates {DATE_DEBUT} -> {DATE_FIN}...")
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
        print(f"[Découverte] Tableau trouvé : {table_id}")
    except Exception:
        print("[Découverte] Aucun tableau trouvé pour cette plage de dates.")
        await page.close()
        return numeros

    # Affiche le total réel annoncé par le site, si un texte de ce type existe sur la page
    # (utile pour savoir si on a bien récupéré tous les résultats disponibles)
    try:
        texte_page = await page.inner_text("body")
        match_total = re.search(
            r"(\d+)\s*(?:résultat|résultats|marché|marchés|appel|appels)",
            texte_page,
            re.IGNORECASE,
        )
        if match_total:
            print(f"[Découverte] Total annoncé par le site (approximatif) : {match_total.group(0)!r}")
        else:
            print("[Découverte] Aucun texte de total trouvé sur la page (pas grave, on continue).")
    except Exception:
        pass

    async def extraire_numeros_du_tableau(table_id_actuel):
        """Extrait les numéros d'ordre des lignes de données du tableau (ignore l'en-tête et la ligne de pagination)."""
        numeros_page = []
        rows = await page.locator(f"#{table_id_actuel} tr").all()
        for row in rows:
            cells = await row.locator("td").all()
            if len(cells) < 3:
                continue  # ligne d'en-tête ou vide, on ignore
            texte_ligne = await row.inner_text()
            match = re.search(r"\b(\d{6,10})\b", texte_ligne)
            if match:
                numeros_page.append(match.group(1))
        return numeros_page

    async def trouver_lien_page(table_id_actuel, numero_page):
        """Cherche, parmi les liens du tableau, celui qui pointe vers Page$<numero_page> via __doPostBack."""
        liens = await page.locator(f"#{table_id_actuel} a").all()
        cible = f"Page${numero_page}')"
        for lien in liens:
            href = await lien.get_attribute("href")
            if href and cible in href:
                return lien
        return None

    # Le tableau est un GridView ASP.NET paginé (10 lignes/page) avec des liens
    # "Page$2", "Page$3"... en bas, qui déclenchent un postback AJAX (pas une vraie
    # navigation de page). On avance donc page par page jusqu'à LIMITE_AO résultats.
    numeros = await extraire_numeros_du_tableau(table_id)
    page_courante = 1

    while len(numeros) < LIMITE_AO:
        page_suivante = page_courante + 1
        lien = await trouver_lien_page(table_id, page_suivante)
        if lien is None:
            print(f"[Découverte] Pas de lien vers la page {page_suivante}, on s'arrête ici.")
            break

        print(f"[Découverte] Passage à la page {page_suivante}...")
        avant_texte = await page.locator(f"#{table_id}").inner_text()
        await lien.click()

        try:
            await page.wait_for_function(
                """(args) => {
                    const t = document.getElementById(args.tableId);
                    if (!t) return false;
                    return t.innerText !== args.avant;
                }""",
                arg={"tableId": table_id, "avant": avant_texte},
                timeout=15000,
            )
        except Exception:
            await page.wait_for_load_state("networkidle", timeout=10000)

        # Le tableau garde en général le même id après le postback, mais on le revérifie
        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        table_element = page.locator("table[id^='TabC']").first
        table_id = await table_element.get_attribute("id")

        nouveaux = await extraire_numeros_du_tableau(table_id)
        avant_ajout = len(numeros)
        for n in nouveaux:
            if n not in numeros:
                numeros.append(n)
        print(f"[Découverte] Page {page_suivante} : {len(nouveaux)} ligne(s), "
              f"{len(numeros) - avant_ajout} nouveau(x) numéro(s). Total cumulé : {len(numeros)}")

        page_courante = page_suivante

    print(f"[Découverte] {len(numeros)} numéro(s) d'ordre trouvé(s) au total : {numeros}")

    await page.close()
    return numeros[:LIMITE_AO]


async def telecharger_un_ao(context, numero_ordre):
    """
    PHASE B : reproduit exactement la logique validée pour un seul numéro d'ordre.
    Ouvre une page fraîche à chaque appel pour repartir d'un état propre.
    """
    page = await context.new_page()
    try:
        print(f"\n[{numero_ordre}] Navigation vers le portail...")
        await aller_vers_archives(page)

        print(f"[{numero_ordre}] Filtrage par numéro d'ordre...")
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

        # La recherche par numéro d'ordre peut renvoyer plusieurs lignes proches
        # (ex: numéros consécutifs publiés en lot par le même organisme). On vérifie
        # donc que la ligne cochée correspond bien EXACTEMENT au numéro demandé,
        # au lieu de prendre systématiquement la première ligne du tableau.
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
            print(f"[{numero_ordre}] ⚠ Aucune ligne ne correspond exactement à ce numéro, AO ignoré.")
            return False

        checkbox = ligne_cible.locator("input[type='checkbox']").first
        await checkbox.check()
        print(f"[{numero_ordre}] Ligne cochée (vérifiée : correspondance exacte).")

        await page.locator("input[value='Détails']").first.click()
        await page.wait_for_load_state("networkidle")

        links = await page.locator("a").all()
        dao_link = None
        for link in links:
            text = await link.inner_text()
            if 'D A O' in text.upper() or 'D.A.O' in text.upper() or 'D A  O' in text.upper():
                dao_link = link
                break

        if not dao_link:
            print(f"[{numero_ordre}] ⚠ Lien D.A.O introuvable, AO ignoré.")
            return False

        url_document = await dao_link.get_attribute("href")
        if not url_document:
            print(f"[{numero_ordre}] ⚠ Le lien D.A.O n'a pas d'URL exploitable, AO ignoré.")
            return False

        # Double vérification : l'URL du document (ex: .../CPS/1042453.zip) doit contenir
        # le numéro d'ordre demandé. Si ce n'est pas le cas, on a probablement récupéré
        # la mauvaise ligne/le mauvais document (numéros proches) : on abandonne plutôt
        # que de sauvegarder un fichier sous un mauvais nom.
        if numero_ordre not in url_document:
            print(f"[{numero_ordre}] ⚠ Incohérence : l'URL du document ({url_document}) ne "
                  f"correspond pas au numéro demandé. AO ignoré par sécurité.")
            return False

        # Le lien D.A.O pointe directement vers un fichier (souvent .zip, parfois .pdf) sur un
        # domaine externe (ex: maroc-business.com). On le récupère par requête HTTP directe,
        # plus fiable que d'attendre un événement de téléchargement du navigateur.
        extension = ".pdf" if url_document.lower().endswith(".pdf") else ".zip"
        chemin_fichier = f"data/raw/AO_{numero_ordre}{extension}"

        try:
            reponse = await context.request.get(
                url_document,
                headers={"Referer": page.url},
                timeout=60000,
            )
            if reponse.ok:
                contenu = await reponse.body()
                with open(chemin_fichier, "wb") as f:
                    f.write(contenu)
                print(f"[{numero_ordre}] ✅ Téléchargé (requête directe) : {chemin_fichier}")
                return True
            else:
                print(f"[{numero_ordre}] ⚠ Réponse HTTP {reponse.status} (avec Referer) pour {url_document}, "
                      f"tentative via clic navigateur...")
        except Exception as e_fetch:
            print(f"[{numero_ordre}] ⚠ Erreur requête directe ({e_fetch}), tentative via clic navigateur...")

        # Filet de sécurité : si la requête directe échoue malgré le Referer, on retente
        # en cliquant réellement sur le lien depuis la page de détails (le Referer sera
        # alors correct de façon native, et un éventuel événement de téléchargement du
        # navigateur sera capté).
        try:
            async with page.expect_download(timeout=30000) as download_info:
                await dao_link.click()
            download = await download_info.value
            await download.save_as(chemin_fichier)
            print(f"[{numero_ordre}] ✅ Téléchargé (via clic navigateur) : {chemin_fichier}")
            return True
        except Exception as e_click:
            print(f"[{numero_ordre}] ❌ Échec également via clic navigateur : {e_click}")
            return False

    except Exception as e:
        print(f"[{numero_ordre}] ❌ Erreur : {e}")
        return False
    finally:
        await page.close()


def numeros_deja_telecharges():
    """Regarde dans data/raw/ quels numéros d'ordre ont déjà un fichier AO_<numero>.* téléchargé."""
    deja_faits = set()
    for chemin in glob.glob("data/raw/AO_*.*"):
        nom_fichier = os.path.basename(chemin)
        # nom_fichier ressemble à "AO_1234567.zip" ou "AO_1234567.pdf"
        sans_prefixe = nom_fichier[len("AO_"):]
        numero = sans_prefixe.rsplit(".", 1)[0]
        deja_faits.add(numero)
    return deja_faits


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)

        # PHASE A : découverte de tous les numéros disponibles
        numeros = await decouvrir_numeros_ordre(context)

        if not numeros:
            print("Aucun appel d'offre trouvé pour cette plage de dates. Fin du script.")
            await browser.close()
            return

        # On ignore les AO déjà présents dans data/raw/ pour ne pas les retélécharger
        deja_faits = numeros_deja_telecharges()
        numeros_a_faire = [n for n in numeros if n not in deja_faits]
        deja_sautes = len(numeros) - len(numeros_a_faire)
        if deja_sautes:
            print(f"\n{deja_sautes} AO déjà présent(s) dans data/raw/, ignoré(s) automatiquement.")

        if not numeros_a_faire:
            print("Tous les AO découverts sont déjà téléchargés. Rien à faire.")
            await browser.close()
            return

        # PHASE B : téléchargement un par un
        reussis = 0
        echoues = 0
        for numero in numeros_a_faire:
            ok = await telecharger_un_ao(context, numero)
            if ok:
                reussis += 1
            else:
                echoues += 1
            await asyncio.sleep(2)  # petite pause polie entre chaque requête

        print(f"\n=== Bilan : {reussis} téléchargé(s), {echoues} échec(s) sur {len(numeros_a_faire)} "
              f"(+ {deja_sautes} déjà présent(s) ignoré(s)) ===")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())