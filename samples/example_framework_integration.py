"""
Example 3: Framework Integration Patterns
Demonstrates how to integrate SmartRouter with different agent frameworks.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import smartRouter modules
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))  # Also add samples dir for local imports

from framework_examples import (
    LangChainStyleAgent,
    ReActAgent,
    HierarchicalCoordinator,
    AdaptiveAgent,
    Tool
)


async def example_langchain_style():
    """LangChain-style agent integration."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3A: LANGCHAIN-STYLE AGENT")
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
    
    print("\n🤖 LangChain-Style Agent Execution:")
    print("-" * 80)
    
    for task in tasks:
        result = await agent.run(task)
        print(f"\nTask: {task}")
        print(f"  Tool: {result['routing_info']['tier']} tier")
        print(f"  Model: {result['routing_info']['model']}")


async def example_react_agent():
    """ReAct pattern agent."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3B: REACT AGENT (Reasoning + Acting)")
    print("=" * 80)
    
    agent = ReActAgent()
    
    tasks = [
        "What is Python?",
        "Design a system for handling 1M users",
    ]
    
    print("\n🎯 ReAct Agent Execution:")
    print("-" * 80)
    
    for task in tasks:
        result = await agent.run(task)
        print(f"\nTask: {task}")
        print(f"  Reasoning: {result['reasoning']['approach']}")
        print(f"  Tier: {result['reasoning']['tier']}")
        print(f"  Complexity: {result['reasoning']['complexity']:.2f}")


async def example_hierarchical():
    """Hierarchical agent system."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3C: HIERARCHICAL AGENT SYSTEM")
    print("=" * 80)
    
    coordinator = HierarchicalCoordinator()
    
    tasks = [
        "Write a Python function",
        "Analyze customer data",
        "Research renewable energy",
    ]
    
    print("\n🏛️  Hierarchical System Execution:")
    print("-" * 80)
    
    for task in tasks:
        result = await coordinator.route_to_specialist(task)
        print(f"\nTask: {task}")
        print(f"  Result: {result[:50]}...")


async def example_adaptive_agent():
    """Adaptive agent with learning."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3D: ADAPTIVE AGENT (Learning from Patterns)")
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
    
    print("\n🧬 Adaptive Agent Execution:")
    print("-" * 80)
    
    for task in tasks:
        result = await agent.execute(task)
        print(f"\nTask: {task}")
        print(f"  Tier: {result['tier']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Behavior: {result['behavior']}")


async def main():
    """Run all framework examples."""
    await example_langchain_style()
    await example_react_agent()
    await example_hierarchical()
    await example_adaptive_agent()


if __name__ == "__main__":
    asyncio.run(main())
