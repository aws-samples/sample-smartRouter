"""
GZip-kNN Classifier for Task Classification
A parameter-free text classification method using Normalized Compression Distance (NCD)
and k-Nearest Neighbors voting.

Based on the theoretical foundation:
NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))

Where C(x) is the compressed size of string x using gzip.
"""

import gzip
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import Counter


@dataclass
class ClassificationResult:
    """Result from GZip-kNN classification."""
    category: str
    confidence: float
    nearest_examples: List[Tuple[float, str, str]]


class GZipKNNClassifier:
    """
    Parameter-free text classifier using GZip compression distance.
    
    Suitable as a standalone classifier or as a component in a
    hybrid classification system for smart routing.
    """

    def __init__(self, k: int = 5, compresslevel: int = 6):
        """
        Initialize the GZip-kNN classifier.
        
        Args:
            k: Number of nearest neighbors to use for voting
            compresslevel: Compression level for gzip (1-9, default 6)
        """
        self.k = k
        self.compresslevel = compresslevel
        self.training_set: List[Tuple[str, str]] = []
        self._compressed_cache: Dict[int, int] = {}

    def add_examples(self, examples: List[Tuple[str, str]]):
        """
        Add labeled examples to the training set.
        
        Args:
            examples: List of (text, label) tuples
        """
        self.training_set.extend(examples)
        
        # Pre-compress examples for faster lookup
        for text, _ in examples:
            key = hash(text)
            if key not in self._compressed_cache:
                self._compressed_cache[key] = len(
                    gzip.compress(text.encode('utf-8'), self.compresslevel)
                )

    def _ncd(self, x: str, y: str) -> float:
        """
        Calculate Normalized Compression Distance between two strings.
        
        NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        
        Args:
            x: First string
            y: Second string
            
        Returns:
            NCD value between 0 and ~1
        """
        x_bytes = x.encode('utf-8')
        y_bytes = y.encode('utf-8')
        xy_bytes = x_bytes + b" " + y_bytes

        Cx = len(gzip.compress(x_bytes, self.compresslevel))
        Cy = len(gzip.compress(y_bytes, self.compresslevel))
        Cxy = len(gzip.compress(xy_bytes, self.compresslevel))

        return (Cxy - min(Cx, Cy)) / max(Cx, Cy) if max(Cx, Cy) > 0 else 0.0

    def classify(self, query: str) -> ClassificationResult:
        """
        Classify a query using compression-based k-NN.
        
        Args:
            query: Input text to classify
            
        Returns:
            ClassificationResult with category, confidence, and nearest examples
        """
        if not self.training_set:
            return ClassificationResult(
                category="unknown",
                confidence=0.0,
                nearest_examples=[]
            )

        query_bytes = query.encode('utf-8')
        Cx = len(gzip.compress(query_bytes, self.compresslevel))

        distances = []
        
        for sample_text, label in self.training_set:
            # Get cached compression or compute it
            Cy = self._compressed_cache.get(
                hash(sample_text),
                len(gzip.compress(
                    sample_text.encode('utf-8'),
                    self.compresslevel
                ))
            )

            xy_bytes = query_bytes + b" " + sample_text.encode('utf-8')
            Cxy = len(gzip.compress(xy_bytes, self.compresslevel))

            distance = (Cxy - min(Cx, Cy)) / max(Cx, Cy) if max(Cx, Cy) > 0 else 0.0
            distances.append((distance, sample_text, label))

        # Sort by distance (closest first)
        distances.sort(key=lambda x: x[0])
        top_k = distances[:self.k]

        # Majority vote with distance weighting
        weighted_votes: Dict[str, float] = {}
        
        for dist, text, label in top_k:
            # Weight is inverse of distance (closer = higher weight)
            weight = 1.0 / (dist + 1e-8)
            weighted_votes[label] = weighted_votes.get(label, 0.0) + weight

        total_weight = sum(weighted_votes.values())
        best_label = max(weighted_votes, key=weighted_votes.get)
        confidence = weighted_votes[best_label] / total_weight if total_weight > 0 else 0.0

        return ClassificationResult(
            category=best_label,
            confidence=confidence,
            nearest_examples=top_k
        )

    def classify_scores(self, query: str) -> Dict[str, float]:
        """
        Classify and return scores for all categories.
        
        Args:
            query: Input text to classify
            
        Returns:
            Dictionary mapping categories to their normalized scores
        """
        result = self.classify(query)
        
        # Calculate category scores from weighted votes
        query_bytes = query.encode('utf-8')
        Cx = len(gzip.compress(query_bytes, self.compresslevel))
        
        weighted_votes: Dict[str, float] = {}
        
        for sample_text, label in self.training_set:
            Cy = self._compressed_cache.get(
                hash(sample_text),
                len(gzip.compress(
                    sample_text.encode('utf-8'),
                    self.compresslevel
                ))
            )
            
            xy_bytes = query_bytes + b" " + sample_text.encode('utf-8')
            Cxy = len(gzip.compress(xy_bytes, self.compresslevel))
            
            distance = (Cxy - min(Cx, Cy)) / max(Cx, Cy) if max(Cx, Cy) > 0 else 0.0
            
            # Only consider top-k
            if len([d for d in self.training_set if d[1] == label]) > 0:
                weight = 1.0 / (distance + 1e-8)
                weighted_votes[label] = weighted_votes.get(label, 0.0) + weight

        # Normalize scores
        total_weight = sum(weighted_votes.values())
        if total_weight > 0:
            return {k: v / total_weight for k, v in weighted_votes.items()}
        
        return {result.category: 1.0}

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the classifier."""
        category_counts = Counter(label for _, label in self.training_set)
        
        return {
            "total_examples": len(self.training_set),
            "categories": dict(category_counts),
            "k": self.k,
            "compresslevel": self.compresslevel,
            "cache_size": len(self._compressed_cache)
        }


class AdaptiveHybridClassifier:
    """
    Enhanced hybrid classifier combining rule-based, GZip-kNN, and optional ML.
    Dynamically adjusts weights based on classifier availability.
    """

    def __init__(
        self,
        rule_classifier,
        gzip_classifier: GZipKNNClassifier,
        ml_classifier: Optional[Any] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize adaptive hybrid classifier.
        
        Args:
            rule_classifier: Rule-based classifier instance
            gzip_classifier: GZip-kNN classifier instance
            ml_classifier: Optional ML classifier instance
            weights: Optional custom weights for classifiers
        """
        self.rule_classifier = rule_classifier
        self.gzip_classifier = gzip_classifier
        self.ml_classifier = ml_classifier
        
        self.default_weights = weights or {
            'rule': 0.35,
            'gzip': 0.35,
            'ml': 0.30 if ml_classifier else 0.0
        }
        
        self.confidence_threshold = 0.6

    def _get_active_weights(self, ml_available: bool) -> Dict[str, float]:
        """
        Get weights based on classifier availability.
        
        Args:
            ml_available: Whether ML classifier is available
            
        Returns:
            Dictionary of weights for each classifier
        """
        if ml_available and self.ml_classifier:
            return self.default_weights.copy()
        else:
            # GZip absorbs ML weight during cold start
            base_weight = 1.0 - self.default_weights.get('rule', 0.35)
            return {
                'rule': self.default_weights.get('rule', 0.35),
                'gzip': base_weight,
                'ml': 0.0
            }

    async def classify(
        self,
        user_input: str,
        ml_available: bool = True,
        return_details: bool = False
    ) -> Dict[str, Any]:
        """
        Classify using weighted combination of all available classifiers.
        
        Args:
            user_input: Text to classify
            ml_available: Whether to use ML classifier
            return_details: Whether to return detailed results
            
        Returns:
            Dictionary with classification results and optional details
        """
        weights = self._get_active_weights(ml_available and self.ml_classifier is not None)
        
        combined_scores: Dict[str, float] = {}
        classifier_results = {}
        
        # Rule-based classification
        rule_scores = self.rule_classifier.classify(user_input)
        if rule_scores:
            classifier_results['rule'] = rule_scores
            for category, score in rule_scores.items():
                combined_scores[category] = combined_scores.get(category, 0.0) + weights['rule'] * score
        
        # GZip-kNN classification
        gzip_scores = self.gzip_classifier.classify_scores(user_input)
        if gzip_scores:
            classifier_results['gzip'] = gzip_scores
            for category, score in gzip_scores.items():
                combined_scores[category] = combined_scores.get(category, 0.0) + weights['gzip'] * score
        
        # Optional ML classification
        if ml_available and self.ml_classifier:
            try:
                ml_result = await self.ml_classifier.classify(user_input)
                if ml_result:
                    # Convert ML result to scores
                    ml_scores = {ml_result['category']: ml_result.get('confidence', 0.5)}
                    classifier_results['ml'] = ml_scores
                    for category, score in ml_scores.items():
                        combined_scores[category] = combined_scores.get(category, 0.0) + weights['ml'] * score
            except Exception as e:
                # ML classifier failed, continue without it
                pass
        
        # Normalize combined scores
        total_score = sum(combined_scores.values())
        if total_score > 0:
            normalized_scores = {k: v / total_score for k, v in combined_scores.items()}
        else:
            normalized_scores = {}
        
        # Determine best category
        if normalized_scores:
            best_category = max(normalized_scores, key=normalized_scores.get)
            confidence = normalized_scores[best_category]
        else:
            best_category = 'balanced'
            confidence = 0.5
        
        result = {
            'category': best_category,
            'confidence': confidence,
            'scores': normalized_scores,
            'method': 'adaptive_hybrid'
        }
        
        if return_details:
            result['details'] = {
                'classifier_results': classifier_results,
                'weights': weights
            }
        
        return result


