import dash
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc
from dash import html

import pandas as pd
import collections

from flask_sqlalchemy import SQLAlchemy
from flask import Flask


server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Test123.@192.168.60.70/postgres"

db = SQLAlchemy(app.server)


# ------------------------------------------------------------------------------------------------

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id='adding-rows-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='adding-columns-button', n_clicks=0)
    ], style={'height': 50}),

    dcc.Interval(id='interval_pg', interval=86400000*7, n_intervals=0),  # activated once/week or when page refreshed
    html.Div(id='postgres_datatable'),

    html.Button('Add Row', id='editing-rows-button', n_clicks=0),
    html.Button('Save to PostgreSQL', id='save_to_postgres', n_clicks=0),

    # Create notification when saving to excel
    html.Div(id='placeholder', children=[]),
    dcc.Store(id="store", data=0),
    dcc.Interval(id='interval', interval=1000),


])


# ------------------------------------------------------------------------------------------------


@app.callback(Output('postgres_datatable', 'children'),
              [Input('interval_pg', 'n_intervals')])
def populate_datatable(n_intervals):
    df = pd.read_sql_table('phonebook', con=db.engine)
    return [
        dash_table.DataTable(
            id='our-table',
            columns=[{
                'name': str(x),
                'id': str(x),
                'deletable': True,
                'renamable': True
            }
                     for x in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            # filter_action="native",
            page_action='none',  # render all of the data at once. No paging.
            style_table={'height': '300px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'}
        ),
    ]


@app.callback(
    Output('our-table', 'columns'),
    [Input('adding-columns-button', 'n_clicks')],
    [State('adding-rows-name', 'value'),
     State('our-table', 'columns')],
    prevent_initial_call=True)
def add_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'name': value, 'id': value,
            'renamable': True, 'deletable': True
        })
    # list_of_columns=[]
    # for i in range(len(existing_columns)):
    #     list_of_columns.append(existing_columns[i]['id'])
    return existing_columns


@app.callback(
    Output('our-table', 'data'),
    [Input('editing-rows-button', 'n_clicks')],
    [State('our-table', 'data'),
    State('our-table', 'columns')],
    prevent_initial_call=True)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows



@app.callback(
    [Output('placeholder', 'children'),
     Output("store", "data")],
    [Input('save_to_postgres', 'n_clicks'),
     Input("interval", "n_intervals")],
    [State('our-table', 'data'),
     State('store', 'data'),
     State('our-table', 'columns')],
    prevent_initial_call=True)
def df_to_sql(n_clicks, n_intervals, dataset, s,columns):
    output = html.Plaintext("The data has been saved to your PostgreSQL database.",
                            style={'color': 'green', 'font-weight': 'bold', 'font-size': 'large'})
    no_output = html.Plaintext("", style={'margin': "0px"})
    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_triggered == "save_to_postgres":
        list_of_columns=[]
        for i in range(len(columns)):
            list_of_columns.append(columns[i]['id'])
        pg = pd.DataFrame(dataset)
        pg[list_of_columns].to_sql("phonebook", con=db.engine, if_exists='replace', index=False)
        s = 6
        return output, s
    elif input_triggered == 'interval' and s > 0:
        s = s - 1
        if s > 0:
            return output, s
        else:
            return no_output, s
    elif s == 0:
        return no_output, s


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',port='8050',debug=True)
