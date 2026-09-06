"""
SmartRouter Decorator Usage Examples
Demonstrates how to use the @SmartRouter decorator for automatic model selection
on LLM-calling functions.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_router_decorator import (
    SmartRouter,
    SmartRouterVerbose,
    SmartRouterNoCaching,
    SmartRouterWithMetadata,
    SmartRouterDecorator,
)


# ============================================================================
# EXAMPLE 1: Basic Decorator Usage
# ============================================================================

@SmartRouter
async def translate_text(user_input: str, user_id: str = "user1", **kwargs) -> str:
    """
    Simple translation function with automatic model selection.
    
    The decorator automatically:
    - Analyzes the input task
    - Determines required model tier
    - Selects appropriate model
    - Handles caching
    """
    # Access routing info if needed
    routing_info = kwargs.get("_routing_info", {})
    model = kwargs.get("_selected_model", "unknown")
    
    # Simulate LLM call
    await asyncio.sleep(0.1)
    return f"[{model}] Translated: {user_input}"


# ============================================================================
# EXAMPLE 2: Verbose Decorator for Debugging
# ============================================================================

@SmartRouterVerbose
async def generate_code(user_input: str, user_id: str = "user1", **kwargs) -> str:
    """
    Code generation with verbose routing output.
    
    Shows routing decisions in console for debugging and monitoring.
    """
    await asyncio.sleep(0.1)
    return f"Generated code for: {user_input}"


# ============================================================================
# EXAMPLE 3: Custom Metadata Callback
# ============================================================================

def cost_logger(metadata: dict):
    """Custom callback to log routing decisions."""
    print(f"\n💰 Cost Analysis:")
    print(f"   Tier: {metadata['tier']}")
    print(f"   Cost: ${metadata['cost']:.6f}")
    print(f"   Complexity: {metadata['complexity']:.2f}")
    print(f"   Source: {metadata['source']}")


# Create decorator with callback
router_with_logging = SmartRouterDecorator(
    metadata_callback=cost_logger,
    verbose=True
)


@router_with_logging
async def analyze_document(user_input: str, user_id: str = "user1", **kwargs) -> str:
    """
    Document analysis with cost logging.
    
    The metadata callback is invoked after each routing decision.
    """
    await asyncio.sleep(0.1)
    return f"Analyzed: {user_input}"


# ============================================================================
# EXAMPLE 4: Accessing Routing Info Inside Function
# ============================================================================

@SmartRouter
async def process_request(
    user_input: str,
    user_id: str = "user1",
    _routing_info: Optional[dict] = None,
    _selected_tier: Optional[str] = None,
    _selected_model: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Access routing decisions inside the function.
    
    The decorator injects:
    - _routing_info: Full routing metadata dict
    - _selected_tier: Model tier (fast/balanced/powerful)
    - _selected_model: Selected model name
    """
    result = {
        "input": user_input,
        "user_id": user_id,
        "tier": _selected_tier,
        "model": _selected_model,
        "routing_info": _routing_info,
    }
    
    # Use tier-specific logic if needed
    if _selected_tier == "fast":
        await asyncio.sleep(0.05)  # Quick response
    elif _selected_tier == "balanced":
        await asyncio.sleep(0.1)
    else:  # powerful
        await asyncio.sleep(0.2)  # More thinking time
    
    return result


# ============================================================================
# EXAMPLE 5: Caching Control
# ============================================================================

@SmartRouterNoCaching
async def generate_random_response(user_input: str, user_id: str = "user1", **kwargs) -> str:
    """
    Decorator with caching disabled.
    
    Useful for:
    - Non-deterministic responses
    - Real-time data that shouldn't be cached
    - Testing/debugging
    """
    await asyncio.sleep(0.1)
    return f"Random response to: {user_input}"


# ============================================================================
# EXAMPLE 6: Advanced - Metadata Tracking
# ============================================================================

# Create decorator with full metadata tracking
tracker = SmartRouterWithMetadata(verbose=False)


@tracker
async def batch_process(user_input: str, user_id: str = "user1", **kwargs) -> str:
    """Process with full execution tracking."""
    await asyncio.sleep(0.1)
    return f"Processed: {user_input}"


# ============================================================================
# EXAMPLE 7: Custom User ID Key
# ============================================================================

custom_router = SmartRouterDecorator(user_id_key="customer_id", verbose=True)


@custom_router
async def call_with_custom_key(
    user_input: str,
    customer_id: str = "cust123",
    **kwargs
) -> str:
    """
    Use custom parameter name for user ID.
    
    The decorator can extract user ID from any parameter name via user_id_key.
    """
    await asyncio.sleep(0.1)
    return f"Processed for customer {customer_id}: {user_input}"


# ============================================================================
# EXAMPLE 8: Multi-User Scenario
# ============================================================================

@SmartRouterVerbose
async def chat_endpoint(user_input: str, user_id: str, **kwargs) -> str:
    """
    Handle multiple users with automatic tier selection per request.
    
    The router makes independent decisions for each user's request,
    taking into account their specific input complexity.
    """
    await asyncio.sleep(0.1)
    return f"[User {user_id}] Response: {user_input}"


