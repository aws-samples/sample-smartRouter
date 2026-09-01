"""
Configuration Loader for SmartRouter
Loads tier, regex patterns, and ML sample prompts from JSON configuration files.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class ConfigLoader:
    """Loads and manages configuration files for SmartRouter."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the config loader.
        
        Args:
            config_dir: Directory containing config files. 
                       Defaults to '../config' relative to this file (parent directory).
        """
        if config_dir is None:
            # Look for config in parent directory (since config_loader moved to utils/)
            config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
        
        self.config_dir = Path(config_dir)
        self._tier_config = None
        self._regex_patterns = None
        self._ml_prompts = None

    def load_tier_config(self) -> Dict[str, Any]:
        """
        Load tier configuration (models, costs, latencies).
        
        Returns:
            Dictionary with tier configurations
        """
        if self._tier_config is not None:
            return self._tier_config
        
        config_file = self.config_dir / "tier_config.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Tier config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            self._tier_config = json.load(f)
        
        return self._tier_config

    def load_regex_patterns(self) -> Dict[str, List[str]]:
        """
        Load regex patterns for classification.
        
        Returns:
            Dictionary with category names as keys and lists of regex patterns as values
        """
        if self._regex_patterns is not None:
            return self._regex_patterns
        
        config_file = self.config_dir / "regex_patterns.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Regex patterns file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        # Extract just the patterns dictionary
        self._regex_patterns = data.get("classification_patterns", {})
        
        return self._regex_patterns

    def load_ml_sample_prompts(self) -> Dict[str, List[str]]:
        """
        Load sample prompts for ML classifier training/tuning.
        
        Returns:
            Dictionary with category names as keys and lists of sample prompts as values
        """
        if self._ml_prompts is not None:
            return self._ml_prompts
        
        config_file = self.config_dir / "ml_sample_prompts.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"ML sample prompts file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            self._ml_prompts = json.load(f)
        
        return self._ml_prompts

    def get_all_configs(self) -> Dict[str, Any]:
        """
        Load all configurations at once.
        
        Returns:
            Dictionary with 'tier_config', 'regex_patterns', and 'ml_prompts'
        """
        return {
            "tier_config": self.load_tier_config(),
            "regex_patterns": self.load_regex_patterns(),
            "ml_prompts": self.load_ml_sample_prompts()
        }

    @staticmethod
    def get_category_names(regex_patterns: Dict[str, List[str]]) -> List[str]:
        """
        Extract all category names from regex patterns.
        
        Args:
            regex_patterns: Dictionary of regex patterns by category
            
        Returns:
            List of category names
        """
        return list(regex_patterns.keys())

    @staticmethod
    def validate_tier_config(tier_config: Dict[str, Any]) -> bool:
        """
        Validate tier configuration structure.
        
        Args:
            tier_config: Tier configuration dictionary
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        required_fields = {
            "tiers": dict,
            "complexity_thresholds": dict,
            "category_complexity_scores": dict
        }
        
        for field, field_type in required_fields.items():
            if field not in tier_config:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(tier_config[field], field_type):
                raise ValueError(f"Field {field} must be {field_type.__name__}")
        
        # Validate tier structure
        tiers = tier_config["tiers"]
        for tier_name, tier_info in tiers.items():
            required_tier_fields = {
                "models": list,
                "cost_per_1k_tokens": (int, float),
                "max_tokens": int,
                "avg_latency_ms": int
            }
            
            for field, field_type in required_tier_fields.items():
                if field not in tier_info:
                    raise ValueError(f"Missing tier field: {tier_name}.{field}")
                if not isinstance(tier_info[field], field_type):
                    raise ValueError(f"Tier field {field} must be {field_type}")
        
        return True

    @staticmethod
    def validate_regex_patterns(patterns: Dict[str, List[str]]) -> bool:
        """
        Validate regex patterns structure.
        
        Args:
            patterns: Dictionary of regex patterns by category
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        import re
        
        if not isinstance(patterns, dict):
            raise ValueError("Patterns must be a dictionary")
        
        for category, pattern_list in patterns.items():
            if not isinstance(pattern_list, list):
                raise ValueError(f"Patterns for {category} must be a list")
            
            for i, pattern in enumerate(pattern_list):
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise ValueError(
                        f"Invalid regex pattern in {category}[{i}]: {pattern}\n{e}"
                    )
        
        return True

    @staticmethod
    def validate_ml_prompts(prompts: Dict[str, List[str]]) -> bool:
        """
        Validate ML sample prompts structure.
        
        Args:
            prompts: Dictionary of sample prompts by category
            
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not isinstance(prompts, dict):
            raise ValueError("Prompts must be a dictionary")
        
        for category, prompt_list in prompts.items():
            if not isinstance(prompt_list, list):
                raise ValueError(f"Prompts for {category} must be a list")
            
            if not prompt_list:
                raise ValueError(f"No prompts defined for category: {category}")
            
            for i, prompt in enumerate(prompt_list):
                if not isinstance(prompt, str):
                    raise ValueError(
                        f"Prompt {i} in {category} must be a string"
                    )
                if len(prompt.strip()) == 0:
                    raise ValueError(
                        f"Prompt {i} in {category} is empty"
                    )
        
        return True


