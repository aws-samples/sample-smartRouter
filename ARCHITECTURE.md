# SmartRouter Architecture & Flow

## System Overview

SmartRouter is an intelligent request routing system that automatically selects the optimal AI model tier based on task complexity, manages caching, balances load, and handles failures gracefully.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER REQUEST                                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   SmartRouter           │
                    │  (Main Orchestrator)    │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
    ┌─────────────┐      ┌──────────────┐      ┌──────────────────┐
    │   Cache     │      │  Classifier  │      │  Complexity      │
    │  Optimizer  │      │   (Hybrid)   │      │   Scorer         │
    │             │      │              │      │                  │
    │ • Hash      │      │ • Rule-based │      │ • Input length   │
    │   generation│      │ • GZip-kNN   │      │ • Category score │
    │ • Cache hit │      │ • Confidence │      │ • Context size   │
    │   detection │      │              │      │ • Reasoning depth│
    │ • TTL mgmt  │      └──────────────┘      └──────────────────┘
    └─────────────┘
        │
        ▼ (Cache Miss)
    ┌────────────────────────────────────────────┐
    │  Tier Selection Pipeline                   │
    │  ┌────────────────────────────────────┐   │
    │  │ 1. Score to Tier Mapping           │   │
    │  │    Complexity Score → ModelTier    │   │
    │  └────────┬───────────────────────────┘   │
    │           │                               │
    │  ┌────────▼───────────────────────────┐   │
    │  │ 2. Apply User Preferences          │   │
    │  │    Override tier if specified      │   │
    │  └────────┬───────────────────────────┘   │
    │           │                               │
    │  ┌────────▼───────────────────────────┐   │
    │  │ 3. Cost Estimation                 │   │
    │  │    Token calculation               │   │
    │  │    Price per tier                  │   │
    │  └────────┬───────────────────────────┘   │
    │           │                               │
    │  ┌────────▼───────────────────────────┐   │
    │  │ 4. Endpoint Selection              │   │
    │  │    with Fallback Router            │   │
    │  │    Try primary tier,               │   │
    │  │    fallback if unavailable         │   │
    │  └────────┬───────────────────────────┘   │
    │           │                               │
    │  ┌────────▼───────────────────────────┐   │
    │  │ 5. Model Selection                 │   │
    │  │    Get model for final tier        │   │
    │  └────────┬───────────────────────────┘   │
    └───────────┼────────────────────────────────┘
                │
    ┌───────────▼─────────────────┐
    │  Cache-Aware Router         │
    │  Structure request for      │
    │  caching with prompt caching│
    │  points                     │
    └───────────┬─────────────────┘
                │
    ┌───────────▼─────────────────┐
    │   LLM Call (Simulated)      │
    │   (or real API in prod)     │
    └───────────┬─────────────────┘
                │
    ┌───────────▼──────────────────────┐
    │  Cache Response                  │
    │  Store in cache with TTL         │
    └───────────┬──────────────────────┘
                │
                ▼
    ┌────────────────────────────────┐
    │  RoutingResult                 │
    │  • response                    │
    │  • tier                        │
    │  • model                       │
    │  • complexity_score            │
    │  • estimated_cost              │
    │  • latency_ms                  │
    │  • classification details      │
    │  • source (cache or llm)       │
    └────────────────────────────────┘
                │
                ▼
    ┌────────────────────────────────┐
    │   UPDATE METRICS               │
    │  • request_count               │
    │  • cache_hits/misses           │
    │  • tier distribution           │
    └────────────────────────────────┘
