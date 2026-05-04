# =============================================================
# app.py – Immobilien-Preisschätzer Zürich
# Ausführen im Terminal: streamlit run app.py
# =============================================================

import streamlit as st #importiert das Framework Streamlit, mit der Abkürzung st
import folium #importiert interaktive Landkarten
from streamlit_folium import st_folium #Bindeglied, damit die Karte in Streamlit angezeigt werden kann
from feature_dataset         import get_daten #importiert get_daten vom Dataset Feature
from feature_koordinaten     import get_koordinaten #importiert get_koordinaten vom Koordinaten Feature
from feature_berechnung      import berechne_preis, AUSSTATTUNG_LABELS #importiert berechne_preis und AUSSTATTUNG_LABELS vom Berechnung Feature
from feature_waterfall_chart import erstelle_waterfall_chart #importiert erstelle_waterfall_chart vom Waterfall Chart Feature
from feature_gauge_chart     import erstelle_gauge_chart #importiert erstelle_gauge_chart vom Gauge Chart Feature
from feature_heatmap_chart   import erstelle_heatmap_karte #importiert erstelle_heatmap_karte vom Heatmap Chart Feature

# Seitenkonfiguration von Streamlit: Titel setzen und mittig zentrieren
st.set_page_config(
    page_title="Immobilien-Preisschätzer Zürich",
    layout="centered"
)

# ─────────────────────────────────────────────
# BASISPREISE PRO QUARTIER (CHF pro m²)
# ─────────────────────────────────────────────
df = get_daten() # Daten werden einmalig geladen (aus feature_dataset.py)
BASISPREIS_PRO_QUARTIER = (
    df.groupby("Quartier")["Preis_pro_m2"]
    .mean()
    .round()
    .astype(int)
    .to_dict()
) # Berechnet den durchschnittlichen Preis pro m² pro Quartier aus den echten Marktdaten und speichert ihn als Dictionary ab

QUARTIER_KOORDINATEN = get_koordinaten() # Koordinaten aus feature_koordinaten.py laden

# =============================================================
# STREAMLIT APP
# =============================================================

st.title("Immobilien-Preisschaetzer Zürich") # Erstellt den Titel in Streamlit
st.write("Gib die Eigenschaften deiner Immobilie ein - wir berechnen den geschätzten Marktwert.") # Erstellt den Beschreibungstext in Streamlit
st.markdown("---") # Erstellt eine horizontale Trennlinie in Streamlit

# ── 1. LAGE ──
st.subheader("Lage") # Erstellt einen Untertitel in Streamlit
QUARTIERE = ["— Bitte waehlen —"] + sorted(BASISPREIS_PRO_QUARTIER.keys()) # Zwei Listen werden erstellt und miteinander verbunden. Die erste besteht aus dem Platzhalter. Die zweite aus allen Quartiernamen alphabetisch sortiert.
quartier  = st.selectbox("In welchem Stadtquartier liegt die Immobilie?", options=QUARTIERE) # Ein Dropdown Menü wird in Streamlit erstellt mit einem Beschriftungstext und der Liste aller Quartiere

# ── 2. GROESSE ──
st.subheader("Groesse") # Erstellt einen Untertitel in Streamlit
col1, col2 = st.columns(2) # Die Seite wird in zwei gleich breite Spalten aufgeteilt. col1 links und col2 rechts.
with col1: # Definiert, was in der linken Spalte angezeigt wird
    zimmerzahl = st.selectbox( # Erstellt ein Dropdown Menü und speichert den Eingabewert unter zimmerzahl ab
        "Anzahl Zimmer", # Definiert den Text über dem Dropdown Menu
        options=["1", "1.5", "2", "2.5", "3", "3.5", "4", "4.5", "5+"], # Liste aller auswählbaren Optionen
        index=0 # Setzt 1 Zimmer als Standardwert
    )
with col2: # Definiert, was in der rechten Spalte angezeigt wird
    wohnflaeche = st.number_input( # Erstellt ein Eingabefeld und speichert den Eingabewert unter wohnflaeche
        "Wohnflaeche (m2)", min_value=10, max_value=500, value=10, step=5 # Definiert Mindestwert, Maximalwert, Standardwert und Schrittgrösse
    )

