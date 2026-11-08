import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import math

st.set_page_config(page_title="Red de Monitoreo de Humedales", page_icon="🌿", layout="wide")

st.title("Red de Monitoreo de Humedales de Valdivia")
st.caption("Monitoreo del agua de siete sitios de los humedales de Valdivia.")

# ---------- LINKS: físico-químico ----------
SITES = {
    "Krahmer": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF1ytVbTax4MOv_LUW5Dv4jkqg6mWe5PeoCy1K6PMSNy8aF5db1Qmpfv3iLdIehCAvgMcmtadmLM7M/pub?gid=1505743408&single=true&output=csv",
    "Catrico": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPuC4o1Naw-92olH3K_9a2mzowrAFDmVkJy3rEpECQPiQOjZUMe8O9PU7HZLiWyn6Js6w7wwjAeQAO/pub?gid=1505743408&single=true&output=csv",
    "La Punta": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWtOZeSWAfDAix_FQQvIKgw2B8CSn-TIyJrjZtY3_JA6dEGri-_mkwm3EgGvqWpJ2dO0s02qV3UZeq/pub?gid=1505743408&single=true&output=csv",
    "Los Conquistadores": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFraFOb66MaTlaG-KE1YO1sfciApaRM4U1IApgBVyypKgS-OcJ_YWk2PP2rOMbKD32uD2d3nX3HDRo/pub?gid=1505743408&single=true&output=csv",
    "Rio Angachilla": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMCUsfdqFtgTdvPjhui17q8AjCh9t-3c7yzIyZ0j-nmAiDWYm3qSTCEllUTqhT4YXKleMXxoKb45Rd/pub?gid=1505743408&single=true&output=csv",
    "Piedra Blanca": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTKd00e1SFLJiDHfNW3gei5fXmVBUuY8Z-T5DRyg_vb1LbMMVFETAIsdMHrDH6AWqmSU_IGLdJQi6OT/pub?gid=1505743408&single=true&output=csv",
    # "Catrico Pedro Montt": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQnxlCsxxiM2Lz3Lp_id5Keyu2x7jpulAkgfcgQiZ9EjLX8SzgDXZezK7nG6GS9AQdosXylXwmFOQKP/pub?gid=1505743408&single=true&output=csv",
}

# ---------- LINKS: coliformes (PASTE YOUR DICTIONARY HERE) ----------
COLIFORMES = {
    "Krahmer": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF1ytVbTax4MOv_LUW5Dv4jkqg6mWe5PeoCy1K6PMSNy8aF5db1Qmpfv3iLdIehCAvgMcmtadmLM7M/pub?gid=306852629&single=true&output=csv",
    "Catrico": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPuC4o1Naw-92olH3K_9a2mzowrAFDmVkJy3rEpECQPiQOjZUMe8O9PU7HZLiWyn6Js6w7wwjAeQAO/pub?gid=306852629&single=true&output=csv",
    "La Punta": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWtOZeSWAfDAix_FQQvIKgw2B8CSn-TIyJrjZtY3_JA6dEGri-_mkwm3EgGvqWpJ2dO0s02qV3UZeq/pub?gid=306852629&single=true&output=csv",
    "Los Conquistadores": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFraFOb66MaTlaG-KE1YO1sfciApaRM4U1IApgBVyypKgS-OcJ_YWk2PP2rOMbKD32uD2d3nX3HDRo/pub?gid=306852629&single=true&output=csv",
    "Rio Angachilla": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMCUsfdqFtgTdvPjhui17q8AjCh9t-3c7yzIyZ0j-nmAiDWYm3qSTCEllUTqhT4YXKleMXxoKb45Rd/pub?gid=306852629&single=true&output=csv",
    "Piedra Blanca": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTKd00e1SFLJiDHfNW3gei5fXmVBUuY8Z-T5DRyg_vb1LbMMVFETAIsdMHrDH6AWqmSU_IGLdJQi6OT/pub?gid=306852629&single=true&output=csv",
    "Catrico Pedro Montt": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQnxlCsxxiM2Lz3Lp_id5Keyu2x7jpulAkgfcgQiZ9EjLX8SzgDXZezK7nG6GS9AQdosXylXwmFOQKP/pub?gid=306852629&single=true&output=csv",
}

