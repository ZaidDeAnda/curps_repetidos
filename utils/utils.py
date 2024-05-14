import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

import base64
from utils.config import Config
import streamlit.components.v1 as components

def download_button(object_to_download, download_filename):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    """

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    dl_link = f"""
    <html>
    <head>
    <title>Start Auto Download file</title>
    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
    <script>
    $('<a href="data:text/csv;base64,{b64}" download="{download_filename}">')[0].click()
    </script>
    </head>
    </html>
    """
    return dl_link

@st.cache_resource
def connect(secrets):
    DATABASE_CONNECTION = f'mssql://{secrets["USERNAME"]}:{secrets["PASSWORD"]}@{secrets["SERVER"]}/{secrets["DATABASE"]}?driver={secrets["DRIVER"]}'

    engine = create_engine(DATABASE_CONNECTION)
    connection = engine.connect()

    return connection

@st.cache_data
def obtener_viviendas_repetidas():

    config = Config()

    secrets = config.get_config()['db']

    connection = connect(secrets)
    # Obtén todos los datos necesarios en una sola consulta SQL que también agrupa por CURP y IDVivienda
    query = '''
    SELECT db.CURP, db.IDVivienda, bc.IDEstatusBeneficiario
    FROM DatosBeneficiario AS db
    LEFT JOIN BeneficiarioControl AS bc ON db.IDBeneficiario = bc.IDBeneficiario
    WHERE CURP IN (SELECT CURP FROM DatosBeneficiario GROUP BY CURP)
    AND CURP != ''
    ORDER BY db.CURP, db.IDVivienda, bc.IDEstatusBeneficiario DESC
    '''
    df = pd.read_sql_query(query, connection)

    # Inicializa una lista para almacenar las viviendas a eliminar
    viviendas_a_eliminar = []

    curps_repetidos = []

    # Procesa el DataFrame por CURP
    counter = 0
    for curp, group in df.groupby('CURP'):
        # Revisa si hay alguna vivienda con IDEstatusBeneficiario == 4.0
        viviendas_con_beneficiario = group[group['IDEstatusBeneficiario'] == 4.0]
        if group.shape[0] > 1:
            curps_repetidos.append(curp)

        if viviendas_con_beneficiario.shape[0] > 1:
            counter +=1
        
        if not viviendas_con_beneficiario.empty:
            # Si existe alguna vivienda con estado 4.0, selecciona la primera (debido al ordenamiento)
            vivienda_valida = viviendas_con_beneficiario['IDVivienda'].iloc[0]
        else:
            # Si no hay ninguna vivienda con estado 4.0, toma el IDVivienda máximo de ese CURP
            vivienda_valida = group['IDVivienda'].max()
        
        # Añade todas las viviendas menos la válida a la lista de eliminación
        viviendas_a_eliminar.extend(group[group['IDVivienda'] != vivienda_valida]['IDVivienda'].unique())

    # Elimina duplicados en la lista de viviendas a eliminar
    viviendas_a_eliminar = list(set([str(vivienda) for vivienda in viviendas_a_eliminar]))

    return viviendas_a_eliminar, counter, df[df['CURP'].isin(curps_repetidos)]

def download_csv(list):
    new_list = ','.join([str(element) for element in list])
    components.html(
        download_button(bytes(new_list, 'utf-8'), f"beneficiarios_repetidos.csv"),
        height=0,)