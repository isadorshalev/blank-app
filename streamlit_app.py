import streamlit as st
import pandas as pd

st.set_page_config(page_title="Red de Monitoreo de Humedales", page_icon="🌿", layout="wide")

st.title("Red de Monitoreo de Humedales de Valdivia")
st.caption("Monitoreo del agua de siete sitios de los humedales de Valdivia.")

SITES = {
    "Krahmer": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF1ytVbTax4MOv_LUW5Dv4jkqg6mWe5PeoCy1K6PMSNy8aF5db1Qmpfv3iLdIehCAvgMcmtadmLM7M/pub?gid=1505743408&single=true&output=csv",
    "Catrico": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPuC4o1Naw-92olH3K_9a2mzowrAFDmVkJy3rEpECQPiQOjZUMe8O9PU7HZLiWyn6Js6w7wwjAeQAO/pub?gid=1505743408&single=true&output=csv",
    "La Punta": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWtOZeSWAfDAix_FQQvIKgw2B8CSn-TIyJrjZtY3_JA6dEGri-_mkwm3EgGvqWpJ2dO0s02qV3UZeq/pub?gid=1505743408&single=true&output=csv",
    "Los Conquistadores": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFraFOb66MaTlaG-KE1YO1sfciApaRM4U1IApgBVyypKgS-OcJ_YWk2PP2rOMbKD32uD2d3nX3HDRo/pub?gid=1505743408&single=true&output=csv",
    "Rio Angachilla": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMCUsfdqFtgTdvPjhui17q8AjCh9t-3c7yzIyZ0j-nmAiDWYm3qSTCEllUTqhT4YXKleMXxoKb45Rd/pub?gid=1505743408&single=true&output=csv",
    "Piedra Blanca": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTKd00e1SFLJiDHfNW3gei5fXmVBUuY8Z-T5DRyg_vb1LbMMVFETAIsdMHrDH6AWqmSU_IGLdJQi6OT/pub?gid=1505743408&single=true&output=csv",
   # "Catrico Pedro Montt": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQnxlCsxxiM2Lz3Lp_id5Keyu2x7jpulAkgfcgQiZ9EjLX8SzgDXZezK7nG6GS9AQdosXylXwmFOQKP/pub?gid=1505743408&single=true&output=csv",
}

KEEP = ["Fecha", "Temp(aire)", "Temp(agua)", "PH",
        "Oxigeno 1 (ppm: línea de la jeringa)",
        "Oxigeno 2 (ppm: línea de la jeringa)",
        "Promedio Oxigeno", "Saturación Oxígeno (%)"]


def clean_site(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df = df[[c for c in KEEP if c in df.columns]]
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Fecha"])          # <-- new line
    for col in df.columns:
        if col != "Fecha":
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ".", regex=False),
                errors="coerce")
    return df


@st.cache_data(ttl=3600)
def load_all():
    frames = []
    for site, url in SITES.items():
        if url.startswith("PASTE"):
            continue  # skip sites you haven't added yet
        d = clean_site(url)
        d["Sitio"] = site
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


df = load_all()

tab1, tab2 = st.tabs(["🏠 Resumen", "📊 Detalle por sitio"])

with tab1:
    st.subheader("Indicadores clave (promedio)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("pH", f"{df['PH'].mean():.1f}")
    c2.metric("Temp. agua", f"{df['Temp(agua)'].mean():.1f} °C")
    c3.metric("Oxígeno", f"{df['Promedio Oxigeno'].mean():.1f} mg/L")
    c4.metric("Saturación", f"{df['Saturación Oxígeno (%)'].mean():.0f}%")

    st.subheader("Sitios")

    ultimo = (df.dropna(subset=["PH"])
                .sort_values("Fecha")
                .groupby("Sitio")
                .tail(1)
                .set_index("Sitio"))

    cols = st.columns(3)
    for i, (sitio, fila) in enumerate(ultimo.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{sitio}**")
                st.caption(f"Último muestreo: {fila['Fecha']:%d-%m-%Y}")
                st.caption("Calidad bacteriológica: pendiente")
                m1, m2, m3 = st.columns(3)
                m1.metric("pH", f"{fila['PH']:.1f}")
                m2.metric("Temp.", f"{fila['Temp(agua)']:.1f} °C")
                m3.metric("O₂ mg/L", f"{fila['Promedio Oxigeno']:.1f}")

with tab2:
    sitio = st.selectbox("Elige un humedal", sorted(df["Sitio"].unique()))
    sd = df[df["Sitio"] == sitio].sort_values("Fecha").set_index("Fecha")

    st.subheader(f"Parámetros físico-químicos – {sitio}")
    g1, g2, g3 = st.columns(3)

    g1.write("pH")
    g1.line_chart(sd["PH"])

    g2.write("Temperatura del agua (°C)")
    g2.line_chart(sd["Temp(agua)"])

    g3.write("Oxígeno (ppm)")
    g3.line_chart(sd["Promedio Oxigeno"])