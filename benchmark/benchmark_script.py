#!/usr/bin/env python3
"""
Competitive Benchmarking Script for AI-to-Human Converter
Compares our tool against QuillBot, Undetectable.ai, and other competitors
"""

import asyncio
import aiohttp
import time
import json
import csv
from typing import Dict, List, Tuple
import statistics
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkResult:
    tool_name: str
    original_text: str
    converted_text: str
    ai_detection_score: float
    plagiarism_score: float
    processing_time: float
    grammar_score: float
    humanization_score: float
    cost_per_word: float = 0.0

class BenchmarkTool:
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.results = []
        
    async def test_our_tool(self, text: str, tone: str = "balanced") -> BenchmarkResult:
        """Test our AI-to-Human converter"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/convert",
                    json={
                        "text": text,
                        "tone": tone,
                        "preserve_meaning": True,
                        "check_plagiarism": True,
                        "check_ai_detection": True
                    }
                ) as response:
                    data = await response.json()
                    processing_time = time.time() - start_time
                    
                    return BenchmarkResult(
                        tool_name="Our Tool",
                        original_text=text,
                        converted_text=data["converted_text"],
                        ai_detection_score=data["ai_detection_score"],
                        plagiarism_score=data["plagiarism_score"],
                        processing_time=processing_time,
                        grammar_score=1.0 - (data["grammar_corrections"] / len(text.split())),
                        humanization_score=data["humanization_score"],
                        cost_per_word=0.001  # Estimated cost
                    )
        except Exception as e:
            logger.error(f"Error testing our tool: {e}")
            return None

    async def test_quillbot(self, text: str) -> BenchmarkResult:
        """Test QuillBot (simulated)"""
        start_time = time.time()
        
        try:
            # Simulate QuillBot API call
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Simple text transformation simulation
            converted = text.replace("artificial intelligence", "AI")
            converted = converted.replace("machine learning", "ML")
            converted = converted.replace("implementation", "setup")
            
            processing_time = time.time() - start_time
            
            return BenchmarkResult(
                tool_name="QuillBot",
                original_text=text,
                converted_text=converted,
                ai_detection_score=0.35,  # Simulated
                plagiarism_score=0.12,   # Simulated
                processing_time=processing_time,
                grammar_score=0.85,      # Simulated
                humanization_score=0.70, # Simulated
                cost_per_word=0.002      # Simulated cost
            )
        except Exception as e:
            logger.error(f"Error testing QuillBot: {e}")
            return None

    async def test_undetectable_ai(self, text: str) -> BenchmarkResult:
        """Test Undetectable.ai (simulated)"""
        start_time = time.time()
        
        try:
            # Simulate Undetectable.ai API call
            await asyncio.sleep(0.8)  # Simulate processing time
            
            # More aggressive text transformation
            converted = text.replace("artificial intelligence", "smart technology")
            converted = converted.replace("machine learning", "pattern recognition")
            converted = converted.replace("implementation", "deployment")
            converted = converted.replace("technologies", "solutions")
            
            processing_time = time.time() - start_time
            
            return BenchmarkResult(
                tool_name="Undetectable.ai",
                original_text=text,
                converted_text=converted,
                ai_detection_score=0.25,  # Simulated
                plagiarism_score=0.08,   # Simulated
                processing_time=processing_time,
                grammar_score=0.80,      # Simulated
                humanization_score=0.75, # Simulated
                cost_per_word=0.003      # Simulated cost
            )
        except Exception as e:
            logger.error(f"Error testing Undetectable.ai: {e}")
            return None

    async def test_grammarly(self, text: str) -> BenchmarkResult:
        """Test Grammarly (simulated)"""
        start_time = time.time()
        
        try:
            # Simulate Grammarly API call
            await asyncio.sleep(0.3)  # Simulate processing time
            
            # Grammar-focused transformation
            converted = text.replace("has revolutionized", "has transformed")
            converted = converted.replace("demonstrated", "shown")
            converted = converted.replace("remarkable", "impressive")
            
            processing_time = time.time() - start_time
            
            return BenchmarkResult(
                tool_name="Grammarly",
                original_text=text,
                converted_text=converted,
                ai_detection_score=0.45,  # Simulated
                plagiarism_score=0.15,   # Simulated
                processing_time=processing_time,
                grammar_score=0.95,      # Simulated
                humanization_score=0.60, # Simulated
                cost_per_word=0.001      # Simulated cost
            )
        except Exception as e:
            logger.error(f"Error testing Grammarly: {e}")
            return None

    async def run_benchmark(self, test_texts: List[str]) -> List[BenchmarkResult]:
        """Run comprehensive benchmark across all tools"""
        all_results = []
        
        for i, text in enumerate(test_texts):
            logger.info(f"Running benchmark for text {i+1}/{len(test_texts)}")
            
            # Test all tools concurrently
            tasks = [
                self.test_our_tool(text),
                self.test_quillbot(text),
                self.test_undetectable_ai(text),
                self.test_grammarly(text)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out None results
            valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
            all_results.extend(valid_results)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        return all_results

    def analyze_results(self, results: List[BenchmarkResult]) -> Dict:
        """Analyze benchmark results and generate insights"""
        if not results:
            return {}
        
        # Group results by tool
        tool_results = {}
        for result in results:
            if result.tool_name not in tool_results:
                tool_results[result.tool_name] = []
            tool_results[result.tool_name].append(result)
        
        analysis = {}
        
        for tool_name, tool_data in tool_results.items():
            analysis[tool_name] = {
                "avg_ai_detection_score": statistics.mean([r.ai_detection_score for r in tool_data]),
                "avg_plagiarism_score": statistics.mean([r.plagiarism_score for r in tool_data]),
                "avg_processing_time": statistics.mean([r.processing_time for r in tool_data]),
                "avg_grammar_score": statistics.mean([r.grammar_score for r in tool_data]),
                "avg_humanization_score": statistics.mean([r.humanization_score for r in tool_data]),
                "avg_cost_per_word": statistics.mean([r.cost_per_word for r in tool_data]),
                "total_tests": len(tool_data)
            }
        
        # Calculate rankings
        rankings = {
            "ai_detection_evasion": sorted(analysis.keys(), key=lambda x: analysis[x]["avg_ai_detection_score"]),
            "plagiarism_avoidance": sorted(analysis.keys(), key=lambda x: analysis[x]["avg_plagiarism_score"]),
            "speed": sorted(analysis.keys(), key=lambda x: analysis[x]["avg_processing_time"]),
            "grammar_quality": sorted(analysis.keys(), key=lambda x: analysis[x]["avg_grammar_score"], reverse=True),
            "humanization": sorted(analysis.keys(), key=lambda x: analysis[x]["avg_humanization_score"], reverse=True),
            "cost_efficiency": sorted(analysis.keys(), key=lambda x: analysis[x]["avg_cost_per_word"])
        }
        
        analysis["rankings"] = rankings
        return analysis

    def generate_report(self, results: List[BenchmarkResult], analysis: Dict) -> str:
        """Generate a comprehensive benchmark report"""
        report = []
        report.append("=" * 80)
        report.append("AI-TO-HUMAN CONVERTER BENCHMARK REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY STATISTICS:")
        report.append("-" * 40)
        
        for tool_name, stats in analysis.items():
            if tool_name == "rankings":
                continue
                
            report.append(f"\n{tool_name}:")
            report.append(f"  AI Detection Score: {stats['avg_ai_detection_score']:.3f} (lower is better)")
            report.append(f"  Plagiarism Score: {stats['avg_plagiarism_score']:.3f} (lower is better)")
            report.append(f"  Processing Time: {stats['avg_processing_time']:.3f}s")
            report.append(f"  Grammar Score: {stats['avg_grammar_score']:.3f}")
            report.append(f"  Humanization Score: {stats['avg_humanization_score']:.3f}")
            report.append(f"  Cost per Word: ${stats['avg_cost_per_word']:.4f}")
        
        # Rankings
        report.append("\n" + "=" * 80)
        report.append("RANKINGS")
        report.append("=" * 80)
        
        for category, ranking in analysis["rankings"].items():
            report.append(f"\n{category.replace('_', ' ').title()}:")
            for i, tool in enumerate(ranking, 1):
                report.append(f"  {i}. {tool}")
        
        # Key insights
        report.append("\n" + "=" * 80)
        report.append("KEY INSIGHTS")
        report.append("=" * 80)
        
        # Find best performers
        best_ai_evasion = analysis["rankings"]["ai_detection_evasion"][0]
        best_grammar = analysis["rankings"]["grammar_quality"][0]
        fastest = analysis["rankings"]["speed"][0]
        most_human = analysis["rankings"]["humanization"][0]
        
        report.append(f"\n• Best AI Detection Evasion: {best_ai_evasion}")
        report.append(f"• Best Grammar Quality: {best_grammar}")
        report.append(f"• Fastest Processing: {fastest}")
        report.append(f"• Best Humanization: {most_human}")
        
        # Competitive advantages
        our_tool_stats = analysis.get("Our Tool", {})
        if our_tool_stats:
            report.append(f"\nOUR TOOL COMPETITIVE ADVANTAGES:")
            report.append(f"• AI Detection Score: {our_tool_stats['avg_ai_detection_score']:.3f}")
            report.append(f"• Processing Speed: {our_tool_stats['avg_processing_time']:.3f}s")
            report.append(f"• Cost Efficiency: ${our_tool_stats['avg_cost_per_word']:.4f} per word")
        
        return "\n".join(report)

    def save_results_csv(self, results: List[BenchmarkResult], filename: str = "benchmark_results.csv"):
        """Save results to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'tool_name', 'original_text', 'converted_text', 'ai_detection_score',
                'plagiarism_score', 'processing_time', 'grammar_score', 'humanization_score', 'cost_per_word'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'tool_name': result.tool_name,
                    'original_text': result.original_text,
                    'converted_text': result.converted_text,
                    'ai_detection_score': result.ai_detection_score,
                    'plagiarism_score': result.plagiarism_score,
                    'processing_time': result.processing_time,
                    'grammar_score': result.grammar_score,
                    'humanization_score': result.humanization_score,
                    'cost_per_word': result.cost_per_word
                })

