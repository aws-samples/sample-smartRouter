# SmartRouter Usage Examples

This directory contains comprehensive examples demonstrating how to use the SmartRouter system in various scenarios.

## Quick Start

All examples are fully executable and require the SmartRouter modules to be installed. Each example demonstrates different integration patterns.

### Prerequisites

```bash
# Ensure you're in the smartRouter directory
cd /path/to/smartRouter
```

## Examples Overview

### 1. Basic Routing (`example_basic_routing.py`)

The simplest way to use SmartRouter - automatic model tier selection for different task complexities.

**What it demonstrates:**
- Direct SmartRouter usage
- Automatic tier selection (Fast/Balanced/Powerful)
- Task classification
- Complexity scoring
- Cost estimation

**Run it:**
```bash
python samples/example_basic_routing.py
```

**Expected output:**
- Tier selection for 6 different query types
- Routing statistics and cache metrics

**Key concepts:**
- Fast tier: Simple queries (~$0.003)
- Balanced tier: Code and analysis (~$0.009)
- Powerful tier: Complex reasoning (~$0.052)

---

### 2. Agent Harness Integration (`example_agent_harness.py`)

Shows how to integrate SmartRouter with an agent system that selects appropriate tools based on routing decisions.

**What it demonstrates:**
- Single agent harness with integrated router
- Multi-agent orchestrator
- Tool selection based on task classification
- Performance metrics collection
- Agent decision history

**Run it:**
```bash
python samples/example_agent_harness.py
```

**Expected output:**
- Agent execution with tool selection
- Performance report with metrics
- Cost breakdown by tier

**Patterns shown:**
- **Single Agent**: One harness handles all requests with automatic tool selection
- **Multi-Agent**: Multiple specialized agents, requests routed to appropriate agent

---

### 3. Framework Integration Patterns (`example_framework_integration.py`)

Demonstrates how SmartRouter integrates with different agent frameworks and architectural patterns.

**What it demonstrates:**
- LangChain-style agent integration
- ReAct pattern (Reasoning + Acting)
- Hierarchical agent system
- Adaptive agent with learning

**Run it:**
```bash
python samples/example_framework_integration.py
```

**Expected output:**
- Different framework integration approaches
- Tool execution results
- Adaptive behavior patterns

**Patterns shown:**
1. **LangChain-Style**: Tool-based agent with Think→Decide→Act→Observe loop
2. **ReAct**: Reasoning step followed by acting, adaptive complexity-based planning
3. **Hierarchical**: Multiple specialist agents, task routing to appropriate specialist
4. **Adaptive**: Agent learns from patterns and adjusts behavior

---

## Integration Patterns

### Pattern 1: Simple Harness
```python
from agent_harness import AgentHarness

harness = AgentHarness()
result = await harness.execute(
    user_input="Your task",
    user_id="user123"
)
print(f"Tier: {result['routing_info']['tier']}")
```

### Pattern 2: Multi-Agent Orchestrator
```python
from agent_harness import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()
result = await orchestrator.execute_task(
    task="Complex task",
    agent_preference="specialist"
)
```

### Pattern 3: Framework Integration
```python
from framework_examples import LangChainStyleAgent

agent = LangChainStyleAgent(tools)
result = await agent.run("Your task")
```

### Pattern 4: Custom Integration
```python
from smart_router import SmartRouter

router = SmartRouter()
result = await router.route_request({
    "user_input": "Your task",
    "user_id": "user123"
})
# Use result.tier, result.model, result.complexity_score
```

---

## Key Metrics Explained

### Routing Information
- **Tier**: Model tier selected (fast/balanced/powerful)
- **Model**: Specific LLM to use (e.g., claude-3-5-haiku)
- **Complexity Score**: 0.0-1.0, indicates task difficulty
- **Estimated Cost**: Predicted cost before execution
- **Classification**: Task category identified
- **Latency**: Time to make routing decision

### Performance Metrics
- **Cache Hit Rate**: % of requests served from cache
- **Tier Distribution**: How requests distributed across tiers
- **Tool Usage**: Which tools used most frequently
- **Average Cost**: Mean cost per request
- **Average Complexity**: Mean complexity score

---

## Cost Optimization Examples

### Simple Query
```
Query: "What is Python?"
→ Classification: simple_query
→ Tier: fast (1x cost)
→ Cost: $0.003
→ Savings vs Powerful: 94% ✅
```

### Code Generation
```
Query: "Write a Python function for binary search"
→ Classification: code_generation
→ Tier: balanced (3-4x cost)
→ Cost: $0.009
→ Savings vs Powerful: 83% ✅
```

### Complex Reasoning
```
Query: "Design a microservices architecture for 1M users"
→ Classification: complex_reasoning
→ Tier: powerful (5-8x cost)
→ Cost: $0.052
→ No savings (necessary complexity)
```

---

## Classification Categories

SmartRouter automatically classifies tasks into:

1. **simple_query**: Definitions, lookups, basic questions
2. **code_generation**: Function/class creation, boilerplate
3. **complex_reasoning**: Architecture, debugging, analysis
4. **document_analysis**: Summarization, extraction, review
5. **creative_writing**: Stories, marketing, content
6. **data_analysis**: Statistics, visualization, interpretation

---

## Running All Examples

To run all examples sequentially:

```bash
#!/bin/bash
echo "Running all SmartRouter examples..."

echo -e "\n=== Example 1: Basic Routing ==="
python samples/example_basic_routing.py

echo -e "\n=== Example 2: Agent Harness ==="
python samples/example_agent_harness.py

echo -e "\n=== Example 3: Framework Integration ==="
python samples/example_framework_integration.py

echo -e "\nAll examples completed!"
```

---

## Performance Expectations

### Latency
- SmartRouter routing decision: <100ms
- Agent tool selection: <50ms
- Total overhead: <150ms (vs 1-5s LLM call)

### Accuracy
- Classification: >90% accuracy on known patterns
- Tier selection: 95%+ appropriate for task complexity

### Cost Savings
- Average: 20-40% reduction
- Simple tasks: 80-90% reduction
- Complex tasks: 0% (uses appropriate tier)

---

## Troubleshooting

### Issue: Same tier always selected
**Solution**: Review complexity scoring distribution
```python
scorer = ComplexityScorer()
for test in test_inputs:
    score = scorer.calculate_complexity_score({...})
    print(f"{test} → {score:.2f}")
```

### Issue: Wrong tool selected
**Solution**: Check classification patterns
```python
classifier = RuleBasedClassifier()
result = classifier.classify(user_input)
print(f"Classification: {result}")
```

### Issue: Low cache hit rate
**Solution**: Normalize queries and extend TTL
```python
cache = CachingOptimizer()
cache.cache_ttl = 7200  # 2 hours
```

---

## Next Steps

1. **Try Example 1** to understand basic routing
2. **Try Example 2** to see agent integration
3. **Try Example 3** to explore framework patterns
4. **Customize** patterns for your use case
5. **Monitor** metrics in production
6. **Optimize** thresholds based on actual workload

---

## Files in This Directory

```
samples/
├── README.md                          # This file
├── example_basic_routing.py           # Basic SmartRouter usage
├── example_agent_harness.py           # Agent integration
├── example_framework_integration.py   # Framework patterns
└── [future: benchmarks, data files]
```

---

## Questions?

- See `START_HERE.md` for navigation
- See `INTEGRATION_GUIDE.md` for detailed patterns
- See `QUICK_REFERENCE.txt` for syntax lookup
- Check code comments in each example file
