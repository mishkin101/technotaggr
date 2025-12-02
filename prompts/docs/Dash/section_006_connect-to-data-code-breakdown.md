### Connect to Data: Code Breakdown

```py
# Import packages
from dash import Dash, html
import dash_ag_grid as dag
import pandas as pd
```

- We import the `dash_ag_grid` package (as `dag`) to display the data inside a Dash AG Grid table. We also import the pandas library to read the CSV sheet data.

```py
# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
```

- Here we read the CSV sheet into a pandas dataframe. This will make it easier to slice, filter, and inspect the data.

- If you prefer to use a CSV sheet that is on your computer (and not online), make sure to save it in the same folder that contains the `app.py` file.
Then, update the line of code to: `df = pd.read_csv('NameOfYourFile.csv')`

- If you're using an Excel sheet, make sure to `pip install openpyxl`. Then, update the line of code to:
`df = pd.read_excel('NameOfYourFile.xlsx', sheet_name='Sheet1')`


> **Tip**: You can read the [pandas docs](https://pandas.pydata.org/pandas-docs/stable/reference/io.html) on reading data if your data is in a different format, or consider using another Python library if you are connecting to a specific database type or file format.
> For example, if you're considering using Databricks as a backend for your Dash app, you may review their Python documentation for recommendations on how to connect.

```py
# App layout
app.layout = [\
    html.Div(children='My First App with Data'),\
    dag.AgGrid(\
        rowData=df.to_dict('records'),\
        columnDefs=[{"field": i} for i in df.columns]\
    )\
]
```

- In addition to the app title, we add the AG Grid component and read the pandas dataframe into the table. We define the columns using `columnDefs`.

