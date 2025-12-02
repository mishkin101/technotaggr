### Controls: Code Breakdown

```py
# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
```

- We import `dcc` like we did in the previous section to use `dcc.Graph`. In this example, we need `dcc` for `dcc.Graph` as well as the radio buttons component, `dcc.RadioItems`.

- We import `dash_ag_grid` (as `dag`) to display the data in a table.

- To work with the callback in a Dash app, we import the `callback` module and the two arguments commonly used within the callback: `Output` and `Input`.


```py
# App layout
app.layout = [\
    html.Div(children='My First App with Data, Graph, and Controls'),\
    html.Hr(),\
    dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'], value='lifeExp', id='controls-and-radio-item'),\
    dag.AgGrid(\
        rowData=df.to_dict('records'),\
        columnDefs=[{"field": i} for i in df.columns]\
    ),\
    dcc.Graph(figure={}, id='controls-and-graph')\
]
```

- Notice that we add the `RadioItems` component to the layout, directly above the AG Grid.
There are three options, one for every radio button. The `lifeExp` option is assigned to the `value` property, making it the currently selected value.

- Both the `RadioItems` and the `Graph` components were given `id` names: these will be used by the callback to identify the components.


```py
# Add controls to build the interaction
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
    return fig
```

- The inputs and outputs of our app are the properties of a particular component.
In this example, our input is the `value` property of the component that has the ID "controls-and-radio-item". If you look back at the layout, you will see that this is currently `lifeExp`.
Our output is the `figure` property of the component with the ID "controls-and-graph", which is currently an empty dictionary (empty graph).

- The callback function's argument `col_chosen` refers to the component property of the input `lifeExp`.
We build the histogram chart inside the callback function, assigning the chosen radio item to the y-axis attribute of the histogram.
This means that every time the user selects a new radio item, the figure is rebuilt and the y-axis of the figure is updated.

- Finally, we return the histogram at the end of the function. This assigns the histogram to the `figure` property of the `dcc.Graph`, thus displaying the figure in the app.


