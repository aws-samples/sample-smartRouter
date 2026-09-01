# SmartRouter Samples & Usage Examples Index

## 📁 Directory Structure

```
samples/
├── README.md                          # Complete guide to all examples
├── SAMPLES_INDEX.md                   # This file
├── example_basic_routing.py           # Core routing functionality
├── example_agent_harness.py           # Agent integration patterns
└── example_framework_integration.py   # Framework-specific patterns
```

## 🚀 Quick Navigation

### New to SmartRouter?
1. Start with `README.md` - Overview of all examples
2. Run `example_basic_routing.py` - Understand tier selection
3. Run `example_agent_harness.py` - See agent integration
4. Read integration patterns in `README.md`

### Want to Integrate with Your Framework?
→ `example_framework_integration.py` - Shows 4 different patterns

### Need Code Examples?
→ Each `.py` file is a standalone, runnable example

### Need Detailed Explanations?
→ `README.md` - Comprehensive guide with all concepts explained

---

## 📚 Examples Quick Reference

| Example | File | Focus | Complexity | Time |
|---------|------|-------|-----------|------|
| Basic Routing | `example_basic_routing.py` | Core functionality | ⭐ Beginner | 5 min |
| Agent Harness | `example_agent_harness.py` | Agent integration | ⭐⭐ Intermediate | 10 min |
| Framework Integration | `example_framework_integration.py` | Framework patterns | ⭐⭐⭐ Advanced | 15 min |

---

## 🎯 Example Details

### Example 1: Basic Routing
**File:** `example_basic_routing.py`

**Shows:**
- SmartRouter initialization
- Automatic tier selection
- Task classification
- Complexity scoring
- Cost estimation
- Performance statistics

**Run:** `python samples/example_basic_routing.py`

**Key Output:**
```
Tier Selection: Fast/Balanced/Powerful
Cost Estimation: $0.003-$0.052
Classification: simple_query, code_generation, etc.
Cache Statistics: Hit rate, storage
```

---

### Example 2: Agent Harness Integration
**File:** `example_agent_harness.py`

**Shows:**
- Single agent harness with routing
- Multi-agent orchestrator
- Tool selection based on classification
- Performance metrics
- Decision history

**Run:** `python samples/example_agent_harness.py`

**Key Patterns:**
- Pattern 2A: Single agent handling all requests
- Pattern 2B: Multiple agents for specialized tasks

---

### Example 3: Framework Integration Patterns
**File:** `example_framework_integration.py`

**Shows:**
- LangChain-style integration
- ReAct pattern (Reasoning + Acting)
- Hierarchical agent system
- Adaptive agent with learning

**Run:** `python samples/example_framework_integration.py`

**Key Patterns:**
- Pattern 3A: LangChain integration
- Pattern 3B: ReAct pattern
- Pattern 3C: Hierarchical system
- Pattern 3D: Adaptive behavior

---

## 🔧 Integration Patterns Quick Reference

### Pattern 1: Basic SmartRouter
```python
from smart_router import SmartRouter

router = SmartRouter()
result = await router.route_request({
    "user_input": "Your task",
    "user_id": "user123"
})
```
✅ Best for: Understanding routing fundamentals

### Pattern 2: Agent Harness
```python
from agent_harness import AgentHarness

harness = AgentHarness()
result = await harness.execute("Your task")
```
✅ Best for: Single agent with tool selection

### Pattern 3: Multi-Agent
```python
from agent_harness import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()
result = await orchestrator.execute_task("task")
```
✅ Best for: Multiple specialized agents

### Pattern 4: Framework-Specific
```python
from framework_examples import LangChainStyleAgent

agent = LangChainStyleAgent(tools)
result = await agent.run("Your task")
```
✅ Best for: Specific framework integration

---

## 📊 Key Metrics to Observe

### Routing Metrics
- **Tier**: Model tier selected (fast/balanced/powerful)
- **Complexity**: 0.0-1.0 score
- **Cost**: Estimated execution cost
- **Classification**: Task category detected

### Performance Metrics
- **Cache Hit Rate**: Cached responses %
- **Average Cost**: Mean cost per request
- **Latency**: Response time
- **Tool Usage**: Which tools used

