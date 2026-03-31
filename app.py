from dash import Dash, html, dcc, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import os
import economy.datamgmt as econ
import economy.presets as presets


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
preset_models = {'Consumer Conditions':{
                        'ISMVCFCF':presets.ISMVCFCF, 
                        'ENGCOST': presets.ENGCOST,
                        'INFLATION':presets.INFLATION, 
                        'PARTTIME':presets.PARTTIME
                    }, 
                'Financial Conditions':{
                            'TWOTOTENVISM':presets.TWOTOTENVISM
                    }
                }


navbar = dbc.Navbar(
    dbc.Container(
        [
            # Left Side: Brand/Title
            dbc.NavbarBrand("Economic Analysis Dashboard", href="#", className="ms-2"),
            
            # Right Side: Professional Credit
            dbc.Nav(
                [
                    html.Div([
                        html.P("Created by Victor A. Rodriguez, CFA", 
                               style={'margin': 0, 'fontSize': '14px', 'fontWeight': 'bold', 'color':'white'}),
                        html.A("victor.a.dicecco@gmail.com", # Replace with your actual email
                               href="mailto:victor.rodriguez@example.com",
                               style={'fontSize': '11px', 'color': 'rgba(255,255,255,0.7)', 'textDecoration': 'none'})
                    ], className="text-end") # Aligns text to the right within its container
                ],
                className="ms-auto", # This pushes the entire Nav to the right
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="secondary",
    dark=True,
    sticky="top",
    className="mb-2",
)

def title_row(title, bgcolor):
    return dbc.Row([html.H5(title, style={'color':'white', 'fontFamily':'Arial, sans-serif', 'textAlign':'center', 'margin':'0'})], justify="center", style={'backgroundColor': bgcolor}, className='pt-2 pb-2 mb-2')

def data_table(obj):
    series_meta = obj.series_meta.loc[obj.global_series]
    frame = obj.data_[obj.global_series].tail(10).round(2).reset_index()
    
    # Format dates
    frame.date = [x.strftime('%Y-%m-%d') for x in frame.date]
    
    # Transpose so series are rows and dates are columns
    frame = frame.T.reset_index()
    
    # Set the first row (which contains the dates) as column headers
    frame.columns = frame.iloc[0]
    frame = frame[1:]

    for title in frame['date']:
        frame.loc[frame['date'] == title, 'date'] = series_meta.loc[title, 'title']

    # FIX: Convert column strings into the required dictionary format
    # Using str(i) ensures compatibility if headers are numeric
    table_columns = [{"name": str(i), "id": str(i)} for i in frame.columns]


    table = dash_table.DataTable(
        columns=table_columns,  # Pass the list of dictionaries here
        data=frame.to_dict('records'),

    style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },

    fixed_columns={'headers': True, 'data': 1},

    # 1. Wrap the text and shrink font size for headers
    style_header={
        'backgroundColor': 'rgb(210, 210, 210)',
        'fontWeight': 'bold',
        'whiteSpace': 'normal',   # Allows text to wrap
        'height': 'auto',         # Adjusts height based on content
        'fontSize': '10px',       # Smaller font for titles
        'textAlign': 'center'
    },

    # 2. Specific override for the first column ('index')
    style_cell_conditional=[
            {
                'if': {'column_id': 'date'}, 
                'textAlign': 'left',           # Justify text to the left
                'minWidth': '200px',           # Make it significantly larger
                'width': '200px',
                'maxWidth': '250px',
                'fontWeight': 'bold',          # Optional: Make labels bold for readability
                'backgroundColor': '#f9f9f9', 
                'paddingLeft':'15px'   # Optional: Subtle background for the label column
            }
        ],

    style_header_conditional=[
            {
                'if': {'column_id': 'date'},
                'textAlign': 'left',    # Aligns the header label to the left
                'paddingLeft': '15px'   # Matches the data cell margin
            }
        ],

    # 2. Shrink font size for the actual data cells
    style_cell={
        'fontSize': '10px',       # Even smaller font for the numeric data
        'fontFamily': 'sans-serif',
        'minWidth': '80px', 'width': '80px', 'maxWidth': '150px',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'textAlign': 'center'
    },
    
    # Optional: allow rows to grow if data also needs to wrap
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
    })
    return table
        
def get_source_list(obj):
    # Get unique release names and links from the metadata
    sources = obj.series_meta
    
    source_items = []
    for _ in sources.index:
        # Create a clickable link for each source
        source_items.append(
            html.Li([
                f"Series: {sources.loc[_, 'title']}; Release: {sources.loc[_, 'name']}; Link: {sources.loc[_, 'link']}; Notes: {sources.loc[_, 'notes']}"
            ])
        )
    
    return html.Ul(source_items, style={'fontSize': '11px', 'color': 'gray', 'listStyleType': 'none', 'paddingLeft': '15px'})


def data_module(obj):

    container = dbc.Container([
        # Row for the Chart
        dbc.Row([html.P(obj.description)]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=obj.plot())
            ], width=12) # Using 'width' instead of 'className' for better consistency
        ], justify="center"), 
        
        # Row for the Table
        dbc.Row([
            dbc.Col([
                data_table(obj)
            ], width=12)
        ], justify="center")
    ], fluid=True, style={'backgroundColor': "#ffffff"}, className="mb-2") # fluid=True allows it to expand properly
        

    return container

app.layout = html.Div([
                       navbar, 
                       dbc.Container([
                    dcc.Loading(
                        id='loading-initialization', 
                        type='default', 
                        fullscreen=True, 
                        children= html.Div(id="main-content")
                    )

        ], style={'backgroundColor': "#ffffff"})
        ], style={'backgroundColor': '#f1f3f5'})
    

@app.callback(
    Output('main-content', 'children'), 
    Input('loading-initialization', 'id')
)
def update_chart(initialization):
    #models_list = list(preset_models.values())
    models_list = []
    for model in preset_models.keys():
        for _ in preset_models[model].keys():
            models_list.append(preset_models[model][_])

    models = econ.Models(settings_list = models_list, finc_settings = presets.FINANCIAL_SETTINGS)
    models.initialized_models()

    main_children = []
    for model in preset_models.keys():
        main_children.append(title_row(model, "#164b7f"))
        for _ in preset_models[model].keys():
            obj = getattr(models, _)
            main_children.append(title_row(obj.name, "#989898"))
            main_children.append(data_module(obj))
            main_children.append(get_source_list(obj))

    return main_children

if __name__ == '__main__':
    app.run(debug=True)