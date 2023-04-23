import dash
from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import os
import mariadb
import sys
from flask import Flask, render_template, request, json, flash, session,redirect,url_for
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import time
from flask import Flask, render_template
from dash import ctx


# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="usuario",
        password="password",
        host="localhost",
        database="georregias"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

# Font Awesome Icon's
external_scripts = [{'src': 'https://kit.fontawesome.com/19f1c21c33.js',
     'crossorigin': 'anonymous'}]

# Bootstrap
external_stylesheets = [{'href': 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css',
     'rel': 'stylesheet', 'integrity': 'sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi',
     'crossorigin': 'anonymous'}]

# Initialize app
app = Dash(__name__,
           use_pages=True,
           external_scripts = external_scripts,
           external_stylesheets=external_stylesheets
           )

#Secret key
app.server.secret_key='purpleMap'

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-57PKT06DTW"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-57PKT06DTW');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

server = app.server


# Page layout
app.layout = html.Div([
    #dash.page_container
    dcc.Location(id='url', refresh=False),
    html.Div(id="page-content",children=[])
])

app.config['suppress_callback_exceptions']=True

#Call to pages 
from pages import login,index,password_recovery, sent_mail,home,territoria,seccionvioleta,page_not_found


# Navbar - Callback
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)(toggle_navbar_collapse)


# Sidebar - Callback
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)(toggle_offcanvas)


# Map

# Access token
token = 'pk.eyJ1IjoianB6cDIwMDEiLCJhIjoiY2xmcmEzNnhyMDNjdDNycXQ0d3A2N3NjbyJ9.PUJ_q_U96vOQ94oli7JT6g'

# Map layout
map_layout = dict(
    mapbox={
        'accesstoken': token,
        'style': "light",
        'zoom': 13,
        'center': dict(lat=25.675456439828732, lon=-100.31115409182688)
    },
    showlegend=False,
    margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
    modebar=dict(remove=["zoom", "toimage", "pan", "select", "lasso", "zoomin", "zoomout", "autoscale", "reset",
                         "resetscale", "resetview"]),
    hoverlabel_bgcolor="#000000"
)

# Estaciones de Metro
estaciones_metro = pd.read_csv("assets/estaciones_metro.csv")

