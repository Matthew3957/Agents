"""
Agent Manager - Handles agent routing and execution
"""

import json
import re
from typing import List, Dict, Any
import ollama


class Agent:
    """Base agent class"""

    def __init__(self, name, config, tool_registry):
        self.name = name
        self.model = config.get("model", "ministral:3b")
        self.description = config.get("description", "")
        self.temperature = config.get("temperature", 0.7)
        self.tool_names = config.get("tools", [])
        self.tool_registry = tool_registry

    def execute(self, prompt, conversation_history=None):
        """Execute the agent's task"""
        messages = []

        # Add system prompt
        system_prompt = self._build_system_prompt()
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        # Execute with Ollama
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature}
        )

        assistant_message = response['message']['content']

        # Check for tool usage
        tools_used = []
        final_response = assistant_message

        # Parse tool calls from response
        tool_calls = self._extract_tool_calls(assistant_message)

        if tool_calls:
            tool_results = []
            for tool_call in tool_calls:
                result = self._execute_tool(tool_call)
                tools_used.append(tool_call["tool"])
                tool_results.append(result)

            # If tools were called, ask the model to synthesize a response
            if tool_results:
                synthesis_prompt = self._build_synthesis_prompt(prompt, tool_results)
                synthesis_messages = messages + [
                    {"role": "assistant", "content": assistant_message},
                    {"role": "user", "content": synthesis_prompt}
                ]

                synthesis_response = ollama.chat(
                    model=self.model,
                    messages=synthesis_messages,
                    options={"temperature": self.temperature}
                )

                final_response = synthesis_response['message']['content']

        return {
            "response": final_response,
            "tools_used": tools_used
        }

    def _build_system_prompt(self):
        """Build the system prompt for this agent"""
        prompt = f"You are a specialized AI assistant for: {self.description}\n\n"

        if self.tool_names:
            prompt += "You have access to the following tools:\n"
            for tool_name in self.tool_names:
                prompt += f"- {tool_name}\n"

            prompt += "\nTo use a tool, output a JSON block in this format:\n"
            prompt += "```tool\n"
            prompt += '{"tool": "tool_name", "params": {"param1": "value1"}}\n'
            prompt += "```\n\n"
            prompt += "You can call multiple tools by outputting multiple tool blocks.\n"
            prompt += "After using tools, explain the results to the user in natural language.\n\n"

        prompt += "Be helpful, concise, and accurate in your responses."

        return prompt

    def _extract_tool_calls(self, text):
        """Extract tool calls from the response"""
        tool_calls = []

        # Look for ```tool JSON blocks
        pattern = r'```tool\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            try:
                tool_data = json.loads(match.strip())
                if "tool" in tool_data:
                    tool_calls.append(tool_data)
            except json.JSONDecodeError:
                continue

        return tool_calls

    def _execute_tool(self, tool_call):
        """Execute a tool call"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("params", {})

        if not self.tool_registry.has_tool(tool_name):
            return {"success": False, "error": f"Tool {tool_name} not found"}

        if tool_name not in self.tool_names:
            return {"success": False, "error": f"Tool {tool_name} not available to this agent"}

        tool_func = self.tool_registry.get_tool(tool_name)

        try:
            result = tool_func(**params)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_synthesis_prompt(self, original_prompt, tool_results):
        """Build a prompt to synthesize tool results into a response"""
        prompt = f"Based on the tool results below, provide a natural language response to the user's request.\n\n"
        prompt += f"User request: {original_prompt}\n\n"
        prompt += "Tool results:\n"

        for i, result in enumerate(tool_results, 1):
            prompt += f"\nTool {i}: {json.dumps(result, indent=2)}\n"

        prompt += "\nProvide a clear, helpful response based on these results:"

        return prompt


class RouterAgent:
    """Special agent that routes queries to appropriate specialized agents"""

    def __init__(self, config, agent_names):
        self.model = config.get("model", "gemma2:2b")
        self.temperature = config.get("temperature", 0.3)
        self.agent_names = agent_names
        self.agent_descriptions = {}

    def set_agent_descriptions(self, descriptions):
        """Set descriptions for routing"""
        self.agent_descriptions = descriptions

    def route(self, query, conversation_history=None):
        """Determine which agent should handle the query"""
        # Build routing prompt
        system_prompt = "You are a routing assistant. Your job is to determine which specialized agent should handle a user's request.\n\n"
        system_prompt += "Available agents:\n"

        for agent_name, description in self.agent_descriptions.items():
            system_prompt += f"- {agent_name}: {description}\n"

        system_prompt += "\nAnalyze the user's request and respond with ONLY the agent name that should handle it.\n"
        system_prompt += "Respond with just the agent name, nothing else.\n"
        system_prompt += "If no specialized agent fits, respond with 'general'."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Which agent should handle this request?\n\nRequest: {query}"}
        ]

        try:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={"temperature": self.temperature}
            )

            selected_agent = response['message']['content'].strip().lower()

            # Clean up response (remove quotes, periods, etc.)
            selected_agent = selected_agent.replace('"', '').replace("'", "").replace(".", "")

            # Validate agent exists
            if selected_agent in self.agent_names:
                return selected_agent
            else:
                # Default to general if unclear
                return "general"

        except Exception as e:
            print(f"Routing error: {e}")
            return "general"


class AgentManager:
    """Manages all agents and routing"""

    def __init__(self, config, tool_registry):
        self.config = config
        self.tool_registry = tool_registry
        self.agents = {}
        self.router = None

        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all agents from config"""
        agent_configs = self.config.get("agents", {})

        # Create specialized agents
        for agent_name, agent_config in agent_configs.items():
            self.agents[agent_name] = Agent(agent_name, agent_config, self.tool_registry)

        # Create router
        router_config = self.config.get("router", {})
        self.router = RouterAgent(router_config, list(self.agents.keys()))

        # Set agent descriptions for router
        descriptions = {
            name: agent.description
            for name, agent in self.agents.items()
        }
        self.router.set_agent_descriptions(descriptions)

    def process_query(self, query, conversation_history=None):
        """Process a query through the agent system"""
        # Route to appropriate agent
        selected_agent_name = self.router.route(query, conversation_history)

        # Execute with selected agent
        return self.execute_with_agent(selected_agent_name, query, conversation_history)

    def execute_with_agent(self, agent_name, query, conversation_history=None):
        """Execute query with a specific agent"""
        if agent_name not in self.agents:
            return {
                "response": f"Error: Agent '{agent_name}' not found",
                "agent_used": "error",
                "tools_used": []
            }

        agent = self.agents[agent_name]
        result = agent.execute(query, conversation_history)

        return {
            "response": result["response"],
            "agent_used": agent_name,
            "tools_used": result["tools_used"]
        }

    def get_agent_list(self):
        """Get list of available agents with descriptions"""
        return {
            name: {
                "description": agent.description,
                "model": agent.model,
                "tools": agent.tool_names
            }
            for name, agent in self.agents.items()
        }
