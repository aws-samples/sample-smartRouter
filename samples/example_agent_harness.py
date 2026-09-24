"""
Example: Smart Router Advanced Usage
Demonstrates advanced routing scenarios and performance analysis.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import smartRouter modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from smart_router import SmartRouter


async def example_advanced_routing():
    """Advanced routing with performance metrics."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: ADVANCED ROUTING SCENARIOS")
    print("=" * 80)
    
    router = SmartRouter()
    
    # Complex scenario with various task types
    scenarios = [
        ("What is Python?", "simple_query"),
        ("Write a Python function for binary search", "code_generation"),
        ("Design a microservices architecture", "complex_reasoning"),
        ("Summarize this research", "document_analysis"),
        ("Write a marketing post about AI", "creative_writing"),
        ("Analyze customer data trends", "data_analysis"),
    ]
    
    print("\n🎯 Advanced Routing Decisions:")
    print("-" * 80)
    
    tier_distribution = {}
    total_cost = 0.0
    
    for task, expected_category in scenarios:
        result = await router.route_request({
            "user_input": task,
            "user_id": "advanced_user",
            "conversation_history": []
        })
        
        print(f"\nTask: {task[:50]}...")
        print(f"  Expected: {expected_category}")
        print(f"  Actual:   {result.classification['category']}")
        print(f"  ├─ Tier: {result.tier}")
        print(f"  ├─ Model: {result.model}")
        print(f"  ├─ Complexity: {result.complexity_score:.2f}")
        print(f"  └─ Cost: ${result.estimated_cost:.6f}")
        
        tier_distribution[result.tier] = tier_distribution.get(result.tier, 0) + 1
        total_cost += result.estimated_cost
    
    # Print distribution summary
    print("\n" + "=" * 80)
    print("DISTRIBUTION SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Cost: ${total_cost:.6f}")
    print("\nTier Distribution:")
    for tier, count in sorted(tier_distribution.items()):
        pct = (count / len(scenarios)) * 100
        print(f"  {tier.upper()}: {count} requests ({pct:.0f}%)")
    
    # Cache statistics
    stats = router.get_stats()
    print("\nRouter Statistics:")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate']}")


async def example_cost_comparison():
    """Demonstrate cost optimization."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2B: COST OPTIMIZATION")
    print("=" * 80)
    
    router = SmartRouter()
    
    # Test requests with different complexities
    test_requests = [
        {
            "user_input": "What is AI?",
            "user_id": "user1",
            "conversation_history": []
        },
        {
            "user_input": "Design a distributed system for processing 1B events/day",
            "user_id": "user2",
            "conversation_history": []
        },
    ]
    
    print("\n💰 Cost Comparison:")
    print("-" * 80)
    
    for i, req in enumerate(test_requests, 1):
        result = await router.route_request(req)
        
        print(f"\nRequest {i}: {req['user_input'][:40]}...")
        print(f"  Selected Tier: {result.tier.upper()}")
        
        # Show cost for all tiers
        costs = router.cost_estimator.compare_tier_costs(req)
        selected_cost = costs[result.tier]
        
        print(f"  Cost Comparison:")
        for tier, cost in sorted(costs.items(), key=lambda x: x[1]):
            marker = "✓ SELECTED" if tier == result.tier else ""
            savings = ((costs['powerful'] - cost) / costs['powerful'] * 100) if costs['powerful'] > 0 else 0
            print(f"    {tier.upper():12} ${cost:.6f} ({savings:.0f}% savings) {marker}")


async def main():
    """Run all advanced examples."""
    await example_advanced_routing()
    await example_cost_comparison()


if __name__ == "__main__":
    asyncio.run(main())