# Map - Callback
def on_form_change(switches_value):

    #print(switches_value)
    #print(len(switches_value))

    if switches_value == [1]:
        #print("passed through (1)")
        
        estaciones_mapa = go.Figure(go.Scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        ))
        
        estaciones_mapa.update_layout(map_layout)
        
        return estaciones_mapa

    elif switches_value == [2]:
       #print("passed through (2)")
       
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        reportes_mapa = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 10, 'opacity': .3, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                # "step": [50, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3500,
                #          4000, 4500, 5000],
                'color': '#4974a5',
                'opacity': .3
            }
        ))

        reportes_mapa.update_layout(map_layout)

        return reportes_mapa

    elif switches_value == [3]:
        #print("passed through (3)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        percepciones_mapa = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        ))

        percepciones_mapa.update_layout(map_layout)

        return percepciones_mapa

    elif switches_value == [4]:
        #print("passed through (4)")
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        percepciones_seguro_mapa = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        ))

        percepciones_seguro_mapa.update_layout(map_layout)

        return percepciones_seguro_mapa

    elif switches_value == [1, 2] or switches_value == [2, 1]:
        #print("passed through (1, 2)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Estaciones + Reportes
        estaciones_reportes = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 10, 'opacity': .1, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))

        estaciones_reportes.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        estaciones_reportes.update_layout(map_layout)

        return estaciones_reportes

    elif switches_value == [1, 3] or switches_value == [3, 1]:
        #print("passed through (1, 3)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Estaciones + Percepciones
        estaciones_percepciones = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        ))

        estaciones_percepciones.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        estaciones_percepciones.update_layout(map_layout)

        return estaciones_percepciones

    elif switches_value == [1, 4] or switches_value == [4, 1]:
        #print("passed through (1, 4)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Estaciones + Percepciones - Seguro
        estaciones_percepciones_seguro = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        ))

        estaciones_percepciones_seguro.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        estaciones_percepciones_seguro.update_layout(map_layout)

        return estaciones_percepciones_seguro

    elif switches_value == [2, 3] or switches_value == [3, 2]:
        #print("passed through (2, 3)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Reportes + Percepciones
        reportes_percepciones = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 10, 'opacity': .1, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        reportes_percepciones.add_scattermapbox(
            lon = longitud,
            lat = latitud,
            marker = {'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo = "none"
        )

        reportes_percepciones.update_layout(map_layout)

        return reportes_percepciones

    elif switches_value == [2, 4] or switches_value == [4, 2]:
        #print("passed through (2-4)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Reportes + Percepciones - Seguro
        reportes_percepciones_seguro = go.Figure(go.Scattermapbox(
            lon = longitud,
            lat = latitud,
            marker = {'size': 12, 'opacity': .1, 'color': '#4974a5'},
            cluster = {
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        reportes_percepciones_seguro.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        )

        reportes_percepciones_seguro.update_layout(map_layout)

        return reportes_percepciones_seguro

    elif switches_value == [3, 4] or switches_value == [4, 3]:
        #print("passed through (3-4)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Ambas Percepciones
        percepciones_ambas = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        ))
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        percepciones_ambas.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        )

        percepciones_ambas.update_layout(map_layout)

        return percepciones_ambas

    elif switches_value == [1, 2, 3] or switches_value == [1, 3, 2] or switches_value == [2, 1, 3]\
            or switches_value == [2, 3, 1] or switches_value == [3, 1, 2] or switches_value == [3, 2, 1]:
        #print("passed through (1, 2, 3)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Estaciones + Reportes + Percepciones
        estaciones_reportes_percepciones = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 12, 'opacity': .1, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        estaciones_reportes_percepciones.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        )

        estaciones_reportes_percepciones.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        estaciones_reportes_percepciones.update_layout(map_layout)

        return estaciones_reportes_percepciones

    elif switches_value == [1, 2, 4] or switches_value == [1, 4, 2] or switches_value == [2, 1, 4]\
            or switches_value == [2, 4, 1] or switches_value == [4, 1, 2] or switches_value == [4, 2, 1]:
        #print("passed through (1, 2, 4)")

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        # Estaciones + Reportes + Percepciones - Seguro
        estaciones_reportes_percepciones_seguro = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 12, 'opacity': .1, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        estaciones_reportes_percepciones_seguro.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        )

        estaciones_reportes_percepciones_seguro.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        estaciones_reportes_percepciones_seguro.update_layout(map_layout)

        return estaciones_reportes_percepciones_seguro


    elif switches_value == [1, 3, 4] or switches_value == [1, 4, 3] or switches_value == [3, 1, 4] \
            or switches_value == [3, 4, 1] or switches_value == [4, 1, 3] or switches_value == [4, 3, 1]:
        #print("passed through (1, 3, 4)")

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        # Estaciones + Ambas Percepciones
        estaciones_percepciones_ambas = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        ))

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        estaciones_percepciones_ambas.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        )

        estaciones_percepciones_ambas.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        estaciones_percepciones_ambas.update_layout(map_layout)

        return estaciones_percepciones_ambas

    elif switches_value == [2, 3, 4] or switches_value == [2, 4, 3] or switches_value == [3, 2, 4]\
            or switches_value == [3, 4, 2] or switches_value == [4, 2, 3] or switches_value == [4, 3, 2]:
        #print("passed through (2, 3, 4)")

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        # Reportes + Ambas Percepciones
        reportes_percepciones_ambas = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 12, 'opacity': .1, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        reportes_percepciones_ambas.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        )
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        reportes_percepciones_ambas.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        )

        reportes_percepciones_ambas.update_layout(map_layout)

        return reportes_percepciones_ambas

    elif len(switches_value) == 4:
        #print("passed though todas")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='911';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        # Mapa - Todas
        mapa_todas = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 12, 'opacity': .1, 'color': '#4974a5'},
            cluster={
                'enabled': True,
                'size': [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60, 69, 78],
                "step": [60, 120, 180, 240, 300, 360, 420, 480, 540, 600, 660, 720, 780, 840, 900, 960, 1020, 2100,
                         5200],
                'color': '#4974a5',
                'opacity': .3
            }
        ))
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='seguridad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        mapa_todas.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#8bb77f'},
            hoverinfo="none"
        )

        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))
        
        mapa_todas.add_scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 14, 'opacity': .7, 'color': '#A97BB5'},
            hoverinfo="none"
        )

        mapa_todas.add_scattermapbox(
            lon=estaciones_metro["longitud"],
            lat=estaciones_metro["latitud"],
            marker={'size': 14, 'symbol': "rail-metro", "opacity": 1},
            hovertext=estaciones_metro["name"],
            hoverinfo="text"
        )

        mapa_todas.update_layout(map_layout)

        return mapa_todas

    elif len(switches_value) == 0:
        #print("passed through (0)")
        
        cur.execute("SELECT SUBSTRING_INDEX(location,',', 1) AS lat, SUBSTR(location, POSITION(',' IN  location)+2, LENGTH(location)) AS lon FROM record WHERE type='criminalidad';")
        myresult = cur.fetchall()
        latitud = list(map(lambda x: x[0], myresult))
        longitud = list(map(lambda x: x[1], myresult))

        placeholder = go.Figure(go.Scattermapbox(
            lon=longitud,
            lat=latitud,
            marker={'size': 12, 'opacity': .5, 'color': '#E2474B'},
            hoverinfo="none"
        ))

        placeholder.update_layout(map_layout)

        return placeholder

