import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

df = pd.read_excel('hh and ind elect price composition.xlsx',index_col=0)
dfg = pd.read_csv('agg elect prices.csv')
dff= df[~df['nrg_prc'].isin(['Taxes, fees, levies and charges'])] # otherwise double counting taxes

font_family = "Roboto, Open Sans"
country_dict = {
    'AT':'Austria', 'BE':'Belgium', 'BG':'Bulgaria', 
    'CY':'Cyprus', 'CZ':'Czechia', 'DE':'Germany', 
    'DK':'Denmark', 'EE':'Estonia ', 'EU27': 'the European Union',
    'EL':'Greece', 'ES':'Spain', 'FI':'Finland',
    'FR':'France', 'HR':'Croatia', 'HU':'Hungary',
    'IE':'Ireland', 'IT':'Italy', 'LT':'Lithuania',
    'LU':'Luxembourg', 'LV':'Latvia', 'MT':'Malta',
    'NL':'Netherlands', 'PL':'Poland', 'PT':'Portugal',
    'RO':'Romania', 'SE':'Sweden', 'SI':'Slovenia',
    'SK':'Slovakia'
    }

# Dictionary to map nrg_prc values to colors (optional, for better visualization)
pos_color = {
    'Energy and supply': 'skyblue',
    'Value added tax (VAT)': 'lightcyan',  # Shaded color for VAT
    'Capacity taxes' : 'black',
    'Environmental taxes': 'khaki',
    'Network costs':'navy',
    'Nuclear taxes':'purple',
    'Other':'antiquewhite',
    'Renewable taxes':'limegreen',
    'Environmental taxes allowance': 'darkkhaki',
    'Other allowance':'teal',    
}

neg_color = {
    'Capacity taxes': 'darkgrey',  # Dark grey
    'Environmental taxes': 'rosybrown',  # Brownish-red
    'Other': 'silver',  # Grey
    'Renewable taxes': 'salmon',  # Light red
    'Environmental taxes allowance': 'peru',  
    'Other allowance': 'mistyrose',  # rose
}

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Get unique values for dropdowns
unique_countries = df['country'].unique() 
unique_years = [str(year) for year in range(2017, 2023)]  # Adjust years as per your data
unique_tax = dfg['tax'].unique()
unique_time = dfg.columns[4:]  
unique_category = dfg['nrg_cons'].unique()
unique_categories = df['nrg_cons'].unique()

# Dash layout with logo, titile and dropdowns
app.layout = html.Div(children=[             
    html.Div([
        html.H2('1) Electricity tariffs components in EU27 countries across different consumer types')
    ]),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country_dict[country], 'value': country} for country in country_dict.keys()],
        value=unique_countries[0],  # Default value
        style={'font-family': font_family}  # Set font for dropdown options
    ),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in unique_years],
        value=unique_years[-1],  # Default value
        style={'font-family': font_family}
    ),
    dcc.Graph(id='stacked-bar-chart'),
    html.Span(children=[
        'Note: The consumption bands used are: MWh 20-499 for small size firms, MWh 2,000-19,999 for medium size firms and MWh 70,000-149,999 for energy intensive firms.',
    html.Br(),
    '      Businesses are often reimbursed partly or fully some of the displayed taxes, such as VAT.',
    html.Br(),
    'Source: Bruegel based on Eurostat [nrg_pc_204_c and nrg_pc_203_v]']),
    html.Br(), html.Br(), 

    # Dropdowns for the second graph
    html.H2("2) Cross-country comparison"),
    dcc.Dropdown(
        id='tax-dropdown',
        options=[{'label': t, 'value': t} for t in unique_tax],
        value=unique_tax[0],  # Default value
        style={'font-family': font_family}
    ),
    dcc.Dropdown(
        id='time-dropdown',
        options=[{'label': time, 'value': time} for time in unique_time],
        value=unique_time[-1],  # Default value
        style={'font-family': font_family}
    ),
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': c, 'value': c} for c in unique_category],
        value=unique_category[0],  # Default value
        style={'font-family': font_family}
    ),
    dcc.Graph(id='bar-chart'),
    html.Span(children=[
        'Note: the consumption bands used are: KWh 1,000-2,499 for small households, KWh 2,500-4,999 for big households, MWh 20-499 for small size firms, MWh 2,000-19,999 for medium size firms, MWh 70,000-149,999 for energy intensive firms.',
    html.Br(),
    'S1 refers to the first half of the year, while S2 to the second half.',
    html.Br(),
    'Source: Bruegel based on Eurostat [nrg_pc_204 and nrg_pc_205]'
    ]),
    html.Br(), html.Br(),  

    # new third graph evolution of components
    
    # Third graph --> evolution of electricity tariffs components
    html.H2("3) Electricity tariffs components evolution by country"),
    dcc.Dropdown(
        id='countries-dropdown',
        options=[{'label': country_dict[country], 'value': country} for country in country_dict.keys()],
        value=unique_countries[0]  # Default value,
    ),
    dcc.Dropdown(
        id='categories-dropdown',
        options=[{'label': c, 'value': c} for c in unique_categories],
        value=unique_category[0]  # Default value
    ),
    dcc.Graph(id='line-chart'),
    html.Span('Note: the category "Taxes, fees levies and charges" includes all the others except "energy and supply" and "network costs".'),
    html.Br(),
    'Source: Bruegel based on Eurostat [nrg_pc_204_c and nrg_pc_203_v]',
    ])