```

## Request Flow Diagram

```
                          ┌─────────────────┐
                          │  User Request   │
                          │  with user_input│
                          └────────┬────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
                ▼                                     ▼
        ┌─────────────────┐                ┌──────────────────┐
        │ Generate Cache  │                │   Is Cached?     │
        │ Hash            │                └────────┬─────────┘
        └────────┬────────┘                         │
                 │                ┌────────────────┬┘
                 │                │                │
              YES│             YES│             NO │
                 │                │                │
                 ▼                ▼                ▼
          ┌────────────┐   ┌───────────┐   ┌────────────────┐
          │   Cache    │   │  Return   │   │  FULL PIPELINE │
          │   Found?   │   │  Cached   │   │   (see below)  │
          └─────┬──────┘   │ Response  │   └────────────────┘
                │          └───────────┘
            MISS│
                ▼
        ┌──────────────────────────────────────────┐
        │     FULL PROCESSING PIPELINE             │
        │                                          │
        │  Step 1: Classify Task                  │
        │  ├─ Rule-based patterns (fast)          │
        │  ├─ GZip-kNN ML (accurate)              │
        │  └─ Hybrid confidence score             │
        │                                          │
        │  Step 2: Calculate Complexity Score     │
        │  ├─ Input length (20% weight)           │
        │  ├─ Task category (40% weight)          │
        │  ├─ Context size (20% weight)           │
        │  └─ Reasoning depth (20% weight)        │
        │                                          │
        │  Step 3: Map to Model Tier              │
        │  ├─ Fast tier (score < 0.33)            │
        │  ├─ Balanced tier (0.33 - 0.67)         │
        │  └─ Powerful tier (score > 0.67)        │
        │                                          │
        │  Step 4: Apply User Preferences         │
        │  └─ Override tier if specified          │
        │                                          │
        │  Step 5: Estimate Costs                 │
        │  ├─ Token count from text               │
        │  ├─ Input cost = tokens × rate          │
        │  └─ Output cost = expected × 3× rate    │
        │                                          │
        │  Step 6: Select Endpoint (Load Balance) │
        │  ├─ Get lowest load endpoint            │
        │  ├─ Try primary tier                    │
        │  ├─ Fallback to alternate tiers         │
        │  └─ Update load counter                 │
        │                                          │
        │  Step 7: Get Model for Tier             │
        │  └─ Fetch model name from config        │
        │                                          │
        │  Step 8: Structure for Caching          │
        │  ├─ System prompt (static cache point)  │
        │  ├─ User context (cache point)          │
        │  ├─ Conversation history (last 5)       │
        │  └─ Current user message                │
        │                                          │
        │  Step 9: Call LLM / Model               │
        │  └─ Simulate or call real API           │
        │                                          │
        │  Step 10: Cache Response                │
        │  ├─ Generate cache key                  │
        │  ├─ Store response                      │
        │  └─ Set TTL (1 hour default)            │
        └────────────┬─────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Build RoutingResult       │
        │  • response text           │
        │  • selected tier           │
        │  • model name              │
        │  • classification scores   │
        │  • complexity score        │
        │  • estimated cost          │
        │  • latency                 │
        │  • source (llm/cache)      │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  Return to User            │
        └────────────────────────────┘
```

## Tier Selection Logic

```
                    Complexity Score (0.0 - 1.0)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
    0.0 ─ 0.33          0.33 ─ 0.67         0.67 ─ 1.0
        │                   │                   │
        ▼                   ▼                   ▼
    ┌────────┐           ┌─────────┐       ┌──────────┐
    │  FAST  │           │BALANCED │       │POWERFUL  │
    │ Tier 1 │           │ Tier 2  │       │ Tier 3   │
    │        │           │         │       │          │
    │ Cost:  │           │ Cost:   │       │ Cost:    │
    │  $0.001│           │ $0.003  │       │ $0.015   │
    │ /1k    │           │ /1k     │       │ /1k      │
    │ tokens │           │ tokens  │       │ tokens   │
    │        │           │         │       │          │
    │Model:  │           │ Model:  │       │ Model:   │
    │Claude- │           │ Claude- │       │ Claude-  │
    │Haiku   │           │ Sonnet  │       │ Opus     │
    │        │           │         │       │          │
    │Cases:  │           │ Cases:  │       │ Cases:   │
    │• Basic │           │• Analysis│      │• Complex │
    │  Q&A   │           │• Coding │       │  Design  │
    │• Lookup│           │• Medium │       │• Strategy│
    └────────┘           │  tasks  │       │• Research│
                         └─────────┘       └──────────┘
```

## Fallback Routing Strategy

```
Primary Request → Try Tier X
                      │
                      ├─ Success → Use Tier X
                      │
                      └─ Failure → Try Fallback Chain
                                       │
                         ┌─────────────┼─────────────┐
                         │             │             │
                    Try Tier Y     Try Tier Z    All Failed
                         │             │             │
                         ├─ Success    ├─ Success    └─ Return Error
                         │             │
                         └─ Tier Y     └─ Tier Z
