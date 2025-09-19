# Premier League NLP Agent

## 📊 Coverage Status
[![Coverage badge](https://raw.githubusercontent.com/Damcios-s/premier-nlp/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Damcios-s/premier-nlp/blob/python-coverage-comment-action-data/htmlcov/index.html)

## Overview

A conversational AI agent that processes natural language queries about Premier League teams and players, leveraging LangChain and Azure OpenAI for intelligent access to real-time Football Data API information.

## Key Features

- **Natural Language Processing** with fuzzy search for team/player names
- **Real-time Data Integration** from Football Data API
- **Structured Responses** including player names, positions, and dates of birth
- **AI-Powered Tool Orchestration** using Azure OpenAI and LangChain

## Technology Stack

- **Python 3.11+**
- **LangChain** - AI agent framework and tool orchestration  
- **Azure OpenAI** - GPT model for natural language understanding
- **Football Data API** - Real-time Premier League data source
- **Requests & Python-dotenv** - HTTP client and environment management

## System Architecture

The solution implements a **Tool-using AI Agent** pattern where the LLM orchestrates specialized tools to retrieve Premier League data:

```
User Query → AI Agent → Tool Selection → Data Retrieval → Response Generation
     ↓            ↓           ↓              ↓              ↓
"Who plays    LangChain   Player_Info   Football API   Formatted JSON
 for Arsenal?"  Agent       Tool         Service        Response
```

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│    User Interface (main.py) → PremierLeagueAgent        │
│    ↓                                                    │
│    AI Agent Layer (Azure OpenAI + LangChain)            │
│    ↓                                                    │  
│    Tools (Player_Info, Team_Info, Players_By_Position)  │
│    ↓                                                    │
│    SearchService (Fuzzy Matching + Filtering)           │
│    ↓                                                    │
│    FootballAPIService (HTTP + Caching)                  │
│    ↓                                                    │
│    Data Models (Player, Team)                           │
└─────────────────────────────────────────────────────────┘
```

### Design Patterns
- **Agent Pattern**: LangChain orchestrates tool usage from natural language
- **Repository Pattern**: FootballAPIService abstracts data access
- **Service Layer**: SearchService handles fuzzy matching and filtering  
- **Caching Pattern**: TTL-based caching reduces API calls

## Setup and Installation

### Prerequisites
- Azure OpenAI Account with API access
- [Football Data API](https://www.football-data.org/) key (free)
- Python 3.11+

### Installation Steps
1. **Clone and install**:
```bash
git clone https://github.com/Damcios-s/premier-nlp.git
cd premier-nlp
pip install -r requirements.txt
```

2. **Configure environment** - Create `.env` file:
```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_api_key  
AZURE_DEPLOYMENT=your_deployment_name
AZURE_MODEL_NAME=your_model_name
OPENAI_API_VERSION=api_version

# Football Data API
FOOTBALL_API_KEY=your_football_api_key
FOOTBALL_API_BASE=http://api.football-data.org/v4/

# Optional
CACHE_TTL_HOURS=24
MAX_COMPLETION_TOKENS=2048
```

## Usage

**Run the application:**
```bash
python main.py
```

**Example queries:**

- `"List all Manchester United squad members"`
- `"Who are Liverpool's goalkeepers?"`  
- `"Tell me about Mohamed Salah"`

## Implementation Details

### Tool Architecture
Three specialized LangChain tools handle different query types:
- **Player_Info**: Individual player lookup with fuzzy matching
- **Team_Info**: Complete team/squad information  
- **Players_By_Team_And_Position**: Filtered searches (e.g., "Arsenal midfielders")

### Fuzzy Search
Uses Python's `SequenceMatcher` with configurable thresholds:
- Teams: 0.6 similarity (handles variations like "Man United")
- Players: 0.7 similarity (higher precision for names)
- Positions: Case-insensitive substring matching

### API Integration
- **Data Source**: Football Data API v4 with 24-hour TTL caching
- **Fallback**: Serves stale cache when API unavailable
- **Error Handling**: Graceful degradation with informative messages

## Testing

**Run tests with coverage:**
```bash
python -m pytest --cov=. --cov-report=html
```

**Run specific tests:**
```bash
python -m pytest test/test_premier_league_agent.py -v
```
