"""
Smart Routing & Automatic Model Selection
A comprehensive implementation of intelligent model selection and routing for AI systems.
"""

import asyncio
import json
import re
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from utils.config_loader import ConfigLoader, TierConfigManager
from utils.gzip_knn_classifier import GZipKNNClassifier, AdaptiveHybridClassifier


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ModelTier(Enum):
    """Model tier classification."""
    FAST = "fast"
    BALANCED = "balanced"
    POWERFUL = "powerful"


@dataclass
class TierConfig:
    """Configuration for a model tier."""
    models: List[str]
    cost_per_1k_tokens: float
    max_tokens: int
    avg_latency_ms: int


@dataclass
class RoutingResult:
    """Result of a routing decision."""
    response: str
    tier: str
    model: str
    classification: Dict[str, Any]
    complexity_score: float
    estimated_cost: float
    latency_ms: float
    source: str  # 'cache' or 'llm'


# ============================================================================
# TASK CLASSIFICATION SYSTEM
# ============================================================================

class RuleBasedClassifier:
    """Pattern-based task classifier using regex rules loaded from configuration."""

    def __init__(self, patterns: Optional[Dict[str, List[str]]] = None):
        """
        Initialize with patterns from config or provided dictionary.
        
        Args:
            patterns: Optional dictionary of category -> regex patterns.
                     If None, loads from config file.
        """
        if patterns is None:
            loader = ConfigLoader()
            self.patterns = loader.load_regex_patterns()
        else:
            self.patterns = patterns

    def classify(self, user_input: str) -> Optional[Dict[str, float]]:
        """Classify input using pattern matching."""
        scores = {}
        user_input_lower = user_input.lower()

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, user_input_lower):
                        scores[category] = scores.get(category, 0.0) + 1.0
                except re.error:
                    # Skip invalid patterns
                    continue

        if scores:
            total = sum(scores.values())
            scores = {k: v / total for k, v in scores.items()}
            return scores

        return None