```

## Configuration Files

```
┌──────────────────────────────────────────────────────┐
│ config/tier_config.json                              │
│ ├─ fast tier                                         │
│ │  ├─ models: [list of fast models]                 │
│ │  ├─ cost_per_1k_tokens                            │
│ │  ├─ max_tokens                                     │
│ │  └─ avg_latency_ms                                │
│ ├─ balanced tier                                     │
│ └─ powerful tier                                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ config/regex_patterns.json                           │
│ ├─ simple_query: [pattern1, pattern2, ...]          │
│ ├─ code_generation: [pattern1, pattern2, ...]       │
│ ├─ complex_reasoning: [...]                         │
│ └─ ... (6 categories total)                         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ config/ml_sample_prompts.json                        │
│ ├─ simple_query: [example1, example2, ...]          │
│ ├─ code_generation: [example1, example2, ...]       │
│ └─ ... (training examples for GZip-kNN)             │
└──────────────────────────────────────────────────────┘
```

## Data Flow for Classification

```
User Input Text
      │
      ▼
┌──────────────────────────────┐
│  RuleBasedClassifier         │
│  Pattern matching with regex │
└────────────┬─────────────────┘
             │
             ▼
    ┌────────────────┐
    │ Category scores│  Fast, deterministic
    │ (if matched)   │
    └────────┬───────┘
             │
             ▼
┌──────────────────────────────┐
│  GZipKNNClassifier           │
│  Compression-based ML        │
└────────────┬─────────────────┘
             │
             ▼
    ┌────────────────┐
    │ Category scores│  Slower, more accurate
    │ (via kNN)      │
    └────────┬───────┘
             │
             ▼
┌──────────────────────────────┐
│  Hybrid Confidence Weighting │
│  Adaptive weights based on   │
│  rule confidence             │
└────────────┬─────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Combined Scores            │
    │ Best Category + Confidence │
    └────────────────────────────┘
```

## Complexity Score Calculation

```
Input Analysis
      │
      ├─ Input Length
      │  └─ min(len(text)/1000, 1.0) × 0.20
      │
      ├─ Task Category  
      │  └─ category_score × 0.40
      │
      ├─ Context Size
      │  └─ min(context_tokens/10000, 1.0) × 0.20
      │
      └─ Reasoning Depth
         └─ confidence_score × 0.20
           
           ▼
        Sum All Weighted Scores
           │
           ▼
        Complexity Score (0.0 - 1.0)
```

## Cache Management

```
┌─────────────────────────────────────────────┐
│  Request Coming In                          │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │ Generate Cache Hash │
    │ (SHA256 of request) │
    └──────────┬──────────┘
               │
    ┌──────────▼─────────────────┐
    │ Lookup in Cache Dictionary │
    └────────┬─────────┬─────────┘
             │         │
          YES│      NO │
             │         │
        ┌────▼┐   ┌────▼──────────────┐
        │ HIT │   │ MISS              │
        │     │   │                   │
        │Return   │ Process request   │
        │cached   │ (full pipeline)   │
        │response │                   │
        │         │ Call LLM          │
        │         │                   │
        │         │ Cache response    │
        │         │ with TTL=3600s    │
        │         │                   │
        │         │ Return response   │
        │         │                   │
        └─────┬───┴───────────────────┘
              │
              ▼
        ┌──────────────┐
        │ Track metrics│
        │ cache_hits++ │
        │ or miss++    │
        └──────────────┘
```

## Key Metrics & Statistics

```
SmartRouter Tracks:
├─ Request Processing
│  ├─ total_requests
│  ├─ cache_hits
│  ├─ cache_misses
│  └─ cache_hit_rate (%)
│
├─ Performance
│  ├─ average_latency_ms
│  ├─ classifications_per_second
│  └─ latency_per_category
│
├─ Tier Distribution
│  ├─ requests_per_tier
│  ├─ cost_per_tier
│  └─ tier_distribution (%)
│
└─ Classification
   ├─ category_accuracy
   ├─ confidence_scores
   └─ misclassification_rate
```

## Integration Points

```
SmartRouter can integrate with:
├─ LLM APIs
│  ├─ Anthropic (Claude)
│  ├─ OpenAI (GPT)
│  └─ Google (Gemini)
│
├─ Monitoring
│  ├─ Prometheus
│  ├─ Datadog
│  └─ CloudWatch
│
├─ Caching
│  ├─ In-memory (current)
│  ├─ Redis
│  └─ Memcached
│
└─ Frameworks
   ├─ LangChain
   ├─ LlamaIndex
   └─ AutoGen
```

