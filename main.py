import logging
import sys
from config.settings import load_config
from agents.premier_league_agent import PremierLeagueAgent
from tools.football_tools import FootballTools
from services.football_api_service import FootballAPIService
from services.search_service import SearchService
from langchain_openai import AzureChatOpenAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('premier_league_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def init_agent(config):
    llm = AzureChatOpenAI(
        azure_deployment=config.azure.deployment,
        model_name=config.azure.model_name,
        max_completion_tokens=config.max_completion_tokens,
    )
    api_service = FootballAPIService(config.football_api)
    search_service = SearchService(api_service)
    tools = FootballTools(search_service)
    agent = PremierLeagueAgent(llm, tools)
    return agent


def main():
    try:
        config = load_config()

        if not config.azure.subscription_key:
            logger.error("Azure subscription key is required")
            sys.exit(1)

        if not config.football_api.api_key:
            logger.error("Football API key is required")
            sys.exit(1)

        logger.info("Initializing Premier League agent...")

        agent = init_agent(config)

        print("\n🏆 Premier League Info Agent is ready!")
        print("Ask me about Premier League teams, players, or positions.")
        print("Type 'exit' to quit.\n")

        # Main interaction loop
        while True:
            try:
                query = input("❓ Your question: ").strip()

                if query.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break

                if not query:
                    continue

                print("\n🤔 Processing your question...")
                response = agent.query(query)
                print(f"\n✅ {response}\n")
                print("-" * 80)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print(f"❌ An unexpected error occurred: {e}")

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"❌ Failed to start the application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
