# Intelligent Assistant

A lightweight, cost-optimized AI task execution system that automatically selects an appropriate language model based on the complexity and requirements of each task.

The system is designed for environments where multiple LLMs are available and different tasks may require different levels of reasoning capability. Instead of sending every request to an expensive model, it analyzes the task and routes it to either a lower-cost or higher-capability model.

## Overview

The Intelligent Assistant works as an automated **LLM router and task executor**.

It:

- Loads tasks from a JSON input file.
- Analyzes each task to determine its complexity.
- Selects an appropriate model from a predefined list of allowed models.
- Optimizes and cleans the input prompt.
- Generates task-specific system instructions.
- Sends the request to an OpenAI-compatible API.
- Collects the generated responses.
- Saves all results to a JSON output file.

The project is particularly useful for applications where **cost, response quality, and task-specific model selection** need to be balanced.

## How It Works

```text
                tasks.json
                    |
                    v
            +----------------+
            |   Load Tasks   |
            +----------------+
                    |
                    v
          +---------------------+
          | Task Analysis       |
          |                     |
          | - Prompt length     |
          | - Complexity terms  |
          | - Task type         |
          +---------------------+
                    |
                    v
          +---------------------+
          | Model Selection     |
          |                     |
          | Cheap Model         |
          |        OR           |
          | Expensive Model     |
          +---------------------+
                    |
                    v
          +---------------------+
          | Prompt Optimization |
          | & System Instruction|
          +---------------------+
                    |
                    v
          +---------------------+
          | LLM API Request     |
          +---------------------+
                    |
                    v
               AI Response
                    |
                    v
              results.json
```

## Model Routing

The router identifies models using the list supplied through the `ALLOWED_MODELS` environment variable.

Models containing terms such as:

- `8b`
- `mini`
- `flash`
- `lite`

are treated as lower-cost candidates.

Models containing terms such as:

- `70b`
- `coder`
- `pro`
- `plus`
- `large`

are treated as higher-capability candidates.

If a task appears complex, the router uses the higher-capability model. Otherwise, it uses the lower-cost model.

### Complex Task Detection

A task is considered complex when:

- It contains programming or reasoning-related keywords.
- It contains terms such as `bug`, `fix`, `code`, `python`, `matrix`, `array`, `solve`, `logic`, `puzzle`, `refactor`, or `async`.
- Its cleaned prompt is longer than 500 characters.

This provides a simple heuristic-based routing mechanism without requiring a separate machine-learning model for routing.

## Prompt Optimization

Before sending a task to the model, the router normalizes whitespace and generates a task-specific system instruction.

Different task types receive different instructions.

For example:

### One-Sentence Tasks

The model is instructed to return exactly one sentence.

### Classification / Sentiment Tasks

The model is instructed to return only the classification label.

### Extraction Tasks

The model is instructed to extract the requested information concisely.

### Complex Tasks

The model is instructed to provide the required code or logical answer without unnecessary formatting or conversational filler.

This keeps responses focused and reduces unnecessary token usage.

## Input Format

The application expects a JSON file at:

```text
/input/tasks.json
```

Example:

```json
[
  {
    "task_id": "task_001",
    "prompt": "What is the capital of France?"
  },
  {
    "task_id": "task_002",
    "prompt": "Write a Python function to calculate the factorial of a number."
  }
]
```

Each task must contain:

- `task_id` — unique identifier for the task.
- `prompt` — the instruction that should be sent to the AI model.

## Output Format

Results are written to:

```text
/output/results.json
```

Example:

```json
[
  {
    "task_id": "task_001",
    "answer": "Paris"
  },
  {
    "task_id": "task_002",
    "answer": "def factorial(n): ..."
  }
]
```

## Environment Variables

The application expects the following environment variables:

```text
FIREWORKS_API_KEY
FIREWORKS_BASE_URL
ALLOWED_MODELS
```

### `FIREWORKS_API_KEY`

API key used to authenticate with the configured LLM provider.

### `FIREWORKS_BASE_URL`

Base URL of the OpenAI-compatible API endpoint.

### `ALLOWED_MODELS`

Comma-separated list of models that the router is allowed to use.

Example:

```text
ALLOWED_MODELS=model-a,model-b,model-c
```

The router uses this list when deciding which model should process each task.

## Installation

### Clone the Repository

```bash
git clone https://github.com/dubeyutsaw62-gif/Intelligent-assistant.git
cd Intelligent-assistant
```

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

The current project uses the OpenAI Python client.

## Configuration

Set the required environment variables before running the application.

### Windows PowerShell

```powershell
$env:FIREWORKS_API_KEY="your_api_key"
$env:FIREWORKS_BASE_URL="your_base_url"
$env:ALLOWED_MODELS="model-a,model-b,model-c"
```

### Linux/macOS

```bash
export FIREWORKS_API_KEY="your_api_key"
export FIREWORKS_BASE_URL="your_base_url"
export ALLOWED_MODELS="model-a,model-b,model-c"
```

## Running the Application

Once the environment variables and input file are available:

```bash
python router.py
```

The application will load the tasks, process them through the selected models, and save the responses to:

```text
/output/results.json
```

## Docker

The repository also contains a Docker configuration based on Python 3.11.

Build the image:

```bash
docker build -f DockerFile -t intelligent-assistant .
```

Run the container:

```bash
docker run \
  -e FIREWORKS_API_KEY="your_api_key" \
  -e FIREWORKS_BASE_URL="your_base_url" \
  -e ALLOWED_MODELS="model-a,model-b,model-c" \
  -v ./input:/input \
  -v ./output:/output \
  intelligent-assistant
```

The input and output directories are mounted so that the container can read `tasks.json` and persist `results.json`.

## Project Structure

```text
Intelligent-assistant/
│
├── router.py
├── requirements.txt
└── DockerFile
```

### `router.py`

Main application containing:

- Task loading
- Result saving
- Prompt cleaning
- Task complexity analysis
- Model selection
- System instruction generation
- LLM API execution
- Error handling

### `requirements.txt`

Contains the Python dependency required by the application:

```text
openai>=1.35.0
```

### `DockerFile`

Defines the container environment using Python 3.11 slim and executes `router.py`.

## Error Handling

The application handles several runtime failures:

- Missing input file
- Missing required environment variables
- API failures
- Empty model responses

A failure for an individual task does not terminate the entire task-processing loop; an error response is recorded for that task and processing continues.

## Design Goals

The project focuses on three primary goals:

### Cost Optimization

Use lower-cost models for straightforward tasks instead of routing every request to a more expensive model.

### Task-Aware Routing

Identify potentially complex requests using lightweight heuristics.

### Consistent Output

Apply task-specific system instructions to keep responses concise and aligned with the requested output format.

## Future Improvements

Possible extensions include:

- Benchmarking different routing strategies.
- Adding latency-aware model selection.
- Tracking token usage and cost per task.
- Using a trained classifier for task complexity prediction.
- Adding retry and exponential backoff for API failures.
- Supporting configurable routing rules.
- Adding structured logging.
- Adding automated evaluation of generated responses.
- Supporting more OpenAI-compatible providers.
