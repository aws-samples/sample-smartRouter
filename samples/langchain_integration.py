"""
Real LangChain Integration with SmartRouter
Demonstrates actual integration with the LangChain library for intelligent model selection.

This module requires langchain to be installed:
    pip install langchain langchain-openai
"""

import asyncio
import sys
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_router import SmartRouter

# Try to import real LangChain components
try:
    from langchain_core.tools import Tool
    from langchain_aws import ChatBedrock
    from langgraph.prebuilt import create_react_agent
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    LANGCHAIN_AVAILABLE = False


if LANGCHAIN_AVAILABLE:
    
    class SmartRoutedLangChainAgent:
        """
        Real LangChain Agent integrated with SmartRouter for intelligent model selection.
        
        SmartRouter handles:
        - Task classification (complexity analysis)
        - Automatic model tier selection (fast/balanced/powerful)
        - Cost estimation and optimization
        - Performance metrics
        
        LangChain handles:
        - Agent orchestration
        - Tool management
        - Conversation memory
        - Reasoning and acting
        """

        def __init__(self, aws_region: Optional[str] = None):
            """
            Initialize the SmartRouter-enabled LangChain agent with AWS Bedrock.
            
            Args:
                aws_region: AWS region for Bedrock (uses default if not provided)
            """
            self.router = SmartRouter()
            self.aws_region = aws_region or "us-east-1"
            self.conversation_history = []
            self.tier_usage = {}
            
            # Initialize tools for LangChain
            self.tools = self._setup_tools()

        def _setup_tools(self) -> List[Tool]:
            """
            Set up tools that LangChain agent can use.
            These are real LangChain Tool objects.
            """
            tools = [
                Tool(
                    name="Calculator",
                    func=self._calculator,
                    description="Useful for math calculations. Input should be a math expression."
                ),
                Tool(
                    name="StringTools",
                    func=self._string_tools,
                    description="Useful for string manipulation. Input should be a text operation description."
                ),
                Tool(
                    name="Information",
                    func=self._information,
                    description="Useful for general information. Input should be a question or topic."
                ),
            ]
            return tools

        def _calculator(self, expression: str) -> str:
            """
            Safe calculator tool using ast.literal_eval().
            Only evaluates numeric literals (no code execution or arithmetic).
            """
            try:
                # Use ast.literal_eval for safe evaluation
                # This only accepts literal values: numbers, strings, lists, etc.
                # Completely rejects: arithmetic expressions, function calls, imports, etc.
                result = ast.literal_eval(expression)
                
                # Ensure result is numeric
                if isinstance(result, (int, float)):
                    return f"Result: {result}"
                else:
                    return f"Error: Invalid input. Only numeric values allowed, got {type(result).__name__}"
            
            except (ValueError, SyntaxError):
                return "Error: Invalid input. Only numeric literals allowed (e.g., '42', '3.14', '-10')"
            except Exception as e:
                return f"Error: {type(e).__name__}: {str(e)[:50]}"

        def _string_tools(self, operation: str) -> str:
            """String manipulation tool."""
            operations = {
                "reverse": lambda s: s[::-1],
                "uppercase": lambda s: s.upper(),
                "lowercase": lambda s: s.lower(),
                "length": lambda s: f"Length: {len(s)}",
            }
            # Simple demo
            return f"String operation: {operation}"

        def _information(self, query: str) -> str:
            """Information lookup tool."""
            return f"Information about: {query}"

        async def route_and_select_model(self, user_input: str) -> Dict[str, Any]:
            """
            Use SmartRouter to analyze task and select appropriate model.
            
            Returns routing decision with tier, model, complexity, classification.
            """
            routing_result = await self.router.route_request({
                "user_input": user_input,
                "user_id": "langchain_agent",
                "conversation_history": self.conversation_history,
            })
            
            # Track tier usage
            tier = routing_result.tier
            self.tier_usage[tier] = self.tier_usage.get(tier, 0) + 1
            
            return {
                "tier": tier,
                "model": routing_result.model,
                "complexity_score": routing_result.complexity_score,
                "classification": routing_result.classification,
                "estimated_cost": routing_result.estimated_cost,
            }

        async def execute(self, user_input: str) -> Dict[str, Any]:
            """
            Execute task using SmartRouter-guided LangChain agent.
            
            Process:
            1. Use SmartRouter to analyze task and select model
            2. Initialize LangChain agent with selected model
            3. Run LangChain agent with tools
            4. Track metrics and return results
            """
            print(f"\n{'='*70}")
            print(f"SmartRouter + LangChain Agent")
            print(f"{'='*70}")
            print(f"\n📝 Input: {user_input}")
            
            # Step 1: Use SmartRouter for routing decision
            print(f"\n🧠 Step 1: SmartRouter Analysis")
            print(f"{'-'*70}")
            routing_decision = await self.route_and_select_model(user_input)
            
            print(f"  Classification: {routing_decision['classification']['category']}")
            print(f"  Complexity: {routing_decision['complexity_score']:.2f}")
            print(f"  Selected Tier: {routing_decision['tier'].upper()}")
            print(f"  Model: {routing_decision['model']}")
            print(f"  Estimated Cost: ${routing_decision['estimated_cost']:.6f}")
            
            # Step 2: Initialize LangChain agent with selected model
            print(f"\n🤖 Step 2: Initialize LangChain Agent")
            print(f"{'-'*70}")
            
            try:
                # Create LLM based on selected tier using AWS Bedrock
                # Bedrock model IDs:
                # - Claude 3 Sonnet: anthropic.claude-3-sonnet-20240229-v1:0
                # - Claude 3 Haiku: anthropic.claude-3-haiku-20240307-v1:0
                # - Claude 3 Opus: anthropic.claude-3-opus-20240229-v1:0
                
                bedrock_model_map = {
                    "fast": "anthropic.claude-3-haiku-20240307-v1:0",
                    "balanced": "anthropic.claude-3-sonnet-20240229-v1:0",
                    "powerful": "anthropic.claude-3-opus-20240229-v1:0"
                }
                
                model_id = bedrock_model_map.get(
                    routing_decision['tier'],
                    "anthropic.claude-3-sonnet-20240229-v1:0"
                )
                
                llm = ChatBedrock(
                    model_id=model_id,
                    region_name=self.aws_region,
                    temperature=0.7 if routing_decision['tier'] == 'fast' else 0.9
                )
                print(f"  ✓ LangChain LLM initialized for tier: {routing_decision['tier']}")
                print(f"  ✓ Bedrock model: {model_id}")
                print(f"  ✓ AWS region: {self.aws_region}")
                
                # Step 3: Initialize agent
                print(f"\n⚙️  Step 3: Initialize LangChain Agent with Tools")
                print(f"{'-'*70}")
                print(f"  Available tools: {[tool.name for tool in self.tools]}")
                
                # Use modern LangChain API with ReAct agent
                # create_react_agent returns a runnable that can be invoked directly
                agent = create_react_agent(
                    llm,
                    self.tools,
                )
                print(f"  ✓ Agent initialized with {len(self.tools)} tools")
                
                # Step 4: Run agent
                print(f"\n🎯 Step 4: Execute LangChain Agent")
                print(f"{'-'*70}")
                result = agent.invoke({"input": user_input})
                
                # Handle result (which is now a dict with 'output' key)
                agent_result = result.get("output", str(result)) if isinstance(result, dict) else str(result)
                
                print(f"\n✅ Step 5: Results")
                print(f"{'-'*70}")
                print(f"  Agent Result: {agent_result[:100]}...")
                
                # Track conversation
                self.conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "tier": routing_decision['tier'],
                    "model": routing_decision['model'],
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": agent_result,
                })
                
                return {
                    "success": True,
                    "user_input": user_input,
                    "agent_result": agent_result,
                    "routing_decision": routing_decision,
                    "tools_used": self.tools,
                }
                
            except Exception as e:
                print(f"\n❌ Error executing agent: {e}")
                print(f"\nNote: This requires:")
                print(f"  1. LangChain installed: pip install langchain langchain-aws")
                print(f"  2. AWS credentials configured: aws configure")
                print(f"  3. AWS IAM permissions for Bedrock: bedrock:InvokeModel")
                
                return {
                    "success": False,
                    "error": str(e),
                    "routing_decision": routing_decision,
                }

        def get_performance_report(self) -> Dict[str, Any]:
            """Get performance metrics."""
            total_requests = sum(self.tier_usage.values())
            return {
                "total_requests": total_requests,
                "tier_distribution": self.tier_usage,
                "conversation_length": len(self.conversation_history),
            }


