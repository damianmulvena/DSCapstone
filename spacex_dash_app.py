# Import required libraries
import pandas as pd
import dash
# import dash_html_components as html
# import dash_core_components as dcc
import dash.html as html  # (previously dash.dash_html_components)
import dash.dcc as dcc    # (previously dash.dash_core_components)
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df.drop(columns="Unnamed: 0", inplace=True)              # Don't want to retain the former "index" column!

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

sites = spacex_df['Launch Site'].sort_values().unique()         # Want a unique, sorted, list of sites, for dropdown population
                                                                #   and for selecting them in callback function (when ALL is used).

site_options = [{'label': 'All Sites', 'value': 'ALL'}]         # Initialise with the dummy value we need for selecting ALL values
for site in sites:
    site_options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                    'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(   options=site_options,
                    value='ALL',         # makes no sense to use a Default, while also specifying a placeholder?
                    placeholder="Select a launch site here...",
                    # multi=True,        # Task 2 requires ONE or ALL, not multi-select.
                    searchable=True,     # Doesn't need specifying, as this is the default. Included as per instruction!
                    id='site-dropdown'
                    #  , style={'width': '50%'}  # Make sure dropdown width doesn't distract from using it!
                ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                min=0, max=10000, step=1000,
                marks={0: '0',
                       2500: '2500',
                       5000: '5000',
                       7500: '7500'},
                value=[min_payload, max_payload]),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# add callback decorator
@app.callback(
        Output(component_id='success-pie-chart', component_property='figure'),
        Input(component_id='site-dropdown', component_property='value')
        )

# Add computation to callback function and return graph
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df
        fig = px.pie(   filtered_df,
                        values='class',             # Pie chart represents proportion. Here it seems to "sum" class by Site.
                                                    # Only works because Failure is 0, so doesn't contribute to results!
                        names='Launch Site', 
                        title='Total Success Launches by Site')
    else:
        # return the outcomes piechart for a selected site...

        # To plot where the class values are distinguished, need to groupby and count.
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site
                                ].groupby(['class'])['class'            # group by, and select only the class column,
                                ].count().reset_index(name="count")     # create a new "count" column and name it. Reset 'class' from index name to column label

        fig = px.pie(   filtered_df,
                        values='count', 
                        names='class', 
                        title='Total Success Launches for site {}'.format(entered_site))

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

# add callback decorator
@app.callback(
        Output(component_id='success-payload-scatter-chart', component_property='figure'),
        [Input(component_id='site-dropdown', component_property='value'),
         Input(component_id="payload-slider", component_property="value")]
        )

# Add computation to callback function and return graph
def get_scatter_chart(entered_site, slider_range):
    # Filter data based on RangeSlider
    filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(slider_range[0], slider_range[1])]

    if entered_site == 'ALL':
        fig = px.scatter(   filtered_df,
                            x='Payload Mass (kg)',
                            y='class',
                            color='Booster Version Category', 
                            title='Correlation between Payload and Success, for ALL Sites ({}-{})'.format(slider_range[0], slider_range[1]))
    else:
        # return the scatter plot for a selected site...

        # Further filter data by Site, as selected
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        fig = px.scatter(   filtered_df,
                            x='Payload Mass (kg)',
                            y='class',
                            color='Booster Version Category', 
                            title='Correlation between Payload and Success for site {}'.format(entered_site))

    return fig



# Run the app
if __name__ == '__main__':
    app.run_server()
