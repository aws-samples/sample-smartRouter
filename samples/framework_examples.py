"""
Framework Integration Examples
Shows how to integrate SmartRouter with various agent frameworks and patterns.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from smart_router import SmartRouter, RoutingResult


# ============================================================================
# EXAMPLE 1: LANGCHAIN-STYLE AGENT
# ============================================================================

class Tool:
    """Base tool interface similar to LangChain."""

    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    async def execute(self, *args, **kwargs) -> str:
        """Execute the tool."""
        return await self.func(*args, **kwargs)


class LangChainStyleAgent:
    """
    Agent integrated with SmartRouter following LangChain patterns.
    Demonstrates how to integrate routing with agent frameworks.
    """

    def __init__(self, tools: List[Tool]):
        self.router = SmartRouter()
        self.tools = {tool.name: tool for tool in tools}
        self.memory = []

    async def think(self, user_input: str) -> Dict[str, Any]:
        """
        Think step: Use SmartRouter to understand complexity and select model.
        """
        routing_result = await self.router.route_request(
            {
                "user_input": user_input,
                "user_id": "agent_user",
                "conversation_history": self.memory,
            }
        )

        return {
            "user_input": user_input,
            "tier": routing_result.tier,
            "model": routing_result.model,
            "complexity": routing_result.complexity_score,
            "classification": routing_result.classification,
        }

    async def decide_tool(self, thought: Dict[str, Any]) -> Optional[str]:
        """
        Decide which tool to use based on classification.
        SmartRouter helps by providing classification and complexity.
        """
        classification_category = thought["classification"].get("category", "balanced")

        tool_mapping = {
            "code_generation": "code_tool",
            "data_analysis": "data_tool",
            "research": "web_search_tool",
            "creative_writing": "writer_tool",
            "simple_query": "qa_tool",
        }

        selected_tool = tool_mapping.get(classification_category)

        # Validate tool exists
        if selected_tool and selected_tool in self.tools:
            return selected_tool

        # Fallback to first available tool
        return next(iter(self.tools.keys())) if self.tools else None

    async def act(self, tool_name: str, tool_input: Dict) -> str:
        """
        Act: Execute selected tool.
        """
        if tool_name not in self.tools:
            return f"Tool {tool_name} not found"

        tool = self.tools[tool_name]
        result = await tool.execute(**tool_input)
        return result

    async def observe(self, action_result: str, thought: Dict) -> None:
        """
        Observe: Add to memory for context.
        """
        self.memory.append(
            {
                "role": "assistant",
                "content": action_result,
                "tier_used": thought["tier"],
                "model": thought["model"],
            }
        )

    async def run(self, user_input: str) -> Dict[str, Any]:
        """
        Full agent loop: Think → Decide → Act → Observe
        """
        print(f"\n🤖 Agent Processing: {user_input}")

        # Think
        thought = await self.think(user_input)
        print(f"   Thinking: tier={thought['tier']}, complexity={thought['complexity']:.2f}")

        # Decide
        tool_name = await self.decide_tool(thought)
        print(f"   Decided: {tool_name}")

        # Act
        result = await self.act(tool_name, {"input": user_input})
        print(f"   Acted: {result[:50]}...")

        # Observe
        await self.observe(result, thought)

        return {
            "user_input": user_input,
            "tool_used": tool_name,
            "result": result,
            "routing_info": thought,
        }


# ============================================================================
# EXAMPLE 2: REACT-STYLE AGENT
# ============================================================================

class ReActAgent:
    """
    Agent following ReAct (Reasoning + Acting) pattern with SmartRouter.
    Combines reasoning with smart model selection.
    """

    def __init__(self):
        self.router = SmartRouter()
        self.reasoning_history = []

    async def reason(self, user_input: str) -> Dict[str, Any]:
        """
        Reasoning step: Analyze task and decide approach.
        SmartRouter provides insights into task complexity.
        """
        routing = await self.router.route_request(
            {"user_input": user_input, "user_id": "react_agent"}
        )

        reasoning = {
            "input": user_input,
            "complexity": routing.complexity_score,
            "classification": routing.classification["category"],
            "tier": routing.tier,
            "approach": self._determine_approach(routing.complexity_score),
            "steps": self._plan_steps(routing.complexity_score),
        }

        self.reasoning_history.append(reasoning)
        return reasoning

    def _determine_approach(self, complexity: float) -> str:
        """Determine solution approach based on complexity."""
        if complexity < 0.3:
            return "direct_solution"
        elif complexity < 0.7:
            return "step_by_step"
        else:
            return "deep_analysis"

    def _plan_steps(self, complexity: float) -> List[str]:
        """Plan execution steps based on complexity."""
        if complexity < 0.3:
            return ["search", "return"]
        elif complexity < 0.7:
            return ["analyze", "reason", "implement", "verify"]
        else:
            return ["decompose", "research", "design", "implement", "test", "verify"]

    async def act(self, reasoning: Dict) -> str:
        """
        Acting step: Execute plan from reasoning.
        """
        approach = reasoning["approach"]

        if approach == "direct_solution":
            return await self._simple_action(reasoning)
        elif approach == "step_by_step":
            return await self._step_by_step_action(reasoning)
        else:
            return await self._deep_analysis_action(reasoning)

    async def _simple_action(self, reasoning: Dict) -> str:
        """Simple direct action."""
        await asyncio.sleep(0.1)
        return f"Quick answer for: {reasoning['input'][:40]}"

    async def _step_by_step_action(self, reasoning: Dict) -> str:
        """Step-by-step execution."""
        steps = reasoning["steps"]
        results = []

        for step in steps:
            await asyncio.sleep(0.05)
            results.append(f"Completed: {step}")

        return "\n".join(results)

    async def _deep_analysis_action(self, reasoning: Dict) -> str:
        """Deep analysis with multiple steps."""
        steps = reasoning["steps"]
        analysis = []

        for step in steps:
            await asyncio.sleep(0.1)
            analysis.append(f"✓ {step.upper()}: Thoroughly analyzed")

        return "\n".join(analysis)

    async def run(self, user_input: str) -> Dict[str, Any]:
        """Full ReAct loop."""
        print(f"\n🎯 ReAct Agent: {user_input}")

        # Reason
        reasoning = await self.reason(user_input)
        print(f"   Reasoning: {reasoning['approach']} (complexity: {reasoning['complexity']:.2f})")
        print(f"   Plan: {' → '.join(reasoning['steps'])}")

        # Act
        result = await self.act(reasoning)
        print(f"   Result: {result[:50]}...")

        return {
            "input": user_input,
            "reasoning": reasoning,
            "result": result,
            "tier": reasoning["tier"],
        }


# ============================================================================
# EXAMPLE 3: HIERARCHICAL AGENT SYSTEM
# ============================================================================

class SpecialistAgent:
    """Individual specialist agent with smart routing."""

    def __init__(self, specialty: str, router: Optional[SmartRouter] = None):
        self.specialty = specialty
        self.router = router or SmartRouter()
        self.expertise = self._get_expertise()

    def _get_expertise(self) -> Dict:
        """Define expertise by specialty."""
        expertise_map = {
            "coding": ["code_generation", "debug"],
            "analysis": ["data_analysis", "complex_reasoning"],
            "research": ["document_analysis", "research"],
            "writing": ["creative_writing"],
        }
        return expertise_map.get(self.specialty, [])

    async def can_handle(self, task_classification: str) -> bool:
        """Check if specialist can handle task."""
        return task_classification in self.expertise

    async def execute(self, user_input: str, routing_info: Dict) -> str:
        """Execute task."""
        tier = routing_info["tier"]
        classification = routing_info["classification"]

        print(f"      {self.specialty} specialist handling: {classification}")
        await asyncio.sleep(0.1)

        return f"[{self.specialty.upper()}] Specialized response for: {user_input[:30]}"


class HierarchicalCoordinator:
    """
    Coordinates multiple specialist agents.
    SmartRouter helps route to appropriate specialist.
    """

    def __init__(self):
        self.router = SmartRouter()
        self.specialists = {
            "coding": SpecialistAgent("coding", self.router),
            "analysis": SpecialistAgent("analysis", self.router),
            "research": SpecialistAgent("research", self.router),
            "writing": SpecialistAgent("writing", self.router),
        }

    async def route_to_specialist(self, user_input: str) -> str:
        """Route to appropriate specialist."""
        print(f"\n🏛️  Hierarchical System: {user_input}")

        # Get routing info
        routing = await self.router.route_request(
            {"user_input": user_input, "user_id": "hierarchical_system"}
        )

        classification = routing.classification["category"]
        print(f"   Classification: {classification} (tier: {routing.tier})")

        # Find appropriate specialist
        for specialty, specialist in self.specialists.items():
            if await specialist.can_handle(classification):
                print(f"   Routing to: {specialty} specialist")
                result = await specialist.execute(
                    user_input,
                    {
                        "tier": routing.tier,
                        "classification": classification,
                    },
                )
                return result

        # Fallback
        print(f"   Using general specialist")
        return f"General response: {user_input[:40]}"


# ============================================================================
# EXAMPLE 4: ADAPTIVE AGENT
# ============================================================================

class AdaptiveAgent:
    """
    Agent that adapts its behavior based on routing decisions.
    Learns from tier assignments over time.
    """

    def __init__(self):
        self.router = SmartRouter()
        self.tier_history = {}
        self.pattern_confidence = {}

    async def execute(self, user_input: str) -> Dict[str, Any]:
        """Execute with adaptive behavior."""
        print(f"\n🧬 Adaptive Agent: {user_input}")

        # Get routing
        routing = await self.router.route_request(
            {"user_input": user_input, "user_id": "adaptive_agent"}
        )

        tier = routing.tier
        classification = routing.classification["category"]

        # Track pattern
        pattern_key = classification
        self.tier_history[pattern_key] = self.tier_history.get(pattern_key, []) + [tier]

        # Calculate confidence
        tiers = self.tier_history[pattern_key]
        most_common_tier = max(set(tiers), key=tiers.count)
        confidence = tiers.count(most_common_tier) / len(tiers)
        self.pattern_confidence[pattern_key] = confidence

        # Adapt behavior
        if confidence > 0.8:
            behavior = "confident"
            speed = "fast"
        elif confidence > 0.5:
            behavior = "learning"
            speed = "moderate"
        else:
            behavior = "exploring"
            speed = "thorough"

        print(f"   Tier: {tier}")
        print(f"   Pattern confidence: {confidence:.2f}")
        print(f"   Behavior: {behavior}, Speed: {speed}")

        await asyncio.sleep(0.1)

        return {
            "input": user_input,
            "tier": tier,
            "classification": classification,
            "confidence": confidence,
            "behavior": behavior,
            "speed": speed,
        }


# ============================================================================
# DEMO
# ============================================================================

async def demo_langchain_style():
    """Demonstrate LangChain-style integration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: LANGCHAIN-STYLE AGENT WITH SMART ROUTING")
    print("=" * 80)

    # Create tools
    async def code_tool(**kwargs):
        await asyncio.sleep(0.1)
        return "Generated Python code"

    async def data_tool(**kwargs):
        await asyncio.sleep(0.1)
        return "Data analysis results"

    async def web_search_tool(**kwargs):
        await asyncio.sleep(0.1)
        return "Research findings"

    async def writer_tool(**kwargs):
        await asyncio.sleep(0.1)
        return "Written content"

    async def qa_tool(**kwargs):
        await asyncio.sleep(0.05)
        return "Quick answer"

    tools = [
        Tool("code_tool", "Generate code", code_tool),
        Tool("data_tool", "Analyze data", data_tool),
        Tool("web_search_tool", "Research", web_search_tool),
        Tool("writer_tool", "Write content", writer_tool),
        Tool("qa_tool", "Quick Q&A", qa_tool),
    ]

    agent = LangChainStyleAgent(tools)

    tasks = [
        "Write a Python function for sorting",
        "What is machine learning?",
        "Analyze this dataset",
    ]

    for task in tasks:
        result = await agent.run(task)
        print(f"   ✅ Completed with {result['routing_info']['tier']} tier\n")


