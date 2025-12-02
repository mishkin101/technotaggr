### Dash Mantine Components

Dash Mantine is a community-maintained library built off of the Mantine component system.
Although it is not officially maintained or supported by the Plotly team, Dash Mantine is another powerful way of customizing app layouts.

This example uses the `SimpleGrid` component to create equal-width columns. The `cols` prop makes the layout responsive, showing one
column on smaller screens and two columns from the `md` breakpoint and up.

For the app below to run successfully, make sure to install the Dash Mantine Components library: `pip install dash-mantine-components==2.3.0`

> Read more about the Dash Mantine Components in the [third-party documentation](https://www.dash-mantine-components.com/).

```py
from dash import Dash, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import dash_ag_grid as dag

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

app = Dash()

app.layout = dmc.MantineProvider(
    dmc.Container([\
        dmc.Title("My First App with Data, Graph, and Controls", c="blue", order=3),\
        dmc.RadioGroup(\
           dmc.Group([dmc.Radio(i, value=i) for i in  ['pop', 'lifeExp', 'gdpPercap']]),\
            id='my-dmc-radio-item',\
            value='lifeExp',\
            p="sm"\
        ),\
        dmc.SimpleGrid([\
            dag.AgGrid(\
                rowData=df.to_dict("records"),\
                columnDefs=[{"field": i} for i in df.columns],\
            ),\
            dcc.Graph(figure={}, id='graph-placeholder')\
        ], cols={"base": 1, "md": 2})\
    ], fluid=True)
)

@callback(
    Output('graph-placeholder', 'figure'),
    Input('my-dmc-radio-item', 'value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
```

![Dash Mantine app](https://dash.plotly.com/assets/images/dash_in_20/dash_mantine_images.png)

