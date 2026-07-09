import asyncio
from playwright.async_api import async_playwright

PORTAIL_URL = "http://appels-offres.equipement.gov.ma/recherche/criteres.aspx"
DATE_DEBUT = "01/01/2025"
DATE_FIN = "01/07/2026"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        await page.goto(PORTAIL_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")
        async with page.expect_navigation(timeout=30000):
            await page.click("#LinkButton_Archives")

        await page.evaluate("document.getElementById('date_parution1').removeAttribute('readonly')")
        await page.evaluate("document.getElementById('date_parution2').removeAttribute('readonly')")
        await page.fill("input[name='date_parution1']", DATE_DEBUT)
        await page.fill("input[name='date_parution2']", DATE_FIN)

        async with page.expect_navigation(timeout=30000):
            await page.click("input[name='btn_rechercher']")

        await page.wait_for_selector("table[id^='TabC']", timeout=15000)
        table_element = page.locator("table[id^='TabC']").first
        table_id = await table_element.get_attribute("id")
        print(f"Tableau trouvé : {table_id}")

        # 1) Cherche tout élément cliquable dont le texte ressemble à un numéro de page,
        #    "Suivant", "Page", ">>", etc., n'importe où sur la page (souvent juste après
        #    ou juste avant le tableau dans un GridView ASP.NET).
        print("\n=== LIENS <a> POTENTIELS DE PAGINATION ===\n")
        liens = await page.locator("a").all()
        for lien in liens:
            texte = (await lien.inner_text()).strip()
            href = await lien.get_attribute("href")
            onclick = await lien.get_attribute("onclick")
            # Filtre : texte court, probablement un numéro de page ou un mot-clé de navigation
            if texte and (
                texte.isdigit()
                or texte.lower() in ["suivant", "précédent", "précedent", ">", ">>", "<", "<<", "next", "page suivante"]
            ):
                print(f"Texte={texte!r} | href={href!r} | onclick={onclick!r}")

        # 2) Dump du HTML brut juste après le tableau, pour voir la structure exacte
        print("\n=== HTML APRÈS LE TABLEAU (structure de pagination probable) ===\n")
        html_apres = await page.evaluate(
            """(tableId) => {
                const table = document.getElementById(tableId);
                if (!table) return "Table introuvable";
                let el = table.nextElementSibling;
                let resultat = "";
                let compteur = 0;
                while (el && compteur < 3) {
                    resultat += el.outerHTML.substring(0, 2000) + "\\n---\\n";
                    el = el.nextElementSibling;
                    compteur++;
                }
                return resultat || "(aucun élément après le tableau)";
            }""",
            table_id,
        )
        print(html_apres)

        # 3) Dump aussi la dernière ligne du tableau lui-même (la pagination est parfois
        #    dans une <tr> spéciale à l'intérieur du GridView)
        print("\n=== DERNIÈRE(S) LIGNE(S) DU TABLEAU ===\n")
        derniere_ligne_html = await page.evaluate(
            """(tableId) => {
                const table = document.getElementById(tableId);
                if (!table) return "Table introuvable";
                const rows = table.querySelectorAll('tr');
                if (rows.length === 0) return "(aucune ligne)";
                const derniere = rows[rows.length - 1];
                return derniere.outerHTML.substring(0, 2000);
            }""",
            table_id,
        )
        print(derniere_ligne_html)

        await page.screenshot(path="diagnostic_pagination.png", full_page=True)
        print("\nScreenshot sauvegardé : diagnostic_pagination.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())