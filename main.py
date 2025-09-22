import logging
import sys
import argparse
import time
from config.settings import load_config
from agents.premier_league_agent import PremierLeagueAgent
from tools.football_tools import FootballTools
from services.football_api_service import FootballAPIService
from services.search_service import SearchService
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Premier League Info Agent')
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging output'
    )
    parser.add_argument(
        '-t', '--timing',
        action='store_true',
        help='Show timing information for queries'
    )
    parser.add_argument(
        '-m', '--mode',
        choices=['strict', 'extended'],
        default='strict',
        help='Enable extended mode for the agent'
    )
    return parser.parse_args()


def setup_logging(verbose=False):
    """Setup logging configuration based on verbosity level."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('premier_league_agent.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def init_agent(config, mode: str = "strict", verbose: bool = False) -> PremierLeagueAgent:
    llm = AzureChatOpenAI(
        azure_deployment=config.azure.deployment,
        model_name=config.azure.model_name,
        max_completion_tokens=config.max_completion_tokens,
    )
    api_service = FootballAPIService(config.football_api)
    search_service = SearchService(api_service)
    tools = FootballTools(search_service)
    agent = PremierLeagueAgent(llm, tools, mode, verbose)
    return agent


def main():
    # Parse command line arguments
    args = parse_arguments()

    # Setup logging based on verbosity
    setup_logging(verbose=args.verbose)

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
        if args.verbose:
            print("📝 Verbose logging enabled")
        if args.timing:
            print("⏱️  Timing information enabled")
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

                # Track timing if requested
                if args.timing:
                    start_time = time.time()

                response = agent.query(query)

                if args.timing:
                    end_time = time.time()
                    duration = end_time - start_time
                    print(f"\n⏱️  Query processed in {duration:.2f} seconds")

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
