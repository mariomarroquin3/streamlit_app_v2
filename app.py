import streamlit as st
from model_utils import inject_custom_css

# Configuración global
st.set_page_config(
    page_title="Retinopatía IA",
    layout="wide",
)

# Inyectar estilos globales
inject_custom_css()

# Enrutamiento nativo y sin parpadeos (SPA)
pages = [
    st.Page("Home.py", title="Inicio", icon=":material/home:"),
    st.Page("pages/Clasificador.py", title="Clasificador", icon=":material/biotech:"),
    st.Page("pages/Metricas.py", title="Métricas", icon=":material/bar_chart:"),
    st.Page("pages/Acerca.py", title="Acerca del Proyecto", icon=":material/info:"),
]

nav = st.navigation(pages)
nav.run()