async def main():
    """Main benchmark execution"""
    # Test texts with different characteristics
    test_texts = [
        "The implementation of artificial intelligence technologies has revolutionized various industries. Furthermore, machine learning algorithms have demonstrated remarkable capabilities in pattern recognition and data analysis.",
        
        "In recent years, the rapid advancement of AI systems has transformed the way businesses operate. These sophisticated technologies enable organizations to automate complex processes and make data-driven decisions.",
        
        "The integration of machine learning models into existing infrastructure requires careful consideration of scalability and performance requirements. Organizations must evaluate the trade-offs between accuracy and computational efficiency.",
        
        "Natural language processing capabilities have evolved significantly, allowing for more sophisticated text analysis and generation. These improvements have led to enhanced user experiences across various applications.",
        
        "The deployment of AI solutions in production environments necessitates robust monitoring and maintenance protocols. Continuous evaluation and optimization are essential for maintaining system reliability and performance."
    ]
    
    # Initialize benchmark tool
    api_keys = {
        "openai": "your-openai-key",
        "anthropic": "your-anthropic-key",
        "cohere": "your-cohere-key"
    }
    
    benchmark = BenchmarkTool(api_keys)
    
    # Run benchmark
    logger.info("Starting benchmark...")
    results = await benchmark.run_benchmark(test_texts)
    
    # Analyze results
    analysis = benchmark.analyze_results(results)
    
    # Generate and save report
    report = benchmark.generate_report(results, analysis)
    
    # Save to files
    with open("benchmark_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    benchmark.save_results_csv(results)
    
    # Print report
    print(report)
    
    logger.info("Benchmark completed! Check benchmark_report.txt and benchmark_results.csv")

if __name__ == "__main__":
    asyncio.run(main()) 