"""
Comprehensive Benchmarking Suite for ML Classifier
Tests both accuracy and speed of the GZip-kNN classifier
using synthetic test data.
"""

import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
from utils.gzip_knn_classifier import GZipKNNClassifier
from utils.config_loader import ConfigLoader


class MLClassifierBenchmark:
    """Comprehensive benchmarking suite for ML classifier."""

    def __init__(self, samples_dir: str = "samples"):
        """
        Initialize benchmark suite.
        
        Args:
            samples_dir: Directory containing training and test data
        """
        self.samples_dir = Path(samples_dir)
        self.training_data = self._load_json("training_examples.json")
        self.test_data = self._load_json("synthetic_test_data.json")
        
        self.results = {
            "accuracy": {},
            "speed": {},
            "per_category": {}
        }

    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from samples directory."""
        file_path = self.samples_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r') as f:
            return json.load(f)

    def _create_classifier(self, k: int = 5) -> GZipKNNClassifier:
        """Create and initialize classifier with training data."""
        classifier = GZipKNNClassifier(k=k)
        
        # Add training examples
        training_examples = []
        for category, examples in self.training_data.items():
            for example in examples:
                training_examples.append((example, category))
        
        classifier.add_examples(training_examples)
        return classifier

    def benchmark_accuracy(self) -> Dict[str, Any]:
        """
        Benchmark classification accuracy.
        
        Returns:
            Dictionary with accuracy metrics
        """
        print("\n" + "=" * 80)
        print("ACCURACY BENCHMARK")
        print("=" * 80)
        
        classifier = self._create_classifier(k=5)
        
        total_tests = 0
        correct_predictions = 0
        per_category_results = defaultdict(lambda: {"correct": 0, "total": 0})
        
        print("\n📊 Testing across all categories:")
        print("-" * 80)
        
        for category, test_cases in self.test_data.items():
            category_correct = 0
            category_total = len(test_cases)
            
            for test_case in test_cases:
                text = test_case["text"]
                difficulty = test_case["difficulty"]
                
                result = classifier.classify(text)
                predicted_category = result.category
                
                total_tests += 1
                per_category_results[category]["total"] += 1
                
                if predicted_category == category:
                    correct_predictions += 1
                    category_correct += 1
                    per_category_results[category]["correct"] += 1
            
            accuracy = (category_correct / category_total) * 100 if category_total > 0 else 0
            print(f"  {category:.<25} {category_correct:2d}/{category_total:2d} ({accuracy:6.2f}%)")
        
        overall_accuracy = (correct_predictions / total_tests) * 100 if total_tests > 0 else 0
        
        print("-" * 80)
        print(f"  {'OVERALL':.<25} {correct_predictions:2d}/{total_tests:2d} ({overall_accuracy:6.2f}%)")
        
        # Calculate accuracy by difficulty
        difficulty_results = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for category, test_cases in self.test_data.items():
            for test_case in test_cases:
                text = test_case["text"]
                difficulty = test_case["difficulty"]
                
                result = classifier.classify(text)
                difficulty_results[difficulty]["total"] += 1
                
                if result.category == category:
                    difficulty_results[difficulty]["correct"] += 1
        
        print("\n📈 Accuracy by Difficulty Level:")
        print("-" * 80)
        for difficulty in ["easy", "medium", "hard"]:
            if difficulty in difficulty_results:
                correct = difficulty_results[difficulty]["correct"]
                total = difficulty_results[difficulty]["total"]
                acc = (correct / total) * 100 if total > 0 else 0
                print(f"  {difficulty:.<25} {correct:2d}/{total:2d} ({acc:6.2f}%)")
        
        return {
            "overall_accuracy": overall_accuracy,
            "total_correct": correct_predictions,
            "total_tests": total_tests,
            "per_category": dict(per_category_results),
            "by_difficulty": dict(difficulty_results)
        }

    def benchmark_speed(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark classification speed.
        
        Args:
            iterations: Number of iterations per test
            
        Returns:
            Dictionary with speed metrics
        """
        print("\n" + "=" * 80)
        print("SPEED BENCHMARK")
        print("=" * 80)
        
        classifier = self._create_classifier(k=5)
        
        # Flatten test data
        all_tests = []
        for category, test_cases in self.test_data.items():
            for test_case in test_cases:
                all_tests.append((test_case["text"], category))
        
        print(f"\n⏱️  Measuring latency ({iterations} iterations):")
        print("-" * 80)
        
        # Measure total time for all tests
        start_time = time.time()
        
        for _ in range(iterations):
            for text, _ in all_tests:
                classifier.classify(text)
        
        total_time = time.time() - start_time
        total_classifications = len(all_tests) * iterations
        avg_time_ms = (total_time / total_classifications) * 1000
        
        print(f"  Total classifications: {total_classifications}")
        print(f"  Total time: {total_time:.3f} seconds")
        print(f"  Average latency: {avg_time_ms:.3f} ms")
        print(f"  Classifications per second: {total_classifications / total_time:.0f}")
        
        # Per-category speed
        print("\n📊 Speed by Category:")
        print("-" * 80)
        
        category_times = defaultdict(list)
        
        for category, test_cases in self.test_data.items():
            category_tests = [tc["text"] for tc in test_cases]
            
            start_time = time.time()
            
            for _ in range(iterations):
                for text in category_tests:
                    classifier.classify(text)
            
            elapsed = time.time() - start_time
            total_count = len(category_tests) * iterations
            avg_ms = (elapsed / total_count) * 1000
            
            print(f"  {category:.<25} {avg_ms:.3f} ms/classification")
            category_times[category].append(avg_ms)
        
        # Speed scaling with k parameter
        print("\n📈 Scaling with k-Nearest Neighbors:")
        print("-" * 80)
        
        test_text = all_tests[0][0]
        scaling_results = {}
        
        for k in [3, 5, 7, 10, 15]:
            clf = self._create_classifier(k=k)
            
            start_time = time.time()
            
            for _ in range(100):
                clf.classify(test_text)
            
            elapsed = time.time() - start_time
            avg_ms = (elapsed / 100) * 1000
            scaling_results[k] = avg_ms
            
            print(f"  k={k:2d}: {avg_ms:.3f} ms")
        
        return {
            "average_latency_ms": avg_time_ms,
            "total_classifications": total_classifications,
            "total_time_seconds": total_time,
            "classifications_per_second": total_classifications / total_time,
            "per_category": dict(category_times),
            "scaling_by_k": scaling_results
        }

    def benchmark_k_parameter(self) -> Dict[str, Any]:
        """
        Benchmark accuracy vs speed trade-off with different k values.
        
        Returns:
            Dictionary with k-parameter analysis
        """
        print("\n" + "=" * 80)
        print("K-PARAMETER ANALYSIS (Accuracy vs Speed)")
        print("=" * 80)
        
        print("\n🔬 Testing k values: 3, 5, 7, 10")
        print("-" * 80)
        
        results = {}
        
        for k in [3, 5, 7, 10]:
            classifier = self._create_classifier(k=k)
            
            # Accuracy
            correct = 0
            total = 0
            
            for category, test_cases in self.test_data.items():
                for test_case in test_cases:
                    result = classifier.classify(test_case["text"])
                    total += 1
                    if result.category == category:
                        correct += 1
            
            accuracy = (correct / total) * 100 if total > 0 else 0
            
            # Speed
            all_tests = []
            for category, test_cases in self.test_data.items():
                for test_case in test_cases:
                    all_tests.append(test_case["text"])
            
            start_time = time.time()
            for _ in range(50):
                for text in all_tests:
                    classifier.classify(text)
            
            elapsed = time.time() - start_time
            avg_latency_ms = (elapsed / (len(all_tests) * 50)) * 1000
            
            results[k] = {
                "accuracy": accuracy,
                "latency_ms": avg_latency_ms,
                "correct": correct,
                "total": total
            }
            
            print(f"  k={k:2d}: Accuracy={accuracy:6.2f}%, Latency={avg_latency_ms:.3f}ms")
        
        return results

    def benchmark_training_size(self) -> Dict[str, Any]:
        """
        Benchmark the effect of training set size on accuracy and speed.
        
        Returns:
            Dictionary with training size analysis
        """
        print("\n" + "=" * 80)
        print("TRAINING SIZE ANALYSIS")
        print("=" * 80)
        
        print("\n📊 Testing with reduced training sets:")
        print("-" * 80)
        
        # Create training sets of different sizes
        training_samples = []
        for category, examples in self.training_data.items():
            for example in examples:
                training_samples.append((example, category))
        
        results = {}
        sizes = [5, 10, 20, 30, len(training_samples)]
        
        for size in sizes:
            reduced_samples = training_samples[:size]
            
            classifier = GZipKNNClassifier(k=5)
            classifier.add_examples(reduced_samples)
            
            # Test accuracy
            correct = 0
            total = 0
            
            for category, test_cases in self.test_data.items():
                for test_case in test_cases:
                    result = classifier.classify(test_case["text"])
                    total += 1
                    if result.category == category:
                        correct += 1
            
            accuracy = (correct / total) * 100 if total > 0 else 0
            
            # Test speed
            all_tests = []
            for category, test_cases in self.test_data.items():
                for test_case in test_cases:
                    all_tests.append(test_case["text"])
            
            start_time = time.time()
            for text in all_tests:
                classifier.classify(text)
            
            elapsed = time.time() - start_time
            avg_latency_ms = (elapsed / len(all_tests)) * 1000
            
            results[size] = {
                "accuracy": accuracy,
                "latency_ms": avg_latency_ms,
                "correct": correct
            }
            
            print(f"  {size:3d} examples: Accuracy={accuracy:6.2f}%, Latency={avg_latency_ms:.3f}ms")
        
        return results

    def run_full_benchmark(self) -> Dict[str, Any]:
        """
        Run complete benchmark suite.
        
        Returns:
            Dictionary with all benchmark results
        """
        print("\n" + "╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "ML CLASSIFIER COMPREHENSIVE BENCHMARK" + " " * 22 + "║")
        print("╚" + "=" * 78 + "╝")
        
        all_results = {}
        
        # Run all benchmarks
        all_results["accuracy"] = self.benchmark_accuracy()
        all_results["speed"] = self.benchmark_speed(iterations=50)
        all_results["k_analysis"] = self.benchmark_k_parameter()
        all_results["training_size"] = self.benchmark_training_size()
        
        # Print summary
        self._print_summary(all_results)
        
        return all_results

    def _print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary."""
        print("\n" + "=" * 80)
        print("BENCHMARK SUMMARY")
        print("=" * 80)
        
        print("\n✅ Accuracy Metrics:")
        print(f"   Overall Accuracy: {results['accuracy']['overall_accuracy']:.2f}%")
        print(f"   Total Tests Passed: {results['accuracy']['total_correct']}/{results['accuracy']['total_tests']}")
        
        print("\n⏱️  Speed Metrics:")
        print(f"   Average Latency: {results['speed']['average_latency_ms']:.3f} ms")
        print(f"   Classifications/Second: {results['speed']['classifications_per_second']:.0f}")
        
        print("\n📊 Best k-Parameter:")
        k_results = results['k_analysis']
        best_k = max(k_results.keys(), key=lambda k: k_results[k]['accuracy'])
        print(f"   k={best_k}: {k_results[best_k]['accuracy']:.2f}% accuracy, {k_results[best_k]['latency_ms']:.3f}ms latency")
        
        print("\n💾 Training Size Impact:")
        train_results = results['training_size']
        best_size = max(train_results.keys(), key=lambda s: train_results[s]['accuracy'])
        print(f"   Optimal size: {best_size} examples")
        print(f"   Accuracy: {train_results[best_size]['accuracy']:.2f}%")
        
        print("\n" + "=" * 80)


def main():
    """Run benchmark suite."""
    try:
        benchmark = MLClassifierBenchmark(samples_dir="samples")
        results = benchmark.run_full_benchmark()
        
        # Save results to file
        output_file = Path("samples/benchmark_results.json")
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Benchmark results saved to: {output_file}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please ensure samples/training_examples.json and samples/synthetic_test_data.json exist")


if __name__ == "__main__":
    main()
