# Multi-Agent Research System

A small LangChain application that researches a topic with multiple agents and
returns a structured report with critic feedback.

## What it does

The pipeline runs four steps:

1. **Search agent** - searches the web with Tavily and finds relevant sources.
2. **Reader agent** - selects useful URLs and extracts readable page content.
3. **Writer chain** - turns the gathered information into a report.
4. **Critic chain** - scores the report and suggests improvements.

The pipeline returns `search_results`, `scraped_content`, `report`, and
`feedback`.

┌─────────────────────────────────────────────────────┐
│           Streamlit UI (app.py)                     │
│      Multi-Agent Research Assistant Interface       │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│      Research Pipeline (pipeline.py)                │
│        Orchestrates multi-agent workflow            │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐    ┌────▼─────┐   ┌───▼────┐
│Search │    │   Reader  │   │ Writer │
│Agent  │    │   Agent   │   │ Chain  │
└───┬───┘    └────┬─────┘   └───┬────┘
    │             │             │
    │  ┌──────────▼─────────┐   │
    └─▶│  Tools Layer       │◀──┘
       │                    │
       │ • web_search      │
       │ • scrape_url      │
       │                    │
       └────────┬───────────┘
                │
            ┌───▼────────┐
            │ Critic     │
            │ Chain      │
            └────────────┘

In simple terms: the system searches first, reads the most useful sources,
writes a report, and then checks the report before returning it.

## Project structure

```text
.
├── config/
│   └── prompts.yaml          # Writer and critic prompts
├── src/
│   ├── agents/agents.py      # LLM, agents, and LangChain chains
│   ├── pipeline/pipeline.py  # Main research workflow
│   ├── tools/search_tool.py  # Tavily web-search tool
│   ├── tools/scrape.py       # URL content extraction
│   ├── logger/               # Application logging
│   └── exception/            # Custom exception handling
├── .env.example              # Environment variable template
├── main.py                   # Starter placeholder
├── pyproject.toml            # Dependencies and project metadata
└── uv.lock                   # Locked dependency versions
```

## Requirements

- Python **3.12 or newer**
- A [Tavily](https://tavily.com/) API key
- An [OpenRouter](https://openrouter.ai/) API key
- `uv` (recommended) or another Python package manager

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd LangChain-Multi-Agent-Research-System
```

### 2. Install dependencies

Using `uv`:

```bash
uv sync
```

Using a regular virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows
pip install -e .
```

### 3. Configure API keys

Create a `.env` file in the project root:

```env
TAVILY_API_KEY=your_tavily_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

`.env` is ignored by Git. Never commit real API keys.

`GROQ_API_KEY` is included in `.env.example` for an older/alternative
configuration, but the current implementation uses OpenRouter.

## Run the research pipeline

From the project root, run:

```bash
uv run python -m src.pipeline.pipeline
```

Without `uv`, activate the virtual environment first and run:

```bash
python -m src.pipeline.pipeline
```

The example execution researches **“Artificial Intelligence in Healthcare”**
and prints the generated report and critic feedback.

## Use it from Python

```python
from src.pipeline.pipeline import run_research_pipeline

result = run_research_pipeline("The impact of renewable energy")

print(result["report"])
print(result["feedback"])
```

## Customize the prompts

Edit [`config/prompts.yaml`](config/prompts.yaml) to change the report
structure, writing style, findings, and critic feedback format.

## Change the model

The current model is configured in
[`src/agents/agents.py`](src/agents/agents.py):

```python
model="minimax/minimax-m3:free"
```

Replace it with another OpenRouter-supported model if needed.

## Troubleshooting

### Missing API key

Check that `.env` exists in the project root and contains valid
`TAVILY_API_KEY` and `OPENROUTER_API_KEY` values.

### Import or file errors

Run commands from the repository root. The prompt loader expects the relative
path `config/prompts.yaml`.

### Scraping fails for a website

Some websites block automated requests or require JavaScript. The scraper
tries Trafilatura, Readability, and BeautifulSoup, but it cannot access every
website.

### Timeouts or rate limits

Check your Tavily/OpenRouter quotas and try again later. The scraper uses a
15-second request timeout.

## Development notes

- The pipeline logs progress for each stage.
- Run the automated tests with `python -m unittest discover -s tests`.
- `main.py` currently contains only the project starter placeholder. Use
  `src.pipeline.pipeline` to run the research workflow.
- Generated reports depend on the quality and recency of the web sources found
  by Tavily.
