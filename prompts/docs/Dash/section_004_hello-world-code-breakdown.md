### Hello World: Code Breakdown

```py
# Import packages
from dash import Dash, html
```

- When creating Dash apps, you will almost always use the import statement above. As you create more advanced Dash apps, you will import more packages.

```py
# Initialize the app
app = Dash()
```

- This line is known as the Dash constructor and is responsible for initializing your app. It is almost always the same for any Dash app you create.

```py
# App layout
app.layout = [html.Div(children='Hello World')]
```

- The app layout represents the app components that will be displayed in the web browser and here is provided as a `list`, though it could also be a Dash component.
In this example, a single component was added to the list: an `html.Div`.
The Div has a few properties, such as `children`, which we use to add text content to the page: "Hello World".

```py
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
```

- These lines are for running your app, and they are almost always the same for any Dash app you create.

