from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent, AgentExecutor
from tools.football_tools import FootballTools
from services.football_api_service import FootballAPIService
from config.settings import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class PremierLeagueAgent:
    def __init__(self, config: AppConfig):
        self.config = config
        self.llm = None
        self.agent_executor = None
        # self._setup_env()
        self._init()

    # def _setup_env(self):
    #     os.environ["AZURE_OPENAI_API_KEY"] = self.config.azure.subscription_key
    #     os.environ["AZURE_OPENAI_ENDPOINT"] = self.config.azure.endpoint
    #     os.environ["OPENAI_API_VERSION"] = self.config.azure.api_version

    def _init(self):
        try:
            self.llm = AzureChatOpenAI(
                azure_deployment=self.config.azure.deployment,
                model_name=self.config.azure.model_name,
                max_completion_tokens=self.config.max_completion_tokens,
            )

            api_service = FootballAPIService(self.config.football_api)
            football_tools = FootballTools(api_service)
            tools = football_tools.get_tools()

            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            agent = create_openai_tools_agent(self.llm, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
            )

            logger.info("Premier League agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    def _get_system_prompt(self) -> str:
        return """You are a helpful assistant for Premier League information.

                                IMPORTANT RULES:
                                1. You MUST use the provided tools to get information about players, teams, and positions
                                2. You should ONLY provide information that comes from the tool outputs
                                3. Do NOT use your general knowledge about football - only use what the tools return
                                4. If the tools don't return information about something, say so explicitly
                                5. Always start your response by referencing what the tool found
                                6. If asked about information not available in the tools (like recent news, transfers, current season performance, match results, league tables), clearly state that this information is not available in your data source
                                7. Be helpful and try to suggest alternative searches if the initial search doesn't find results
                                8. When presenting player or team information, format it in a clear, readable way
                                9. If a user asks for multiple pieces of information, use the appropriate tools for each request

                                Available information:
                                - Player details (name, position, nationality, age, team, date of birth)
                                - Team details (name, short_name, tla, venue, founding year, colors, squad)
                                - Players by team and position search

                                Your responses should be based EXCLUSIVELY on the tool outputs."""

    def query(self, question: str) -> str:
        if not self.agent_executor:
            return "Agent is not properly initialized."

        try:
            response = self.agent_executor.invoke({"input": question})
            return response.get('output', 'No response generated.')
        except Exception as e:
            logger.error(f"Error processing query '{question}': {e}")
            return f"I encountered an error while processing your question: {str(e)}"
