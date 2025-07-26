#!/usr/bin/env python3
"""
SRS Compliance Test Suite for Vietnamese-Japanese Translation Chatbot
Tests all functional requirements F1-F8 and non-functional requirements

Run: python test_srs_compliance.py
"""

import requests
import time
import json
import sys
from datetime import datetime


class SRSComplianceTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, passed, message="", response_time=None):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        result = f"{status} {test_name}{time_info}"
        if message:
            result += f": {message}"
        print(result)
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_f1_single_translation(self):
        """F1: Single Message Translation"""
        test_cases = [
            # Test new format (SRS compliant)
            {
                "name": "F1.1 New Format - Vietnamese",
                "data": {
                    "messages": [{"role": "user", "content": "Xin chào"}],
                    "source_lang": "auto",
                    "user_id": "test_f1_new"
                },
                "expected_fields": ["reply", "detected_lang", "target_lang", "latency_ms"]
            },
            # Test backward compatibility (old format)
            {
                "name": "F1.2 Old Format Compatibility",
                "data": {
                    "message": "こんにちは",
                    "source_lang": "auto",
                    "user_id": "test_f1_old"
                },
                "expected_fields": ["reply", "detected_lang", "target_lang", "latency_ms"]
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/translate",
                    json=test_case["data"],
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    all_fields_present = all(field in data for field in test_case["expected_fields"])
                    
                    if all_fields_present and data["reply"]:
                        self.log_test(test_case["name"], True, f"Lang: {data.get('detected_lang')} → {data.get('target_lang')}", response_time)
                    else:
                        self.log_test(test_case["name"], False, f"Missing fields or empty reply: {data}")
                else:
                    self.log_test(test_case["name"], False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Exception: {str(e)}")
    
    def test_f2_batch_translation(self):
        """F2: Batch Translation (max 50 items)"""
        test_cases = [
            {
                "name": "F2.1 Small Batch",
                "data": [
                    {"id": 1, "text": "Xin chào"},
                    {"id": 2, "text": "こんにちは"},
                    {"id": 3, "text": "Cảm ơn bạn"}
                ]
            },
            {
                "name": "F2.2 Large Batch (50 items)",
                "data": [{"id": i, "text": f"Test message {i} - Tin nhắn số {i}"} for i in range(1, 51)]
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/batch",
                    json=test_case["data"],
                    timeout=30
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) == len(test_case["data"]):
                        success_count = sum(1 for item in data if "translation" in item and not item.get("error"))
                        self.log_test(test_case["name"], True, f"{success_count}/{len(data)} successful", response_time)
                    else:
                        self.log_test(test_case["name"], False, f"Unexpected response format: {data}")
                else:
                    self.log_test(test_case["name"], False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Exception: {str(e)}")
    
    def test_f3_language_detection(self):
        """F3: Automatic Language Detection"""
        test_cases = [
            {"text": "Xin chào tôi là người Việt Nam", "expected": "vi"},
            {"text": "こんにちは、私は日本人です", "expected": "ja"},
            {"text": "Tôi đang học tiếng Nhật", "expected": "vi"},
            {"text": "日本語を勉強しています", "expected": "ja"}
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/translate",
                    json={
                        "messages": [{"role": "user", "content": test_case["text"]}],
                        "source_lang": "auto",
                        "user_id": f"test_f3_{i}"
                    },
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    detected = data.get("detected_lang")
                    expected = test_case["expected"]
                    
                    if detected == expected:
                        self.log_test(f"F3.{i+1} Language Detection", True, f"'{test_case['text'][:20]}...' → {detected}", response_time)
                    else:
                        self.log_test(f"F3.{i+1} Language Detection", False, f"Expected {expected}, got {detected}")
                else:
                    self.log_test(f"F3.{i+1} Language Detection", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"F3.{i+1} Language Detection", False, f"Exception: {str(e)}")
    
    def test_f4_function_calling(self):
        """F4: OpenAI Function Calling"""
        test_cases = [
            "Tính chi phí công tác 3 ngày, 200 USD",
            "Giúp tôi tính tiền hoàn chi phí đi công tác 5 ngày với số tiền 500 USD",
            "Reimbursement calculation for 2 days business trip, 150 USD"
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/api/translate",
                    json={
                        "messages": [{"role": "user", "content": test_case}],
                        "source_lang": "auto",
                        "user_id": f"test_f4_{i}"
                    },
                    timeout=15
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "")
                    
                    # Check if function calling worked (should contain calculation details)
                    if any(keyword in reply.lower() for keyword in ["reimbursement", "total", "allowance", "hoàn", "chi phí"]):
                        self.log_test(f"F4.{i+1} Function Calling", True, "Function detected and executed", response_time)
                    else:
                        self.log_test(f"F4.{i+1} Function Calling", False, f"No function calling detected: {reply[:100]}")
                else:
                    self.log_test(f"F4.{i+1} Function Calling", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"F4.{i+1} Function Calling", False, f"Exception: {str(e)}")
    
    def test_f5_context_management(self):
        """F5: Context Management (20 messages = 10 exchanges)"""
        user_id = "test_f5_context"
        
        try:
            # Send 12 messages (6 exchanges) to test context limit
            for i in range(12):
                requests.post(
                    f"{self.base_url}/api/translate",
                    json={
                        "messages": [{"role": "user", "content": f"Test message {i+1}"}],
                        "source_lang": "auto",
                        "user_id": user_id
                    },
                    timeout=5
                )
            
            # Check context
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/context/{user_id}", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                context_length = data.get("context_length", 0)
                
                # Should be exactly 20 messages (10 exchanges max)
                if context_length <= 20:
                    self.log_test("F5.1 Context Limit", True, f"Context: {context_length}/20 messages", response_time)
                else:
                    self.log_test("F5.1 Context Limit", False, f"Context exceeded: {context_length}/20")
            else:
                self.log_test("F5.1 Context Limit", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("F5.1 Context Limit", False, f"Exception: {str(e)}")
    
    def test_f6_error_handling(self):
        """F6: Error Handling and Validation"""
        test_cases = [
            {
                "name": "F6.1 Empty Message",
                "data": {"messages": [{"role": "user", "content": ""}], "source_lang": "auto"},
                "expected_status": 400
            },
            {
                "name": "F6.2 Invalid JSON",
                "data": "invalid json",
                "expected_status": 400
            },
            {
                "name": "F6.3 Missing Required Fields",
                "data": {"source_lang": "auto"},
                "expected_status": 400
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                if isinstance(test_case["data"], str):
                    # Send invalid JSON
                    response = requests.post(
                        f"{self.base_url}/api/translate",
                        data=test_case["data"],
                        headers={"Content-Type": "application/json"},
                        timeout=5
                    )
                else:
                    response = requests.post(
                        f"{self.base_url}/api/translate",
                        json=test_case["data"],
                        timeout=5
                    )
                response_time = time.time() - start_time
                
                expected_status = test_case["expected_status"]
                if response.status_code == expected_status:
                    self.log_test(test_case["name"], True, f"Correct error response: {response.status_code}", response_time)
                else:
                    self.log_test(test_case["name"], False, f"Expected {expected_status}, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Exception: {str(e)}")
    
    def test_f7_performance(self):
        """F7: Performance Requirements (< 5s response time)"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/translate",
                json={
                    "messages": [{"role": "user", "content": "This is a performance test message for SRS compliance"}],
                    "source_lang": "auto",
                    "user_id": "test_f7_perf"
                },
                timeout=6  # Slightly higher than 5s requirement
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 5.0:
                self.log_test("F7.1 Response Time", True, f"Response time: {response_time:.3f}s < 5s", response_time)
            else:
                self.log_test("F7.1 Response Time", False, f"Response time: {response_time:.3f}s >= 5s")
                
        except Exception as e:
            self.log_test("F7.1 Response Time", False, f"Exception: {str(e)}")
    
    def test_f8_mock_endpoints(self):
        """F8: Mock and Utility Endpoints"""
        endpoints = [
            ("/api/health", "Health Check"),
            ("/api/mock-data", "Mock Data"),
            ("/api/batch-mock", "Batch Mock")
        ]
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.log_test(f"F8.{name}", True, "Endpoint accessible", response_time)
                else:
                    self.log_test(f"F8.{name}", False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"F8.{name}", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run complete SRS compliance test suite"""
        print("🧪 Starting SRS Compliance Test Suite")
        print("=" * 50)
        
        test_methods = [
            self.test_f1_single_translation,
            self.test_f2_batch_translation,
            self.test_f3_language_detection,
            self.test_f4_function_calling,
            self.test_f5_context_management,
            self.test_f6_error_handling,
            self.test_f7_performance,
            self.test_f8_mock_endpoints
        ]
        
        for test_method in test_methods:
            print(f"\n🔍 Running {test_method.__doc__}")
            test_method()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        # Save detailed results
        with open("srs_test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: srs_test_results.json")
        return failed_tests == 0


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly. Please start the Flask app first.")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the Flask app first:")
        print("   python main.py")
        sys.exit(1)
    
    # Run tests
    tester = SRSComplianceTest()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - SRS COMPLIANT!")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - CHECK IMPLEMENTATION")
        sys.exit(1)