async def demo_with_real_langchain():
    """
    Demonstrate real LangChain integration with SmartRouter using AWS Bedrock.
    
    This requires:
    - LangChain installed: pip install langchain langchain-aws
    - AWS credentials configured: aws configure
    - AWS IAM permissions for Bedrock: bedrock:InvokeModel
    """
    print("\n" + "="*70)
    print("REAL LANGCHAIN + SMARTROUTER INTEGRATION (AWS BEDROCK)")
    print("="*70)
    
    try:
        # Initialize agent
        agent = SmartRoutedLangChainAgent()
        
        # Example tasks
        tasks = [
            "What is 25 + 17?",
            "Reverse the string 'hello world'",
            "Tell me about artificial intelligence",
        ]
        
        for task in tasks:
            result = await agent.execute(task)
            
            if result["success"]:
                print(f"\n✅ Task completed successfully")
            else:
                print(f"\n❌ Task failed: {result.get('error')}")
        
        # Show metrics
        print(f"\n" + "="*70)
        print("PERFORMANCE REPORT")
        print("="*70)
        report = agent.get_performance_report()
        print(f"Total Requests: {report['total_requests']}")
        print(f"Tier Distribution: {report['tier_distribution']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure LangChain and AWS Bedrock are configured correctly.")
        print("\nSetup steps:")
        print("  1. pip install langchain langchain-aws")
        print("  2. aws configure (to set up AWS credentials)")
        print("  3. Ensure your IAM user/role has bedrock:InvokeModel permission")