COORDS = {
    "Krahmer": (-39.833384, -73.231134),
    "Catrico": (-39.843039, -73.224381),
    "La Punta": (-39.854414, -73.241500),
    "Los Conquistadores": (-39.849651750128054, -73.21789481349317),
    "Rio Angachilla": (-39.879019, -73.238099),
    "Piedra Blanca": (-39.884594550392094, -73.13949290687675),
    "Catrico Pedro Montt": (-39.847258, -73.231716),
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
    df = df.dropna(subset=["Fecha"])
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
        d = clean_site(url)
        d["Sitio"] = site
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def clean_coli(url):
    raw = pd.read_csv(url, header=None, dtype=str)
    # the real header row is the one that contains "E.Coli en 100"
    es_encabezado = raw.apply(
        lambda fila: fila.str.contains("E.Coli en 100", regex=False, na=False).any(),
        axis=1)
    if not es_encabezado.any():
        return pd.DataFrame(columns=["Fecha", "E.coli"])
    h = es_encabezado.idxmax()
    encabezado = raw.iloc[h].str.strip()
    c_fecha = encabezado[encabezado == "Fecha"].index[0]
    c_ecoli = encabezado[encabezado.str.contains("E.Coli en 100", regex=False, na=False)].index[0]

    datos = raw.loc[h + 1:]
    d = pd.DataFrame({
        "Fecha": pd.to_datetime(datos[c_fecha], dayfirst=True, errors="coerce"),
        "E.coli": pd.to_numeric(
            datos[c_ecoli].str.replace(",", ".", regex=False), errors="coerce"),
    })
    return d.dropna(subset=["Fecha", "E.coli"])


@st.cache_data(ttl=3600)
def load_coli():
    frames = []
    for site, url in COLIFORMES.items():
        if url.startswith("PASTE"):
            continue
        d = clean_coli(url)
        d["Sitio"] = site
        frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["Fecha", "E.coli", "Sitio"])
    return pd.concat(frames, ignore_index=True)


def clasificar(valor):
    """Bueno < 200 | Moderado 200-1000 | Malo > 1000 (por 100 mL)"""
    if pd.isna(valor):
        return "Sin datos"
    if valor < 200:
        return "Bueno"
    if valor <= 1000:
        return "Moderado"
    return "Malo"


ICONOS = {"Bueno": "🟢", "Moderado": "🟠", "Malo": "🔴", "Sin datos": "⚪"}

df = load_all()
dfc = load_coli()

tab1, tab2 = st.tabs(["Resumen", "Detalle por sitio"])

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

    ultimo_coli = (dfc.sort_values("Fecha")
                      .groupby("Sitio")
                      .tail(1)
                      .set_index("Sitio"))

    cols = st.columns(3)
    for i, (sitio, fila) in enumerate(ultimo.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{sitio}**")
                st.caption(f"Último muestreo: {fila['Fecha']:%d-%m-%Y}")

                if sitio in ultimo_coli.index:
                    valor = ultimo_coli.loc[sitio, "E.coli"]
                    est = clasificar(valor)
                    st.markdown(f"{ICONOS[est]} **{est}** · E. coli: {valor:.0f} /100 mL")
                else:
                    st.caption("Calidad bacteriológica: sin datos")

                m1, m2, m3 = st.columns(3)
                m1.metric("pH", f"{fila['PH']:.1f}")
                m2.metric("Temp. del agua", f"{fila['Temp(agua)']:.1f} °C")
                m3.metric("O₂ mg/L", f"{fila['Promedio Oxigeno']:.1f}")
    st.subheader("Mapa de los humedales")
    puntos = pd.DataFrame(
        [{"Sitio": s, "lat": c[0], "lon": c[1]}
         for s, c in COORDS.items() if c is not None]
    )
    if puntos.empty:
        st.info("Agrega las coordenadas en COORDS para ver el mapa.")
    else:
        capa = pdk.Layer(
            "ScatterplotLayer",
            data=puntos,
            get_position="[lon, lat]",
            get_radius=120,
            radius_min_pixels=7,
            get_fill_color=[47, 107, 79, 210],
            pickable=True,
        )
        etiquetas = pdk.Layer(
            "TextLayer",
            data=puntos,
            get_position="[lon, lat]",
            get_text="Sitio",
            get_size=14,
            get_color=[27, 42, 51, 255],
            get_pixel_offset=[0, -16],
        )
        vista = pdk.ViewState(
            latitude=puntos["lat"].mean(),
            longitude=puntos["lon"].mean(),
            zoom=11,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=[capa, etiquetas],
                initial_view_state=vista,
                tooltip={"text": "{Sitio}"},
                map_style="light",
            ),
            use_container_width=True,
        )
