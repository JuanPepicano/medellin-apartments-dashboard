# -*- coding: utf-8 -*-
"""Dashboard Apartamentos Medellin

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CuaMi80kIQc4X5cb87wlOD7Kgc7E8IWP
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_csv("house_medellin_cleaned.csv")

# Renombrar columnas para uso consistente
df.rename(columns={
    'Área construída (m²)': 'AreaConstruida',
    'Baños': 'Banos',
    'Administración': 'Administracion'
}, inplace=True)

app = dash.Dash(__name__)
server = app.server

def filter_by_group(df, variable):
    """
    Filtra el DataFrame eliminando outliers a nivel de cada grupo de Estrato,
    conservando solo los registros entre el percentil 5 y el 95% de cada grupo.
    """
    groups = []
    for estrato, group in df.groupby("Estrato"):
        lower = group[variable].quantile(0.05)
        upper = group[variable].quantile(0.95)
        group_filtered = group[(group[variable] >= lower) & (group[variable] <= upper)]
        groups.append(group_filtered)
    return pd.concat(groups)

# Layout del dashboard
app.layout = html.Div([
    html.H1("Dashboard: Precio de Apartamentos en Medellín por Estrato"),

    html.Div([
        html.Label("Seleccionar variable para boxplot"),
        dcc.Dropdown(
            id='variable_dropdown',
            options=[
                {'label': 'Precio', 'value': 'Precio'},
                {'label': 'Área Construida', 'value': 'AreaConstruida'},
                {'label': 'Habitaciones', 'value': 'Habitaciones'},
                {'label': 'Baños', 'value': 'Banos'},
                {'label': 'Administración', 'value': 'Administracion'},
                {'label': 'Parqueaderos', 'value': 'Parqueaderos'}
            ],
            value='Precio'
        )
    ], style={'width': '40%', 'display': 'inline-block'}),

    dcc.Graph(id='boxplot_graph', style={'width': '100%', 'height': '600px'}),

    html.Div([
        html.Label("Filtrar por número de baños"),
        dcc.Slider(
            id='banos_slider',
            min=int(df['Banos'].min()),
            max=int(df['Banos'].max()),
            step=1,
            marks={int(b): str(int(b)) for b in sorted(df['Banos'].dropna().unique())},
            value=int(df['Banos'].min())
        )
    ], style={'width': '80%', 'padding': '40px'}),

    dcc.Graph(id='scatter_area_precio', style={'width': '100%', 'height': '600px'}),

    html.Div([
        html.H3("Narrativa"),
        html.P("Antes de presentar el dashboard a la audiencia, se han realizado ajustes para que los gráficos sean más claros. "
               "Se han removido los datos extremos (outliers) a nivel de cada estrato, limitando los valores mostrados a los percentiles "
               "5 y 95 de cada grupo. Esto evita espacios en blanco innecesarios y facilita la interpretación visual para usuarios no técnicos, "
               "permitiendo ver de forma clara las tendencias y patrones en el mercado inmobiliario.")
    ], style={"padding": "20px"})
])

# Callback para actualizar el boxplot con eliminación de outliers a nivel de cada grupo
@app.callback(
    Output('boxplot_graph', 'figure'),
    Input('variable_dropdown', 'value')
)
def update_boxplot(variable):
    # Filtrar los datos por grupo para eliminar outliers en cada estrato
    df_filtered_group = filter_by_group(df, variable)

    # Para "Precio" se puede aplicar logaritmo en el eje y para mejorar la visualización
    log_y = True if variable == 'Precio' else False

    fig = px.box(df_filtered_group, x='Estrato', y=variable, points="all",
                 log_y=log_y,
                 title=f"Distribución de {variable} por Estrato (Datos entre 5% y 95% por grupo)")
    return fig

# Callback para actualizar el scatter plot según el filtro de baños
@app.callback(
    Output('scatter_area_precio', 'figure'),
    Input('banos_slider', 'value')
)
def update_scatter(banos):
    filtered_df = df[df['Banos'] == banos]
    fig = px.scatter(filtered_df, x='AreaConstruida', y='Precio', color='Estrato',
                     title=f"Precio vs. Área Construida para {banos} baños")
    return fig

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)


