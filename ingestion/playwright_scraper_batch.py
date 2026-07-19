import asyncio
import glob
import os
import re
import json
from playwright.async_api import async_playwright

PORTAIL_URL = "http://appels-offres.equipement.gov.ma/recherche/criteres.aspx"

# Plage de dates à explorer pour la découverte des AO (à ajuster selon vos besoins)
DATE_DEBUT = "01/04/2025"
DATE_FIN = "01/07/2026"

# Nombre maximum d'AO à traiter dans cette exécution (le site plafonne à 50 par page de résultats)
LIMITE_AO = 50

SELECTORS_PATH = os.path.join(os.path.dirname(__file__), "config_selectors.json")
CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "scraper_checkpoint.json")


def load_selectors():
    """Charge les sélecteurs depuis le fichier de configuration JSON ou utilise les valeurs par défaut (ING-02)."""
    if os.path.exists(SELECTORS_PATH):
        try:
            with open(SELECTORS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Scraper] Erreur lors du chargement des sélecteurs externes : {e}")
    return {
        "link_archives": "#LinkButton_Archives",
        "date_parution_1": "input[name='date_parution1']",
        "date_parution_2": "input[name='date_parution2']",
        "btn_rechercher": "input[name='btn_rechercher']",
        "results_table": "table[id^='TabC']",
        "txt_nordre": "input[name='TXTNORDRE']",
        "checkbox": "input[type='checkbox']",
        "btn_details": "input[value='Détails']",
        "links": "a"
    }


SELECTORS = load_selectors()


def load_checkpoint():
    """Charge le checkpoint de scraping si disponible (ING-03)."""
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_checkpoint(data):
    """Enregistre le checkpoint de scraping (ING-03)."""
    try:
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Checkpoint] Erreur lors de la sauvegarde : {e}")


async def aller_vers_archives(page):
    """Navigue vers le portail et bascule sur la section AO archivés (ING-02)."""
    await page.goto(PORTAIL_URL, timeout=60000)
    await page.wait_for_load_state("networkidle")
    async with page.expect_navigation(timeout=30000):
        await page.click(SELECTORS["link_archives"])


