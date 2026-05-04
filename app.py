# =============================================================
# fragebogen.py – Immobilien-Preisschätzer Zürich
# Ausführen im Terminal: streamlit run fragebogen.py
# =============================================================

import streamlit as st #importiert das Framework Streamlit, mit der Abkürzung st
import plotly.graph_objects as go #importiert eine Bibliothek für interaktive Diagramme mit der low-level Variante go
import plotly.express as px #???? raus nehmen, nutzen wir nicht???? Bibliothek für interaktive Diagramme, px als high-level Variante
import folium #importiert interaktive Landkarten
from streamlit_folium import st_folium #Bindeglied, damit die Karte in Streamlit angezeigt werden kann
from feature_dataset import get_daten #importiert get_daten vom Dataset Feature
from feature_Koordinaten import get_koordinaten
from feature_heatmap_chart import erstelle_heatmap_karte
from feature_machine_learning import trainiere_knn_modell, ml_basispreis_schaetzen
from feature_waterfall_chart import erstelle_waterfall_chart 
from feature_berechnung import berechne_preis, FAKTOR_ZIMMER, FAKTOR_ZUSTAND, FAKTOR_STOCKWERK, AUSSTATTUNG_FAKTOREN, AUSSTATTUNG_LABELS, faktor_baujahr #importiert die Berechnungsfunktion und alle Faktoren aus feature_berechnung

# Seitenkonfiguration von Streamlit: Titel setzen und mittig zentrieren
st.set_page_config(
    page_title="Immobilien-Preisschätzer Zürich",
    layout="centered"
)

# ─────────────────────────────────────────────
# BASISPREISE PRO QUARTIER (CHF pro m²)
# ─────────────────────────────────────────────
df= get_daten()
#Daten werden einmalig geladen (aus Feature Dataset.py)
BASISPREIS_PRO_QUARTIER = (
    df.groupby("Quartier")["Preis_pro_m2"]
    .mean()
    .round()
    .astype(int)
    .to_dict()
)

#ML-Modell wird beim start einmalig trainiert
knn_modell, knn_le, _, _, _ = trainiere_knn_modell(df)

# ─────────────────────────────────────────────
# KOORDINATEN DER QUARTIERE (Mittelpunkte)
# Fuer die Heatmap auf der Karte !!!!! wurde mit feature_Koordinaten angepasst
# ─────────────────────────────────────────────

QUARTIER_KOORDINATEN = get_koordinaten()


# ─────────────────────────────────────────────
# CHART 2: GAUGE – Preis im Marktvergleich
# ─────────────────────────────────────────────
def erstelle_gauge_chart(preis_pro_m2, quartier):
    """
    Zeigt ob der geschätzte Preis für das gewählte
    Quartier günstig, durchschnittlich oder teuer ist.
    """
    basispreis  = BASISPREIS_PRO_QUARTIER.get(quartier, 11000)
    min_preis   = min(BASISPREIS_PRO_QUARTIER.values())   # günstigstes Quartier
    max_preis   = max(BASISPREIS_PRO_QUARTIER.values())   # teuerstes Quartier

    fig = go.Figure(go.Indicator(
        mode  = "gauge+number+delta",
        value = preis_pro_m2,
        delta = {
            "reference": basispreis,
            "increasing": {"color": "#16a34a"},
            "decreasing": {"color": "#dc2626"},
            "suffix": " CHF/m²"
        },
        number = {"suffix": " CHF/m²", "font": {"size": 28}},
        title  = {"text": f"Preis im Vergleich zum Quartier-Durchschnitt ({quartier})",
                  "font": {"size": 14}},
        gauge  = {
            "axis": {
                "range":     [min_preis * 0.8, max_preis * 1.1],
                "ticksuffix": " CHF",
                "tickfont":   {"size": 11},
            },
            "bar":       {"color": "#2563eb"},
            "steps": [
                {"range": [min_preis * 0.8, min_preis * 1.1], "color": "#dcfce7"},
                {"range": [min_preis * 1.1, max_preis * 0.9], "color": "#fef9c3"},
                {"range": [max_preis * 0.9, max_preis * 1.1], "color": "#fee2e2"},
            ],
            "threshold": {
                "line":  {"color": "#1D9E75", "width": 3},
                "value": basispreis,
            },
        }
    ))

    fig.update_layout(
        plot_bgcolor  = "white",
        paper_bgcolor = "white",
        height        = 300,
        margin        = dict(t=80, b=20, l=40, r=40),
    )
    return fig


# ─────────────────────────────────────────────

# =============================================================
# STREAMLIT APP
# =============================================================

st.title("Immobilien-Preisschaetzer Zürich") #Erstellt den Titel in Streamlit
st.write("Gib die Eigenschaften deiner Immobilie ein - wir berechnen den geschätzten Marktwert.") #Erstellt den Beschreibungstext in Streamlit
st.markdown("---") #Erstellt eine horizontale Trennlinie in Streamlit

# ── 1. LAGE ──
st.subheader("Lage") #Erstellt einen Untertitel in Streamlit
QUARTIERE = ["— Bitte waehlen —"] + sorted(BASISPREIS_PRO_QUARTIER.keys()) #Zwei Listen werden erstellt und miteinander verbunden. Die erste besteht aus dem Platzhalter: Bitte waehlen. Die zweite Liste besteht aus allen Schlüsseln (Quartiernamen) des Dictionaries, welche alphabetisch sortiert werden.
quartier  = st.selectbox("In welchem Stadtquartier liegt die Immobilie?", options=QUARTIERE) #Ein Dropdown Menü wird in Streamlit erstellt mit einem Beschriftungstext. Das Dropdown Menu beinhaltet eine Liste aller Optionen, die in der vorherigen Zeile definiert wurde. 

# ── 2. GROESSE ──
st.subheader("Groesse") #Erstellt einen Untertitel in Streamlit
col1, col2 = st.columns(2) #Die Seite wird in zwei gleich breite Spalten aufgeteilt. col1 links und col2 rechts.
with col1: #Definiert, was in der linken Spalte angezeigt wird
    zimmerzahl = st.selectbox( #Erstellt ein Dropdown Menü und speichert den Eingabewert unter zimmerzahl ab
        "Anzahl Zimmer", #Definiert den Text über dem Dropdown Menu
        options=["1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5+"], #Beschreibt die Liste aller auswählbaren Optionen
        index=0 #Definiert den Standardwert bei Index 0 --> 1 Zimmer
    )
with col2: #Definiert, was in der rechten Spalte angezeigt wird
    wohnflaeche = st.number_input( #Erstellt ein Eingabefeld und speichert den Eingabewert unter wohnflaeche
        "Wohnflaeche (m2)", min_value=10, max_value=500, value=10, step=5 #Definiert die kleinste erlaubte Zahl, die grösste erlaubte Zahl, den Standardwert und die Steps (wenn man auf + klickt, springt die Zahl um diesen Wert)
    )

# ── 3. GEBAEUDE ──
st.subheader("Gebaeude") #Erstellt einen Untertitel in Streamlit
col3, col4 = st.columns(2) #Die Seite wird in zwei gleich breite Spalten aufgeteilt. col3 links und col4 rechts.
with col3: #Definiert die linke Seite
    baujahr = st.slider("Baujahr", min_value=1900, max_value=2026, value=1990) #Erstellt einen Schieberegler in Streamlit mit dem Beschriftungstext, dem Mindestwert, dem Maximalwert und dem Standardwert und speichert den Eingabewert unter baujahr
with col4: #Definiert die rechte Seite
    stockwerk = st.selectbox( #Erstellt ein Dropdown Menu und sp