class HybridClassifier:
    """Combines rule-based and GZip-kNN classification with adaptive weighting."""

    def __init__(
        self,
        rule_classifier: Optional["RuleBasedClassifier"] = None,
        gzip_classifier: Optional[GZipKNNClassifier] = None,
        sample_prompts: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize hybrid classifier.
        
        Args:
            rule_classifier: Optional custom rule-based classifier
            gzip_classifier: Optional custom GZip-kNN classifier
            sample_prompts: Optional custom sample prompts for GZip-kNN
        """
        if rule_classifier is None:
            rule_classifier = RuleBasedClassifier()
        self.rule_classifier = rule_classifier
        
        if gzip_classifier is None:
            # Load sample prompts if not provided
            if sample_prompts is None:
                loader = ConfigLoader()
                sample_prompts = loader.load_ml_sample_prompts()
            
            # Create GZip-kNN classifier
            gzip_classifier = GZipKNNClassifier(k=5)
            
            # Add training examples
            training_examples = []
            for category, prompts in sample_prompts.items():
                for prompt in prompts:
                    training_examples.append((prompt, category))
            
            gzip_classifier.add_examples(training_examples)
        
        self.gzip_classifier = gzip_classifier
        self.confidence_threshold = 0.6

    async def classify(self, user_input: str) -> Dict[str, Any]:
        """
        Classify using adaptive hybrid approach.
        
        Returns both rule-based and GZip-kNN results with adaptive weighting.
        """
        # Rule-based classification (fast, deterministic)
        rule_result = self.rule_classifier.classify(user_input)
        
        # GZip-kNN classification (compression-based)
        gzip_result = self.gzip_classifier.classify_scores(user_input)
        
        # Adaptive weights: adjust based on rule confidence
        if rule_result and max(rule_result.values()) >= self.confidence_threshold:
            # High confidence in rule-based, weight it heavily
            weights = {'rule': 0.6, 'gzip': 0.4}
        else:
            # Uncertain, equal weights
            weights = {'rule': 0.5, 'gzip': 0.5}
        
        # Combine results
        combined_scores: Dict[str, float] = {}
        
        if rule_result:
            for category, score in rule_result.items():
                combined_scores[category] = combined_scores.get(category, 0.0) + weights['rule'] * score
        
        if gzip_result:
            for category, score in gzip_result.items():
                combined_scores[category] = combined_scores.get(category, 0.0) + weights['gzip'] * score
        
        # Normalize
        total = sum(combined_scores.values())
        if total > 0:
            combined_scores = {k: v / total for k, v in combined_scores.items()}
        
        # Determine best category
        if combined_scores:
            best_category = max(combined_scores, key=combined_scores.get)
            confidence = combined_scores[best_category]
        else:
            best_category = 'balanced'
            confidence = 0.5
        
        return {
            'category': best_category,
            'confidence': confidence,
            'scores': combined_scores,
            'method': 'hybrid',
            'weights': weights
        }


# ============================================================================
# MODEL TIER SELECTION
# ============================================================================

class ModelTierConfig:
    """Manages model tier configurations loaded from config file."""

    def __init__(self, tier_config: Optional[Dict[str, Any]] = None):
        """
        Initialize with tier configuration.
        
        Args:
            tier_config: Optional tier configuration dictionary.
                        If None, loads from config file.
        """
        if tier_config is None:
            loader = ConfigLoader()
            tier_config = loader.load_tier_config()
        
        self.tier_manager = TierConfigManager(tier_config)
        self.tiers = self.tier_manager.tiers
        self.category_scores = self.tier_manager.category_scores
        self.thresholds = self.tier_manager.thresholds

    def get_tier_config(self, tier: "ModelTier") -> "TierConfig":
        """Get configuration for a tier."""
        tier_info = self.tier_manager.get_tier_info(tier.value)
        return TierConfig(
            models=tier_info["models"],
            cost_per_1k_tokens=tier_info["cost_per_1k_tokens"],
            max_tokens=tier_info["max_tokens"],
            avg_latency_ms=tier_info["avg_latency_ms"],
        )

    def get_model_for_tier(self, tier: "ModelTier") -> str:
        """Get first model for a tier."""
        return self.tier_manager.get_model_for_tier(tier.value)


class ComplexityScorer:
    """Calculates task complexity score using configured weights."""

    def __init__(self, tier_config: Optional[Dict[str, Any]] = None):
        """
        Initialize scorer with tier configuration.
        
        Args:
            tier_config: Optional tier configuration dictionary.
                        If None, loads from config file.
        """
        if tier_config is None:
            loader = ConfigLoader()
            tier_config = loader.load_tier_config()
        
        self.tier_manager = TierConfigManager(tier_config)
        self.complexity_weights = {
            "input_length": 0.2,
            "task_category": 0.4,
            "context_size": 0.2,
            "reasoning_depth": 0.2,
        }
        self.category_scores = self.tier_manager.category_scores

    def calculate_complexity_score(self, task_data: Dict) -> float:
        """Calculate normalized complexity score (0.0 to 1.0)."""
        scores = {}

        # Input length score
        input_length = len(task_data.get("user_input", ""))
        scores["input_length"] = min(input_length / 1000, 1.0)

        # Task category score
        category = task_data.get("category", "balanced")
        scores["task_category"] = self.category_scores.get(category, 0.5)

        # Context size score
        context_tokens = task_data.get("context_tokens", 0)
        scores["context_size"] = min(context_tokens / 10000, 1.0)

        # Reasoning depth score
        scores["reasoning_depth"] = task_data.get("reasoning_depth", 0.5)

        # Weighted sum
        total_score = sum(
            scores[key] * self.complexity_weights[key] for key in scores
        )

        return total_score

    def score_to_tier(self, complexity_score: float) -> ModelTier:
        """Map complexity score to model tier."""
        fast_max = self.tier_manager.get_complexity_threshold("fast_max")
        balanced_max = self.tier_manager.get_complexity_threshold("balanced_max")
        
        if complexity_score < fast_max:
            return ModelTier.FAST
        elif complexity_score < balanced_max:
            return ModelTier.BALANCED
        else:
            return ModelTier.POWERFUL


# ============================================================================
# ROUTING MECHANISMS
# ============================================================================

class ContentBasedRouter:
    """Routes requests based on content characteristics."""

    def __init__(self):
        self.routing_keys = ["user_id", "task_type", "complexity_tier"]

    def generate_routing_key(self, request_data: Dict) -> str:
        """Generate consistent routing key."""
        key_components = [
            request_data.get("user_id", "anonymous"),
            request_data.get("task_type", "general"),
            request_data.get("complexity_tier", "balanced"),
        ]
        routing_key = ":".join(key_components)
        return hashlib.md5(routing_key.encode(), usedforsecurity=False).hexdigest()

    def route_to_cluster(self, routing_key: str, num_clusters: int = 10) -> int:
        """Determine cluster based on routing key."""
        hash_value = int(routing_key, 16)
        return hash_value % num_clusters


class CacheAwareRouter:
    """Structures requests to maximize caching."""

    def structure_request_for_caching(self, request_data: Dict) -> List[Dict]:
        """Structure request for multi-level caching."""
        messages = []

        # Cache Point 1: System prompt (static, cacheable)
        messages.append(
            {
                "role": "system",
                "content": request_data.get(
                    "system_prompt", "You are a helpful AI assistant."
                ),
                "cache_control": {"type": "ephemeral"},
            }
        )

        # Cache Point 2: User-specific context
        user_context = f"User ID: {request_data.get('user_id', 'anonymous')}"
        messages.append(
            {
                "role": "user",
                "content": user_context,
                "cache_control": {"type": "ephemeral"},
            }
        )

        # Cache Point 3: Conversation history (last 5 messages)
        for msg in request_data.get("conversation_history", [])[-5:]:
            messages.append(msg)

        # Current user message
        messages.append({"role": "user", "content": request_data["user_input"]})

        return messages


class LoadBalancedRouter:
    """Distributes requests across endpoints."""

    def __init__(self):
        self.endpoints = {}
        self.endpoint_load = {}

    def register_endpoint(self, tier: ModelTier, endpoint: str, capacity: int):
        """Register an endpoint for a tier."""
        tier_key = tier.value
        if tier_key not in self.endpoints:
            self.endpoints[tier_key] = []
            self.endpoint_load[tier_key] = {}

        self.endpoints[tier_key].append(endpoint)
        self.endpoint_load[tier_key][endpoint] = 0

    def select_endpoint(self, tier: ModelTier) -> str:
        """Select endpoint with lowest load."""
        tier_key = tier.value
        if tier_key not in self.endpoints or not self.endpoints[tier_key]:
            return "default"

        endpoints = self.endpoints[tier_key]
        selected = min(
            endpoints, key=lambda e: self.endpoint_load[tier_key].get(e, 0)
        )
        self.endpoint_load[tier_key][selected] += 1
        return selected

    def release_endpoint(self, tier: ModelTier, endpoint: str):
        """Release endpoint after use."""
        tier_key = tier.value
        if tier_key in self.endpoint_load and endpoint in self.endpoint_load[tier_key]:
            self.endpoint_load[tier_key][endpoint] = max(
                0, self.endpoint_load[tier_key][endpoint] - 1
            )


class FallbackRouter:
    """Handles failures with automatic fallback."""

    def __init__(self):
        self.fallback_chain = {
            ModelTier.POWERFUL: [ModelTier.BALANCED, ModelTier.FAST],
            ModelTier.BALANCED: [ModelTier.FAST, ModelTier.POWERFUL],
            ModelTier.FAST: [ModelTier.BALANCED, ModelTier.POWERFUL],
        }

    async def route_with_fallback(
        self, tier: ModelTier, request_data: Dict, primary_router: LoadBalancedRouter
    ) -> Tuple[str, ModelTier]:
        """Try primary tier, fall back to alternatives if needed."""
        tiers_to_try = [tier] + self.fallback_chain.get(tier, [])

        for attempt_tier in tiers_to_try:
            try:
                endpoint = primary_router.select_endpoint(attempt_tier)
                return endpoint, attempt_tier
            except Exception:
                if attempt_tier == tiers_to_try[-1]:
                    raise Exception("All routing attempts failed")
                continue

        return "default", tier


# ============================================================================
# COST OPTIMIZATION
# ============================================================================

class CostEstimator:
    """Estimates request costs."""

    def __init__(self, tier_config: ModelTierConfig):
        self.tier_config = tier_config

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)."""
        return len(text) // 4

    def estimate_request_cost(
        self, request_data: Dict, tier: ModelTier
    ) -> float:
        """Estimate cost for a request at a given tier."""
        tier_config = self.tier_config.get_tier_config(tier)

        input_tokens = self.estimate_tokens(request_data.get("user_input", ""))
        context_tokens = request_data.get("context_tokens", 0)
        expected_output_tokens = request_data.get("max_output_tokens", 1000)

        total_input_tokens = input_tokens + context_tokens

        input_cost = (total_input_tokens / 1000) * tier_config.cost_per_1k_tokens
        output_cost = (expected_output_tokens / 1000) * tier_config.cost_per_1k_tokens * 3

        return input_cost + output_cost

    def compare_tier_costs(self, request_data: Dict) -> Dict[str, float]:
        """Compare costs across all tiers."""
        return {
            tier.value: self.estimate_request_cost(request_data, tier)
            for tier in ModelTier
        }


class CachingOptimizer:
    """Manages request caching."""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

    def generate_request_hash(self, request_data: Dict) -> str:
        """Generate cache key for a request."""
        cache_key_data = {
            "user_input": request_data["user_input"],
            "system_prompt": request_data.get("system_prompt", ""),
            "model_tier": request_data.get("tier", "balanced"),
        }
        key_string = json.dumps(cache_key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get_cached_response(self, request_hash: str) -> Optional[str]:
        """Retrieve cached response if valid."""
        cached = self.cache.get(request_hash)
        if cached and time.time() - cached["timestamp"] < self.cache_ttl:
            return cached["response"]
        return None

    def cache_response(self, request_hash: str, response: str):
        """Cache a response."""
        self.cache[request_hash] = {
            "response": response,
            "timestamp": time.time(),
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_cached": len(self.cache),
            "valid_cached": sum(
                1
                for item in self.cache.values()
                if time.time() - item["timestamp"] < self.cache_ttl
            ),
        }


# ============================================================================
# MAIN SMART ROUTER
# ============================================================================

class SmartRouter:
    """Main router orchestrating the complete routing pipeline."""

    def __init__(self):
        self.hybrid_classifier = HybridClassifier()
        self.complexity_scorer = ComplexityScorer()
        self.tier_config = ModelTierConfig()
        self.cost_estimator = CostEstimator(self.tier_config)
        self.load_balancer = LoadBalancedRouter()
        self.cache_optimizer = CachingOptimizer()
        self.content_router = ContentBasedRouter()
        self.cache_router = CacheAwareRouter()
        self.fallback_router = FallbackRouter()

        # Register endpoints
        self._register_endpoints()

        # Metrics
        self.request_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def _register_endpoints(self):
        """Register default endpoints for each tier."""
        for tier in ModelTier:
            self.load_balancer.register_endpoint(tier, f"{tier.value}_endpoint", 100)

    async def route_request(self, request_data: Dict) -> RoutingResult:
        """Route a request through the complete pipeline."""
        start_time = time.time()
        self.request_count += 1

        # Step 1: Check cache
        request_hash = self.cache_optimizer.generate_request_hash(request_data)
        cached_response = self.cache_optimizer.get_cached_response(request_hash)

        if cached_response:
            self.cache_hits += 1
            return RoutingResult(
                response=cached_response,
                tier="cache",
                model="cache",
                classification={},
                complexity_score=0.0,
                estimated_cost=0.0,
                latency_ms=(time.time() - start_time) * 1000,
                source="cache",
            )

        self.cache_misses += 1

        # Step 2: Classify task
        classification = await self.hybrid_classifier.classify(
            request_data["user_input"]
        )

        # Step 3: Calculate complexity
        complexity_score = self.complexity_scorer.calculate_complexity_score(
            {
                "user_input": request_data["user_input"],
                "category": classification["category"],
                "context_tokens": len(request_data.get("conversation_history", [])) * 100,
                "reasoning_depth": classification.get("confidence", 0.5),
            }
        )

        # Step 4: Select tier
        tier = self.complexity_scorer.score_to_tier(complexity_score)

        # Step 5: Apply user preferences/overrides
        if request_data.get("user_tier_preference"):
            tier_name = request_data["user_tier_preference"]
            tier = ModelTier(tier_name) if tier_name in [t.value for t in ModelTier] else tier

        # Step 6: Cost estimation
        estimated_cost = self.cost_estimator.estimate_request_cost(request_data, tier)

        # Step 7: Select endpoint with fallback
        endpoint, final_tier = await self.fallback_router.route_with_fallback(
            tier, request_data, self.load_balancer
        )

        # Step 8: Get model
        model = self.tier_config.get_model_for_tier(final_tier)

        # Step 9: Structure for caching
        messages = self.cache_router.structure_request_for_caching(request_data)

        # Step 10: Simulate LLM call
        response = await self._simulate_llm_call(model, messages, request_data)

        # Cache the response
        self.cache_optimizer.cache_response(request_hash, response)

        latency_ms = (time.time() - start_time) * 1000

        return RoutingResult(
            response=response,
            tier=final_tier.value,
            model=model,
            classification=classification,
            complexity_score=complexity_score,
            estimated_cost=estimated_cost,
            latency_ms=latency_ms,
            source="llm",
        )

    async def _simulate_llm_call(
        self, model: str, messages: List[Dict], request_data: Dict
    ) -> str:
        """Simulate LLM call (in real implementation, would call actual API)."""
        await asyncio.sleep(0.1)  # Simulate API latency

        user_input = request_data["user_input"]
        return f"[{model}] Response to: {user_input[:50]}..."

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        cache_total = self.cache_hits + self.cache_misses
        cache_hit_rate = (
            (self.cache_hits / cache_total * 100) if cache_total > 0 else 0
        )

        return {
            "total_requests": self.request_count,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "cache_stats": self.cache_optimizer.get_cache_stats(),
        }


# ============================================================================
# USAGE EXAMPLES AND TESTING
# ============================================================================

async def run_examples():
    """Run example routing scenarios."""
    print("=" * 70)
    print("SMART ROUTING & AUTOMATIC MODEL SELECTION - DEMO")
    print("=" * 70)

    router = SmartRouter()

    # Example 1: Simple query
    print("\n[Example 1] Simple Query")
    print("-" * 70)
    result1 = await router.route_request(
        {
            "user_id": "user123",
            "user_input": "What is Python?",
            "conversation_history": [],
        }
    )
    print(f"Input: What is Python?")
    print(f"Tier Selected: {result1.tier}")
    print(f"Model: {result1.model}")
    print(f"Complexity Score: {result1.complexity_score:.2f}")
    print(f"Estimated Cost: ${result1.estimated_cost:.6f}")
    print(f"Latency: {result1.latency_ms:.1f}ms")
    print(f"Classification: {result1.classification}")
    print(f"Source: {result1.source}")

    # Example 2: Code generation
    print("\n[Example 2] Code Generation")
    print("-" * 70)
    result2 = await router.route_request(
        {
            "user_id": "user456",
            "user_input": "Write a Python function to implement binary search",
            "conversation_history": [],
        }
    )
    print(f"Input: Write a Python function to implement binary search")
    print(f"Tier Selected: {result2.tier}")
    print(f"Model: {result2.model}")
    print(f"Complexity Score: {result2.complexity_score:.2f}")
    print(f"Estimated Cost: ${result2.estimated_cost:.6f}")
    print(f"Latency: {result2.latency_ms:.1f}ms")
    print(f"Classification: {result2.classification}")

    # Example 3: Complex reasoning
    print("\n[Example 3] Complex Reasoning")
    print("-" * 70)
    result3 = await router.route_request(
        {
            "user_id": "user789",
            "user_input": "Design a microservices architecture for an e-commerce platform with high availability",
            "conversation_history": [],
        }
    )
    print(
        f"Input: Design a microservices architecture for an e-commerce platform..."
    )
    print(f"Tier Selected: {result3.tier}")
    print(f"Model: {result3.model}")
    print(f"Complexity Score: {result3.complexity_score:.2f}")
    print(f"Estimated Cost: ${result3.estimated_cost:.6f}")
    print(f"Latency: {result3.latency_ms:.1f}ms")
    print(f"Classification: {result3.classification}")

    # Example 4: Cache hit (repeated query)
    print("\n[Example 4] Cache Hit (Same as Example 1)")
    print("-" * 70)
    result4 = await router.route_request(
        {
            "user_id": "user123",
            "user_input": "What is Python?",
            "conversation_history": [],
        }
    )
    print(f"Input: What is Python?")
    print(f"Source: {result4.source} (CACHED)")
    print(f"Latency: {result4.latency_ms:.1f}ms")
    print(f"Cost: ${result4.estimated_cost:.6f} (saved by caching)")

    # Print final statistics
    print("\n" + "=" * 70)
    print("ROUTER STATISTICS")
    print("=" * 70)
    stats = router.get_stats()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Cache Hits: {stats['cache_hits']}")
    print(f"Cache Misses: {stats['cache_misses']}")
    print(f"Cache Hit Rate: {stats['cache_hit_rate']}")
    print(f"Cached Responses: {stats['cache_stats']['valid_cached']}")

    # Cost comparison
    print("\n" + "=" * 70)
    print("COST COMPARISON FOR SAMPLE REQUEST")
    print("=" * 70)
    sample_request = {
        "user_input": "Explain how neural networks work",
        "context_tokens": 500,
        "max_output_tokens": 1000,
    }
    costs = router.cost_estimator.compare_tier_costs(sample_request)
    for tier, cost in costs.items():
        print(f"{tier.upper():<12}: ${cost:.6f}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(run_examples())