class TierConfigManager:
    """Manages tier configuration and provides convenience methods."""

    def __init__(self, tier_config: Dict[str, Any]):
        """
        Initialize tier config manager.
        
        Args:
            tier_config: Tier configuration dictionary
        """
        ConfigLoader.validate_tier_config(tier_config)
        self.config = tier_config
        self.tiers = tier_config["tiers"]
        self.thresholds = tier_config["complexity_thresholds"]
        self.category_scores = tier_config["category_complexity_scores"]

    def get_tier_names(self) -> List[str]:
        """Get all tier names."""
        return list(self.tiers.keys())

    def get_tier_info(self, tier_name: str) -> Dict[str, Any]:
        """Get information for a specific tier."""
        if tier_name not in self.tiers:
            raise ValueError(f"Unknown tier: {tier_name}")
        return self.tiers[tier_name]

    def get_model_for_tier(self, tier_name: str) -> str:
        """Get first model for a tier."""
        return self.get_tier_info(tier_name)["models"][0]

    def get_complexity_threshold(self, threshold_name: str) -> float:
        """Get a complexity threshold value."""
        if threshold_name not in self.thresholds:
            raise ValueError(f"Unknown threshold: {threshold_name}")
        return self.thresholds[threshold_name]

    def get_category_complexity_score(self, category: str) -> float:
        """Get complexity score for a category."""
        if category not in self.category_scores:
            raise ValueError(f"Unknown category: {category}")
        return self.category_scores[category]

    def get_cost_per_1k_tokens(self, tier_name: str) -> float:
        """Get cost per 1000 tokens for a tier."""
        return self.get_tier_info(tier_name)["cost_per_1k_tokens"]

    def get_avg_latency_ms(self, tier_name: str) -> int:
        """Get average latency in milliseconds for a tier."""
        return self.get_tier_info(tier_name)["avg_latency_ms"]

    def get_max_tokens(self, tier_name: str) -> int:
        """Get max tokens for a tier."""
        return self.get_tier_info(tier_name)["max_tokens"]


if __name__ == "__main__":
    # Example usage
    loader = ConfigLoader()
    
    print("Loading all configurations...")
    configs = loader.get_all_configs()
    
    print("\n✅ Tier Configuration Loaded")
    tier_config = configs["tier_config"]
    print(f"   Tiers: {list(tier_config['tiers'].keys())}")
    
    print("\n✅ Regex Patterns Loaded")
    patterns = configs["regex_patterns"]
    for category, patterns_list in patterns.items():
        print(f"   {category}: {len(patterns_list)} patterns")
    
    print("\n✅ ML Sample Prompts Loaded")
    prompts = configs["ml_prompts"]
    for category, prompt_list in prompts.items():
        print(f"   {category}: {len(prompt_list)} prompts")
    
    print("\n✅ All configurations validated successfully!")
    
    # Demonstrate TierConfigManager
    print("\n📊 Tier Configuration Manager Demo:")
    tier_mgr = TierConfigManager(tier_config)
    print(f"   Available tiers: {tier_mgr.get_tier_names()}")
    print(f"   Fast tier model: {tier_mgr.get_model_for_tier('fast')}")
    print(f"   Balanced tier cost: ${tier_mgr.get_cost_per_1k_tokens('balanced'):.4f} per 1K tokens")
    print(f"   Powerful tier max tokens: {tier_mgr.get_max_tokens('powerful')}")
