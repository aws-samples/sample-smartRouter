"""
SmartRouter Decorator
Provides @SmartRouter decorator for automatic model selection on LLM-calling functions.
"""

import asyncio
import functools
import time
from typing import Callable, Any, Dict, Optional, Awaitable
from smart_router import SmartRouter as SmartRouterEngine, RoutingResult


class SmartRouterDecorator:
    """
    Decorator for automatic model selection on LLM-calling functions.
    
    Usage:
        @SmartRouter()
        async def my_llm_function(user_input: str, user_id: str = "default"):
            # Your LLM call here
            return result
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_ttl: int = 3600,
        metadata_callback: Optional[Callable] = None,
        verbose: bool = False,
        user_id_key: str = "user_id",
    ):
        """
        Initialize the decorator.

        Args:
            cache_enabled: Whether to cache responses (default: True)
            cache_ttl: Cache time-to-live in seconds (default: 3600 = 1 hour)
            metadata_callback: Optional callback to receive routing metadata
            verbose: Whether to print routing info (default: False)
            user_id_key: Key for extracting user_id from function kwargs (default: "user_id")
        """
        self.router = SmartRouterEngine()
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self.metadata_callback = metadata_callback
        self.verbose = verbose
        self.user_id_key = user_id_key
        self.call_metadata = {}  # Store latest metadata

    def __call__(self, func: Callable) -> Callable:
        """Apply decorator to function."""
        if asyncio.iscoroutinefunction(func):
            return self._decorate_async(func)
        else:
            return self._decorate_sync(func)

    def _decorate_async(self, func: Callable) -> Callable:
        """Decorate async function."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract user_input and user_id
            user_input = self._extract_user_input(func, args, kwargs)
            user_id = kwargs.get(self.user_id_key, "default")

            # Route request through SmartRouter
            routing_result = await self.router.route_request(
                {
                    "user_input": user_input,
                    "user_id": user_id,
                    "conversation_history": kwargs.get("conversation_history", []),
                }
            )

            # Store metadata
            self.call_metadata = {
                "tier": routing_result.tier,
                "model": routing_result.model,
                "cost": routing_result.estimated_cost,
                "complexity": routing_result.complexity_score,
                "classification": routing_result.classification,
                "source": routing_result.source,
                "latency_ms": routing_result.latency_ms,
            }

            # Print if verbose
            if self.verbose:
                self._print_routing_info(user_input, routing_result)

            # Call metadata callback if provided
            if self.metadata_callback:
                self.metadata_callback(self.call_metadata)

            # Inject routing info into kwargs
            kwargs["_routing_info"] = self.call_metadata
            kwargs["_selected_model"] = routing_result.model
            kwargs["_selected_tier"] = routing_result.tier

            # Call original function
            result = await func(*args, **kwargs)

            return result

        # Add helper methods to wrapper
        wrapper.get_last_metadata = lambda: self.call_metadata
        wrapper.get_stats = lambda: self.router.get_stats()
        wrapper.clear_cache = lambda: (
            self.router.cache_optimizer.cache.clear(),
            print("Cache cleared"),
        )

        return wrapper

    def _decorate_sync(self, func: Callable) -> Callable:
        """Decorate synchronous function."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Extract user_input and user_id
            user_input = self._extract_user_input(func, args, kwargs)
            user_id = kwargs.get(self.user_id_key, "default")

            # Route request through SmartRouter (run in event loop)
            loop = asyncio.new_event_loop()
            try:
                routing_result = loop.run_until_complete(
                    self.router.route_request(
                        {
                            "user_input": user_input,
                            "user_id": user_id,
                            "conversation_history": kwargs.get("conversation_history", []),
                        }
                    )
                )
            finally:
                loop.close()

            # Store metadata
            self.call_metadata = {
                "tier": routing_result.tier,
                "model": routing_result.model,
                "cost": routing_result.estimated_cost,
                "complexity": routing_result.complexity_score,
                "classification": routing_result.classification,
                "source": routing_result.source,
                "latency_ms": routing_result.latency_ms,
            }

            # Print if verbose
            if self.verbose:
                self._print_routing_info(user_input, routing_result)

            # Call metadata callback if provided
            if self.metadata_callback:
                self.metadata_callback(self.call_metadata)

            # Inject routing info into kwargs
            kwargs["_routing_info"] = self.call_metadata
            kwargs["_selected_model"] = routing_result.model
            kwargs["_selected_tier"] = routing_result.tier

            # Call original function
            result = func(*args, **kwargs)

            return result

        # Add helper methods to wrapper
        wrapper.get_last_metadata = lambda: self.call_metadata
        wrapper.get_stats = lambda: self.router.get_stats()
        wrapper.clear_cache = lambda: (
            self.router.cache_optimizer.cache.clear(),
            print("Cache cleared"),
        )

        return wrapper

    def _extract_user_input(self, func: Callable, args: tuple, kwargs: Dict) -> str:
        """Extract user_input from function arguments."""
        # Try to get from kwargs first
        if "user_input" in kwargs:
            return kwargs["user_input"]

        # Try common parameter names
        for param_name in ["input", "prompt", "query", "message", "text"]:
            if param_name in kwargs:
                return kwargs[param_name]

        # Try positional arguments
        if args:
            return str(args[0])

        return ""

    def _print_routing_info(self, user_input: str, routing_result: RoutingResult):
        """Print routing information."""
        print(f"\n{'='*70}")
        print(f"🔀 SmartRouter Decision")
        print(f"{'='*70}")
        print(f"Input: {user_input[:60]}...")
        print(f"Tier: {routing_result.tier}")
        print(f"Model: {routing_result.model}")
        print(f"Complexity: {routing_result.complexity_score:.2f}")
        print(f"Cost: ${routing_result.estimated_cost:.6f}")
        print(f"Classification: {routing_result.classification.get('category', 'unknown')}")
        print(f"Source: {routing_result.source}")
        print(f"Latency: {routing_result.latency_ms:.1f}ms")
        print(f"{'='*70}\n")


# Convenience instances with different configurations
SmartRouter = SmartRouterDecorator()
SmartRouterVerbose = SmartRouterDecorator(verbose=True)
SmartRouterNoCaching = SmartRouterDecorator(cache_enabled=False)
SmartRouterVerboseNoCaching = SmartRouterDecorator(verbose=True, cache_enabled=False)


# ============================================================================
# ADVANCED: Decorator with Custom Metadata Handling
# ============================================================================

class SmartRouterWithMetadata(SmartRouterDecorator):
    """
    Extended decorator that stores and tracks routing metadata.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execution_history = []
        self.cost_tracker = {"total": 0.0, "by_tier": {}, "by_user": {}}
        self.tier_stats = {"fast": 0, "balanced": 0, "powerful": 0}

    def _decorate_async(self, func: Callable) -> Callable:
        """Decorate async function with metadata tracking."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()

            # Extract user_input and user_id
            user_input = self._extract_user_input(func, args, kwargs)
            user_id = kwargs.get(self.user_id_key, "default")

            # Route request
            routing_result = await self.router.route_request(
                {
                    "user_input": user_input,
                    "user_id": user_id,
                    "conversation_history": kwargs.get("conversation_history", []),
                }
            )

            # Store metadata
            self.call_metadata = {
                "tier": routing_result.tier,
                "model": routing_result.model,
                "cost": routing_result.estimated_cost,
                "complexity": routing_result.complexity_score,
                "classification": routing_result.classification,
                "source": routing_result.source,
                "latency_ms": routing_result.latency_ms,
            }

            # Inject routing info
            kwargs["_routing_info"] = self.call_metadata
            kwargs["_selected_model"] = routing_result.model
            kwargs["_selected_tier"] = routing_result.tier

            # Call original function
            result = await func(*args, **kwargs)

            # Track execution
            execution_time = (time.time() - start_time) * 1000
            execution_record = {
                "timestamp": time.time(),
                "user_id": user_id,
                "user_input": user_input[:50],
                "tier": routing_result.tier,
                "model": routing_result.model,
                "cost": routing_result.estimated_cost,
                "total_latency_ms": execution_time,
                "routing_latency_ms": routing_result.latency_ms,
            }

            self.execution_history.append(execution_record)
            self._update_stats(execution_record)

            # Print if verbose
            if self.verbose:
                self._print_routing_info(user_input, routing_result)
                print(f"Total Execution Time: {execution_time:.1f}ms")

            # Call metadata callback if provided
            if self.metadata_callback:
                self.metadata_callback(self.call_metadata)

            return result

        # Add helper methods
        wrapper.get_last_metadata = lambda: self.call_metadata
        wrapper.get_stats = self.get_execution_stats
        wrapper.get_history = lambda: self.execution_history
        wrapper.clear_cache = lambda: (
            self.router.cache_optimizer.cache.clear(),
            print("Cache cleared"),
        )
        wrapper.print_summary = self.print_summary

        return wrapper

    def _update_stats(self, record: Dict):
        """Update statistics from execution record."""
        tier = record["tier"]
        cost = record["cost"]
        user_id = record["user_id"]

        # Update tier stats
        self.tier_stats[tier] = self.tier_stats.get(tier, 0) + 1

        # Update cost tracker
        self.cost_tracker["total"] += cost
        self.cost_tracker["by_tier"][tier] = (
            self.cost_tracker["by_tier"].get(tier, 0.0) + cost
        )
        self.cost_tracker["by_user"][user_id] = (
            self.cost_tracker["by_user"].get(user_id, 0.0) + cost
        )

    def get_execution_stats(self) -> Dict:
        """Get execution statistics."""
        total_executions = len(self.execution_history)
        if total_executions == 0:
            return {"error": "No executions yet"}

        avg_complexity = sum(
            r.get("complexity", 0) for r in self.execution_history
        ) / total_executions if self.execution_history else 0

        avg_latency = sum(
            r.get("total_latency_ms", 0) for r in self.execution_history
        ) / total_executions if self.execution_history else 0

        return {
            "total_executions": total_executions,
            "tier_distribution": self.tier_stats,
            "total_cost": f"${self.cost_tracker['total']:.6f}",
            "cost_by_tier": {k: f"${v:.6f}" for k, v in self.cost_tracker["by_tier"].items()},
            "cost_by_user": {k: f"${v:.6f}" for k, v in self.cost_tracker["by_user"].items()},
            "average_complexity": f"{avg_complexity:.2f}",
            "average_latency_ms": f"{avg_latency:.1f}",
        }

    def print_summary(self):
        """Print execution summary."""
        stats = self.get_execution_stats()
        print("\n" + "=" * 70)
        print("📊 SmartRouter Execution Summary")
        print("=" * 70)
        for key, value in stats.items():
            print(f"{key:.<40} {value}")
        print("=" * 70 + "\n")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: Basic decorator usage
    @SmartRouter
    async def call_llm_basic(user_input: str, user_id: str = "user1", **kwargs):
        """Simulated LLM call with automatic smart routing."""
        # The decorator provides routing info automatically in kwargs
        await asyncio.sleep(0.1)
        return f"Response to: {user_input}"

    # Example 2: Verbose decorator
    @SmartRouterVerbose
    async def call_llm_verbose(user_input: str, user_id: str = "user1", **kwargs):
        """LLM call with verbose routing info."""
        await asyncio.sleep(0.1)
        return f"Response to: {user_input}"

    # Example 3: With metadata callback
    def log_routing(metadata):
        print(f"\n✅ Routing Decision Logged:")
        print(f"   Tier: {metadata['tier']}")
        print(f"   Cost: ${metadata['cost']:.6f}")

    router_with_callback = SmartRouterDecorator(metadata_callback=log_routing, verbose=True)

    @router_with_callback
    async def call_llm_with_callback(user_input: str, user_id: str = "user1", **kwargs):
        """LLM call with metadata callback."""
        await asyncio.sleep(0.1)
        return f"Response to: {user_input}"

    # Example 4: With metadata tracking
    router_tracker = SmartRouterWithMetadata(verbose=True)

    @router_tracker
    async def call_llm_tracked(user_input: str, user_id: str = "user1", **kwargs):
        """LLM call with metadata tracking."""
        await asyncio.sleep(0.1)
        return f"Response to: {user_input}"

    # Example 5: Accessing routing info inside function
    @SmartRouter
    async def call_llm_with_info(
        user_input: str,
        user_id: str = "user1",
        _routing_info=None,
        _selected_tier=None,
        _selected_model=None,
        **kwargs
    ):
        """Access routing info inside function."""
        print(f"\nInside function:")
        print(f"  Routing Info: {_routing_info}")
        print(f"  Selected Tier: {_selected_tier}")
        print(f"  Selected Model: {_selected_model}")
        await asyncio.sleep(0.1)
        return f"Response to: {user_input}"

    async def run_examples():
        """Run all examples."""
        print("\n" + "=" * 70)
        print("SMARTROUTER DECORATOR EXAMPLES")
        print("=" * 70)

        # Example 1: Basic
        print("\n[Example 1] Basic Decorator")
        print("-" * 70)
        result = await call_llm_basic("What is Python?", user_id="user1")
        print(f"Result: {result}")
        print(f"Last Metadata: {call_llm_basic.get_last_metadata()}")

        # Example 2: Verbose
        print("\n[Example 2] Verbose Decorator")
        print("-" * 70)
        result = await call_llm_verbose("Write a sorting function", user_id="user2")
        print(f"Result: {result}")

        # Example 3: With callback
        print("\n[Example 3] With Metadata Callback")
        print("-" * 70)
        result = await call_llm_with_callback("Design an architecture", user_id="user3")
        print(f"Result: {result}")

        # Example 4: With tracking
        print("\n[Example 4] With Metadata Tracking")
        print("-" * 70)
        for i, task in enumerate(
            ["What is AI?", "Write code", "Analyze data"], 1
        ):
            print(f"\nTask {i}: {task}")
            result = await call_llm_tracked(task, user_id=f"user{i}")
        call_llm_tracked.print_summary()

        # Example 5: Access info inside function
        print("\n[Example 5] Access Routing Info Inside Function")
        print("-" * 70)
        result = await call_llm_with_info("Complex task", user_id="user5")
        print(f"Result: {result}")

        # Get stats
        print("\n[Stats] Router Statistics")
        print("-" * 70)
        stats = call_llm_tracked.get_stats()
        print(stats)

    # Run async examples
    asyncio.run(run_examples())