app.callback(
    Output("mapa-movil", "figure"),
    Input("switches-input-movil", "value")
)(on_form_change)

app.callback(
    Output("mapa-desktop", "figure"),
    Input("switches-input-desktop", "value")
)(on_form_change)

#Deleting records route (plan b por si no se puede con dash)
@app.server.route("/delete_record/<int:id>",methods=['GET'])
def page_delete_record(id):
        if 'user' not in session:
            return redirect('/page_not_found')
        else:
            cur.execute("CALL check_record(%s)",(id,))
            data=cur.fetchone()
            if data[0]:
                cur.execute('CALL get_record(%s)', (id,))
                table=cur.fetchone()
                return render_template('delete.html', record=table)
            else:
                return redirect('/page_not_found')


#Based on the path, returns a page's layout
@app.callback(
    Output("page-content","children"),
    Input("url","pathname")
)

def display_page(pathname):
    if pathname=="/":
        return home.layout
    if pathname=="/territoria":
        return territoria.layout
    if pathname=="/seccionvioleta":
        return seccionvioleta.layout
    if pathname=="/login":
        if 'user' in session:
            redirect('/index')
            return index.layout
        else:
            return login.layout
    if pathname=="/password_recovery":
        return password_recovery.layout
    if pathname=="/index":
        if 'user' not in session:
            return login.layout
        else:
            return index.layout
    else:
        return page_not_found.layout
#LOGIN

#Checks the conditions the email has to fulfill
def check_email(email):
    if email is not None and ('@' not in email or '.' not in email or '@.' in email):
        return True
    return False

#Checks the conditions the password has to fulfill
def check_password(password):
    if password is not None and len(password)<=0:
        return True
    return False

#Validate login form inputs : If at least one input is empty, the submit button is disabled
@app.callback(
    Output("submit_button", "disabled"),
    [Input("email", "value"),Input("password", "value")])

def login_inputs_validation(email, password):
        if email is None or password is None or check_email(email) or check_password(password):
            return True
        return False

#Email input feedback : If the email is not valid, feedback will be shown to the user
@app.callback(
    Output("email", "invalid"),
    Input("email", "value"),
    prevent_initial_call=True
)

def show_email_feedback(email):
    if check_email(email):
        return True
    return False

#Password input feedback : If the password is not valid, feedback will be shown to the user
@app.callback(
    Output("password", "invalid"),
    Input("password", "value"),
    prevent_initial_call=True
)
def show_password_feedback(password):
    if check_password(password):
        return True
    return False

#User credentials authentication : Checks that both credentials exist in the db to authenticate the user into the system
@app.callback(
    [Output("login_form", "children"),Output("bad_credentials_alert","is_open")],
    Input("submit_button","n_clicks"),
    State("email", "value"),
    State("password", "value"),
    prevent_initial_call=True
)

def authenticate_login(n_clicks, email, password):
    if n_clicks is not None:
        cur.execute("CALL authenticate_login(%s,%s)",(email,password))
        data = cur.fetchone()[0]
        if data:
            cur.execute("CALL user_num(%s)",(email,))
            data_id=cur.fetchone()[0]
            session['user']=data_id
            return dcc.Location(href="/index", id="Index"), False
        else:
            return True, True
    return True, False

#INDEX (RECORDS)

#Add record modal : Allows the admin to open the modal to add a report
@app.callback(
    Output("add_record_modal", "is_open"),
    Input("open_add_record_modal", "n_clicks"),
    State("add_record_modal", "is_open"),
    prevent_initial_call=True
)

def toggle_add_record_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


#Checks the conditions the latitude has to fulfill
def check_latitude(latitude):
    if latitude is not None:
        try:
            number=float(latitude)
            if number>90 or number<-90:
                return False
            return True
        except ValueError:
            return False
    return False

#Checks the conditions the longitude has to fulfill
def check_longitude(longitude):
    if longitude is not None:
        try:
            number=float(longitude)
            if number>180 or number<-180:
                return False
            return True
        except ValueError:
            return False
    return False
    
#Validate add record form inputs : If at least one input is empty, the submit button is disabled
@app.callback(
    Output("add_record_button", "disabled"),
    [Input("type", "value"),Input("latitude", "value"),Input("longitude","value")])

