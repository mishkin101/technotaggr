FileExplorer

gradio.FileExplorer(···)

Description
Creates a file explorer component that allows users to browse files on the machine hosting the Gradio app. As an input component, it also allows users to select files to be used as input to a function, while as an output component, it displays selected files.
Behavior
As input component: Passes the selected file or directory as a str path (relative to root) or list[str} depending on file_count
Your function should accept one of these types:

def predict(
	value: list[str] | str | None
)
	...


As output component: Expects function to return a str path to a file, or list[str] consisting of paths to files.
Your function should return one of these types:

def predict(···) -> str | list[str] | None
	...	
	return value