#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from dash import dash, html, dcc, Input, Output, callback_context

######################### PASS THE CSS INTO DASH ########################
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://codepen.io/chriddyp/pen/bWLwgP.css'
    ]
)

################### GET XML ARGUMENT FROM COMMAND LINE ###################
if '.nmap' not in str(sys.argv):
    sys.stderr.write("Usage: {} FILENAME\n".format(sys.argv[0]))
    exit()

filename = sys.argv

################### CONVERT XML TO CSV ###################

if isinstance(filename, list):
    for nmaps in filename:
        subprocess.call(['python', 'nmaptocsv/nmaptocsv.py', '-i', nmaps, '>> output.csv'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
else:
        subprocess.call(['python', 'nmaptocsv/nmaptocsv.py', '-i', filename[1], '-o', 'output.csv'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

################### CREATE DATAFRAME FROM CSV ###################

df = pd.read_csv('output.csv', delimiter=';')
df = df.fillna(0)
df["PORT"] = df["PORT"].astype(int)

# Remove duplicated in second loop
df = df.drop_duplicates(subset=["IP", "PORT"])

# Extract all ports in a list
all_ports =  df['PORT'].tolist()
all_ports = sorted(set(all_ports))

################### PREPARE GRAPH ###################
def network_graph(dataframe):
    # Group repeated IPs and common elements as ports, services....
    groupby_column = 'IP'
    aggregate_port = 'PORT'
    aggregate_service = 'SERVICE'
    aggregate_host = 'FQDN'
    aggregate_product = 'VERSION'

    agg_df = dataframe.groupby('IP').aggregate({aggregate_port: list, aggregate_service: list,aggregate_host: list, aggregate_product: list})
    df_alias = dataframe.drop(columns=[aggregate_port,aggregate_service,aggregate_host,aggregate_product]).set_index(groupby_column)

    df = agg_df.join(df_alias).reset_index(groupby_column).drop_duplicates(groupby_column).reset_index(drop=True)

    # Create a column with the subnet, structure 192.168.1.X 
    subnet_ips = []
    for ip in df['IP']:
        subnet_ips.append(ip[:ip.rfind(".")])
    df['Subnet'] = subnet_ips

    # EXTRACT NODES AND EDGES FROM DATAFRAME
    G = nx.from_pandas_edgelist(df, 'Subnet', 'IP', ['FQDN','PORT','PROTOCOL','SERVICE','VERSION'])
    nx.set_node_attributes(G, df.set_index('IP')['PORT'].to_dict(), 'PORT')
    nx.set_node_attributes(G, df.set_index('IP')['SERVICE'].to_dict(), 'SERVICE')

    # get a x,y position for each node
    pos = nx.layout.spring_layout(G)

    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])

    pos=nx.get_node_attributes(G,'pos')

    dmin=1
    ncenter=0
    for n in pos:
        x,y=pos[n]
        d=(x-0.5)**2+(y-0.5)**2
        if d<dmin:
            ncenter=n
            dmin=d

    # Create Edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    # Create nodes with info (IP, Ports, Color, Size...)
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        textposition="bottom center",
        hoverinfo='text',
        hovertext=[],
        marker=dict(
            showscale=True,
            # 'aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            # 'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            # 'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            # 'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            # 'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            # 'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            # 'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            # 'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            # 'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            # 'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            # 'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            # 'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            # 'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            # 'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            # 'yylorrd'
            colorscale='redor',
            color=[],
            size=13,
            colorbar=dict(
                thickness=10,
                title='Port Number',
                xanchor='left',
                titleside='right'
            ),
            line_width=2)
        )

    index = 0
    len_nports = []
    len_nports_excp = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        if G.nodes[node].get('PORT') != None:
            hovertext = str(G.nodes[node]['PORT']) + "<br>" + str(G.nodes[node]['SERVICE'])
            node_trace['hovertext'] += tuple([hovertext])
            len_nports.append(len(G.nodes[node]['PORT']))
            len_nports_excp.append(len(G.nodes[node]['PORT']))
        else:
            hovertext = ""
            node_trace['hovertext'] += tuple([hovertext])
            len_nports.append(0)
            len_nports_excp.append(3)
        text = node
        node_trace['text'] += tuple([text])
        index = index + 1

    node_trace.marker.color = len_nports
    # node_trace.marker.size = [i * 10 for i in len_nports_excp]

    # Create the figure values
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='<br>Network Graph',
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    return(fig)


app.layout = html.Div(children=[
    html.Div(children=[
        html.H3('OPEN PORTS'),
        dcc.Checklist(["All"], [], id="all-checklist"),
        dcc.Checklist(all_ports, value=[],id='port-checklist'),
        html.Br(),
    ], className="one columns"),
    html.Div(children=[
        html.H3('NETWORK DIAGRAM'),
        dcc.Graph(id='Graph',figure=network_graph(df)),
        html.Br(),
    ], className="ten columns"),
], className="row")

# Callback for adding the all check
@app.callback(
    Output("port-checklist", "value"),
    Output("all-checklist", "value"),
    Input("port-checklist", "value"),
    Input("all-checklist", "value"),
)
def sync_checklists(ports_selected, all_selected):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "port-checklist":
        all_selected = ["All"] if set(ports_selected) == set(all_ports) else []    
    else:
        ports_selected = all_ports if all_selected else []
    return ports_selected, all_selected

# Callback to update the graph according to the checklist
@app.callback(
    Output("Graph", "figure"),
    Input("port-checklist", "value")
)
def update_figure(value):
    ctx = callback_context
    filter_df = pd.DataFrame()
    if not value:
        return network_graph(df)
    else:
        for port in ctx.triggered[0]["value"]:
                filter_df = pd.concat([filter_df, pd.DataFrame.from_records(df[df['PORT'] == port])])
        return network_graph(filter_df)


########### TODO ###########

## Generate table

# def generate_table(df, max_rows=10):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in df.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(df.iloc[i][col]) for col in df.columns
#             ]) for i in range(min(len(df), max_rows))
#         ])
#     ])


###########################

if __name__ == '__main__':
    app.run_server(debug=True)