async def decouvrir_numeros_ordre(context):
    """
    PHASE A : recherche large par dates (sans filtre de numéro),
    puis extrait tous les numéros d'ordre trouvés dans le tableau.
    Gère la reprise sur checkpoint (ING-03).
    """
    page = await context.new_page()
    
    # Reprise sur checkpoint
    checkpoint = load_checkpoint()
    if (checkpoint.get("date_debut") == DATE_DEBUT and 
            checkpoint.get("date_fin") == DATE_FIN and 
            "discovered_numbers" in checkpoint):
        numeros = checkpoint["discovered_numbers"]
        page_courante = checkpoint.get("last_page_discovered", 1)
        print(f"[Découverte] [Checkpoint] Reprise à la page {page_courante} avec {len(numeros)} numéros déjà découverts.")
    else:
        numeros = []
        page_courante = 1

    print("[Découverte] Navigation vers le portail...")
    await aller_vers_archives(page)

    print(f"[Découverte] Filtrage par dates {DATE_DEBUT} -> {DATE_FIN}...")
    await page.evaluate(f"document.getElementById('{SELECTORS['date_parution_1'].split('\'')[1]}').removeAttribute('readonly')")
    await page.evaluate(f"document.getElementById('{SELECTORS['date_parution_2'].split('\'')[1]}').removeAttribute('readonly')")
    await page.fill(SELECTORS["date_parution_1"], DATE_DEBUT)
    await page.fill(SELECTORS["date_parution_2"], DATE_FIN)

    async with page.expect_navigation(timeout=30000):
        await page.click(SELECTORS["btn_rechercher"])

    print("[Découverte] Attente du tableau de résultats...")
    try:
        await page.wait_for_selector(SELECTORS["results_table"], timeout=15000)
        table_element = page.locator(SELECTORS["results_table"]).first
        table_id = await table_element.get_attribute("id")
        print(f"[Découverte] Tableau trouvé : {table_id}")
    except Exception:
        print("[Découverte] Aucun tableau trouvé pour cette plage de dates.")
        await page.close()
        return numeros

    try:
        texte_page = await page.inner_text("body")
        match_total = re.search(
            r"(\d+)\s*(?:résultat|résultats|marché|marchés|appel|appels)",
            texte_page,
            re.IGNORECASE,
        )
        if match_total:
            print(f"[Découverte] Total annoncé par le site (approximatif) : {match_total.group(0)!r}")
    except Exception:
        pass

    async def extraire_numeros_du_tableau(table_id_actuel):
        """Extrait les numéros d'ordre des lignes du tableau."""
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

    async def trouver_lien_page(table_id_actuel, numero_page_cible):
        """Cherche le lien de pagination ASP.NET."""
        liens = await page.locator(f"#{table_id_actuel} a").all()
        cible = f"Page${numero_page_cible}')"
        for lien in liens:
            href = await lien.get_attribute("href")
            if href and cible in href:
                return lien
        return None

    # Reconstruire le viewstate ASP.NET si on a repris depuis une page avancée
    if page_courante > 1:
        print(f"[Découverte] Reconstitution de l'état ASP.NET jusqu'à la page {page_courante}...")
        for p in range(2, page_courante + 1):
            lien = await trouver_lien_page(table_id, p)
            if lien:
                print(f"[Découverte] Simulation du clic de pagination pour la page {p}...")
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
                await page.wait_for_selector(SELECTORS["results_table"], timeout=15000)
                table_element = page.locator(SELECTORS["results_table"]).first
                table_id = await table_element.get_attribute("id")

    # Extraire les numéros de la page courante si on démarre à zéro
    if not numeros:
        numeros = await extraire_numeros_du_tableau(table_id)

    while len(numeros) < LIMITE_AO:
        page_suivante = page_courante + 1
        lien = await trouver_lien_page(table_id, page_suivante)
        if lien is None:
            print(f"[Découverte] Pas de lien vers la page {page_suivante}, fin de la pagination.")
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

        await page.wait_for_selector(SELECTORS["results_table"], timeout=15000)
        table_element = page.locator(SELECTORS["results_table"]).first
        table_id = await table_element.get_attribute("id")

        nouveaux = await extraire_numeros_du_tableau(table_id)
        avant_ajout = len(numeros)
        for n in nouveaux:
            if n not in numeros:
                numeros.append(n)
        print(f"[Découverte] Page {page_suivante} : {len(nouveaux)} ligne(s), "
              f"{len(numeros) - avant_ajout} nouveau(x) numéro(s). Total : {len(numeros)}")

        page_courante = page_suivante

        # Sauvegarde du checkpoint
        save_checkpoint({
            "date_debut": DATE_DEBUT,
            "date_fin": DATE_FIN,
            "discovered_numbers": numeros,
            "last_page_discovered": page_courante,
            "processed_numbers": checkpoint.get("processed_numbers", [])
        })

    print(f"[Découverte] {len(numeros)} numéro(s) d'ordre trouvé(s) au total.")
    await page.close()
    return numeros[:LIMITE_AO]