with tab2:
    opciones = {
        "Último mes": 1,
        "Últimos 3 meses": 3,
        "Últimos 6 meses": 6,
        "Último año": 12,
        "Todo el período": None,
    }

    a, b = st.columns(2)
    todos = sorted(set(df["Sitio"]) | set(dfc["Sitio"]))
    sitio = a.selectbox("Elige un humedal", todos)
    periodo = b.selectbox("Período", list(opciones.keys()), index=4)
    meses = opciones[periodo]

    if meses is None:
        dff = df
    else:
        corte = df["Fecha"].max() - pd.DateOffset(months=meses)
        dff = df[df["Fecha"] > corte]

    # ----- físico-químico -----
    sd = dff[dff["Sitio"] == sitio].sort_values("Fecha").set_index("Fecha")

    st.subheader(f"Parámetros físico-químicos – {sitio}")
    if sd.empty:
        st.info("No hay datos físico-químicos para este sitio en el período elegido.")
    else:
        g1, g2, g3 = st.columns(3)

        g1.write("pH")
        g1.line_chart(sd["PH"])

        g2.write("Temperatura del agua (°C)")
        g2.line_chart(sd["Temp(agua)"])

        g3.write("Oxígeno (ppm)")
        g3.line_chart(sd["Promedio Oxigeno"])

    # ----- bacteriológico -----
    st.subheader(f"Análisis bacteriológico – {sitio}")
    st.caption("E. coli por 100 mL · Bueno: < 200 · Moderado: 200–1000 · Malo: > 1000")

    sc = dfc[dfc["Sitio"] == sitio]
    if meses is not None and not dfc.empty:
        sc = sc[sc["Fecha"] > dfc["Fecha"].max() - pd.DateOffset(months=meses)]
    sc = sc.sort_values("Fecha")

    if sc.empty:
        st.info("No hay datos bacteriológicos para este sitio en el período elegido.")
    else:
        graf = sc[sc["E.coli"] > 0].copy()
        if len(graf) < len(sc):
            st.caption("Los valores de 0 no se pueden mostrar en escala logarítmica.")

        graf["Calidad"] = graf["E.coli"].apply(clasificar)

        tope = max(graf["E.coli"].max() if not graf.empty else 0, 1000)

        fig = px.bar(
            graf, x="Fecha", y="E.coli", log_y=True,
            color="Calidad",
            color_discrete_map={"Bueno": "#2E8B57",
                                "Moderado": "#E0A030",
                                "Malo": "#C0392B"},
            category_orders={"Calidad": ["Bueno", "Moderado", "Malo"]},
            labels={"E.coli": "E. coli por 100 mL (escala logarítmica)"},
        )
        fig.update_layout(barmode="overlay")
        fig.add_hline(y=200, line_dash="dash", line_color="#E0A030")
        fig.add_hline(y=1000, line_dash="dash", line_color="#C0392B")
        fig.update_yaxes(range=[0, math.ceil(math.log10(tope))])

        for valor, color in [(200, "#B7791F"), (1000, "#C0392B")]:
            fig.add_annotation(
                x=1, xref="paper", y=math.log10(valor), yref="y",
                text=str(valor), showarrow=False,
                xanchor="right", yanchor="bottom", font=dict(color=color),
            )

        st.plotly_chart(fig, use_container_width=True)

        tabla = pd.DataFrame({
            "Fecha": sc["Fecha"].dt.strftime("%d-%m-%Y"),
            "E. coli (por 100 mL)": sc["E.coli"],
            "Calidad": sc["E.coli"].apply(
                lambda v: f"{ICONOS[clasificar(v)]} {clasificar(v)}"),
        }).iloc[::-1]
        st.dataframe(tabla, hide_index=True)