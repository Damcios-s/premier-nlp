# Premier League NLP Agent 🏆⚽

A conversational AI agent powered by LangChain and Azure OpenAI that provides intelligent access to Premier League data. Ask natural language questions about teams, players, and positions to get detailed information from the Football Data API.

## 📊 Coverage Status
[![Coverage badge](https://raw.githubusercontent.com/Damcios-s/premier-nlp/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/Damcios-s/premier-nlp/blob/python-coverage-comment-action-data/htmlcov/index.html)

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English about Premier League teams and players
- **Intelligent Player Search**: Find players by name with fuzzy matching and get detailed information
- **Team Information**: Get comprehensive team data including squads, venues, and club details  
- **Position-Based Search**: Find all players in specific positions for any team
- **Real-time Data**: Fetches up-to-date information from the Football Data API
- **Caching System**: Optimized performance with intelligent data caching
- **Robust Error Handling**: Graceful handling of API failures and data issues

## 🛠️ Tech Stack

- **Python 3.11+**
- **LangChain** - AI agent framework
- **Azure OpenAI** - Large language model
- **Football Data API** - Premier League data source
- **Requests** - HTTP client for API calls
- **Python-dotenv** - Environment variable management

## 📋 Prerequisites

1. **Azure OpenAI Account**: You'll need access to Azure OpenAI services
2. **Football Data API Key**: Get a free API key from [Football Data](https://www.football-data.org/)
3. **Python 3.11+**: Make sure you have Python installed

## 🔧 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Damcios-s/premier-nlp.git
cd premier-nlp
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the root directory:
```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_DEPLOYMENT=your_deployment_name
AZURE_MODEL_NAME=your_model_name
OPENAI_API_VERSION=api_version

# Football Data API
FOOTBALL_API_KEY=your_football_api_key
FOOTBALL_API_BASE=http://api.football-data.org/v4/

# Optional Configuration
CACHE_TTL_HOURS=24
MAX_COMPLETION_TOKENS=2048
```

## 🎯 Usage

### Running the Interactive Agent

```bash
python main.py
```

This starts an interactive session where you can ask questions like:
- "Tell me about Mohamed Salah"
- "Who are the goalkeepers for Liverpool?"
- "Show me information about Arsenal"
- "Find all midfielders playing for Manchester City"

## 🏗️ Architecture

```
├── agents/                    # AI agent implementation
│   └── premier_league_agent.py
├── config/                    # Configuration management
│   └── settings.py
├── data_classes/             # Data models
│   ├── player.py
│   └── team.py
├── services/                 # Service layer
│   ├── football_api_service.py
│   └── search_service.py
├── tools/                    # LangChain tools
│   └── football_tools.py
├── test/                     # Unit tests
└── main.py                   # Entry point
```

### Key Components

- **PremierLeagueAgent**: Main conversational agent using LangChain
- **FootballTools**: LangChain tools for accessing Premier League data
- **FootballAPIService**: Service for interacting with Football Data API
- **SearchService**: Fuzzy search functionality for players and teams
- **Data Classes**: Type-safe models for players and teams

## 🔍 Available Tools

The agent has access to three main tools:

1. **Player_Info**: Get detailed information about any Premier League player
2. **Team_Info**: Get comprehensive team information including full squad
3. **Players_By_Team_And_Position**: Find all players in a specific position for a given team

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest test/test_premier_league_agent.py -v
```

## 📊 API Data Coverage

The agent provides access to:
- **Player Information**: Name, position, nationality, age, date of birth
- **Team Details**: Name, venue, founding year, colors, full squad
- **Squad Data**: Complete player rosters for all Premier League teams
- **Search Capabilities**: Fuzzy matching for player and team names

## 🔒 Error Handling

The application includes robust error handling for:
- API connection failures
- Invalid search queries  
- Missing environment variables
- Data parsing errors
- Azure OpenAI service issues

## 📈 Performance Features

- **Caching**: Team data is cached for 24 hours by default
- **Fuzzy Search**: Uses SequenceMatcher for flexible name matching
- **Graceful Degradation**: Falls back to cached data if API is unavailable
- **Request Optimization**: Minimizes API calls through caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
