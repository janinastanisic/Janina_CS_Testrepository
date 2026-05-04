# =============================================================
# feature_berechnung.py
# Enthält alle Korrekturfaktoren und die Preisberechnungslogik
# =============================================================

# ─────────────────────────────────────────────
# KORREKTURFAKTOREN: Der Faktor wird mit dem Basispreis multipliziert
# und passt den Preis prozentual an.
# Bsp. Faktor 0.92 = Preis wird um 8% reduziert.
# Die Faktoren basieren auf Schätzwerten.
# ─────────────────────────────────────────────

FAKTOR_ZIMMER = {
    "1": 0.92, "1.5": 0.95, "2": 0.97, "2.5": 0.99,
    "3": 1.00, "3.5": 1.01, "4": 1.02, "4.5": 1.03, "5+": 1.04,
}

FAKTOR_ZUSTAND = {
    "Neuwertig / Neubau":    1.10,
    "Gut gepflegt":          1.00,
    "Renovationsbeduerftig": 0.85,
}

FAKTOR_STOCKWERK = {
    "Erdgeschoss":       0.95,
    "1. Obergeschoss":   0.98,
    "2. Obergeschoss":   1.00,
    "3. Obergeschoss":   1.02,
    "4. Obergeschoss":   1.04,
    "5. OG oder hoeher": 1.06,
    "Dachgeschoss":      1.08,
}

AUSSTATTUNG_FAKTOREN = {
    "hat_balkon":    0.03,
    "hat_parkplatz": 0.04,
    "hat_lift":      0.02,
    "hat_keller":    0.01,
    "hat_seesicht":  0.08,
    "hat_minergie":  0.03,
} # Jede zusätzliche Ausstattung addiert einen Prozentsatz zum Preis.
  # Bsp. Faktor 0.03 = +3%. Der Prozentsatz basiert auf Schätzwerten.

AUSSTATTUNG_LABELS = {
    "hat_balkon":    "Balkon / Terrasse",
    "hat_parkplatz": "Parkplatz / Garage",
    "hat_lift":      "Lift",
    "hat_keller":    "Keller / Estrich",
    "hat_seesicht":  "Seesicht",
    "hat_minergie":  "Minergie",
} # Übersetzung von internen Bezeichnungen in lesbare Texte für die App


# ─────────────────────────────────────────────
# BAUJAHR-FAKTOR
# Das Alter der Immobilie wird berechnet und in Kategorien eingeteilt.
# Bsp. wenn Immobilie jünger als 5 Jahre ist, wird der Preis um 10% erhöht.
# ─────────────────────────────────────────────
def faktor_baujahr(baujahr):
    alter = 2026 - baujahr
    if alter <= 5:    return 1.10
    elif alter <= 15: return 1.05
    elif alter <= 30: return 1.00
    elif alter <= 50: return 0.95
    else:             return 0.90


# ─────────────────────────────────────────────
# BERECHNUNGSFUNKTION
# Definition der Funktion berechne_preis mit allen Eingabewerten des Users
# ─────────────────────────────────────────────
def berechne_preis(quartier, zimmerzahl, wohnflaeche, baujahr,
                   stockwerk, zustand, ausstattung, basispreis_pro_quartier):
    """
    Berechnet den geschätzten Kaufpreis einer Immobilie.

    Eingaben:   Alle Angaben des Users aus dem Fragebogen
    Rückgabe:   Preis pro m² (int), Gesamtpreis (int), Faktoren (dict)
    """

    basispreis  = basispreis_pro_quartier.get(quartier, 11000) # Basispreis aus Quartier holen, Standardwert 11000 falls nicht gefunden
    f_zimmer    = FAKTOR_ZIMMER.get(zimmerzahl, 1.00)           # Korrekturfaktor Zimmerzahl, Standardwert 1.00
    f_zustand   = FAKTOR_ZUSTAND.get(zustand, 1.00)             # Korrekturfaktor Zustand, Standardwert 1.00
    f_stockwerk = FAKTOR_STOCKWERK.get(stockwerk, 1.00)         # Korrekturfaktor Stockwerk, Standardwert 1.00
    f_baujahr   = faktor_baujahr(baujahr)                       # Korrekturfaktor Baujahr aus Funktion holen

    f_ausstattung = 1.00 # Startet bei 1.00
    for merkmal, wert in ausstattung.items(): # Iteriert durch alle Ausstattungsmerkmale
        if wert: # Nur wenn Checkbox aktiviert (True)
            f_ausstattung += AUSSTATTUNG_FAKTOREN.get(merkmal, 0) # Prozentsatz addieren

    preis_pro_m2 = (basispreis * f_zimmer * f_zustand
                    * f_stockwerk * f_baujahr * f_ausstattung) # Preis pro m² mit allen Faktoren berechnen
    gesamtpreis  = preis_pro_m2 * wohnflaeche # Gesamtpreis = Preis pro m² × Wohnfläche

    faktoren = { # Alle berechneten Faktoren als Dictionary abspeichern
        "Basispreis (Quartier)": basispreis,
        "Zimmerzahl":            f_zimmer,
        "Zustand":               f_zustand,
        "Stockwerk":             f_stockwerk,
        "Baujahr":               f_baujahr,
        "Ausstattung":           f_ausstattung,
    }

    return round(preis_pro_m2), round(gesamtpreis), faktoren # Gerundete Werte und Faktoren zurückgeben