async def demo_without_langchain():
    """
    Show SmartRouter routing analysis when LangChain is not available.
    """
    print("\n" + "="*70)
    print("SMARTROUTER ANALYSIS (Demonstration Mode)")
    print("="*70)
    print("\nLangChain is not installed.")
    print("\nTo run the full real LangChain integration with AWS Bedrock, install it with:")
    print("  pip install langchain langchain-aws")
    print("\nThen configure AWS credentials:")
    print("  aws configure")
    
    print(f"\n{'='*70}")
    print("SmartRouter Routing Analysis")
    print(f"{'='*70}")
    print("\nThis demonstrates what SmartRouter does internally:")
    print("It analyzes tasks and selects the appropriate model tier.\n")
    
    router = SmartRouter()
    
    tasks = [
        "What is 25 + 17?",
        "Reverse the string 'hello world'",
        "Design a scalable microservices architecture",
    ]
    
    for task in tasks:
        routing = await router.route_request({
            "user_input": task,
            "user_id": "demo_user",
        })
        
        print(f"\n📝 Task: {task[:50]}...")
        print(f"  ├─ Classification: {routing.classification['category']}")
        print(f"  ├─ Complexity: {routing.complexity_score:.2f}")
        print(f"  ├─ Selected Tier: {routing.tier.upper()}")
        print(f"  ├─ Model: {routing.model}")
        print(f"  └─ Cost: ${routing.estimated_cost:.6f}")
        print(f"\n  🎯 With LangChain: Agent would use {routing.model}")
        print(f"     with temperature settings for tier: {routing.tier.upper()}")


async def main():
    """Run the appropriate demo."""
    if LANGCHAIN_AVAILABLE:
        print("✅ LangChain is available - running real integration")
        await demo_with_real_langchain()
    else:
        print("⚠️  LangChain not available - running demonstration mode")
        await demo_without_langchain()


if __name__ == "__main__":
    asyncio.run(main())
