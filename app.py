import streamlit as st
from utils.utils import obtener_viviendas_repetidas, download_csv

st.header("Sistema de búsqueda para viviendas repetidas")

lista_viviendas, counter, curps_repetidos = obtener_viviendas_repetidas()

st.subheader(f"👤 Usuarios (CURPS) con viviendas repetidas: {counter}")

st.subheader(f"🏡 Viviendas repetidas: {len(lista_viviendas)}")

st.write("Algunos curps duplicados son:")

st.write(curps_repetidos.head(10))

st.download_button(label="Descargar listado", data=','.join(lista_viviendas), mime='text/csv')