---

## 💡 Learning Progression

### Level 1: Beginner
1. Read `README.md` introduction
2. Run `example_basic_routing.py`
3. Understand tier selection concept
4. **Time: 15 minutes**

### Level 2: Intermediate
1. Read agent integration section in `README.md`
2. Run `example_agent_harness.py`
3. Understand tool selection
4. **Time: 30 minutes**

### Level 3: Advanced
1. Read framework patterns in `README.md`
2. Run `example_framework_integration.py`
3. Understand all 4 integration patterns
4. **Time: 45 minutes**

### Level 4: Expert
1. Customize examples for your use case
2. Integrate with your system
3. Monitor and optimize metrics
4. **Time: Variable**

---

## 🎓 Common Use Cases

### Use Case 1: Cost Optimization
See: `example_basic_routing.py`
Focus: How tier selection saves money

### Use Case 2: Task-Specific Models
See: `example_agent_harness.py` (Example 2B)
Focus: Multi-agent with specialization

### Use Case 3: LangChain Integration
See: `example_framework_integration.py` (Example 3A)
Focus: Tool-based agent architecture

### Use Case 4: Reasoning + Acting
See: `example_framework_integration.py` (Example 3B)
Focus: ReAct pattern with adaptive planning

### Use Case 5: Adaptive Systems
See: `example_framework_integration.py` (Example 3D)
Focus: Learning from patterns

---

## ⚡ Running Examples

### Run Single Example
```bash
python samples/example_basic_routing.py
```

### Run All Examples
```bash
cd samples
for example in example_*.py; do
    echo "Running $example..."
    python "$example"
    echo ""
done
```

### Run with Output Capture
```bash
python samples/example_basic_routing.py > output.log 2>&1
```

---

## 🔍 Understanding Example Output

### Tier Selection Example
```
Query: What is Python?
  ├─ Tier Selected: fast      ← Lowest cost tier
  ├─ Model: claude-3-5-haiku  ← Selected model
  ├─ Cost: $0.003006          ← Estimated cost
  └─ Complexity: 0.29         ← 0.0-1.0 score
```

### Agent Execution Example
```
Task: Write a function
  ├─ Tool Used: code_analyzer     ← Selected tool
  ├─ Tier: balanced               ← Selected tier
  ├─ Model: claude-3-5-sonnet     ← Selected model
  └─ Cost: $0.009027              ← Total cost
```

### Framework Integration Example
```
Task: Simple question
  ├─ Reasoning: direct_solution   ← Approach used
  ├─ Plan: search → return        ← Steps to take
  └─ Tier: fast                   ← Tier selected
```

---

## 📝 Expected Results

All examples should complete successfully with:
- ✅ No errors
- ✅ Clear output showing routing decisions
- ✅ Performance metrics
- ✅ Tier/cost information

If you see errors, check:
1. All dependencies installed
2. Config files present
3. Sample data files exist
4. Python version 3.7+

---

## 🔗 Related Files

### Core System Files
- `smart_router.py` - Core routing engine
- `agent_harness.py` - Agent integration
- `framework_examples.py` - Framework patterns
- `gzip_knn_classifier.py` - ML classifier
- `config_loader.py` - Configuration management

### Configuration Files
- `config/tier_config.json` - Tier definitions
- `config/regex_patterns.json` - Classification patterns
- `config/ml_sample_prompts.json` - ML training data

### Documentation
- `START_HERE.md` - Entry point
- `README.md` - Quick start
- `INTEGRATION_GUIDE.md` - Detailed patterns
- `QUICK_REFERENCE.txt` - Syntax reference

---

## 🚀 Next Steps

1. **Explore** - Run each example
2. **Understand** - Read explanations in README.md
3. **Experiment** - Modify examples
4. **Integrate** - Apply to your system
5. **Optimize** - Monitor and tune metrics

---

## 📞 Help & Support

- **Questions about examples?** → See `README.md`
- **Need syntax help?** → See `QUICK_REFERENCE.txt`
- **Want integration guide?** → See `INTEGRATION_GUIDE.md`
- **Full documentation?** → See `INDEX.md`
- **Getting started?** → See `START_HERE.md`

---

**Happy routing!** 🎉
