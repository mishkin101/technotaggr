JSON

gradio.JSON(···)

Description
Used to display arbitrary JSON output prettily. As this component does not accept user input, it is rarely used as an input component.
Behavior
As input component: Passes the JSON value as a dict or list depending on the value.
Your function should accept one of these types:

def predict(
	value: dict | list | None
)
	...


As output component: Expects a valid JSON str -- or a list or dict that can be serialized to a JSON string. The list or dict value can contain numpy arrays.
Your function should return one of these types:

def predict(···) -> dict | list | str | None
	...	
	return value

Initialization
Parameters
🔗

value: str | dict | list | Callable | None

🔗

label: str | I18nData | None

🔗

every: Timer | float | None

🔗

inputs: Component | list[Component] | set[Component] | None

🔗

show_label: bool | None

🔗

container: bool

🔗

scale: int | None

🔗

min_width: int

🔗

visible: bool | Literal['hidden']

🔗

elem_id: str | None

🔗

elem_classes: list[str] | str | None

🔗

render: bool

🔗

key: int | str | tuple[int | str, ...] | None

🔗

preserved_by_key: list[str] | str | None

🔗

open: bool

🔗

show_indices: bool

🔗

height: int | str | None

🔗

max_height: int | str | None

🔗

min_height: int | str | None

🔗

buttons: list[Literal['copy']] | None

