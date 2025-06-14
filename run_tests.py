#!/usr/bin/env python3
"""
Comprehensive Test Runner for AI-to-Human Converter
Runs backend (pytest) and frontend (Jest) tests
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.backend_dir = Path("backend")
        self.frontend_dir = Path("frontend")
        self.results = {
            "backend": {"passed": 0, "failed": 0, "errors": []},
            "frontend": {"passed": 0, "failed": 0, "errors": []},
            "total_time": 0
        }
    
    def run_backend_tests(self):
        """Run backend pytest tests"""
        print("🧪 Running Backend Tests (pytest)...")
        print("=" * 50)
        
        if not self.backend_dir.exists():
            print("❌ Backend directory not found!")
            return False
        
        try:
            # Change to backend directory
            os.chdir(self.backend_dir)
            
            # Run pytest with coverage
            cmd = [
                sys.executable, "-m", "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--cov=.",
                "--cov-report=html",
                "--cov-report=term-missing"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = time.time()
            
            # Parse results
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "passed" in line and "failed" in line:
                    # Extract test counts
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            self.results["backend"]["passed"] = int(parts[i-1])
                        elif part == "failed":
                            self.results["backend"]["failed"] = int(parts[i-1])
            
            if result.returncode == 0:
                print("✅ Backend tests completed successfully!")
                print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            else:
                print("❌ Backend tests failed!")
                print("Error output:")
                print(result.stderr)
                self.results["backend"]["errors"].append(result.stderr)
            
            # Go back to root directory
            os.chdir("..")
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running backend tests: {e}")
            self.results["backend"]["errors"].append(str(e))
            os.chdir("..")
            return False
    
    def run_frontend_tests(self):
        """Run frontend Jest tests"""
        print("\n🧪 Running Frontend Tests (Jest)...")
        print("=" * 50)
        
        if not self.frontend_dir.exists():
            print("❌ Frontend directory not found!")
            return False
        
        try:
            # Change to frontend directory
            os.chdir(self.frontend_dir)
            
            # Check if node_modules exists
            if not Path("node_modules").exists():
                print("📦 Installing frontend dependencies...")
                subprocess.run(["npm", "install"], check=True)
            
            # Run Jest tests
            cmd = ["npm", "test", "--", "--passWithNoTests", "--watchAll=false"]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True)
            end_time = time.time()
            
            # Parse Jest results
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "Tests:" in line and "passed" in line:
                    # Extract test counts
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed":
                            self.results["frontend"]["passed"] = int(parts[i-1])
                        elif part == "failed":
                            self.results["frontend"]["failed"] = int(parts[i-1])
            
            if result.returncode == 0:
                print("✅ Frontend tests completed successfully!")
                print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
            else:
                print("❌ Frontend tests failed!")
                print("Error output:")
                print(result.stderr)
                self.results["frontend"]["errors"].append(result.stderr)
            
            # Go back to root directory
            os.chdir("..")
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running frontend tests: {e}")
            self.results["frontend"]["errors"].append(str(e))
            os.chdir("..")
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("\n🔗 Running Integration Tests...")
        print("=" * 50)
        
        try:
            # Test backend API endpoints
            import requests
            import time
            
            # Start backend server (if not running)
            print("🚀 Starting backend server...")
            backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"
            ], cwd=self.backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Test health endpoint
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=10)
                if response.status_code == 200:
                    print("✅ Health check passed")
                else:
                    print(f"❌ Health check failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Health check error: {e}")
            
            # Test conversion endpoint
            try:
                test_data = {
                    "text": "The implementation of artificial intelligence technologies has revolutionized various industries.",
                    "tone": "balanced"
                }
                response = requests.post("http://127.0.0.1:8000/api/convert", json=test_data, timeout=30)
                if response.status_code == 200:
                    print("✅ Conversion endpoint test passed")
                else:
                    print(f"❌ Conversion endpoint test failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Conversion endpoint error: {e}")
            
            # Stop backend server
            backend_process.terminate()
            backend_process.wait()
            
        except Exception as e:
            print(f"❌ Integration test error: {e}")
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("\n⚡ Running Performance Tests...")
        print("=" * 50)
        
        try:
            import requests
            import time
            import statistics
            
            # Test response time
            test_text = "The implementation of artificial intelligence technologies has revolutionized various industries."
            times = []
            
            for i in range(5):
                start_time = time.time()
                try:
                    response = requests.post("http://127.0.0.1:8000/api/convert", 
                                          json={"text": test_text, "tone": "balanced"}, 
                                          timeout=30)
                    end_time = time.time()
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                        print(f"Test {i+1}: {end_time - start_time:.2f}s")
                except Exception as e:
                    print(f"Test {i+1}: Error - {e}")
            
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                print(f"\n📊 Performance Results:")
                print(f"Average response time: {avg_time:.2f}s")
                print(f"Maximum response time: {max_time:.2f}s")
                
                if avg_time < 2.0:
                    print("✅ Performance target met (< 2s)")
                else:
                    print("⚠️  Performance target not met (> 2s)")
            
        except Exception as e:
            print(f"❌ Performance test error: {e}")
    
    def generate_report(self):
        """Generate test report"""
        print("\n📋 Test Report")
        print("=" * 50)
        
        total_passed = self.results["backend"]["passed"] + self.results["frontend"]["passed"]
        total_failed = self.results["backend"]["failed"] + self.results["frontend"]["failed"]
        
        print(f"Backend Tests:")
        print(f"  ✅ Passed: {self.results['backend']['passed']}")
        print(f"  ❌ Failed: {self.results['backend']['failed']}")
        
        print(f"\nFrontend Tests:")
        print(f"  ✅ Passed: {self.results['frontend']['passed']}")
        print(f"  ❌ Failed: {self.results['frontend']['failed']}")
        
        print(f"\nTotal:")
        print(f"  ✅ Passed: {total_passed}")
        print(f"  ❌ Failed: {total_failed}")
        print(f"  ⏱️  Total Time: {self.results['total_time']:.2f}s")
        
        # Save report to file
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "summary": {
                "total_passed": total_passed,
                "total_failed": total_failed,
                "success_rate": total_passed / (total_passed + total_failed) if (total_passed + total_failed) > 0 else 0
            }
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Report saved to: test_report.json")
        
        return total_failed == 0
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run backend tests
        backend_success = self.run_backend_tests()
        
        # Run frontend tests
        frontend_success = self.run_frontend_tests()
        
        # Run integration tests (optional)
        if backend_success:
            self.run_integration_tests()
            self.run_performance_tests()
        
        end_time = time.time()
        self.results["total_time"] = end_time - start_time
        
        # Generate report
        all_passed = self.generate_report()
        
        if all_passed:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print("\n💥 Some tests failed!")
            return 1

def main():
    """Main function"""
    runner = TestRunner()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "backend":
            success = runner.run_backend_tests()
            return 0 if success else 1
        elif test_type == "frontend":
            success = runner.run_frontend_tests()
            return 0 if success else 1
        elif test_type == "integration":
            runner.run_integration_tests()
            return 0
        elif test_type == "performance":
            runner.run_performance_tests()
            return 0
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: backend, frontend, integration, performance, all")
            return 1
    
    # Run all tests by default
    return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main()) 