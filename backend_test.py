#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Ayur Vaidya App
Tests all endpoints including auth, categories, medicines, symptoms, and health check
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class AyurVaidyaAPITester:
    def __init__(self, base_url: str = "https://wellness-vaid.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = None
        self.test_user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []
        
        print(f"🧪 Testing Ayur Vaidya API at: {base_url}")
        print("=" * 60)

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test results"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {name}")
        if details:
            print(f"     {details}")
        
        if success:
            self.tests_passed += 1
            self.passed_tests.append(name)
        else:
            self.failed_tests.append({"test": name, "details": details})

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200, use_auth: bool = False) -> tuple[bool, Dict]:
        """Make HTTP request and validate response"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if use_auth and self.session_token:
            headers['Authorization'] = f'Bearer {self.session_token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text, "status_code": response.status_code}
            
            if not success:
                print(f"     Expected {expected_status}, got {response.status_code}")
                if response.text:
                    print(f"     Response: {response.text[:200]}")
            
            return success, response_data
            
        except requests.exceptions.RequestException as e:
            print(f"     Request failed: {str(e)}")
            return False, {"error": str(e)}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.make_request('GET', 'health')
        
        if success and 'status' in response:
            self.log_test("Health Check", True, f"Status: {response.get('status')}")
            return True
        else:
            self.log_test("Health Check", False, "Health endpoint not responding correctly")
            return False

    def create_test_session(self):
        """Create a test user and session for authenticated endpoints"""
        print("\n🔐 Setting up test authentication...")
        
        # For testing, we'll create a mock session token
        # In real scenario, this would come from Google OAuth flow
        timestamp = int(time.time())
        self.session_token = f"test_session_{timestamp}"
        self.test_user_id = f"test_user_{timestamp}"
        
        print(f"Created test session: {self.session_token}")
        print(f"Test user ID: {self.test_user_id}")
        return True

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test /auth/me without token (should fail)
        success, response = self.make_request('GET', 'auth/me', expected_status=401)
        self.log_test("Auth Me (No Token)", success, "Correctly returns 401 without token")
        
        # Test /auth/me with invalid token (should fail)
        old_token = self.session_token
        self.session_token = "invalid_token"
        success, response = self.make_request('GET', 'auth/me', expected_status=401, use_auth=True)
        self.log_test("Auth Me (Invalid Token)", success, "Correctly returns 401 with invalid token")
        self.session_token = old_token
        
        # Test logout endpoint
        success, response = self.make_request('POST', 'auth/logout')
        self.log_test("Logout Endpoint", success, "Logout endpoint accessible")

    def test_categories_api(self):
        """Test categories endpoints"""
        print("\n📂 Testing Categories API...")
        
        # Test get all categories
        success, response = self.make_request('GET', 'categories')
        
        if success:
            categories = response if isinstance(response, list) else []
            category_count = len(categories)
            self.log_test("Get All Categories", True, f"Retrieved {category_count} categories")
            
            # Test specific category if categories exist
            if categories:
                first_category = categories[0]
                category_id = first_category.get('category_id')
                
                if category_id:
                    success, response = self.make_request('GET', f'categories/{category_id}')
                    if success and 'category' in response:
                        medicines_count = len(response.get('medicines', []))
                        self.log_test("Get Category Detail", True, f"Category has {medicines_count} medicines")
                    else:
                        self.log_test("Get Category Detail", False, "Category detail not found")
                else:
                    self.log_test("Get Category Detail", False, "No category_id found")
            else:
                self.log_test("Get Category Detail", False, "No categories available to test")
        else:
            self.log_test("Get All Categories", False, "Failed to retrieve categories")

    def test_medicines_api(self):
        """Test medicines endpoints"""
        print("\n💊 Testing Medicines API...")
        
        # Test get all medicines
        success, response = self.make_request('GET', 'medicines')
        
        if success:
            medicines = response if isinstance(response, list) else []
            medicine_count = len(medicines)
            self.log_test("Get All Medicines", True, f"Retrieved {medicine_count} medicines")
            
            # Test medicine search
            success, response = self.make_request('GET', 'medicines?search=tulsi')
            if success:
                search_results = response if isinstance(response, list) else []
                self.log_test("Medicine Search", True, f"Search returned {len(search_results)} results")
            else:
                self.log_test("Medicine Search", False, "Medicine search failed")
            
            # Test category filter
            success, response = self.make_request('GET', 'medicines?category=respiratory')
            if success:
                filtered_results = response if isinstance(response, list) else []
                self.log_test("Medicine Category Filter", True, f"Category filter returned {len(filtered_results)} results")
            else:
                self.log_test("Medicine Category Filter", False, "Category filter failed")
            
            # Test specific medicine if medicines exist
            if medicines:
                first_medicine = medicines[0]
                medicine_id = first_medicine.get('medicine_id')
                
                if medicine_id:
                    success, response = self.make_request('GET', f'medicines/{medicine_id}')
                    if success and 'name' in response:
                        self.log_test("Get Medicine Detail", True, f"Retrieved medicine: {response.get('name')}")
                    else:
                        self.log_test("Get Medicine Detail", False, "Medicine detail not found")
                else:
                    self.log_test("Get Medicine Detail", False, "No medicine_id found")
            else:
                self.log_test("Get Medicine Detail", False, "No medicines available to test")
        else:
            self.log_test("Get All Medicines", False, "Failed to retrieve medicines")

    def test_symptoms_api(self):
        """Test symptoms and symptom checker endpoints"""
        print("\n🩺 Testing Symptoms API...")
        
        # Test get all symptoms
        success, response = self.make_request('GET', 'symptoms')
        
        if success:
            symptoms = response if isinstance(response, list) else []
            symptom_count = len(symptoms)
            self.log_test("Get All Symptoms", True, f"Retrieved {symptom_count} symptoms")
            
            # Test symptom checker if symptoms exist
            if symptoms:
                # Use first few symptoms for testing
                test_symptoms = symptoms[:3] if len(symptoms) >= 3 else symptoms
                
                success, response = self.make_request('POST', 'symptom-check', 
                                                    data={"symptoms": test_symptoms})
                if success and 'medicines' in response:
                    recommended_count = len(response.get('medicines', []))
                    message = response.get('message', '')
                    self.log_test("Symptom Check", True, f"Found {recommended_count} recommendations: {message}")
                else:
                    self.log_test("Symptom Check", False, "Symptom check failed")
                
                # Test empty symptoms
                success, response = self.make_request('POST', 'symptom-check', 
                                                    data={"symptoms": []})
                if success:
                    self.log_test("Symptom Check (Empty)", True, "Handles empty symptoms correctly")
                else:
                    self.log_test("Symptom Check (Empty)", False, "Failed to handle empty symptoms")
            else:
                self.log_test("Symptom Check", False, "No symptoms available to test")
        else:
            self.log_test("Get All Symptoms", False, "Failed to retrieve symptoms")

    def test_seed_endpoint(self):
        """Test database seeding endpoint"""
        print("\n🌱 Testing Seed Endpoint...")
        
        success, response = self.make_request('POST', 'seed')
        
        if success and 'message' in response:
            categories_count = response.get('categories_count', 0)
            medicines_count = response.get('medicines_count', 0)
            self.log_test("Database Seed", True, 
                         f"Seeded {categories_count} categories and {medicines_count} medicines")
        else:
            self.log_test("Database Seed", False, "Seed endpoint failed")

    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n⚠️  Testing Error Handling...")
        
        # Test non-existent medicine
        success, response = self.make_request('GET', 'medicines/non-existent-id', expected_status=404)
        self.log_test("Non-existent Medicine", success, "Correctly returns 404 for invalid medicine ID")
        
        # Test non-existent category
        success, response = self.make_request('GET', 'categories/non-existent-id', expected_status=404)
        self.log_test("Non-existent Category", success, "Correctly returns 404 for invalid category ID")
        
        # Test invalid symptom check data
        success, response = self.make_request('POST', 'symptom-check', 
                                            data={"invalid": "data"}, expected_status=422)
        self.log_test("Invalid Symptom Check Data", success, "Correctly validates symptom check input")

    def run_all_tests(self):
        """Run all test suites"""
        start_time = time.time()
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - API may be down")
            return False
        
        # Setup test session
        self.create_test_session()
        
        # Run test suites
        self.test_auth_endpoints()
        self.test_seed_endpoint()  # Seed first to ensure data exists
        self.test_categories_api()
        self.test_medicines_api()
        self.test_symptoms_api()
        self.test_error_handling()
        
        # Print summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"Duration: {duration}s")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"  • {failure['test']}: {failure['details']}")
        
        if self.passed_tests:
            print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
            for test in self.passed_tests:
                print(f"  • {test}")
        
        return len(self.failed_tests) == 0

def main():
    """Main test execution"""
    print("🚀 Starting Ayur Vaidya Backend API Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tester = AyurVaidyaAPITester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())