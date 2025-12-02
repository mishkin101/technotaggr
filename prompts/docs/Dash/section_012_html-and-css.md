### HTML and CSS

HTML and CSS are the lowest level of interface for rendering content on the web.
The HTML is a set of components, and CSS is a set of styles applied to those components.
CSS styles can be applied within components via the `style` property, or they can be defined as a separate CSS file in reference with the `className` property, as in the example below.

```python
# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(external_stylesheets=external_stylesheets)

# App layout
app.layout = [\
    html.Div(className='row', children='My First App with Data, Graph, and Controls',\
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),\
\
    html.Div(className='row', children=[\
        dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'],\
                       value='lifeExp',\
                       inline=True,\
                       id='my-radio-buttons-final')\
    ]),\
\
    html.Div(className='row', children=[\
        html.Div(className='six columns', children=[\
            dag.AgGrid(\
                rowData=df.to_dict('records'),\
                columnDefs=[{"field": i} for i in df.columns]\
            )\
        ]),\
        html.Div(className='six columns', children=[\
            dcc.Graph(figure={}, id='histo-chart-final')\
        ])\
    ])\
]

# Add controls to build the interaction
@callback(
    Output(component_id='histo-chart-final', component_property='figure'),
    Input(component_id='my-radio-buttons-final', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
```

My First App with Data, Graph, and Controls

poplifeExpgdpPercap

Country

Pop

Continent

Life Exp

Gdp Percap

Afghanistan

31889923

Asia

43.828

974.5803384

Albania

3600523

Europe

76.423

5937.029525999999

Algeria

33333216

Africa

72.301

6223.367465

Angola

12420476

Africa

42.731

4797.231267

Argentina

40301927

Americas

75.32

12779.37964

Australia

20434176

Oceania

81.235

34435.367439999995

Austria

8199783

Europe

79.829

36126.4927

Bahrain

708573

Asia

75.635

29796.04834

Bangladesh

150448339

Asia

64.062

1391.253792

Belgium

10392226

Europe

79.441

33692.60508

Benin

8078314

Africa

56.728

1441.284873

Bolivia

9119152

Americas

65.554

3822.137084

Bosnia and Herzegovina

4552198

Europe

74.852

7446.298803

Botswana

1639131

Africa

50.728

12569.85177

Brazil

190010647

Americas

72.39

9065.800825

Bulgaria

7322858

Europe

73.005

10680.79282

Burkina Faso

14326203

Africa

52.295

1217.032994

Burundi

8390505

Africa

49.58

430.0706916

Cambodia

14131858

Asia

59.723

1713.778686

toof

Pageof

AsiaEuropeAfricaAmericasOceania01020304050607080

continentavg of lifeExp

[plotly-logomark](https://plotly.com/)

