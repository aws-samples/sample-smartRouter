"""
Example 1: Basic Smart Routing
Demonstrates the core SmartRouter functionality with automatic model tier selection.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import smartRouter modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_router import SmartRouter


async def main():
    """Basic routing example."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: BASIC SMART ROUTING")
    print("=" * 80)
    
    # Initialize router
    router = SmartRouter()
    
    # Example queries with different complexities
    examples = [
        "What is Python?",
        "Write a Python function for binary search",
        "Design a microservices architecture for handling 1M concurrent users",
        "Summarize this research paper",
        "Create a marketing campaign for AI products",
        "Analyze customer data for trends",
    ]
    
    print("\n📊 Smart Routing Decisions:")
    print("-" * 80)
    
    for query in examples:
        # Route the request
        result = await router.route_request({
            "user_input": query,
            "user_id": "user123",
            "conversation_history": []
        })
        
        print(f"\nQuery: {query[:50]}...")
        print(f"  ├─ Tier Selected: {result.tier}")
        print(f"  ├─ Model: {result.model}")
        print(f"  ├─ Classification: {result.classification['category']}")
        print(f"  ├─ Complexity Score: {result.complexity_score:.2f}")
        print(f"  ├─ Estimated Cost: ${result.estimated_cost:.6f}")
        print(f"  └─ Latency: {result.latency_ms:.1f}ms")
    
    # Print statistics
    print("\n" + "=" * 80)
    print("ROUTER STATISTICS")
    print("=" * 80)
    stats = router.get_stats()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Cache Hit Rate: {stats['cache_hit_rate']}")
    print(f"Cache Stats: {stats['cache_stats']}")


if __name__ == "__main__":
    asyncio.run(main())
