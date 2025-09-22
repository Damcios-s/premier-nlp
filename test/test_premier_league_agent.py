"""
Unit tests for the PremierLeagueAgent class.
Tests cover agent initialization, query handling, and LangChain integration functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from agents.premier_league_agent import PremierLeagueAgent
from tools.football_tools import FootballTools
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, Tool


@pytest.fixture
def mock_llm():
    """Create a mock AzureChatOpenAI."""
    llm = Mock(spec=AzureChatOpenAI)
    return llm


@pytest.fixture
def mock_football_tools():
    """Create a mock FootballTools instance."""
    tools = Mock(spec=FootballTools)

    # Create mock LangChain tools
    mock_tool1 = Mock(spec=Tool)
    mock_tool1.name = "Player_Info"
    mock_tool1.description = "Get player information"

    mock_tool2 = Mock(spec=Tool)
    mock_tool2.name = "Team_Info"
    mock_tool2.description = "Get team information"

    mock_tool3 = Mock(spec=Tool)
    mock_tool3.name = "Players_By_Team_And_Position"
    mock_tool3.description = "Get players by team and position"

    tools.get_tools.return_value = [mock_tool1, mock_tool2, mock_tool3]
    return tools


@pytest.fixture
def mock_agent_executor():
    """Create a mock AgentExecutor."""
    executor = Mock(spec=AgentExecutor)
    return executor


class TestPremierLeagueAgentInitialization:
    """Test PremierLeagueAgent initialization."""

    @patch('agents.premier_league_agent.create_openai_tools_agent')
    @patch('agents.premier_league_agent.AgentExecutor')
    @patch('agents.premier_league_agent.ChatPromptTemplate')
    def test_initialization_success(self, mock_prompt_template, mock_agent_executor_class,
                                    mock_create_agent, mock_llm, mock_football_tools):
        """Test successful agent initialization."""
        # Setup mocks
        mock_prompt = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt

        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        mock_executor = Mock(spec=AgentExecutor)
        mock_agent_executor_class.return_value = mock_executor

        # Create agent
        agent = PremierLeagueAgent(mock_llm, mock_football_tools)

        # Verify initialization
        assert agent.llm == mock_llm
        assert agent.tools == mock_football_tools
        assert agent.agent_executor == mock_executor
        assert agent.mode == "strict"  # Default mode
        assert agent.verbose == False  # Default verbose

        # Verify method calls
        mock_football_tools.get_tools.assert_called_once()
        mock_prompt_template.from_messages.assert_called_once()
        mock_create_agent.assert_called_once()
        mock_agent_executor_class.assert_called_once()

    @patch('agents.premier_league_agent.create_openai_tools_agent')
    def test_initialization_create_agent_error(self, mock_create_agent, mock_llm, mock_football_tools):
        """Test initialization when create_openai_tools_agent fails."""
        mock_create_agent.side_effect = Exception("Agent creation failed")

        with pytest.raises(Exception, match="Agent creation failed"):
            PremierLeagueAgent(mock_llm, mock_football_tools)

    @patch('agents.premier_league_agent.create_openai_tools_agent')
    @patch('agents.premier_league_agent.AgentExecutor')
    def test_initialization_agent_executor_error(self, mock_agent_executor_class, mock_create_agent,
                                                 mock_llm, mock_football_tools):
        """Test initialization when AgentExecutor creation fails."""
        mock_create_agent.return_value = Mock()
        mock_agent_executor_class.side_effect = Exception(
            "Executor creation failed")

        with pytest.raises(Exception, match="Executor creation failed"):
            PremierLeagueAgent(mock_llm, mock_football_tools)

    @patch('agents.premier_league_agent.create_openai_tools_agent')
    @patch('agents.premier_league_agent.AgentExecutor')
    @patch('agents.premier_league_agent.ChatPromptTemplate')
    def test_initialization_system_prompt_creation(self, mock_prompt_template, mock_agent_executor_class,
                                                   mock_create_agent, mock_llm, mock_football_tools):
        """Test that system prompt is created correctly."""
        mock_prompt = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt
        mock_create_agent.return_value = Mock()
        mock_agent_executor_class.return_value = Mock()

        agent = PremierLeagueAgent(mock_llm, mock_football_tools)

        # Verify prompt template was called with correct structure
        call_args = mock_prompt_template.from_messages.call_args[0][0]

        # Should have 3 message types: system, user, and MessagesPlaceholder
        assert len(call_args) == 3
        assert call_args[0][0] == "system"  # System message
        assert call_args[1][0] == "user"    # User message

    @patch('agents.premier_league_agent.create_openai_tools_agent')
    @patch('agents.premier_league_agent.AgentExecutor')
    @patch('agents.premier_league_agent.ChatPromptTemplate')
    def test_initialization_with_custom_parameters(self, mock_prompt_template, mock_agent_executor_class,
                                                   mock_create_agent, mock_llm, mock_football_tools):
        """Test initialization with custom mode and verbose parameters."""
        mock_prompt = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt
        mock_create_agent.return_value = Mock()
        mock_executor = Mock(spec=AgentExecutor)
        mock_agent_executor_class.return_value = mock_executor

        # Create agent with custom parameters
        agent = PremierLeagueAgent(
            mock_llm, mock_football_tools, mode="extended", verbose=True)

        # Verify custom parameters are set
        assert agent.mode == "extended"
        assert agent.verbose == True

        # Verify AgentExecutor is called with verbose=True
        mock_agent_executor_class.assert_called_once_with(
            agent=mock_create_agent.return_value,
            tools=mock_football_tools.get_tools.return_value,
            verbose=True
        )


class TestGetSystemPrompt:
    """Test the _get_system_prompt private method."""

    def test_get_system_prompt_strict_mode(self, mock_llm, mock_football_tools):
        """Test that system prompt is properly formatted in strict mode."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):
            agent = PremierLeagueAgent(
                mock_llm, mock_football_tools, mode="strict")

            prompt = agent._get_system_prompt()

            # Should be a string
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Should be substantial

            # Should have proper structure with rules and available information
            assert "ROLE:" in prompt
            assert "CORE RULES:" in prompt
            assert "AVAILABLE INFORMATION:" in prompt
            assert "RESPONSE FORMATTING:" in prompt
            assert "INVALID QUERIES:" in prompt

            # Should NOT have extended rules in strict mode
            assert "EXTENDED RULES:" not in prompt

    def test_get_system_prompt_extended_mode(self, mock_llm, mock_football_tools):
        """Test that system prompt includes extended rules in extended mode."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):
            agent = PremierLeagueAgent(
                mock_llm, mock_football_tools, mode="extended")

            prompt = agent._get_system_prompt()

            # Should be a string
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Should be substantial

            # Should have all sections including extended rules
            assert "ROLE:" in prompt
            assert "CORE RULES:" in prompt
            assert "EXTENDED RULES:" in prompt
            assert "AVAILABLE INFORMATION:" in prompt
            assert "RESPONSE FORMATTING:" in prompt
            assert "INVALID QUERIES:" in prompt

    def test_get_system_prompt_content_validation(self, mock_llm, mock_football_tools):
        """Test that system prompt contains expected content."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):
            agent = PremierLeagueAgent(mock_llm, mock_football_tools)

            prompt = agent._get_system_prompt()

            # Check for key content elements
            assert "Premier League information assistant" in prompt
            assert "ALWAYS use the provided tools" in prompt
            assert "Player details" in prompt
            assert "Team details" in prompt
            assert "football assistant" in prompt