# Callback to update the first graph based on dropdowns
@app.callback(
    Output('stacked-bar-chart', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)

# First stacked-bar graph 
def update_graph(selected_country, selected_year):
    return create_stacked_bar_chart(selected_country, selected_year)

# First stacked-bar graph 
def create_stacked_bar_chart(country, year):
    country_df = dff[dff['country'] == country]
    pivot_df = country_df.pivot(index='nrg_cons', columns='nrg_prc', values=year)

    fig = go.Figure()
    for col in pivot_df.columns:
        # Separate positive and negative values
        pos_values = pivot_df[col].clip(lower=0)
        neg_values = pivot_df[col].clip(upper=0)

        # Add trace for positive values if they exist
        if pos_values.sum() > 0:
            fig.add_trace(go.Bar(
                x=pivot_df.index,
                y=pos_values,
                name=f'{col} (+)',
                marker_color=pos_color.get(col, 'blue')  # Default color if not in dict
            ))

        # Add trace for negative values if they exist
        if neg_values.sum():
            fig.add_trace(go.Bar(
                x=pivot_df.index,
                y=neg_values,
                name=f'{col} (-)',
                marker_color=neg_color.get(col, 'red')  # Default color if not in dict
            ))

    # Calculate the sum of all components for each index
    total_values = pivot_df.sum(axis=1)

    # Add a scatter trace with diamonds to mark the total values
    fig.add_trace(go.Scatter(
        x=pivot_df.index,
        y=total_values,
        mode='markers',
        marker=dict(
            color='gold',  # Choose a color that stands out
            size=8,       # Size of the marker
            symbol='diamond',  # Diamond shape
            line=dict(
                color='black', # Color of the border
                width=0.8        # Width of the border
            )
        ),
        name='Final retail price'
    ))

    fig.update_layout(barmode='relative',
                title=f'Electricity Prices in {country_dict[country]}, in {year}',
                yaxis_title='EUR/kWh',
                font_family="Roboto")

    return fig

# Second -bar graph 

# New Callback to update the horizontal bar graph
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('tax-dropdown', 'value'),
     Input('time-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)

def update_bar_graph(selected_tax, selected_time, selected_category):
    return create_bar_chart(selected_tax, selected_time, selected_category)

# Function to create the bar graph
def create_bar_chart(tax, time, category):
    df_graph = dfg[dfg['tax'] == tax]
    df_piv = df_graph.pivot_table(index='country', columns='nrg_cons', values=time)
    df_comp = df_piv[[category]].sort_values(by=category)

    # Create a bar chart using Plotly
    fig2 = go.Figure(go.Bar(
        x=df_comp[category],
        y=df_comp.index,
        orientation='h',
        width=0.8
    ))

    # Update layout for the chart
    fig2.update_layout(
        title=f'Retail Electricity Price for {category}, {tax}, in {time}',
        xaxis_title='Electricity Price in €/KWh',
        yaxis_title='Country',
        height=600,
        font_family="Roboto"
    )

    return fig2

# Third, line-graph
# Define the callback to update the graph
@app.callback(
    Output('line-chart', 'figure'),
    [Input('countries-dropdown', 'value'),
     Input('categories-dropdown', 'value')]
)

# Function to create line chart 
def update_line_plot(selected_country, selected_type):
    return create_line_plot(selected_country, selected_type)

# Function to create the line plot
def create_line_plot(country, type):
    single_components = ['Network costs', 'Energy and supply', 'Other', 'Capacity taxes',
                         'Environmental taxes', 'Nuclear taxes', 'Renewable taxes', 'Value added tax (VAT)']
    fig = go.Figure()

    for i in single_components:
            df_plot = df[(df['nrg_prc'] == i) & (df['country'] == country) & (df['nrg_cons'] == type)]
            df_melt = pd.melt(df_plot, id_vars='nrg_prc', value_vars=['2017', '2018', '2019', '2020', '2021', '2022'])
            fig.add_trace(go.Scatter(x=df_melt['variable'], y=df_melt['value'], mode='lines', name=i, line_color=pos_color.get(i, 'black')))

    # does not seem to work
    df_all_tax = df[(df['nrg_prc'] == 'Taxes, fees, levies and charges') & (df['country'] == country) & (df['nrg_cons'] == type)]
    df_tpiv = pd.melt(df_all_tax, id_vars='nrg_prc', value_vars=['2017', '2018', '2019', '2020', '2021', '2022'])
    fig.add_trace(go.Scatter(x=df_tpiv['variable'], y=df_tpiv['value'], mode='lines', name='Taxes, fees, levies and charges', line=dict(dash='dot'), line_color='black'))

    fig.update_layout(title=f'Electricity tariff evolution by component in {country} for {type}',
                    xaxis_title='Year',
                    yaxis_title='EUR/kWh',
                    legend_title='Component',
                    font_family="Roboto")

    return fig

# Run the app
if __name__ == '__main__':
     app.run_server(debug=False)