def add_record_input_validation(type, latitude,longitude):
    if check_latitude(latitude)==False or check_longitude(longitude)==False or type is None:
        return True
    return False

#Latitude input feedback : If the latitude is not valid, feedback will be shown to the user
@app.callback(
    Output("latitude", "invalid"),
    Input("latitude", "value"),
    prevent_initial_call=True
)

def latitude_validation(latitude):
    if check_latitude(latitude)==False:
        return True
    return False

#Longitude input feedback : If the longitude is not valid, feedback will be shown to the user
@app.callback(
    Output("longitude", "invalid"),
    Input("longitude", "value"),
    prevent_initial_call=True
)
def longitude_validation(longitude):
    if check_longitude(longitude)==False:
        return True
    return False

#Filter records modal :  Allows the user to open the modal to filter the records
@app.callback(
    Output("filter_records_modal", "is_open"),
    Input("open_filter_records_modal", "n_clicks"),
    State("filter_records_modal", "is_open"),
    prevent_initial_call=True
)

def toggle_filter_records_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

#Show records:  Shows the records in the table by default when accesing index but also when using filters
@app.callback(
        Output('table', 'children'),
        [Input("filter_records_button","n_clicks"),
        State("type_filter", "value"),
        State("day_filter", "value"),
        State("month_filter","value"),
        State("year_filter", "value")
        ],
)

def show_records(n, type_filter, day_filter, month_filter, year_filter):
    if n>0:
        if type_filter is None:
            type_filter=""
        if day_filter is None:
            day_filter=""
        if month_filter is None:
            month_filter=""
        if year_filter is None: 
            year_filter=""
        cur.execute("CALL filter_records(%s,%s,%s,%s)",(type_filter,day_filter,month_filter,year_filter))
        data = cur.fetchall()
        return create_table(data)
    cur.execute("CALL obtain_records()")
    data = cur.fetchall()
    return create_table(data)


#Add record form : Inserts the given information as a record in the db and shows succesful alert
@app.callback(
   [Output("added_record_alert","is_open"), Output("add_record_modal","is_open", allow_duplicate=True)],
    Input("add_record_button","n_clicks"),
    [State("type", "value"),
    State("latitude", "value"),
    State("longitude","value")],
    prevent_initial_call=True
)

def add_record(n_clicks, type, latitude,longitude):
    if n_clicks > 0:
       cur.execute("CALL add_record(%s,%s,%s,%s)",(session['user'],type,latitude,longitude))
       conn.commit()
       return True, False
    
#When record added alert is closed, refreshes the page
@app.callback(
    Output("url","pathname", allow_duplicate=True),
    Input("added_record_alert","is_open"),
    prevent_initial_call=True
)

def redirect_after_alert(change):
    if not change:
        time.sleep(1)
        return "/index"
    raise PreventUpdate
    
#Returns the html table of the given data
def create_table(data):
    table_records = []
    table_headers=html.Tr([html.Th("id"),html.Th("Tipo"),html.Th("Ubicación"),html.Th("Fecha de admisión"),html.Th("Registrado por"),html.Th("Acciones")])
    for record in data:
        record_cols = [html.Td(str(col)) for col in record]
       # link_col = html.Td(html.A("Eliminar",id="delete_record_button",className="delete_record_btn",href='/delete_record/%s' % (str(record[0]))))
        link_col = html.Td(html.Button("Eliminar",n_clicks=0,className="delete_record_btn",id='delete_record_%s' % (str(record[0]))))
        table_records.append(html.Tr(record_cols + [link_col]))
    table = html.Table([table_headers,html.Tbody(table_records)],className="table")
    return table


#Delete records modal
#Medio funciona si agregas los elementos manualmente en el diccionario.
'''@app.callback(
    Output("delete_record_modal", "is_open"),
    inputs={
            "all_inputs":{
                  "btn1": Input("delete_record_1", "n_clicks"),
                  "btn2": Input("delete_record_2", "n_clicks"),
                  "btn3": Input("delete_record_3", "n_clicks")
            }
    
    },
    prevent_initial_call=True
)

def display(all_inputs):
    c = ctx.args_grouping.all_inputs
    if c.btn1.triggered:
        return True
    if c.btn2.triggered:
        return True
    if c.btn3.triggered:
        return True 
    return False
'''

#Sign out :  When user clicks "close session", the session variable is popped and the user is redirected to login
@app.callback(
    Output("url","pathname"),
    Input("sign_out_button","n_clicks"),
    prevent_initial_call=True
)

def sign_out(clicked):
    if clicked:
        session.pop('user',None)
        return "/login"
    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)
conn.close()