async def demo_react_style():
    """Demonstrate ReAct-style integration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: REACT-STYLE AGENT WITH SMART ROUTING")
    print("=" * 80)

    agent = ReActAgent()

    tasks = [
        "What is Python?",
        "Design a system for handling 1M users",
    ]

    for task in tasks:
        result = await agent.run(task)


async def demo_hierarchical():
    """Demonstrate hierarchical agent system."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: HIERARCHICAL AGENT SYSTEM WITH SMART ROUTING")
    print("=" * 80)

    coordinator = HierarchicalCoordinator()

    tasks = [
        "Write a Python function",
        "Analyze customer data",
        "Research renewable energy",
    ]

    for task in tasks:
        result = await coordinator.route_to_specialist(task)


async def demo_adaptive():
    """Demonstrate adaptive agent."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: ADAPTIVE AGENT WITH SMART ROUTING")
    print("=" * 80)

    agent = AdaptiveAgent()

    tasks = [
        "What is Python?",
        "Define machine learning",
        "Explain AI concepts",
        "Write a sorting function",
        "Design architecture",
        "What is data science?",
    ]

    for task in tasks:
        await agent.execute(task)


async def main():
    """Run all framework examples."""
    await demo_langchain_style()
    await demo_react_style()
    await demo_hierarchical()
    await demo_adaptive()

    print("\n" + "=" * 80)
    print("All framework examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
