document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("ao-grid");
    const searchInput = document.getElementById("searchInput");
    let allAOs = [];

    async function fetchData() {
        try {
            const response = await fetch('/api/appels_offres/');
            allAOs = await response.json();
            document.getElementById("total-ao").textContent = allAOs.length;
            renderAOs(allAOs);
        } catch (error) {
            grid.innerHTML = `<div style="color: red;">Erreur API</div>`;
        }
    }

    function renderAOs(aos) {
        grid.innerHTML = '';
        aos.forEach((ao) => {
            const card = document.createElement("div");
            card.className = "card";

            card.innerHTML = `
                <div class="card-header">
                    <div>
                        <span class="badge">N° ${ao.numero_ordre || 'Inconnu'}</span>
                        <span class="badge-cat">${ao.categorie_marche || 'Secteur Public'}</span>
                    </div>
                    <span style="font-size:0.8rem;color:#64748b;">⏳ Ouverture : ${ao.date_ouverture_plis || 'Non précisé'}</span>
                </div>
                <h2>${ao.objet || 'Objet non extrait'}</h2>
                <div class="moa">🏢 ${ao.maitre_ouvrage || 'Administration'}</div>
                
                <div class="data-grid">
                    <div class="data-item">
                        <span class="data-label">💰 Budget Estimé</span>
                        <span class="data-value">${ao.estimation_mad || 'N/A'}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">🔒 Caution Provisoire</span>
                        <span class="data-value">${ao.caution_mad || 'N/A'}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">⏱️ Délai d'exécution</span>
                        <span class="data-value" style="color:#0284c7;">${ao.delai_execution || 'N/A'}</span>
                    </div>
                    <div class="data-item">
                        <span class="data-label">⚠️ Pénalités de retard</span>
                        <span class="data-value" style="color:#e11d48;">${ao.penalite_retard || 'N/A'}</span>
                    </div>
                </div>
                
                <div class="rh-section">
                    <div class="section-title">👥 Exigences Techniques & RH (Eliminatoire)</div>
                    <p><strong>Agréments :</strong> ${ao.agrements_exiges || 'Non précisé'}</p>
                    <p><strong>Équipe exigée :</strong> ${ao.profils_exiges || 'Non précisé'}</p>
                </div>

                <div class="eval-section">
                    <div class="section-title">📊 Règle du jeu (Notation)</div>
                    <p>${ao.methode_notation || 'Non précisé'}</p>
                </div>
                
                <div style="margin-top: auto;">
                    <button class="btn" style="width: 100%;">Générer Dossier Administratif</button>
                </div>
            `;
            grid.appendChild(card);
        });
    }

    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase();
        const filtered = allAOs.filter(ao => 
            (ao.objet && ao.objet.toLowerCase().includes(term)) || 
            (ao.numero_ordre && ao.numero_ordre.toLowerCase().includes(term)) ||
            (ao.profils_exiges && ao.profils_exiges.toLowerCase().includes(term)) ||
            (ao.maitre_ouvrage && ao.maitre_ouvrage.toLowerCase().includes(term))
        );
        renderAOs(filtered);
    });

    fetchData();
});