async def telecharger_un_ao(context, numero_ordre):
    """
    PHASE B : Télécharge le D.A.O. pour un numéro d'ordre donné (ING-02).
    """
    page = await context.new_page()
    try:
        print(f"\n[{numero_ordre}] Navigation vers le portail...")
        await aller_vers_archives(page)

        print(f"[{numero_ordre}] Filtrage par numéro d'ordre...")
        await page.evaluate(f"document.getElementById('{SELECTORS['date_parution_1'].split('\'')[1]}').removeAttribute('readonly')")
        await page.evaluate(f"document.getElementById('{SELECTORS['date_parution_2'].split('\'')[1]}').removeAttribute('readonly')")
        await page.fill(SELECTORS["date_parution_1"], DATE_DEBUT)
        await page.fill(SELECTORS["date_parution_2"], DATE_FIN)
        await page.fill(SELECTORS["txt_nordre"], numero_ordre)

        async with page.expect_navigation(timeout=30000):
            await page.click(SELECTORS["btn_rechercher"])

        await page.wait_for_selector(SELECTORS["results_table"], timeout=15000)
        table_element = page.locator(SELECTORS["results_table"]).first
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
            print(f"[{numero_ordre}] ⚠ Aucune ligne ne correspond exactement à ce numéro, AO ignoré.")
            return False

        checkbox = ligne_cible.locator(SELECTORS["checkbox"]).first
        await checkbox.check()
        print(f"[{numero_ordre}] Ligne cochée (correspondance exacte).")

        await page.locator(SELECTORS["btn_details"]).first.click()
        await page.wait_for_load_state("networkidle")

        links = await page.locator(SELECTORS["links"]).all()
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

        if numero_ordre not in url_document:
            print(f"[{numero_ordre}] ⚠ Incohérence : l'URL du document ({url_document}) ne correspond pas au numéro.")
            return False

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
        except Exception as e_fetch:
            print(f"[{numero_ordre}] ⚠ Erreur requête directe ({e_fetch}), tentative via clic navigateur...")

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
    """Détecte les AO déjà présents localement dans data/raw/."""
    deja_faits = set()
    for chemin in glob.glob("data/raw/AO_*.*"):
        nom_fichier = os.path.basename(chemin)
        sans_prefixe = nom_fichier[len("AO_"):]
        numero = sans_prefixe.rsplit(".", 1)[0]
        deja_faits.add(numero)
    return deja_faits


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)

        # PHASE A : découverte de tous les numéros disponibles (ING-03)
        numeros = await decouvrir_numeros_ordre(context)

        if not numeros:
            print("Aucun appel d'offre trouvé pour cette plage de dates. Fin du script.")
            await browser.close()
            return

        # On ignore les AO déjà présents localement
        deja_faits = numeros_deja_telecharges()
        
        # Charger également les AO marqués comme traités dans le checkpoint (ING-03)
        checkpoint = load_checkpoint()
        processed_in_checkpoint = set(checkpoint.get("processed_numbers", []))
        deja_faits.update(processed_in_checkpoint)
        
        numeros_a_faire = [n for n in numeros if n not in deja_faits]
        deja_sautes = len(numeros) - len(numeros_a_faire)
        if deja_sautes:
            print(f"\n{deja_sautes} AO déjà traité(s)/téléchargé(s), ignoré(s) automatiquement.")

        if not numeros_a_faire:
            print("Tous les AO découverts sont déjà traités. Rien à faire.")
            await browser.close()
            return

        # PHASE B : Téléchargement parallèle avec un sémaphore de 3 (ING-01)
        sem = asyncio.Semaphore(3)
        
        async def worker(numero):
            async with sem:
                ok = await telecharger_un_ao(context, numero)
                if ok:
                    # Enregistrer le progrès dans le checkpoint (ING-03)
                    cp = load_checkpoint()
                    if "processed_numbers" not in cp:
                        cp["processed_numbers"] = []
                    if numero not in cp["processed_numbers"]:
                        cp["processed_numbers"].append(numero)
                    save_checkpoint(cp)
                return numero, ok

        print(f"\n[Scraper] Lancement du téléchargement parallèle de {len(numeros_a_faire)} AO(s) (limite: 3 simultanés)...")
        tasks = [worker(num) for num in numeros_a_faire]
        results = await asyncio.gather(*tasks)

        reussis = sum(1 for _, ok in results if ok)
        echoues = len(results) - reussis

        print(f"\n=== Bilan : {reussis} téléchargé(s), {echoues} échec(s) sur {len(numeros_a_faire)} "
              f"(+ {deja_sautes} déjà traité(s) ignoré(s)) ===")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())