import math
import os
import re
import unicodedata

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st
from PIL import Image, ImageOps

st.set_page_config(page_title="Red de Monitoreo de Humedales", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@400;600;700&display=swap');
.stApp { font-family: 'Nunito', sans-serif; }
h1, h2, h3, h4 { font-family: 'Baloo 2', sans-serif !important; font-weight: 700 !important; color: #1B2A33; }
[data-testid="stMetricValue"] { font-family: 'Baloo 2', sans-serif; font-weight: 700; }
.titulo { font-family: 'Baloo 2', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("Red de Monitoreo Comunitario del Santuario de la Naturaleza Humedales de Angachilla")
st.caption("Monitoreo del agua en siete sitios del Santuario.")

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

# ---------- LINKS: coliformes ----------
COLIFORMES = {
    "Krahmer": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF1ytVbTax4MOv_LUW5Dv4jkqg6mWe5PeoCy1K6PMSNy8aF5db1Qmpfv3iLdIehCAvgMcmtadmLM7M/pub?gid=306852629&single=true&output=csv",
    "Catrico": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPuC4o1Naw-92olH3K_9a2mzowrAFDmVkJy3rEpECQPiQOjZUMe8O9PU7HZLiWyn6Js6w7wwjAeQAO/pub?gid=306852629&single=true&output=csv",
    "La Punta": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWtOZeSWAfDAix_FQQvIKgw2B8CSn-TIyJrjZtY3_JA6dEGri-_mkwm3EgGvqWpJ2dO0s02qV3UZeq/pub?gid=306852629&single=true&output=csv",
    "Los Conquistadores": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFraFOb66MaTlaG-KE1YO1sfciApaRM4U1IApgBVyypKgS-OcJ_YWk2PP2rOMbKD32uD2d3nX3HDRo/pub?gid=306852629&single=true&output=csv",
    "Rio Angachilla": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMCUsfdqFtgTdvPjhui17q8AjCh9t-3c7yzIyZ0j-nmAiDWYm3qSTCEllUTqhT4YXKleMXxoKb45Rd/pub?gid=306852629&single=true&output=csv",
    "Piedra Blanca": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTKd00e1SFLJiDHfNW3gei5fXmVBUuY8Z-T5DRyg_vb1LbMMVFETAIsdMHrDH6AWqmSU_IGLdJQi6OT/pub?gid=306852629&single=true&output=csv",
    "Catrico Pedro Montt": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQnxlCsxxiM2Lz3Lp_id5Keyu2x7jpulAkgfcgQiZ9EjLX8SzgDXZezK7nG6GS9AQdosXylXwmFOQKP/pub?gid=306852629&single=true&output=csv",
}

# ---------- COORDENADAS ----------
COORDS = {
    "Krahmer": (-39.833384, -73.231134),
    "Catrico": (-39.843039, -73.224381),
    "La Punta": (-39.854414, -73.241500),
    "Los Conquistadores": (-39.849651750128054, -73.21789481349317),
    "Rio Angachilla": (-39.879019, -73.238099),
    "Piedra Blanca": (-39.884594550392094, -73.13949290687675),
    "Catrico Pedro Montt": (-39.847258, -73.231716),
}

# ancho fijo de las barras (en milisegundos: 18 días)
BARRA_MS = 18 * 24 * 3600 * 1000

KEEP = ["Fecha", "Temp(aire)", "Temp(agua)", "PH",
        "Oxigeno 1 (ppm: línea de la jeringa)",
        "Oxigeno 2 (ppm: línea de la jeringa)",
        "Promedio Oxigeno", "Saturación Oxígeno (%)"]


# ---------- LECTURA Y LIMPIEZA DE DATOS ----------
def clean_site(url):
    df = pd.read_csv(url)
    df.columns = df.columns.astype(str).str.strip()

    def col_despues(prefijo):
        """Devuelve la columna que está justo después de la última
        columna cuyo nombre empieza con `prefijo`."""
        pos = [i for i, c in enumerate(df.columns) if c.startswith(prefijo)]
        if not pos or pos[-1] + 1 >= len(df.columns):
            return None
        return df.iloc[:, pos[-1] + 1]

    alcalinidad = col_despues("Alcalinidad")
    turbidez = col_despues("Turbidez")

    def col_por(cond):
        """Columna cuyo encabezado cumple `cond`. Busca en los nombres y en las 3 primeras
        filas, por si el encabezado ocupa dos filas en la planilla."""
        norm = lambda x: " ".join(str(x).split()).lower()
        for i, c in enumerate(df.columns):
            if cond(norm(c)):
                return df.iloc[:, i]
        for fila in range(min(3, len(df))):
            for i, v in enumerate(df.iloc[fila]):
                if cond(norm(v)):
                    return df.iloc[:, i]
        return None

    mes_eq = col_por(lambda t: "mes" in t and "equiv" in t)
    anio_eq = col_por(lambda t: "año" in t and "equiv" in t)

    df = df[[c for c in KEEP if c in df.columns]].copy()
    df["Alcalinidad"] = alcalinidad if alcalinidad is not None else float("nan")
    df["Turbidez"] = turbidez if turbidez is not None else float("nan")
    df["MesEq"] = mes_eq.astype(str).str.strip() if mes_eq is not None else ""
    df["AnioEq"] = anio_eq if anio_eq is not None else float("nan")

    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce", format="mixed")
    df = df.dropna(subset=["Fecha"])
    for col in df.columns:
        if col not in ("Fecha", "MesEq"):
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
    # la fila de encabezado real es la que contiene "E.Coli en 100"
    es_encabezado = raw.apply(
        lambda fila: fila.str.contains("E.Coli en 100", regex=False, na=False).any(),
        axis=1)
    if not es_encabezado.any():
        return pd.DataFrame(columns=["Fecha", "E.coli"])
    h = es_encabezado.idxmax()
    encabezado = raw.iloc[h].str.strip()
    c_fecha = encabezado[encabezado == "Fecha"].index[0]
    c_ecoli = encabezado[encabezado.str.contains("E.Coli en 100", regex=False, na=False)].index[0]

    def buscar(texto):
        ok = encabezado.str.lower().str.contains(texto, regex=False, na=False)
        return ok[ok].index[0] if ok.any() else None

    c_mes = buscar("mes equivalente")
    c_anio = buscar("año equivalente")

    datos = raw.loc[h + 1:]
    d = pd.DataFrame({
        "Fecha": pd.to_datetime(datos[c_fecha], dayfirst=True, errors="coerce", format="mixed"),
        "E.coli": pd.to_numeric(
            datos[c_ecoli].str.replace(",", ".", regex=False), errors="coerce"),
        "MesEq": datos[c_mes].str.strip() if c_mes is not None else "",
        "AnioEq": (pd.to_numeric(datos[c_anio], errors="coerce")
                   if c_anio is not None else float("nan")),
    })
    # Si las tarjetas 1, 2 y 3 están vacías, la muestra aún no se analiza: no es un 0
    tarjetas = datos[[c_ecoli - 3, c_ecoli - 2, c_ecoli - 1]]
    d = d[tarjetas.notna().any(axis=1)]
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


# ---------- CLASIFICACIÓN BACTERIOLÓGICA ----------
def clasificar(valor):
    """Bueno < 200 | Moderado 200-1000 | Malo > 1000 (por 100 mL)"""
    if pd.isna(valor):
        return "Sin datos"
    if valor < 200:
        return "Bueno"
    if valor <= 1000:
        return "Moderado"
    return "Malo"

ESTILOS_BADGE = {
    "Bueno": ("#E1F0E7", "#21613B", "#4FA774"),
    "Moderado": ("#FFF1D6", "#946414", "#E3A82B"),
    "Malo": ("#FBE5E3", "#A83228", "#CF4B3B"),
    "Sin datos": ("#EEEEEE", "#666666", "#999999"),
}


def badge_calidad(estado):
    bg, color, punto = ESTILOS_BADGE[estado]
    return (
        f'<span style="display:inline-flex;align-items:center;gap:8px;'
        f'background-color:{bg};color:{color};padding:4px 12px;border-radius:30px;'
        f'font-size:14px;font-weight:600;white-space:nowrap;">'
        f'<span style="width:10px;height:10px;min-width:10px;background-color:{punto};'
        f'border-radius:50%;"></span>{estado}</span>'
    )


def foto(sitio):
    ruta = f"fotos/{sitio.lower().replace(' ', '_')}.jpg"
    if os.path.exists(ruta):
        st.image(ruta, use_container_width=True)
    else:
        st.markdown(
            '<div style="height:120px;border-radius:10px;background:#CFE3D3;'
            'display:flex;align-items:center;justify-content:center;'
            'color:#2B4A38;font-size:13px;">Foto del humedal</div>',
            unsafe_allow_html=True)


def posicion(v):
    """Posición del marcador en la barra, 0-100. Cada zona ocupa un tercio."""
    if v < 200:
        return v / 200 * 33.3
    if v <= 1000:
        return 33.3 + (v - 200) / 800 * 33.3
    return 66.6 + min(math.log10(v / 1000) / 2, 1) * 33.4


def medidor(v):
    p = posicion(v)
    return (
        '<div style="position:relative;height:8px;border-radius:99px;margin:14px 0 6px;'
        'background:linear-gradient(to right,#4FA774 0 33.3%,#E3A82B 33.3% 66.6%,#CF4B3B 66.6% 100%);">'
        f'<div style="position:absolute;top:-4px;left:{p}%;width:4px;height:16px;'
        'background:#1B2A33;border-radius:2px;"></div></div>'
    )


# ---------- TARJETAS DE PARÁMETROS ----------
def fmt(v, dec=1):
    return "—" if pd.isna(v) else f"{v:.{dec}f}".replace(".", ",")


def estado_rango(v, minimo, maximo):
    if pd.isna(v):
        return "info"
    if v < minimo:
        return "bajo"
    if v > maximo:
        return "alto"
    return "ok"


# (color de la barra superior, texto, fondo de la etiqueta, color del texto)
ESTADOS = {
    "ok": ("#4FA774", "En rango", "#E1F0E7", "#21613B"),
    "bajo": ("#E3A82B", "Bajo el rango", "#FFF1D6", "#946414"),
    "alto": ("#E3A82B", "Sobre el rango", "#FFF1D6", "#946414"),
    "info": ("#6BB0D1", None, None, None),
}


def desc_turbidez(v):
    if pd.isna(v):
        return "Sin datos"
    return "Agua clara" if v <= 5 else "Agua turbia"


def tarjeta(titulo, valor, unidad, detalle, estado="info", dec=1):
    color, etiqueta, bg, fg = ESTADOS[estado]
    pill = (
        f'<div><span style="display:inline-block;background:{bg};color:{fg};'
        f'font-size:14px;font-weight:600;border-radius:99px;padding:3px 12px;'
        f'margin-top:8px;">{etiqueta}</span></div>' if etiqueta else ""
    )
    return (
        f'<div style="background:#fff;border:1px solid #DDE6DE;border-top:6px solid {color};'
        f'border-radius:16px;padding:14px 20px 16px;min-height:150px;margin-bottom:12px;">'
        f'<div style="font-size:16px;font-weight:600;color:#3A4D55;">{titulo}</div>'
        f'<div class="titulo" style="font-size:40px;font-weight:700;'
        f'color:#1B2A33;line-height:1.2;">{fmt(valor, dec)}'
        f'<span style="font-size:16px;margin-left:6px;">{unidad}</span></div>'
        f'<div style="font-size:14px;color:#4A5B63;">{detalle}</div>'
        f'{pill}</div>'
    )


# ---------- MACROINVERTEBRADOS ----------
MACRO = {
    "Krahmer": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF1ytVbTax4MOv_LUW5Dv4jkqg6mWe5PeoCy1K6PMSNy8aF5db1Qmpfv3iLdIehCAvgMcmtadmLM7M/pub?gid=554481310&single=true&output=csv",
    "Catrico": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQPuC4o1Naw-92olH3K_9a2mzowrAFDmVkJy3rEpECQPiQOjZUMe8O9PU7HZLiWyn6Js6w7wwjAeQAO/pub?gid=554481310&single=true&output=csv",
    "La Punta": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRWtOZeSWAfDAix_FQQvIKgw2B8CSn-TIyJrjZtY3_JA6dEGri-_mkwm3EgGvqWpJ2dO0s02qV3UZeq/pub?gid=554481310&single=true&output=csv",
    "Los Conquistadores": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFraFOb66MaTlaG-KE1YO1sfciApaRM4U1IApgBVyypKgS-OcJ_YWk2PP2rOMbKD32uD2d3nX3HDRo/pub?gid=554481310&single=true&output=csv",
    "Rio Angachilla": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMCUsfdqFtgTdvPjhui17q8AjCh9t-3c7yzIyZ0j-nmAiDWYm3qSTCEllUTqhT4YXKleMXxoKb45Rd/pub?gid=554481310&single=true&output=csv",
    "Piedra Blanca": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTKd00e1SFLJiDHfNW3gei5fXmVBUuY8Z-T5DRyg_vb1LbMMVFETAIsdMHrDH6AWqmSU_IGLdJQi6OT/pub?gid=554481310&single=true&output=csv",
    "Catrico Pedro Montt": "PASTE_LINK",
}

# Nombres comunes opcionales. Clave = encabezado de la planilla en minúsculas.
NOMBRES = {
    "mollusca caracol(izq) physidae": "Caracoles (Physidae)",
    "sanguijuela": "Sanguijuelas",
    "lombriz de agua": "Lombrices de agua",
    "diptera; chironomidae": "Quironómidos (larvas)",
    "amphipoda; hyalellidae": "Pulgas de agua (Hyalella)",
}

# grupo: (nombre, color de fondo, color de texto)
GRUPOS = {
    1: ("sensibles", "#3A7D52", "#FFFFFF"),
    2: ("tolerantes", "#7CBF86", "#1B2A33"),
    3: ("resistentes", "#CBE8B8", "#1F4D2B"),
}

CLASES = [("Pobre", "menos de 11", "#C0392B"), ("Regular", "11 a 16", "#E0A030"),
          ("Bueno", "17 a 22", "#7DB66B"), ("Excelente", "más de 22", "#2F7D52")]
# text color to use on top of each class color (white on the dark red and dark green)
TXT_CLASE = {"Pobre": "#FFFFFF", "Regular": "#1B2A33", "Bueno": "#1B2A33", "Excelente": "#FFFFFF"}
COLOR_CLASE_TXT = {"Pobre": "#C0392B", "Regular": "#B7791F", "Bueno": "#4F8F2F", "Excelente": "#1F6B4A"}
COLOR_CLASE_BARRA = {"Pobre": "#C0392B", "Regular": "#E0A030", "Bueno": "#7DB66B", "Excelente": "#2F7D52"}

def _txt(x):
    return " ".join(str(x).split()) if pd.notna(x) else ""


def clean_macro(url):
    """Lee la pestaña de macroinvertebrados. Devuelve (índices, taxones) o lanza ValueError."""
    raw = pd.read_csv(url, header=None, dtype=str)
    texto = raw.apply(lambda col: col.map(_txt))
    norm = texto.apply(lambda col: col.str.lower())

    def es_indice(t):
        return "acumulado" in t and ("mero" in t or "texto" in t)

    # la fila de encabezados es la que tiene "Indice acumulado número/texto"
    cand = norm.apply(lambda f: any(es_indice(t) for t in f), axis=1)
    if not cand.any():
        cand = norm.apply(lambda f: f.str.contains("ndice", regex=False).any(), axis=1)
    if not cand.any():
        celdas = [c for c in texto.iloc[:4].values.ravel() if c][:10]
        raise ValueError(
            f"No encontré la fila con 'Indice acumulado'. La pestaña tiene {raw.shape[0]} filas y "
            f"{raw.shape[1]} columnas. Primeras celdas: {celdas}. "
            "Probablemente el enlace corresponde a otra pestaña.")
    h = cand.idxmax()
    enc, nom = norm.iloc[h], texto.iloc[h]
    datos = raw.iloc[h + 1:]

    def donde(cond):
        return [c for c in enc.index if cond(enc[c])]

    def num(c):
        return pd.to_numeric(datos[c].str.replace(",", ".", regex=False), errors="coerce")

    c_fecha = donde(lambda t: t == "fecha")
    c_idx = donde(lambda t: "acumulado" in t and "mero" in t)
    c_txt = donde(lambda t: "acumulado" in t and "texto" in t)
    c_obs = donde(lambda t: t.replace(" ", "").startswith("observaci"))
    c_mes = donde(lambda t: "mes equivalente" in t)
    c_anio = donde(lambda t: "año" in t and "equiv" in t)
    if not (c_idx and c_txt):
        # encabezados con otro nombre: usar las columnas "índice" y decidir por los datos
        cols_i = donde(lambda t: "ndice" in t)
        numericas = [c for c in cols_i if num(c).notna().any()]
        if numericas:
            c_idx, c_txt = numericas[:1], [max(cols_i)]
    if not (c_fecha and c_idx and c_txt):
        raise ValueError(
            "Encontré la fila de encabezados pero faltan columnas: "
            f"Fecha={bool(c_fecha)}, Indice número={bool(c_idx)}, Indice texto={bool(c_txt)}. "
            f"Encabezados de esa fila: {[c for c in nom if c][:25]}")
    c_txt = c_txt[0]
    totales = [c for c in donde(lambda t: t.startswith("total")) if c > c_txt]
    if len(totales) < 3:
        raise ValueError(
            f"Esperaba 3 columnas 'Total N°Individuo' después del índice y encontré {len(totales)}. "
            f"Encabezados de esa fila: {[c for c in nom if c][:25]}")

    fechas = pd.to_datetime(datos[c_fecha[0]], dayfirst=True, errors="coerce", format="mixed")
    ok = fechas.notna()
    datos, fechas = datos[ok], fechas[ok]

    obs = datos[c_obs[0]].map(_txt) if c_obs else ""
    mes_eq = datos[c_mes[0]].map(_txt) if c_mes else ""
    anio_eq = (pd.to_numeric(datos[c_anio[0]], errors="coerce")
               if c_anio else float("nan"))
    indices = pd.DataFrame({"Fecha": fechas, "Indice": num(c_idx[0]), "Obs": obs,
                            "MesEq": mes_eq, "AnioEq": anio_eq})
    # Grupo 1: entre el índice y el primer "Total"; grupos 2 y 3: tras cada "Total"
    # (se salta la columna "N° Familias") hasta el siguiente "Total".
    rangos = {1: range(c_txt + 1, totales[0]),
              2: range(totales[0] + 2, totales[1]),
              3: range(totales[1] + 2, totales[2])}
    partes = []
    for g, rango in rangos.items():
        for c in rango:
            if nom[c]:
                partes.append(pd.DataFrame(
                    {"Fecha": fechas, "Taxon": nom[c], "Grupo": g, "Cantidad": num(c)}))
    if partes:
        taxa = pd.concat(partes, ignore_index=True)
        taxa = taxa[taxa["Cantidad"] > 0]
    else:
        taxa = pd.DataFrame(columns=["Fecha", "Taxon", "Grupo", "Cantidad"])
    return indices, taxa


@st.cache_data(ttl=3600)
def load_macro():
    idx, tax = [], []
    for site, url in MACRO.items():
        if url.startswith("PASTE"):
            continue
        try:
            i, t = clean_macro(url)
        except Exception:
            continue
        i["Sitio"], t["Sitio"] = site, site
        idx.append(i)
        tax.append(t)
    if not idx:
        return (pd.DataFrame(columns=["Fecha", "Indice", "Obs", "MesEq", "AnioEq", "Sitio"]),
                pd.DataFrame(columns=["Fecha", "Taxon", "Grupo", "Cantidad", "Sitio"]))
    return pd.concat(idx, ignore_index=True), pd.concat(tax, ignore_index=True)


def clase_indice(v):
    """Pobre < 11 | Regular 11-16 | Bueno 17-22 | Excelente > 22"""
    if pd.isna(v):
        return None
    if v < 11:
        return "Pobre"
    if v <= 16:
        return "Regular"
    if v <= 22:
        return "Bueno"
    return "Excelente"


def nombre_taxon(t):
    return NOMBRES.get(t.lower(), t)


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", t).strip("_")


def _tipos(k):
    return f"{k} tipo" + ("" if k == 1 else "s")


def numero_indice(v, clase):
    color = COLOR_CLASE_TXT.get(clase, "#1B2A33")
    return (
        f'<div class="titulo" style="font-size:72px;line-height:1;font-weight:800;color:{color};">{fmt(v, 0)}</div>'
        '<div style="font-size:15px;color:#4A5B63;">índice acumulado</div>'
    )


def tiles_clase(clase):
    h = ""
    for nombre, rango, color in CLASES:
        sel = nombre == clase
        borde = "3px solid #1B2A33" if sel else "3px solid transparent"
        h += (f'<div style="flex:1;background:{color};border:{borde};opacity:{1 if sel else 0.55};'
              f'border-radius:14px;padding:10px 6px;text-align:center;color:{TXT_CLASE[nombre]};">'
              f'<div style="font-size:13px;">{rango}</div></div>')
    return f'<div style="display:flex;gap:10px;">{h}</div>'


def frase_macro(g):
    if not g:
        return "En este muestreo no se registraron organismos."
    if 1 in g:
        return "Encontramos organismos sensibles a la contaminación (grupo 1), una buena señal para el humedal."
    lista = " y ".join(str(x) for x in sorted(g))
    de = f"de los grupos {lista}" if len(g) > 1 else f"del grupo {lista}"
    return f"En este muestreo solo encontramos organismos {de}, que toleran agua con más contaminación."


def barra_grupos(n):
    pesos = {1: 3, 2: 2, 3: 1}
    mas = '<div style="align-self:center;font-size:24px;font-weight:700;color:#4A5B63;">+</div>'
    cajas = []
    for g in (1, 2, 3):
        nombre, bg, fg = GRUPOS[g]
        if n[g]:
            estilo = f"flex:{n[g]};background:{bg};color:{fg};"
        else:
            estilo = "flex:0 0 130px;background:#F1F5F1;color:#4A5B63;border:2px dashed #BFD2C3;"
        cajas.append(
            f'<div style="{estilo}min-width:130px;border-radius:12px;padding:12px 14px;box-sizing:border-box;">'
            f'<div style="font-size:13px;font-weight:700;">Grupo {g} · {nombre}</div>'
            f'<div style="font-size:15px;margin-top:4px;">{_tipos(n[g])} × {pesos[g]}</div>'
            f'<div class="titulo" style="font-size:26px;font-weight:700;">{n[g] * pesos[g]}'
            f'<span style="font-size:14px;font-weight:600;"> puntos</span></div></div>')
    total = sum(n[g] * pesos[g] for g in (1, 2, 3))
    caja_total = (
        '<div style="flex:0 0 170px;background:#E3EFE6;border-radius:12px;padding:12px 14px;'
        'box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;">'
        '<div style="font-size:13px;font-weight:700;color:#3A4D55;">Índice acumulado</div>'
        f'<div class="titulo" style="font-size:32px;font-weight:800;">= {total}</div></div>')
    return ('<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:stretch;">'
            + mas.join(cajas) + caja_total + '</div>')

def badge_grupo(g):
    _, bg, fg = GRUPOS[g]
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font-size:13px;'
            f'font-weight:700;border-radius:99px;padding:2px 10px;">Grupo {g}</span>')

def diagnostico_macro(sitio):
    url = MACRO.get(sitio, "PASTE_LINK")
    if url.startswith("PASTE"):
        return "No hay enlace para este sitio en MACRO (sigue como PASTE_LINK)."
    try:
        i, t = clean_macro(url)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"No se pudo leer el enlace: {e}"
    return (f"Lectura correcta: {len(i)} muestreos, pero ninguno tiene un valor en "
            "'Indice acumulado número'.")



def foto_taxon(taxon, g):
    path = f"fotos_macro/{slug(taxon)}.jpg"

    if os.path.exists(path):
        img = Image.open(path).convert("RGB")

        # Resize while preserving the original proportions
        img.thumbnail((360, 360))

        # Create a consistent white square background
        canvas = Image.new("RGB", (400, 400), "white")

        # Center the organism without cropping
        x = (400 - img.width) // 2
        y = (400 - img.height) // 2

        canvas.paste(img, (x, y))

        st.image(canvas, width=250)

from pathlib import Path

# ---------- PANEL E. COLI ----------
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# (nombre, rango, color de fondo, color de texto)
NIVELES_ECOLI = [
    ("Bueno", "0 a 200", "#2F7D52", "#FFFFFF"),
    ("Moderado", "200 a 1.000", "#E0A030", "#1B2A33"),
    ("Malo", "más de 1.000", "#C0392B", "#FFFFFF"),
]
COLOR_ECOLI_TXT = {"Bueno": "#2F7D52", "Moderado": "#B7791F", "Malo": "#C0392B"}


def panel_ecoli(valor, etiqueta):
    clase = clasificar(valor)
    num = f"{valor:,.0f}".replace(",", ".")
    mes = etiqueta
    tiles = ""
    for nombre, rango, bg, fg in NIVELES_ECOLI:
        sel = nombre == clase
        marca = (
            '<div style="position:absolute;top:-36px;left:50%;transform:translateX(-50%);'
            'background:#1B2A33;color:#fff;font-size:14px;font-weight:700;border-radius:8px;'
            f'padding:3px 12px;white-space:nowrap;">{mes}</div>'
            '<div style="position:absolute;top:-11px;left:50%;width:10px;height:10px;'
            'background:#1B2A33;transform:translateX(-50%) rotate(45deg);"></div>'
        ) if sel else ""
        borde = "3px solid #1B2A33" if sel else "3px solid transparent"
        tiles += (
            f'<div style="flex:1;position:relative;background:{bg};color:{fg};border:{borde};'
            f'opacity:{1 if sel else 0.4};border-radius:14px;padding:14px 8px;text-align:center;">'
            f'{marca}<div style="font-weight:700;font-size:17px;">{nombre}</div>'
            f'<div style="font-size:14px;">{rango}</div></div>')
    return (
        '<div style="background:#fff;border:1px solid #DDE6DE;border-radius:20px;padding:24px 28px;">'
        '<div style="display:flex;align-items:flex-end;gap:16px;flex-wrap:wrap;">'
        f'<div class="titulo" style="font-size:88px;line-height:.9;font-weight:800;'
        f'color:{COLOR_ECOLI_TXT[clase]};">{num}</div>'
        '<div style="font-size:18px;color:#3A4D55;padding-bottom:6px;">colonias en<br>100 mL de agua</div></div>'
        f'<div style="display:flex;gap:12px;margin-top:52px;">{tiles}</div></div>'
    )

MESES_ABR = {"ene": "enero", "feb": "febrero", "mar": "marzo", "abr": "abril", "may": "mayo",
             "jun": "junio", "jul": "julio", "ago": "agosto", "sep": "septiembre",
             "set": "septiembre", "oct": "octubre", "nov": "noviembre", "dic": "diciembre"}


def etiqueta_mes(fila):
    anio, mes = clave_mes(fila)
    return f"{MESES[mes - 1]} {anio}"

def clave_mes(fila):
    """(año, mes) al que pertenece el muestreo, según 'Mes equivalente' y 'Año equivalente'.
    Si faltan, usa la Fecha."""
    v = str(fila.get("MesEq", "")).strip().lower()
    if v.replace(".0", "").isdigit() and 1 <= int(float(v)) <= 12:
        mes = int(float(v))
    else:
        nombre = MESES_ABR.get(v[:3])
        mes = MESES.index(nombre) + 1 if nombre else fila["Fecha"].month
    anio = fila.get("AnioEq")
    anio = int(anio) if pd.notna(anio) else fila["Fecha"].year
    return (anio, mes)


def meses_sin_datos(c_sitio):
    """Fechas (día 28) de los meses sin ninguna medición entre la primera y la última."""
    claves = [clave_mes(r) for _, r in c_sitio.iterrows()]
    if not claves:
        return []
    presentes = set(claves)
    a, m = min(claves)
    fin = max(claves)
    faltan = []
    while (a, m) <= fin:
        if (a, m) not in presentes:
            faltan.append(pd.Timestamp(year=a, month=m, day=28))
        m += 1
        if m > 12:
            a, m = a + 1, 1
    return faltan


def con_mes(d):
    """Agrega la columna 'Mes': primer día del mes equivalente de cada muestreo."""
    d = d.copy()
    d["Mes"] = pd.to_datetime([pd.Timestamp(year=a, month=m, day=1)
                               for a, m in (clave_mes(r) for _, r in d.iterrows())])
    return d


def nombre_mes(ts):
    return f"{MESES[ts.month - 1]} {ts.year}"


def recorte(d, meses, fin):
    """Deja los últimos `meses` meses equivalentes, contando hacia atrás desde `fin`."""
    if meses is None or d.empty:
        return d
    return d[d["Mes"] >= fin - pd.DateOffset(months=meses - 1)]


def un_dato_por_mes(d):
    """Si dos muestreos caen en el mismo mes equivalente, deja el más reciente."""
    return d.sort_values("Fecha").drop_duplicates("Mes", keep="last")


def eje_meses(d):
    """Todos los meses entre el primero y el último con datos (incluye meses sin datos)."""
    if d.empty:
        return []
    return list(pd.date_range(d["Mes"].min(), d["Mes"].max(), freq="MS"))

def texto_ecoli(valor):
    clase = clasificar(valor)
    return (
        f'<p style="font-size:17px;line-height:1.5;margin:12px 0 0;">'
        f'<b style="color:{COLOR_ECOLI_TXT[clase]};">{clase}.</b> '
        '<i>E. coli</i> es una bacteria que indica contaminación de origen fecal. '
        'Sobre 1.000 colonias, el agua es peligrosa para el contacto humano.</p>'
    )

def fila_indice(sitio, v, clase, etiqueta):
    if v is None:
        centro = "<div></div>"
        pill = '<span style="font-size:13px;color:#4A5B63;">Sin datos</span>'
        mes = ""
    else:
        ancho = min(v / 25, 1) * 100
        ticks = "".join(
            f'<i style="position:absolute;top:-2px;left:{p}%;width:2px;height:16px;background:#9DBB9D;"></i>'
            for p in (44, 68, 88))
        centro = ('<div style="position:relative;height:12px;background:#EAF0EA;border-radius:99px;">'
                  f'<div style="width:{ancho}%;height:100%;background:{COLOR_CLASE_BARRA[clase]};'
                  f'border-radius:99px;"></div>{ticks}</div>')
        bg = COLOR_CLASE_BARRA[clase]
        pill = (f'<span style="display:inline-block;background:{bg};color:{TXT_CLASE[clase]};font-size:13px;'
                f'font-weight:600;border-radius:99px;padding:3px 12px;white-space:nowrap;">'
                f'{clase} · {fmt(v, 0)}</span>')
        mes = etiqueta
    return (
        '<div style="display:grid;grid-template-columns:minmax(110px,150px) 1fr 140px 120px;gap:12px;'
        'align-items:center;padding:9px 0;border-bottom:1px solid #EEF3EE;">'
        f'<span class="titulo" style="font-size:17px;font-weight:700;">{sitio}</span>'
        f'{centro}<div style="text-align:right;">{pill}</div>'
        f'<span style="font-size:13px;color:#4A5B63;text-align:right;">{mes}</span></div>')

# ---------- CARGA ----------
df = load_all()
dfc = load_coli()
dfm_i, dfm_t = load_macro()
df, dfc, dfm_i = con_mes(df), con_mes(dfc), con_mes(dfm_i)

tab1, tab2 = st.tabs(["Resumen", "Detalle por sitio"])

# =====================================================
# PESTAÑA 1: RESUMEN
# =====================================================
with tab1:
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

#
    cols = st.columns(3)
    for i, (sitio, fila) in enumerate(ultimo.iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                foto(sitio)

                tiene_coli = sitio in ultimo_coli.index
                valor = ultimo_coli.loc[sitio, "E.coli"] if tiene_coli else None
                est = clasificar(valor) if tiene_coli else "Sin datos"

                # nombre a la izquierda, etiqueta de calidad a la derecha
                st.markdown(
                    '<div style="display:flex;justify-content:space-between;'
                    'align-items:center;gap:8px;flex-wrap:wrap;">'
                    '<span class="titulo" style="font-size:20px;'
                    f'font-weight:700;">{sitio}</span>'
                    f'{badge_calidad(est)}</div>',
                    unsafe_allow_html=True)

                st.caption(f"Último muestreo: {fila['Fecha']:%d-%m-%Y}")

                m1, m2, m3 = st.columns(3)
                m1.metric("pH", f"{fila['PH']:.1f}")
                m2.metric("Temp. del agua", f"{fila['Temp(agua)']:.1f} °C")
                m3.metric("O₂ mg/L", f"{fila['Promedio Oxigeno']:.1f}")

                if tiene_coli:
                    st.markdown(medidor(valor), unsafe_allow_html=True)
                    st.caption(f"E. coli: {valor:,.0f} /100 mL".replace(",", "."))

    # ----- última fila: sitio con solo E. coli + índices de macroinvertebrados -----
    SOLO_ECOLI = "Catrico Pedro Montt"
    ult_macro = (dfm_i.dropna(subset=["Indice"])
                      .sort_values("Fecha")
                      .groupby("Sitio")
                      .tail(1)
                      .set_index("Sitio"))

    col_pm, col_idx = st.columns([1, 2])

    with col_pm:
        with st.container(border=True):
            foto(SOLO_ECOLI)
            tiene_pm = SOLO_ECOLI in ultimo_coli.index
            v_pm = ultimo_coli.loc[SOLO_ECOLI, "E.coli"] if tiene_pm else None
            est_pm = clasificar(v_pm) if tiene_pm else "Sin datos"

            st.markdown(
                '<div style="display:flex;justify-content:space-between;'
                'align-items:center;gap:8px;flex-wrap:wrap;">'
                '<span class="titulo" style="font-size:20px;'
                f'font-weight:700;">{SOLO_ECOLI}</span>'
                f'{badge_calidad(est_pm)}</div>',
                unsafe_allow_html=True)

            if tiene_pm:
                f_pm = ultimo_coli.loc[SOLO_ECOLI, "Fecha"]
                st.caption(f"Último muestreo: {f_pm:%d-%m-%Y}")
                st.markdown(medidor(v_pm), unsafe_allow_html=True)
                st.caption(f"E. coli: {v_pm:,.0f} /100 mL".replace(",", "."))
            st.caption("En este sitio solo se mide E. coli.")

    with col_idx:
        with st.container(border=True):
            st.markdown("**Índice de macroinvertebrados de cada sitio**")
            st.caption("Último muestreo de cada sitio · Pobre < 11 · Regular 11–16 · "
                       "Bueno 17–22 · Excelente > 22")
            filas = ""
            for s in ultimo.index:
                if s in ult_macro.index:
                    r = ult_macro.loc[s]
                    filas += fila_indice(s, r["Indice"], clase_indice(r["Indice"]), etiqueta_mes(r))
                else:
                    filas += fila_indice(s, None, None, "")
            st.markdown(filas, unsafe_allow_html=True)

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
            font_family='"\'Baloo 2\', sans-serif"',
            font_weight=700,
            character_set='"auto"',
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
                tooltip={"text": "{Sitio}",
                         "style": {"fontFamily": "'Baloo 2', sans-serif", "fontSize": "14px"}},
                map_style="light",
            ),
            use_container_width=True,
        )

# =====================================================
# PESTAÑA 2: DETALLE POR SITIO
# =====================================================
with tab2:
    opciones = {
        "Último mes": 1,
        "Últimos 3 meses": 3,
        "Últimos 6 meses": 6,
        "Último año": 12,
        "Todo el período": None,
    }

    def grafico_linea(col, titulo, sd, columna, meses_x):
        col.write(titulo)
        serie = sd.set_index("Mes")[columna].dropna()
        if serie.empty:
            col.caption("Sin datos en este período")
            return
        etiquetas = [nombre_mes(m) for m in meses_x]
        fig = go.Figure(go.Scatter(
            x=etiquetas,
            y=[serie.get(m) for m in meses_x],
            mode="lines+markers", connectgaps=False,
            line=dict(color="#2F6B4F", width=2),
            hovertemplate="%{x}: %{y}<extra></extra>"))
        # --- marca "S/D" en los meses sin dato de este parámetro ---
        for m, x in zip(meses_x, etiquetas):
            if m not in serie.index:
                fig.add_annotation(
                    x=x, xref="x", y=0, yref="paper",
                    text="<b>S/D</b>", showarrow=False,
                    yanchor="bottom", yshift=3, font=dict(size=11, color="#6B7B72"))
        fig.update_xaxes(type="category")
        fig.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        col.plotly_chart(fig, use_container_width=True, key=f"linea_{columna}")

    a, _ = st.columns(2)
    todos = sorted(set(df["Sitio"]) | set(dfc["Sitio"]))
    sitio = a.selectbox("Elige un humedal", todos)

    # ===== 1. ÚLTIMA MEDICIÓN (tarjetas) =====
    st.subheader(f"Monitoreo Físicoquimico – {sitio}")
    ult = (df[df["Sitio"] == sitio]
           .dropna(subset=["PH"])
           .sort_values("Fecha")
           .tail(1))

    if ult.empty:
        st.info("No hay mediciones físico-químicas para este sitio.")
    else:
        f = ult.iloc[0]
        st.caption(f"Muestreo del {f['Fecha']:%d-%m-%Y}")

        fila1 = st.columns(3)
        fila2 = st.columns(3)

        fila1[0].markdown(
            tarjeta("pH", f.get("PH"), "", "Óptimo 6,5 a 8,5",
                    estado_rango(f.get("PH"), 6.5, 8.5)),
            unsafe_allow_html=True)
        fila1[1].markdown(
            tarjeta("Oxígeno disuelto", f.get("Promedio Oxigeno"), "ppm",
                    "Óptimo 4 a 11 ppm",
                    estado_rango(f.get("Promedio Oxigeno"), 4, 11)),
            unsafe_allow_html=True)
        fila1[2].markdown(
            tarjeta("Alcalinidad", f.get("Alcalinidad"), "mg/L",
                    "Óptimo 30 a 150 mg/L",
                    estado_rango(f.get("Alcalinidad"), 30, 150), dec=0),
            unsafe_allow_html=True)

        fila2[0].markdown(
            tarjeta("Turbidez", f.get("Turbidez"), "JTU",
                    desc_turbidez(f.get("Turbidez")), dec=0),
            unsafe_allow_html=True)
        fila2[1].markdown(
            tarjeta("Temp. del agua", f.get("Temp(agua)"), "°C", "Informativo"),
            unsafe_allow_html=True)
        fila2[2].markdown(
            tarjeta("Temp. del aire", f.get("Temp(aire)"), "°C", "Informativo"),
            unsafe_allow_html=True)

    # ===== 2. ANÁLISIS BACTERIOLÓGICO (panel con números) =====
    st.subheader(f"Análisis bacteriológico – {sitio}")
    c_sitio = dfc[dfc["Sitio"] == sitio].sort_values("Fecha")

    if c_sitio.empty:
        st.info("No hay datos bacteriológicos para este sitio.")
    else:
        fechas_c = list(c_sitio["Fecha"].sort_values(ascending=False))
        etiquetas_c = {r["Fecha"]: etiqueta_mes(r) for _, r in c_sitio.iterrows()}
        fecha_c = st.selectbox("Mes de muestreo (E. coli)", fechas_c,
                               format_func=lambda d: etiquetas_c[d].capitalize(),
                               key=f"muestreo_ecoli_{sitio}")
        fila_c = c_sitio[c_sitio["Fecha"] == fecha_c].iloc[0]
        valor_c = fila_c["E.coli"]
        st.markdown(panel_ecoli(valor_c, etiqueta_mes(fila_c)), unsafe_allow_html=True)
        st.markdown(texto_ecoli(valor_c), unsafe_allow_html=True)

    # ===== 3. MACROINVERTEBRADOS (índice y organismos) =====
    st.subheader(f"Macroinvertebrados – {sitio}")
    mi = dfm_i[dfm_i["Sitio"] == sitio].dropna(subset=["Indice"]).sort_values("Fecha")

    if mi.empty:
        st.info("Aún no hay datos de macroinvertebrados para este sitio.")
    else:
        fechas_m = list(mi["Fecha"].sort_values(ascending=False))
        etiquetas_m = {r["Fecha"]: etiqueta_mes(r) for _, r in mi.iterrows()}
        fecha_sel = st.selectbox("Mes de muestreo", fechas_m,
                                 format_func=lambda d: etiquetas_m[d].capitalize())
        fila_m = mi[mi["Fecha"] == fecha_sel].iloc[0]
        indice = fila_m["Indice"]
        clase = clase_indice(indice)

        tx = (dfm_t[(dfm_t["Sitio"] == sitio) & (dfm_t["Fecha"] == fecha_sel)]
              .sort_values(["Grupo", "Cantidad"], ascending=[True, False]))
        cuenta = tx["Grupo"].value_counts()
        n = {g: int(cuenta.get(g, 0)) for g in (1, 2, 3)}

        izq, der = st.columns([1, 2])
        with izq:
            st.markdown(numero_indice(indice, clase), unsafe_allow_html=True)
        with der:
            st.markdown(tiles_clase(clase), unsafe_allow_html=True)
            st.markdown(frase_macro({g for g in n if n[g]}))

        st.markdown("**Tipos de organismos por grupo de tolerancia y cálculo del índice**")
        st.caption("Cada tipo de organismo encontrado suma 3 puntos si es del grupo 1, "
                   "2 puntos si es del grupo 2 y 1 punto si es del grupo 3.")
        st.markdown(barra_grupos(n), unsafe_allow_html=True)
        if pd.notna(indice) and sum(n[g] * p for g, p in ((1, 3), (2, 2), (3, 1))) != indice:
            st.caption(f"Nota: el índice registrado en la planilla es {indice:.0f}.")

        if not tx.empty:
            st.markdown("**Encontramos en este muestreo**")
            for ini in range(0, len(tx), 4):
                cols_m = st.columns(4)
                for col, (_, t) in zip(cols_m, tx.iloc[ini:ini + 4].iterrows()):
                    with col:
                        with st.container(border=True):
                            foto_taxon(t["Taxon"], int(t["Grupo"]))
                            st.markdown(f"**{nombre_taxon(t['Taxon'])}**")
                            st.markdown(
                                badge_grupo(int(t["Grupo"]))
                                + f' <span style="font-size:13px;color:#4A5B63;">× {int(t["Cantidad"])}</span>',
                                unsafe_allow_html=True)

        if str(fila_m["Obs"]).strip():
            st.caption(f"Observaciones del muestreo: {fila_m['Obs']}")

    # ===== 4. GRÁFICOS =====
    st.subheader(f"Gráficos – {sitio}")
    p, _ = st.columns(2)
    periodo = p.selectbox("Período de los gráficos", list(opciones.keys()), index=4)
    meses = opciones[periodo]

    # ----- gráficos físico-químicos -----
    st.markdown("**Gráficos de los parámetros físico-químicos**")
    st.caption("**S/D**: sin datos de ese mes")
    sd = un_dato_por_mes(recorte(df[df["Sitio"] == sitio], meses, df["Mes"].max()))

    if sd.empty:
        st.info("No hay datos físico-químicos para este sitio en el período elegido.")
    else:
        meses_fq = eje_meses(sd)
        gf1 = st.columns(3)
        gf2 = st.columns(3)
        grafico_linea(gf1[0], "pH", sd, "PH", meses_fq)
        grafico_linea(gf1[1], "Temperatura del agua (°C)", sd, "Temp(agua)", meses_fq)
        grafico_linea(gf1[2], "Oxígeno (ppm)", sd, "Promedio Oxigeno", meses_fq)
        grafico_linea(gf2[0], "Alcalinidad (mg/L)", sd, "Alcalinidad", meses_fq)
        grafico_linea(gf2[1], "Turbidez (JTU)", sd, "Turbidez", meses_fq)
        grafico_linea(gf2[2], "Temperatura del aire (°C)", sd, "Temp(aire)", meses_fq)

    # ----- gráfico del E. coli -----
    st.markdown("**Gráfico del E. coli**")
    st.caption("E. coli por 100 mL · Bueno: < 200 · Moderado: 200–1000 · Malo: > 1000")

    sc = un_dato_por_mes(recorte(dfc[dfc["Sitio"] == sitio], meses, dfc["Mes"].max()))

    if sc.empty:
        st.info("No hay datos bacteriológicos para este sitio en el período elegido.")
    else:
        meses_c = eje_meses(sc)
        orden = [nombre_mes(m) for m in meses_c]
        graf = sc[sc["E.coli"] > 0].copy()
        graf["MesTxt"] = graf["Mes"].map(nombre_mes)
        graf["Calidad"] = graf["E.coli"].apply(clasificar)
        st.caption("**0**: no se encontraron colonias · **S/D**: sin datos de ese mes")

        tope = max(graf["E.coli"].max() if not graf.empty else 0, 1000)

        fig = px.bar(
            graf, x="MesTxt", y="E.coli", log_y=True,
            color="Calidad",
            color_discrete_map={"Bueno": "#2E8B57",
                                "Moderado": "#E0A030",
                                "Malo": "#C0392B"},
            category_orders={"MesTxt": orden, "Calidad": ["Bueno", "Moderado", "Malo"]},
            labels={"E.coli": "E. coli por 100 mL (escala logarítmica)", "MesTxt": ""},
            hover_data={"Fecha": "|%d-%m-%Y", "MesTxt": False},
        )
        fig.update_layout(barmode="overlay")
        # traza invisible para que aparezcan todos los meses, aunque no tengan barra
        fig.add_trace(go.Scatter(x=orden, y=[None] * len(orden), mode="markers",
                                 showlegend=False, hoverinfo="skip"))
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=orden)
        fig.add_hline(y=200, line_dash="dash", line_color="#E0A030")
        fig.add_hline(y=1000, line_dash="dash", line_color="#C0392B")
        fig.update_yaxes(range=[0, math.ceil(math.log10(tope))])

        # --- marcas "0" y "S/D" sobre el eje ---
        con_datos = set(sc["Mes"])
        marcas = [(nombre_mes(m), "0", "#2E8B57") for m in sc.loc[sc["E.coli"] == 0, "Mes"]]
        marcas += [(nombre_mes(m), "S/D", "#6B7B72") for m in meses_c if m not in con_datos]
        for x, texto, color_m in marcas:
            fig.add_annotation(
                x=x, xref="x", y=0, yref="y",
                text=f"<b>{texto}</b>", showarrow=False,
                yanchor="bottom", yshift=3, font=dict(size=14, color=color_m),
            )

        for valor_linea, color in [(200, "#B7791F"), (1000, "#C0392B")]:
            fig.add_annotation(
                x=1, xref="paper", y=math.log10(valor_linea), yref="y",
                text=str(valor_linea), showarrow=False,
                xanchor="right", yanchor="bottom", font=dict(color=color),
            )

        st.plotly_chart(fig, use_container_width=True)

    # ----- gráfico del índice de macroinvertebrados -----
    st.markdown("**Gráfico del índice de macroinvertebrados**")
    st.caption("**0**: no se encontraron organismos · **S/D**: sin datos de ese mes")

    if mi.empty:
        st.info("Aún no hay datos de macroinvertebrados para este sitio.")
    else:
        hist = un_dato_por_mes(recorte(mi, meses, dfm_i["Mes"].max()))
        if hist.empty:
            st.info("No hay datos de macroinvertebrados en el período elegido.")
        else:
            orden_m = [nombre_mes(m) for m in eje_meses(hist)]
            hist = hist.assign(Clase=hist["Indice"].apply(clase_indice),
                               MesTxt=hist["Mes"].map(nombre_mes))
            fig_m = px.bar(
                hist, x="MesTxt", y="Indice", color="Clase",
                color_discrete_map=COLOR_CLASE_BARRA,
                category_orders={"MesTxt": orden_m, "Clase": [c[0] for c in CLASES]},
                labels={"Indice": "Índice acumulado", "MesTxt": ""},
                hover_data={"Fecha": "|%d-%m-%Y", "MesTxt": False},
            )
            fig_m.update_layout(barmode="overlay")
            fig_m.add_trace(go.Scatter(x=orden_m, y=[None] * len(orden_m), mode="markers",
                                       showlegend=False, hoverinfo="skip"))
            fig_m.update_xaxes(type="category", categoryorder="array", categoryarray=orden_m)
            # --- marcas "0" y "S/D" sobre el eje ---
            con_datos_m = set(hist["Mes"])
            marcas_m = [(nombre_mes(m), "0", "#C0392B")
                        for m in hist.loc[hist["Indice"] == 0, "Mes"]]
            marcas_m += [(x, "S/D", "#6B7B72")
                         for m, x in zip(eje_meses(hist), orden_m) if m not in con_datos_m]
            for x, texto, color_m in marcas_m:
                fig_m.add_annotation(
                    x=x, xref="x", y=0, yref="y",
                    text=f"<b>{texto}</b>", showarrow=False,
                    yanchor="bottom", yshift=3, font=dict(size=14, color=color_m),
                )
            st.plotly_chart(fig_m, use_container_width=True)