# ── 3. GEBAEUDE ──
st.subheader("Gebaeude") # Erstellt einen Untertitel in Streamlit
col3, col4 = st.columns(2) # Die Seite wird in zwei gleich breite Spalten aufgeteilt. col3 links und col4 rechts.
with col3: # Definiert die linke Seite
    baujahr = st.slider("Baujahr", min_value=1900, max_value=2026, value=1990) # Erstellt einen Schieberegler mit Mindestwert, Maximalwert und Standardwert
with col4: # Definiert die rechte Seite
    stockwerk = st.selectbox( # Erstellt ein Dropdown Menu und speichert den Eingabewert unter stockwerk ab
        "Stockwerk", # Definiert den Text über dem Dropdown Menü
        options=[ # Liste aller auswählbaren Optionen, Erdgeschoss wird als Standardwert angezeigt
            "Erdgeschoss", "1. Obergeschoss", "2. Obergeschoss",
            "3. Obergeschoss", "4. Obergeschoss",
            "5. OG oder hoeher", "Dachgeschoss"
        ]
    )

# ── 4. ZUSTAND ──
st.subheader("Zustand") # Erstellt einen Untertitel in Streamlit
zustand = st.radio( # Erstellt Radio-Buttons, von denen der User eine Option wählen kann
    "Wie ist der aktuelle Renovationsstand?", # Definiert den Text über den Buttons
    options=["Neuwertig / Neubau", "Gut gepflegt", "Renovationsbeduerftig"], # Liste aller auswählbaren Optionen
    index=1, # Setzt Gut gepflegt als Standardwert
    horizontal=True # Formatiert die Buttons nebeneinander
)

# ── 5. AUSSTATTUNG ──
st.subheader("Ausstattung") # Erstellt einen Untertitel in Streamlit
col5, col6 = st.columns(2) # Die Seite wird in zwei gleich breite Spalten aufgeteilt. col5 links und col6 rechts.
with col5: # Definiert die linke Seite
    hat_balkon    = st.checkbox("Balkon / Terrasse") # Erstellt eine Checkbox. True wenn aktiviert, False wenn nicht aktiviert.
    hat_parkplatz = st.checkbox("Parkplatz / Garage") # Erstellt eine Checkbox. True wenn aktiviert, False wenn nicht aktiviert.
    hat_lift      = st.checkbox("Lift im Gebaeude") # Erstellt eine Checkbox. True wenn aktiviert, False wenn nicht aktiviert.
with col6: # Definiert die rechte Seite
    hat_keller   = st.checkbox("Keller / Estrich") # Erstellt eine Checkbox. True wenn aktiviert, False wenn nicht aktiviert.
    hat_seesicht = st.checkbox("Seesicht / Aussicht") # Erstellt eine Checkbox. True wenn aktiviert, False wenn nicht aktiviert.
    hat_minergie = st.checkbox("Minergie-Standard") # Erstellt eine Checkbox. True wenn aktiviert, False wenn nicht aktiviert.

# ── 6. BERECHNUNG & ERGEBNIS ──
st.markdown("---") # Erstellt eine horizontale Trennlinie in Streamlit
berechnen = st.button("Marktwert berechnen") # Erstellt einen Button. Wenn geklickt wird True in berechnen gespeichert, sonst False.

if "ergebnis" not in st.session_state: # Beim ersten Start der App existiert "ergebnis" noch nicht – wir legen einen leeren Platz dafür an, damit die App nicht abstürzt
    st.session_state.ergebnis = None   # None = leer. Wird später mit dem berechneten Preis überschrieben, sobald der User auf "Marktwert berechnen" klickt

