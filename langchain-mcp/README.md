# Calling MCP servers using LangGraph

This directory contains a simple example showing how to call an MCP server using LangGraph.

## Requirements

* [python](https://www.python.org/)
* [uv](https://docs.astral.sh/uv/)

## Running the Demo

### Installing Python Dependencies
To set the python dependencies use uv to create a virtual environment and install the dependencies:

```bash
uv sync
```

Once you have downloaded the depencencies you need to activate the virtual environment:

```bash
./.venv/bin/activate
```

Once this is done, let's move on to starting the user interface.

### Starting the UI

Once the dependencies are installed you can run the example using:

```bash
langraph dev
```

This will start the LangGraph development server. You can then use the link
provided in the terminal to open the LangGraph interface in your web browser.