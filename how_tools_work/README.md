# How Tools Work

This directory contains an example showing how manual tool calling can be implemented in an LLM
through the use of a special prompt and output parsing.

The example implements a simple weather tool using the OpenWeatherMap API and demonstrates how
functions can be called by prompting the LLM to return structured JSON output.

The intention is not to show a production-ready implementation as this is best carried out using a
framework like [LangChain](https://langchain.com/) and standardized tool protocols such as MCP.
Rather the purpose is to to illustrate the concepts behind tool calling and to demonstrate the components
involved.

## Requirements 

To run the example, ensure you have the required dependencies installed:

* [python](https://www.python.org/)
* [uv](https://docs.astral.sh/uv/)
* [jumppad](https://jumppad.dev/)
* [docker](https://www.docker.com/) or [podman](https://podman.io/)
* OpenWeatherMap API Key (free tier available [here](https://openweathermap.org/api))

## Running the Demo

### Setting the OpenWeatherMap API Key
First set your OpenWeatherMap API key as an environment variable. You can get a free API key by signing up
at [OpenWeatherMap](https://openweathermap.org/api) and then navigating to https://home.openweathermap.org/api_keys
to create a key. **Note:** It can take a couple of hours for the key to become active.

```bash
export WEATHER_API_KEY="your_api_key_here"
```

Once this has been set let's set the python dependencies.

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
This example uses the Hugging Face chat interface which provides a simple chat UI 
for interacting with OpenAI compatable APIs.

Start the Hugging Face chat interface locally with docker or podman using the 
following command:

```bash
jumppad up -f ./jumppad
```

```bash
INFO Creating resources from configuration path=/home/nicj/code/github.com/nicholasjackson/ai-patterns/how_tools_work/jumppad
INFO Creating ImageCache ref=resource.image_cache.default
INFO Creating output ref=output.mongodb_connection
INFO Creating output ref=output.chat_ui_url
INFO Creating output ref=output.instructions
INFO Creating Network ref=resource.network.chat_ui_network
INFO Creating Container ref=resource.container.mongodb
INFO Creating Container ref=resource.container.chat_ui
INFO Please wait, still creating resources [Elapsed Time: 15.000154]
```

With the Hugging Face chat interface running, we can now start the example server.

### Running the Example Server
To start the example server, run the following command:

```bash
python main.py
```

This will start an OpenAI compatible API server at `http://localhost:8000`.

When you send a chat message from the Hugging Face chat interface, it will be forwarded to the example server,
a custom system prompt is loaded (./prompt.md) that prompts the LLM to respond to 
questions in a structured JSON format when a tool call is required.

For example, if you ask "What's the weather in London?" the LLM will respond with JSON
response that looks like this:

```json
{
  "tool": "weather",
  "parameters": {
    "city": "London"
  }
}
```

The example server will parse this response, detect that a tool call is being requested,
execute the weather tool to get the current weather for London, and then return the result
back to the chat interface as a simple string.

```json
The weather in London is raining and overcast with a temperature of 15C.
```

All the example code is contained in `main.py` and the system prompt is in `prompt.md`.

## Stopping the Example

To stop the example server, simply terminate the process running `main.py` (e.g., by pressing `Ctrl+C` in the terminal).

You can then stop the Hugging Face chat interface by running:

```bash
jumppad down --force
```