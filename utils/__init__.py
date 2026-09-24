"""
SmartRouter Utilities Package

Contains utility modules for SmartRouter:
- config_loader: Configuration management
- gzip_knn_classifier: Compression-based text classification
- benchmark_ml_classifier: Performance benchmarking utilities
"""

from .config_loader import ConfigLoader, TierConfigManager
from .gzip_knn_classifier import GZipKNNClassifier, AdaptiveHybridClassifier, ClassificationResult

__all__ = [
    'ConfigLoader',
    'TierConfigManager',
    'GZipKNNClassifier',
    'AdaptiveHybridClassifier',
    'ClassificationResult',
]