# ============================================================================
# EXAMPLE 9: Conversation Context
# ============================================================================

@SmartRouter
async def conversational_llm(
    user_input: str,
    user_id: str = "user1",
    conversation_history: list = None,
    **kwargs
) -> str:
    """
    LLM call with conversation history.
    
    The router considers:
    - Current input complexity
    - Conversation history length
    - Context tokens
    
    Complexity score increases with more context.
    """
    if conversation_history is None:
        conversation_history = []
    
    await asyncio.sleep(0.1)
    return f"Conversation response to: {user_input}"


# ============================================================================
# EXAMPLE 10: Getting Stats and History
# ============================================================================

async def demo_stats_and_history():
    """Demonstrate accessing stats and history."""
    
    # Define a tracked function
    @tracker
    async def tracked_call(user_input: str, user_id: str = "user1", **kwargs) -> str:
        await asyncio.sleep(0.05)
        return f"Response: {user_input}"
    
    # Make multiple calls
    for i in range(3):
        await tracked_call(f"Task {i+1}", user_id=f"user{i+1}")
    
    # Access history
    history = tracked_call.get_history()
    print(f"\nExecution History ({len(history)} calls):")
    for record in history:
        print(f"  - User: {record['user_id']}, Tier: {record['tier']}, Cost: ${record['cost']:.6f}")
    
    # Print summary
    tracked_call.print_summary()


# ============================================================================
# MAIN: Run All Examples
# ============================================================================

async def run_examples():
    """Run all decorator examples."""
    
    print("\n" + "="*80)
    print("SMARTROUTER DECORATOR USAGE EXAMPLES")
    print("="*80)
    
    # Example 1: Basic
    print("\n[Example 1] Basic Decorator Usage")
    print("-"*80)
    result = await translate_text("Hello, world!", user_id="translator_user")
    print(f"Result: {result}")
    print(f"Metadata: {translate_text.get_last_metadata()}")
    
    # Example 2: Verbose
    print("\n[Example 2] Verbose Decorator for Debugging")
    print("-"*80)
    result = await generate_code("Write a Python function to sort an array", user_id="developer")
    print(f"Result: {result}")
    
    # Example 3: Custom callback
    print("\n[Example 3] Custom Metadata Callback")
    print("-"*80)
    result = await analyze_document("Analyze this contract...", user_id="analyst")
    print(f"Result: {result}")
    
    # Example 4: Access routing info inside
    print("\n[Example 4] Accessing Routing Info Inside Function")
    print("-"*80)
    result = await process_request("Complex analysis task", user_id="power_user")
    print(f"Result:")
    for key, value in result.items():
        if key != "routing_info":
            print(f"  {key}: {value}")
    
    # Example 5: No caching
    print("\n[Example 5] Caching Control (No Caching)")
    print("-"*80)
    result1 = await generate_random_response("Same input", user_id="user1")
    result2 = await generate_random_response("Same input", user_id="user1")
    print(f"Call 1: {result1}")
    print(f"Call 2: {result2}")
    print("(Note: Different responses even though input is same - no caching)")
    
    # Example 6: Metadata tracking
    print("\n[Example 6] Advanced - Metadata Tracking")
    print("-"*80)
    tasks = [
        "What is machine learning?",
        "Design a distributed system",
        "Explain quantum computing"
    ]
    for i, task in enumerate(tasks, 1):
        print(f"\nTask {i}: {task}")
        result = await batch_process(task, user_id=f"user_{i}")
        print(f"  Result: {result}")
    
    # Print summary from tracking
    tracker.print_summary()
    
    # Example 7: Custom user ID key
    print("\n[Example 7] Custom User ID Key")
    print("-"*80)
    result = await call_with_custom_key("Process this", customer_id="CUST_12345")
    print(f"Result: {result}")
    
    # Example 8: Multi-user
    print("\n[Example 8] Multi-User Scenario")
    print("-"*80)
    users = ["alice", "bob", "charlie"]
    for user in users:
        result = await chat_endpoint("Hello!", user_id=user)
        print(f"  {result}")
    
    # Example 9: Conversation context
    print("\n[Example 9] Conversation Context")
    print("-"*80)
    history = [
        {"role": "user", "content": "Hi, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thanks for asking!"},
    ]
    result = await conversational_llm(
        "Tell me about AI",
        user_id="user1",
        conversation_history=history
    )
    print(f"Result: {result}")
    print(f"Context: {len(history)} previous messages")
    
    # Example 10: Stats and history
    print("\n[Example 10] Getting Stats and History")
    print("-"*80)
    await demo_stats_and_history()
    
    # Summary
    print("\n" + "="*80)
    print("✅ All examples completed successfully!")
    print("="*80)
    print("""
Key Takeaways:
1. @SmartRouter - Basic decorator with caching
2. @SmartRouterVerbose - Shows routing decisions
3. Custom decorators - Add callbacks and tracking
4. Decorator injects - _routing_info, _selected_tier, _selected_model
5. Supports async & sync - Works with both function types
6. Conversation history - Complexity increases with context
7. Stats tracking - Get execution history and summaries
8. Flexible routing - Works with any parameter names via user_id_key
    """)


if __name__ == "__main__":
    asyncio.run(run_examples())
