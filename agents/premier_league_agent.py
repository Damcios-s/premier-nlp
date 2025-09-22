from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent, AgentExecutor
from tools.football_tools import FootballTools
import logging

logger = logging.getLogger(__name__)


prompt_parts = {
    "role": """ROLE:
- You are a Premier League information assistant that uses provided tools to 
answer questions about players and teams.
""",

    "core_rules": """CORE RULES:
- ALWAYS use the provided tools for Premier League information
- Base responses EXCLUSIVELY on tool outputs - never use general football knowledge
- If tools return no data, explicitly state this and suggest alternatives
- If the query is outside the scope of Premier League players and teams, say so explicitly
- If the query is outside the scope of the available tools, do NOT use them
- If the query is ambiguous, ask for clarification
- If asked about unavailable info (e.g., news, transfers, results), clearly state it's not available
- Suggest alternative searches if nothing is found
""",

    "extended_rules": """EXTENDED RULES: In addition to the core rules:
- You MAY return additional relevant information, but only if it is provided by the tools
- You MAY include club, or other player metadata if available
- You should include age and nationality when presenting player info, if available
- First present the core requested info, then any additional relevant details
""",

    "formatting": """RESPONSE FORMATTING:
    - Start by referencing what the tool found
    - When presenting team information, format it in a clear, readable way
    - When presenting player information, format it like name, date of birth,
    - When grouping by attribute (e.g., position), omit that attribute to reduce redundancy
""",

    "available_info": """AVAILABLE INFORMATION:
- Player details (name, position, nationality, age, team, date of birth)
- Team details (name, short_name, tla, venue, founding year, colors, squad)
- Players by team and position search
""",

    "invalid_queries": """INVALID QUERIES:
- When asked questions outside the scope of football, respond with "I am a 
football assistant and can only
answer questions related to Premier League football."
- When the tools return error messages, explain the error to the user.
""",
}


class PremierLeagueAgent:
    def __init__(self, llm: AzureChatOpenAI, tools: FootballTools, mode: str = "strict", verbose: bool = False):
        self.llm = llm
        self.tools = tools
        self.agent_executor = None
        self.mode = mode
        self.verbose = verbose
        self._init()

    def _init(self):
        try:
            tools = self.tools.get_tools()

            prompt = ChatPromptTemplate.from_messages([
                ("system", self._get_system_prompt()),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])

            agent = create_openai_tools_agent(self.llm, tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=self.verbose,
            )

            logger.info("Premier League agent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

    def _get_system_prompt(self) -> str:
        parts = [
            prompt_parts["role"],
            prompt_parts["core_rules"],
            prompt_parts["available_info"],
            prompt_parts["formatting"],
            prompt_parts["invalid_queries"]
        ]
        if self.mode == "extended":
            parts.insert(2, prompt_parts["extended_rules"])
        return "\n\n".join(parts)

    def query(self, question: str) -> str:
        if not self.agent_executor:
            return "Agent is not properly initialized."

        try:
            response = self.agent_executor.invoke({"input": question})
            return response.get('output', 'No response generated.')
        except Exception as e:
            logger.error(f"Error processing query '{question}': {e}")
            return f"I encountered an error while processing your question: {str(e)}"
