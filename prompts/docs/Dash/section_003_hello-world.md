## Hello World

Building and launching an app with Dash can be done with just 5 lines of code.

Open a Python IDE on your computer, create an `app.py` file with the code below and install Dash if you haven't done so already.
To launch the app, type into your terminal the command `python app.py`. Then, go to the http link.

Alternatively, with Dash 2.11 or later, you can run this app and other examples from this documentation in a [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/latest/).

The code below creates a very small "Hello World" Dash app.

```python
from dash import Dash, html

app = Dash()

# Requires Dash 2.17.0 or later
app.layout = [html.Div(children='Hello World')]

if __name__ == '__main__':
    app.run(debug=True)
```

Hello World

Follow this example gif (using VS Code) if you are not sure how to set up the app:

![launch app](https://dash.plotly.com/assets/images/dash_in_20/dash-in-20-tutorial.gif)

