### Dash Design Kit (DDK)

Dash Design Kit is our high level UI framework that is purpose-built for Dash.
With Dash Design Kit, you don't need to use HTML or CSS. Apps are mobile responsive by default and everything is themeable.
Dash Design Kit is licensed as part of Dash Enterprise and officially supported by Plotly.

Here's an example of what you can do with Dash Design Kit (note that you won't be able to run this example without a Dash Enterprise license).

```python
# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import dash_design_kit as ddk

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app
app = Dash()

# App layout
app.layout = ddk.App([\
    ddk.Header(ddk.Title('My First App with Data, Graph, and Controls')),\
    dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'],\
                    value='lifeExp',\
                    inline=True,\
                    id='my-ddk-radio-items-final'),\
    ddk.Row([\
        ddk.Card([\
            dag.AgGrid(\
                rowData=df.to_dict('records'),\
                columnDefs=[{"field": i} for i in df.columns]\
            )\
        ], width=50),\
        ddk.Card([\
            ddk.Graph(figure={}, id='graph-placeholder-ddk-final')\
        ], width=50),\
    ]),\
\
])

# Add controls to build the interaction
@callback(
    Output(component_id='graph-placeholder-ddk-final', component_property='figure'),
    Input(component_id='my-ddk-radio-items-final', component_property='value')
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

Afghanistan

31889923

Asia

43.828

Albania

3600523

Europe

76.423

Algeria

33333216

Africa

72.301

Angola

12420476

Africa

42.731

Argentina

40301927

Americas

75.32

Australia

20434176

Oceania

81.235

Austria

8199783

Europe

79.829

Bahrain

708573

Asia

75.635

Bangladesh

150448339

Asia

64.062

Belgium

10392226

Europe

79.441

Benin

8078314

Africa

56.728

Bolivia

9119152

Americas

65.554

Bosnia and Herzegovina

4552198

Europe

74.852

Botswana

1639131

Africa

50.728

Brazil

190010647

Americas

72.39

Bulgaria

7322858

Europe

73.005

Burkina Faso

14326203

Africa

52.295

Burundi

8390505

Africa

49.58

toof

Pageof

AsiaEuropeAfricaAmericasOceania01020304050607080

continentavg of lifeExp

[plotly-logomark](https://plotly.com/)