if berechnen: # Sofern der Button Marktwert berechnen geklickt wurde, ist diese Bedingung True
    if quartier == "— Bitte waehlen —":
        st.error("Bitte waehle ein Stadtquartier aus.") # Zeigt eine Fehlermeldung an wenn kein Quartier gewählt wurde
    else:
        ausstattung = { # Alle Ausstattungswerte des Users werden in einem Dictionary zusammengefasst
            "hat_balkon":    hat_balkon,
            "hat_parkplatz": hat_parkplatz,
            "hat_lift":      hat_lift,
            "hat_keller":    hat_keller,
            "hat_seesicht":  hat_seesicht,
            "hat_minergie":  hat_minergie,
        }

        # Ruft die in feature_berechnung.py definierte Funktion ab
        # und übergibt alle Angaben des Users sowie den Basispreis
        preis_pro_m2, gesamtpreis, faktoren = berechne_preis(
            quartier, zimmerzahl, wohnflaeche,
            baujahr, stockwerk, zustand, ausstattung,
            BASISPREIS_PRO_QUARTIER # Basispreise aus den echten Daten werden mitübergeben
        )

        st.session_state.ergebnis = { # Überschreibt None im Session State mit den berechneten und eingegebenen Werten
            "preis_pro_m2": preis_pro_m2,
            "gesamtpreis":  gesamtpreis,
            "faktoren":     faktoren,
            "quartier":     quartier,
        }

# Ergebnis anzeigen – bleibt sichtbar solange Session State gefüllt ist
if st.session_state.ergebnis: # Sofern Ergebnisse im Session State abgespeichert wurden, wird e als Kurzform definiert
    e = st.session_state.ergebnis

    st.markdown("### Geschaetzter Marktwert") # Erstellt einen mittelgrossen Titel in Streamlit
    col_r1, col_r2 = st.columns(2) # Die Seite wird in zwei gleich breite Spalten aufgeteilt
    with col_r1: # Definiert die linke Seite
        st.metric(
            label="Geschaetzter Kaufpreis",
            value=f"CHF {e['gesamtpreis']:,.0f}".replace(",", "'") # Formatiert die Zahl mit Schweizer Hochkomma als Tausender-Trennzeichen
        )
    with col_r2: # Definiert die rechte Seite
        st.metric(
            label="Preis pro m2",
            value=f"CHF {e['preis_pro_m2']:,.0f}".replace(",", "'") # Formatiert die Zahl mit Schweizer Hochkomma als Tausender-Trennzeichen
        )

    st.markdown("---") # Erstellt eine horizontale Trennlinie in Streamlit

    # Chart 1: Waterfall
    st.markdown("### Zusammensetzung des Preises") # Erstellt einen mittelgrossen Titel in Streamlit
    st.caption("Einfluss der einzelnen Merkmale auf den Preis in CHF/m². Grün = preiserhöhend, Rot = preissenkend.")
    fig_waterfall = erstelle_waterfall_chart(e["faktoren"], e["preis_pro_m2"]) # Ruft die Funktion aus feature_waterfall_chart.py ab
    st.plotly_chart(fig_waterfall, use_container_width=True) # Zeigt den Chart in Streamlit an

    # Chart 2: Gauge
    st.markdown("### Preis im Marktvergleich") # Erstellt einen mittelgrossen Titel in Streamlit
    st.caption(
        f"Der grüne Strich zeigt den Basispreis für {e['quartier']}. "
        "Die farbigen Zonen zeigen günstig (grün), mittel (gelb) und teuer (rot)."
    )
    fig_gauge = erstelle_gauge_chart(e["preis_pro_m2"], e["quartier"]) # Ruft die Funktion aus feature_gauge_chart.py ab
    st.plotly_chart(fig_gauge, use_container_width=True) # Zeigt den Chart in Streamlit an

    # Chart 3: Heatmap
    st.markdown("### Preisübersicht Zürich – Heatmap") # Erstellt einen mittelgrossen Titel in Streamlit
    st.caption(
        "Grün = günstigere Quartiere, Rot = teurere Quartiere. "
        "Ihr Quartier ist dunkel umrandet."
    )
    karte = erstelle_heatmap_karte( # Ruft die Funktion aus feature_heatmap_chart.py ab
        ausgewaehltes_quartier  = e["quartier"],
        quartier_koordinaten    = QUARTIER_KOORDINATEN,
        basispreis_pro_quartier = BASISPREIS_PRO_QUARTIER
    )
    st_folium(karte, use_container_width=True, height=450) # Zeigt die Karte in Streamlit an