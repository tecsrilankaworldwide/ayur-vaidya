#!/usr/bin/env python3
"""
Extended Backend API Testing for Ayur Vaidya App - New Features
Tests booking system, reviews, favorites, and practitioners APIs
"""

import requests
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class AyurVaidyaExtendedTester:
    def __init__(self, base_url: str = "https://wellness-vaid.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = None
        self.test_user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []
        
        print(f"🧪 Testing Ayur Vaidya Extended Features at: {base_url}")
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

    def create_test_user_session(self):
        """Create a test user and session in MongoDB for authenticated endpoints"""
        print("\n🔐 Creating test user and session in database...")
        
        # Create test user and session using MongoDB
        import subprocess
        timestamp = int(time.time())
        self.test_user_id = f"test_user_{timestamp}"
        self.session_token = f"test_session_{timestamp}"
        
        mongo_script = f'''
        use('test_database');
        db.users.insertOne({{
          user_id: "{self.test_user_id}",
          email: "test.user.{timestamp}@example.com",
          name: "Test User",
          picture: "https://via.placeholder.com/150",
          created_at: new Date()
        }});
        db.user_sessions.insertOne({{
          user_id: "{self.test_user_id}",
          session_token: "{self.session_token}",
          expires_at: new Date(Date.now() + 7*24*60*60*1000),
          created_at: new Date()
        }});
        print("Test user and session created successfully");
        '''
        
        try:
            result = subprocess.run(['mongosh', '--eval', mongo_script], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ Created test user: {self.test_user_id}")
                print(f"✅ Created session token: {self.session_token}")
                return True
            else:
                print(f"❌ Failed to create test user: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ MongoDB setup failed: {str(e)}")
            return False

    def test_practitioners_api(self):
        """Test practitioners endpoints"""
        print("\n👨‍⚕️ Testing Practitioners API...")
        
        # Test get all practitioners
        success, response = self.make_request('GET', 'practitioners')
        
        if success:
            practitioners = response if isinstance(response, list) else []
            practitioner_count = len(practitioners)
            self.log_test("Get All Practitioners", True, f"Retrieved {practitioner_count} practitioners")
            
            # Test practitioner search
            success, response = self.make_request('GET', 'practitioners?search=sharma')
            if success:
                search_results = response if isinstance(response, list) else []
                self.log_test("Practitioner Search", True, f"Search returned {len(search_results)} results")
            else:
                self.log_test("Practitioner Search", False, "Practitioner search failed")
            
            # Test city filter
            success, response = self.make_request('GET', 'practitioners?city=Delhi')
            if success:
                city_results = response if isinstance(response, list) else []
                self.log_test("Practitioner City Filter", True, f"City filter returned {len(city_results)} results")
            else:
                self.log_test("Practitioner City Filter", False, "City filter failed")
            
            # Test specialization filter
            success, response = self.make_request('GET', 'practitioners?specialization=Panchakarma')
            if success:
                spec_results = response if isinstance(response, list) else []
                self.log_test("Practitioner Specialization Filter", True, f"Specialization filter returned {len(spec_results)} results")
            else:
                self.log_test("Practitioner Specialization Filter", False, "Specialization filter failed")
            
            # Test specific practitioner
            if practitioners:
                first_practitioner = practitioners[0]
                practitioner_id = first_practitioner.get('practitioner_id')
                
                if practitioner_id:
                    success, response = self.make_request('GET', f'practitioners/{practitioner_id}')
                    if success and 'name' in response:
                        self.log_test("Get Practitioner Detail", True, f"Retrieved practitioner: {response.get('name')}")
                        return practitioner_id  # Return for use in other tests
                    else:
                        self.log_test("Get Practitioner Detail", False, "Practitioner detail not found")
                else:
                    self.log_test("Get Practitioner Detail", False, "No practitioner_id found")
            else:
                self.log_test("Get Practitioner Detail", False, "No practitioners available to test")
        else:
            self.log_test("Get All Practitioners", False, "Failed to retrieve practitioners")
        
        return None

    def test_practitioner_metadata(self):
        """Test practitioner metadata endpoints"""
        print("\n🏙️ Testing Practitioner Metadata...")
        
        # Test cities endpoint
        success, response = self.make_request('GET', 'practitioners/cities')
        if success:
            cities = response if isinstance(response, list) else []
            self.log_test("Get Practitioner Cities", True, f"Retrieved {len(cities)} cities")
        else:
            self.log_test("Get Practitioner Cities", False, "Failed to retrieve cities")
        
        # Test specializations endpoint
        success, response = self.make_request('GET', 'practitioners/specializations')
        if success:
            specializations = response if isinstance(response, list) else []
            self.log_test("Get Practitioner Specializations", True, f"Retrieved {len(specializations)} specializations")
        else:
            self.log_test("Get Practitioner Specializations", False, "Failed to retrieve specializations")

    def test_booking_system(self, practitioner_id: str):
        """Test booking system endpoints"""
        print("\n📅 Testing Booking System...")
        
        if not practitioner_id:
            self.log_test("Booking System", False, "No practitioner ID available for testing")
            return None
        
        # Test get available slots
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        success, response = self.make_request('GET', f'practitioners/{practitioner_id}/slots?date={tomorrow}')
        
        if success and 'available_slots' in response:
            available_slots = response.get('available_slots', [])
            self.log_test("Get Available Slots", True, f"Found {len(available_slots)} available slots for {tomorrow}")
            
            # Test create booking (requires auth)
            if available_slots:
                booking_data = {
                    "practitioner_id": practitioner_id,
                    "date": tomorrow,
                    "time_slot": available_slots[0],
                    "reason": "Test consultation for API testing"
                }
                
                success, response = self.make_request('POST', 'bookings', data=booking_data, 
                                                    expected_status=201, use_auth=True)
                if success and 'booking' in response:
                    booking_id = response['booking']['booking_id']
                    self.log_test("Create Booking", True, f"Created booking: {booking_id}")
                    
                    # Test get user bookings
                    success, response = self.make_request('GET', 'bookings', use_auth=True)
                    if success:
                        bookings = response if isinstance(response, list) else []
                        self.log_test("Get User Bookings", True, f"Retrieved {len(bookings)} bookings")
                        
                        # Test cancel booking
                        success, response = self.make_request('DELETE', f'bookings/{booking_id}', use_auth=True)
                        if success:
                            self.log_test("Cancel Booking", True, "Successfully cancelled booking")
                            return booking_id
                        else:
                            self.log_test("Cancel Booking", False, "Failed to cancel booking")
                    else:
                        self.log_test("Get User Bookings", False, "Failed to retrieve user bookings")
                else:
                    self.log_test("Create Booking", False, "Failed to create booking")
            else:
                self.log_test("Create Booking", False, "No available slots to test booking")
        else:
            self.log_test("Get Available Slots", False, "Failed to get available slots")
        
        return None

    def test_reviews_system(self, practitioner_id: str):
        """Test reviews system endpoints"""
        print("\n⭐ Testing Reviews System...")
        
        if not practitioner_id:
            self.log_test("Reviews System", False, "No practitioner ID available for testing")
            return
        
        # Test get practitioner reviews
        success, response = self.make_request('GET', f'practitioners/{practitioner_id}/reviews')
        if success:
            reviews = response if isinstance(response, list) else []
            self.log_test("Get Practitioner Reviews", True, f"Retrieved {len(reviews)} reviews")
        else:
            self.log_test("Get Practitioner Reviews", False, "Failed to retrieve reviews")
        
        # Test create review (requires auth)
        review_data = {
            "practitioner_id": practitioner_id,
            "rating": 5,
            "comment": "Excellent consultation! Very knowledgeable about Ayurvedic treatments."
        }
        
        success, response = self.make_request('POST', 'reviews', data=review_data, use_auth=True)
        if success and 'review' in response:
            review_id = response['review']['review_id']
            self.log_test("Create Review", True, f"Created review: {review_id}")
            
            # Test duplicate review (should fail)
            success, response = self.make_request('POST', 'reviews', data=review_data, 
                                                expected_status=400, use_auth=True)
            self.log_test("Duplicate Review Prevention", success, "Correctly prevents duplicate reviews")
        else:
            self.log_test("Create Review", False, "Failed to create review")

    def test_favorites_system(self):
        """Test favorites system endpoints"""
        print("\n❤️ Testing Favorites System...")
        
        # Get a medicine and practitioner for testing
        success, medicines = self.make_request('GET', 'medicines')
        success2, practitioners = self.make_request('GET', 'practitioners')
        
        if not (success and success2 and medicines and practitioners):
            self.log_test("Favorites System", False, "No data available for testing favorites")
            return
        
        medicine_id = medicines[0]['medicine_id']
        practitioner_id = practitioners[0]['practitioner_id']
        
        # Test add medicine to favorites
        favorite_data = {"item_type": "medicine", "item_id": medicine_id}
        success, response = self.make_request('POST', 'favorites', data=favorite_data, use_auth=True)
        if success:
            self.log_test("Add Medicine to Favorites", True, "Successfully added medicine to favorites")
        else:
            self.log_test("Add Medicine to Favorites", False, "Failed to add medicine to favorites")
        
        # Test add practitioner to favorites
        favorite_data = {"item_type": "practitioner", "item_id": practitioner_id}
        success, response = self.make_request('POST', 'favorites', data=favorite_data, use_auth=True)
        if success:
            self.log_test("Add Practitioner to Favorites", True, "Successfully added practitioner to favorites")
        else:
            self.log_test("Add Practitioner to Favorites", False, "Failed to add practitioner to favorites")
        
        # Test get favorites
        success, response = self.make_request('GET', 'favorites', use_auth=True)
        if success and 'medicines' in response and 'practitioners' in response:
            medicine_favs = len(response.get('medicines', []))
            practitioner_favs = len(response.get('practitioners', []))
            self.log_test("Get Favorites", True, f"Retrieved {medicine_favs} medicine and {practitioner_favs} practitioner favorites")
        else:
            self.log_test("Get Favorites", False, "Failed to retrieve favorites")
        
        # Test check favorite status
        success, response = self.make_request('GET', f'favorites/check/medicine/{medicine_id}', use_auth=True)
        if success and 'is_favorited' in response:
            is_favorited = response.get('is_favorited')
            self.log_test("Check Favorite Status", True, f"Medicine favorite status: {is_favorited}")
        else:
            self.log_test("Check Favorite Status", False, "Failed to check favorite status")
        
        # Test remove from favorites
        success, response = self.make_request('DELETE', f'favorites/medicine/{medicine_id}', use_auth=True)
        if success:
            self.log_test("Remove Medicine from Favorites", True, "Successfully removed medicine from favorites")
        else:
            self.log_test("Remove Medicine from Favorites", False, "Failed to remove medicine from favorites")
        
        success, response = self.make_request('DELETE', f'favorites/practitioner/{practitioner_id}', use_auth=True)
        if success:
            self.log_test("Remove Practitioner from Favorites", True, "Successfully removed practitioner from favorites")
        else:
            self.log_test("Remove Practitioner from Favorites", False, "Failed to remove practitioner from favorites")

    def test_auth_protected_endpoints(self):
        """Test that protected endpoints require authentication"""
        print("\n🔒 Testing Auth Protection...")
        
        # Test bookings without auth
        success, response = self.make_request('GET', 'bookings', expected_status=401)
        self.log_test("Bookings Auth Protection", success, "Correctly requires auth for bookings")
        
        # Test favorites without auth
        success, response = self.make_request('GET', 'favorites', expected_status=401)
        self.log_test("Favorites Auth Protection", success, "Correctly requires auth for favorites")
        
        # Test reviews without auth
        review_data = {"practitioner_id": "test", "rating": 5, "comment": "test"}
        success, response = self.make_request('POST', 'reviews', data=review_data, expected_status=401)
        self.log_test("Reviews Auth Protection", success, "Correctly requires auth for reviews")

    def cleanup_test_data(self):
        """Clean up test data from database"""
        print("\n🧹 Cleaning up test data...")
        
        import subprocess
        mongo_script = f'''
        use('test_database');
        db.users.deleteMany({{user_id: "{self.test_user_id}"}});
        db.user_sessions.deleteMany({{user_id: "{self.test_user_id}"}});
        db.bookings.deleteMany({{user_id: "{self.test_user_id}"}});
        db.reviews.deleteMany({{user_id: "{self.test_user_id}"}});
        db.favorites.deleteMany({{user_id: "{self.test_user_id}"}});
        print("Test data cleaned up");
        '''
        
        try:
            subprocess.run(['mongosh', '--eval', mongo_script], 
                          capture_output=True, text=True, timeout=30)
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        start_time = time.time()
        
        # Setup test user and session
        if not self.create_test_user_session():
            print("❌ Failed to create test user - skipping auth tests")
            return False
        
        # Test auth protection first
        self.test_auth_protected_endpoints()
        
        # Test practitioners API
        practitioner_id = self.test_practitioners_api()
        self.test_practitioner_metadata()
        
        # Test new features with auth
        if practitioner_id:
            self.test_booking_system(practitioner_id)
            self.test_reviews_system(practitioner_id)
        
        self.test_favorites_system()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print summary
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        print("\n" + "=" * 60)
        print("📊 EXTENDED TEST SUMMARY")
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
    print("🚀 Starting Ayur Vaidya Extended Backend Tests")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tester = AyurVaidyaExtendedTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())