class TestQueryMethod:
    """Test the query method."""

    def test_query_success(self, mock_llm, mock_football_tools):
        """Test successful query processing."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)

            # Mock successful agent executor response
            mock_response = {
                "output": "Mohamed Salah plays for Liverpool FC as a Right Winger."}
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.return_value = mock_response

            result = agent.query("Who is Mohamed Salah?")

            assert result == "Mohamed Salah plays for Liverpool FC as a Right Winger."
            agent.agent_executor.invoke.assert_called_once_with(
                {"input": "Who is Mohamed Salah?"})

    def test_query_no_output_in_response(self, mock_llm, mock_football_tools):
        """Test query when response doesn't contain output key."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)

            # Mock response without output key
            mock_response = {"other_key": "some value"}
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.return_value = mock_response

            result = agent.query("Who is Mohamed Salah?")

            assert result == "No response generated."

    def test_query_agent_executor_not_initialized(self, mock_llm, mock_football_tools):
        """Test query when agent executor is not initialized."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = None  # Simulate initialization failure

            result = agent.query("Who is Mohamed Salah?")

            assert result == "Agent is not properly initialized."

    def test_query_agent_executor_exception(self, mock_llm, mock_football_tools):
        """Test query when agent executor raises an exception."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)

            # Mock agent executor to raise exception
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.side_effect = Exception(
                "Processing error")

            result = agent.query("Who is Mohamed Salah?")

            assert "I encountered an error while processing your question: Processing error" in result

    def test_query_with_special_characters(self, mock_llm, mock_football_tools):
        """Test query with special characters and Unicode."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.return_value = {
                "output": "Unicode response"}

            questions_with_special_chars = [
                "Who is Måten Ødegaard?",
                "Tell me about Real Madrid's José Mourinho",
                "Find players with names like João & André",
                "Search for team: FC Barcelona ⚽",
            ]

            for question in questions_with_special_chars:
                result = agent.query(question)
                assert result == "Unicode response"


class TestAgentIntegration:
    """Test integration with LangChain components."""

    @patch('agents.premier_league_agent.create_openai_tools_agent')
    @patch('agents.premier_league_agent.AgentExecutor')
    @patch('agents.premier_league_agent.ChatPromptTemplate')
    def test_langchain_component_integration(self, mock_prompt_template, mock_agent_executor_class,
                                             mock_create_agent, mock_llm, mock_football_tools):
        """Test proper integration with LangChain components."""
        # Setup mocks
        mock_prompt = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt

        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        mock_executor = Mock(spec=AgentExecutor)
        mock_agent_executor_class.return_value = mock_executor

        # Create agent
        agent = PremierLeagueAgent(mock_llm, mock_football_tools)

        # Verify all components were called with correct parameters
        tools_list = mock_football_tools.get_tools.return_value
        mock_create_agent.assert_called_once_with(
            mock_llm, tools_list, mock_prompt)

        mock_agent_executor_class.assert_called_once_with(
            agent=mock_agent,
            tools=tools_list,
            verbose=agent.verbose
        )

    def test_tools_integration(self, mock_llm, mock_football_tools):
        """Test that agent properly integrates with football tools."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)

            # Verify tools were retrieved during initialization
            mock_football_tools.get_tools.assert_called_once()

            # Verify tools are stored
            assert agent.tools == mock_football_tools

    def test_llm_integration(self, mock_llm, mock_football_tools):
        """Test that agent properly integrates with LLM."""
        with patch('agents.premier_league_agent.create_openai_tools_agent') as mock_create_agent, \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)

            # Verify LLM was passed to create_openai_tools_agent
            args, kwargs = mock_create_agent.call_args
            assert args[0] == mock_llm  # First argument should be the LLM

            # Verify LLM is stored
            assert agent.llm == mock_llm


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""

    def test_initialization_with_none_parameters(self):
        """Test initialization with None parameters."""
        with pytest.raises(Exception):
            PremierLeagueAgent(None, None)

    def test_query_with_none_parameter(self, mock_llm, mock_football_tools):
        """Test query method with None parameter."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.return_value = {
                "output": "Handled None input"}

            result = agent.query(None)

            # Should still work, passing None to the agent executor
            agent.agent_executor.invoke.assert_called_once_with(
                {"input": None})

    def test_complex_error_scenarios(self, mock_llm, mock_football_tools):
        """Test complex error scenarios during query processing."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = Mock()

            # Test different types of exceptions
            exceptions_to_test = [
                ValueError("Invalid input"),
                RuntimeError("Runtime error"),
                KeyError("Missing key"),
                AttributeError("Attribute error"),
                TypeError("Type error"),
            ]

            for exception in exceptions_to_test:
                agent.agent_executor.invoke.side_effect = exception
                result = agent.query("Test query")
                assert "I encountered an error while processing your question:" in result
                assert str(exception) in result

    def test_memory_and_performance_with_long_queries(self, mock_llm, mock_football_tools):
        """Test memory and performance with very long queries."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = Mock()
            agent.agent_executor.invoke.return_value = {
                "output": "Long query response"}

            # Create a very long query
            long_query = "Tell me about players " * 1000

            result = agent.query(long_query)

            assert result == "Long query response"
            agent.agent_executor.invoke.assert_called_once_with(
                {"input": long_query})

    def test_concurrent_query_handling(self, mock_llm, mock_football_tools):
        """Test that agent can handle multiple queries (simulated concurrency)."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = Mock()

            # Simulate multiple rapid queries
            queries = [f"Query {i}" for i in range(10)]
            responses = []

            for i, query in enumerate(queries):
                agent.agent_executor.invoke.return_value = {
                    "output": f"Response {i}"}
                response = agent.query(query)
                responses.append(response)

            # All queries should be handled correctly
            assert len(responses) == 10
            for i, response in enumerate(responses):
                assert response == f"Response {i}"

    def test_state_consistency_after_errors(self, mock_llm, mock_football_tools):
        """Test that agent state remains consistent after errors."""
        with patch('agents.premier_league_agent.create_openai_tools_agent'), \
                patch('agents.premier_league_agent.AgentExecutor'):

            agent = PremierLeagueAgent(mock_llm, mock_football_tools)
            agent.agent_executor = Mock()

            # First query fails
            agent.agent_executor.invoke.side_effect = Exception("First error")
            result1 = agent.query("First query")
            assert "I encountered an error" in result1

            # Second query succeeds
            agent.agent_executor.invoke.side_effect = None
            agent.agent_executor.invoke.return_value = {
                "output": "Second query success"}
            result2 = agent.query("Second query")
            assert result2 == "Second query success"

            # Agent should still be functional
            assert agent.llm == mock_llm
            assert agent.tools == mock_football_tools
            assert agent.agent_executor is not None
