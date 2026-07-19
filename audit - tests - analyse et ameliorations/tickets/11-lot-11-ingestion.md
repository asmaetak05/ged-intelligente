# Lot 11 : Pipeline d'Ingestion, Scraping & OCR

## Tickets Détaillés

### OC-02 — OCR multi-moteurs (Tesseract + EasyOCR fallback) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ocr/multi_engine.py` |
| **Scénarios liés** | ST-OC-003, ST-OC-004 |
| **Description** | Améliorer la qualité OCR arabe (Tesseract sous-performe). |
| **Travail** | 1. Voter entre Tesseract FR, Tesseract AR, EasyOCR.<br>2. Choisir la sortie avec confiance max.<br>3. Métriques CER/WER stockées. |

### OC-03 — Métriques qualité CER/WER par page 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/metrics.py` |
| **Scénarios liés** | ST-OC-014 |
| **Travail** | Calculer `cer = jiwer.cer(reference, hypothesis)` sur un échantillon annoté ; agréger par document. |

### ING-05 — Watermark temporel `last_scrape_at` 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/models.py:Source` |
| **Scénarios liés** | Scénario I-01 (scraping incrémental) |
| **Travail** | Colonne `sources.last_scrape_at`, incrémentée à chaque run réussi ; endpoint `GET /api/v1/scraper/jobs` qui liste l'historique. |

### ING-06 — Endpoint `POST /api/v1/scraper/run` (asynchrone) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/main.py` |
| **Scénarios liés** | ST-API-009, ST-API-010 |
| **Description** | Actuellement, le lancement se fait via WebSocket — il faut un endpoint REST asynchrone. |
| **Travail** | 1. `@app.post("/api/v1/scraper/run")` qui crée un `ScraperJob` et dispatch Celery.<br>2. `GET /api/v1/scraper/jobs/{id}` retourne statut.<br>3. UI : bouton « Lancer » affiche le job ID et écoute les updates. |

### ING-07 — Multi-sources (table `source`) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ingestion/registry.py` |
| **Scénarios liés** | Scénario I-02 |
| **Travail** | 1. Classe abstraite `Scraper` ; sous-classes `MinistereEquipementScraper`, `MarchesPublicsScraper`.<br>2. Registry des sources.<br>3. UI PipelineAdmin : ajouter/éditer une source. |

### OC-07 — Support TIFF / JPEG / PNG scannés 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `ocr/image_input.py` |
| **Scénarios liés** | Scénario O-04 |
| **Travail** | Uniformiser l'entrée : image ou PDF → `np.array` → prétraitement → Tesseract. |

### ING-08 — Mode prévisualisation (dry-run) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `ingestion/scraper.py` |
| **Travail** | `?dry_run=true` : le scraper récupère les URLs sans télécharger ni écrire en BDD ; retourne la liste. |

### OC-08 — Streaming PyMuPDF pour PDF > 200 pages 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/stream_extract.py` |
| **Scénarios liés** | ST-OC-009 |
| **Travail** | `page = doc.load_page(i)` au lieu de `text = doc[i].get_text()` ; libérer la mémoire entre pages. |

### ING-09 — Webhooks sortants (Slack, ERP) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Composant** | `backend/webhooks.py` |
| **Travail** | 1. Table `webhook(id, url, secret, events_json)`.<br>2. À chaque `marches.created`, POST sur les webhooks abonnés.<br>3. Retry exponentiel 3× en cas d'échec. |

### OC-09 — Préservation de la structure (titres, tableaux) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `ocr/structured.py` |
| **Scénarios liés** | ST-OC-012, Scénario O-02 |
| **Travail** | Sortie JSON `[{page, blocks: [{type, text, bbox, font_size}]}]` ; `pymupdf.get_text("dict")`. |

### ING-10 — Détection de changement (versioning ZIP) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | V1 |
| **Travail** | Table `version_history(id, marche_id, checksum, file_uri, created_at)` ; détection d'un ZIP déjà connu avec checksum différent → flag `rectificatif`. |

### OC-10 — Gestion des PDF chiffrés 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `ocr/security.py` |
| **Scénarios liés** | ST-OC-013 |
| **Travail** | `if doc.is_encrypted: raise EncryptedPdfError()` ; log de l'incident dans `audit_event`. |

### ING-11 — Tests d'intégration avec snapshot HTML 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `tests/fixtures/portal_snapshot.html`, `tests/test_scraper_snapshot.py` |
| **Scénarios liés** | ST-IN-009 |
| **Travail** | Charger un snapshot HTML réel (collecté manuellement) ; exécuter le scraper en mode `offline=True` ; vérifier que les champs-clés sont extraits. |

### ING-12 — Planificateur de scraping (cron intégré) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S1 |
| **Composant** | `backend/scheduler.py` |
| **Scénarios liés** | Scénario I-01 |
| **Travail** | 1. `APScheduler` ou Celery beat.<br>2. Cron quotidien à 02h00 : `scraper.run(last_scrape_at, today)`.<br>3. UI : cron builder visuel (optionnel, V1). |