if __name__ == "__main__":
    # Example usage
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from utils.config_loader import ConfigLoader
    
    # Load sample prompts from config
    loader = ConfigLoader()
    sample_prompts = loader.load_ml_sample_prompts()
    
    # Create classifier
    gzip_clf = GZipKNNClassifier(k=5)
    
    # Convert sample prompts to training examples
    training_examples = []
    for category, prompts in sample_prompts.items():
        for prompt in prompts:
            training_examples.append((prompt, category))
    
    # Add examples
    gzip_clf.add_examples(training_examples)
    
    print("✅ GZip-kNN Classifier Demo")
    print("=" * 70)
    
    # Print stats
    stats = gzip_clf.get_stats()
    print(f"\n📊 Classifier Statistics:")
    print(f"   Total Examples: {stats['total_examples']}")
    print(f"   Categories: {stats['categories']}")
    print(f"   k-Nearest Neighbors: {stats['k']}")
    print(f"   Cached Compressions: {stats['cache_size']}")
    
    # Test classifications
    test_queries = [
        "What is machine learning?",
        "Write a Python function for sorting",
        "Design a microservices architecture",
        "Summarize this research paper",
        "Write a marketing campaign",
        "Analyze customer data trends",
    ]
    
    print(f"\n🧪 Testing Classifications:")
    print("-" * 70)
    
    for query in test_queries:
        result = gzip_clf.classify(query)
        scores = gzip_clf.classify_scores(query)
        
        print(f"\nQuery: {query[:50]}...")
        print(f"  Category: {result.category}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Top Scores: {dict(sorted(scores.items(), key=lambda x: -x[1])[:3])}")
        print(f"  Nearest Examples: {[(d, l) for d, _, l in result.nearest_examples[:2]]}")
