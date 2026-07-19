# Lot 12 : Intelligence Artificielle & NLP (Extraction)

## Tickets Détaillés

### NLP-04 — Extraction date d'ouverture des plis 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_dates_ouverture.py` |
| **Scénarios liés** | ST-NL-012, ST-FT-011 |
| **Travail** | Patterns : `r"séance d'ouverture.*?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\s*(?:à\s*)?\d{1,2}h\d{0,2})"` ; normaliser en ISO 8601. |

### NLP-05 — Extraction date limite de remise (déjà partiellement OK) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py` |
| **Scénarios liés** | ST-NL-013, ST-FT-012 |
| **Travail** | Améliorer la précision du pattern existant ; distinguer « date limite de remise » vs « date d'ouverture ». |

### NLP-06 — Reconnaissance des modèles d'avis 12-10, 13-10 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_modele.py` |
| **Scénarios liés** | ST-NL-021 |
| **Travail** | Patterns officiels (avis 12-10, 13-10, etc.) ; remplissage de `marches.modele_reference`. |

### NLP-07 — Extraction des contacts (email, téléphone, adresse) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/extract_contacts.py` |
| **Scénarios liés** | Scénario O-07 |
| **Travail** | Regex email + téléphone marocain `(+212|0)[5-7]\d{8}` ; normalisation. |

### NLP-08 — Extraction des références réglementaires 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/extract_refs_reglementaires.py` |
| **Scénarios liés** | Scénario O-06 |
| **Travail** | `r"(article\s+\d+\s+du\s+d[ée]cret\s+n[°º]?\s*[\d-]+)"` ; LLM en fallback. |

### NLP-09 — Reconnaissance bilingue FR/AR sur les entités 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | L (5 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/multilang_extract.py` |
| **Scénarios liés** | ST-NL-014 |
| **Travail** | spaCy `xx` (multilingue) + CamemBERT (FR) + AraBERT (AR) ; voter les sorties. |

### NLP-10 — Extraction avancée par LLM (Mistral / GPT-4o) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (3 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/llm_extract.py` |
| **Scénarios liés** | Scénario O-03 |
| **Travail** | 1. Prompt structuré : « Extrais les entités de ce DAO au format JSON. ».<br>2. Cache des résultats par hash.<br>3. Mode « fallback » activé si confiance regex < 0.7. |

### NLP-11 — Détection automatique de la langue principale 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/lang_detect.py` |
| **Scénarios liés** | Scénario O-05 |
| **Travail** | `from langdetect import detect` ; sortie par page ; stockée dans `OcrLog.detected_languages`. |

### NLP-12 — Score de confiance par entité 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py` |
| **Scénarios liés** | ST-NL-015 |
| **Travail** | Pour chaque regex, calculer un score (longueur match / contexte, présence de mots-clés validant, etc.). |

### NLP-13 — Détection de documents non conformes (`low_quality`) 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/quality.py` |
| **Scénarios liés** | ST-NL-017 |
| **Travail** | Si < 3 entités extraites → `documents.low_quality = True`. |

### NLP-14 — Idempotence de l'extraction 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (0.5 j) |
| **Sprint cible** | S5 |
| **Composant** | `nlp/extract_entities.py` |
| **Scénarios liés** | ST-NL-018 |
| **Travail** | Contrainte `UNIQUE(document_id, field_name)` sur `extractions_nlp` ; upsert. |

### NLP-15 — Audit des regex utilisées (≥ 50 patterns) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `tests/test_nlp_patterns.py` |
| **Scénarios liés** | ST-NL-020 |
| **Travail** | Suite de tests paramétrée sur 50+ cas. |

### NLP-17 — Pipeline d'extraction asynchrone 🟠
| Champ | Détail |
|---|---|
| **Priorité** | 🟠 P1 |
| **Effort** | M (2 j) |
| **Sprint cible** | S5 |
| **Composant** | `backend/tasks.py` |
| **Scénarios liés** | Scénario I-04 (webhooks) |
| **Travail** | Refactor `process_document_async` pour utiliser Celery ; suivi via `GET /jobs/{id}`. |

### NLP-18 — Tableur des entités extraites (export CSV/Excel) 🟡
| Champ | Détail |
|---|---|
| **Priorité** | 🟡 P2 |
| **Effort** | S (1 j) |
| **Sprint cible** | V1 |
| **Composant** | `nlp/export.py` |
| **Scénarios liés** | Scénario O-08 |
| **Travail** | `GET /api/v1/documents/{id}/entities?format=csv`. |
