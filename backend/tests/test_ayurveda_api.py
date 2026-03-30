"""
Ayur Vaidya API Tests
Tests for categories, medicines, practitioners, and related endpoints
"""
import pytest
import requests
import os

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api")
        assert response.status_code == 200
        print(f"✓ Health check passed: {response.json()}")


class TestCategories:
    """Tests for illness categories API"""
    
    def test_get_all_categories(self):
        """Test GET /api/categories returns 20 categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 20, f"Expected 20 categories, got {len(data)}"
        
        # Verify category structure
        if data:
            category = data[0]
            assert "category_id" in category
            assert "name" in category
            assert "description" in category
        
        print(f"✓ Categories API returned {len(data)} categories")
        return data
    
    def test_categories_include_new_types(self):
        """Test that categories include hair, eyes, heart, kidney, women's, men's, children's, weight, bp, cholesterol"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        category_ids = [c.get("category_id", "").lower() for c in data]
        category_names = [c.get("name", "").lower() for c in data]
        
        # Check for expected categories
        expected_categories = ["hair", "eyes", "heart", "kidney", "women", "men", "children", "weight", "bp", "cholesterol"]
        
        for expected in expected_categories:
            found = any(expected in cid or expected in cname for cid, cname in zip(category_ids, category_names))
            assert found, f"Expected category containing '{expected}' not found"
            print(f"✓ Found category for: {expected}")


class TestMedicines:
    """Tests for medicines API"""
    
    def test_get_all_medicines(self):
        """Test GET /api/medicines returns 76 medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 76, f"Expected 76 medicines, got {len(data)}"
        
        # Verify medicine structure
        if data:
            medicine = data[0]
            assert "medicine_id" in medicine
            assert "name" in medicine
            assert "description" in medicine
            assert "illness_categories" in medicine
        
        print(f"✓ Medicines API returned {len(data)} medicines")
        return data
    
    def test_medicines_by_category_hair(self):
        """Test GET /api/medicines?category=hair returns hair medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines?category=hair")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one hair medicine"
        
        # Verify all returned medicines have hair category
        for med in data:
            assert "hair" in med.get("illness_categories", []), f"Medicine {med.get('name')} doesn't have hair category"
        
        print(f"✓ Hair medicines: {len(data)} found")
    
    def test_medicines_by_category_heart(self):
        """Test GET /api/medicines?category=heart returns heart medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines?category=heart")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one heart medicine"
        
        print(f"✓ Heart medicines: {len(data)} found")
    
    def test_medicines_by_category_eyes(self):
        """Test GET /api/medicines?category=eyes returns eye care medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines?category=eyes")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one eye care medicine"
        
        print(f"✓ Eye care medicines: {len(data)} found")
    
    def test_medicines_by_category_women(self):
        """Test GET /api/medicines?category=women returns women's health medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines?category=women")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one women's health medicine"
        
        print(f"✓ Women's health medicines: {len(data)} found")
    
    def test_medicines_by_category_bp(self):
        """Test GET /api/medicines?category=bp returns blood pressure medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines?category=bp")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one blood pressure medicine"
        
        print(f"✓ Blood pressure medicines: {len(data)} found")
    
    def test_medicines_by_category_cholesterol(self):
        """Test GET /api/medicines?category=cholesterol returns cholesterol medicines"""
        response = requests.get(f"{BASE_URL}/api/medicines?category=cholesterol")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one cholesterol medicine"
        
        print(f"✓ Cholesterol medicines: {len(data)} found")


class TestPractitioners:
    """Tests for practitioners API"""
    
    def test_get_all_practitioners(self):
        """Test GET /api/practitioners returns 16 practitioners"""
        response = requests.get(f"{BASE_URL}/api/practitioners")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 16, f"Expected 16 practitioners, got {len(data)}"
        
        # Verify practitioner structure
        if data:
            practitioner = data[0]
            assert "practitioner_id" in practitioner
            assert "name" in practitioner
            assert "city" in practitioner
        
        print(f"✓ Practitioners API returned {len(data)} practitioners")
        return data
    
    def test_get_practitioner_cities(self):
        """Test GET /api/practitioners/cities includes all expected cities"""
        response = requests.get(f"{BASE_URL}/api/practitioners/cities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Check for Sri Lanka cities
        sri_lanka_cities = ["Colombo", "Kandy", "Galle", "Jaffna"]
        for city in sri_lanka_cities:
            assert city in data, f"Expected Sri Lanka city '{city}' not found in cities list"
            print(f"✓ Found Sri Lanka city: {city}")
        
        # Check for new India cities
        india_cities = ["Pune", "Ahmedabad", "Kolkata", "Lucknow"]
        for city in india_cities:
            assert city in data, f"Expected India city '{city}' not found in cities list"
            print(f"✓ Found India city: {city}")
        
        print(f"✓ Cities API returned {len(data)} cities")
        return data
    
    def test_practitioners_by_city_colombo(self):
        """Test GET /api/practitioners?city=Colombo returns Sri Lankan practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Colombo")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Colombo"
        
        # Verify the practitioner is from Colombo
        for practitioner in data:
            assert "Colombo" in practitioner.get("city", ""), f"Practitioner city mismatch"
        
        print(f"✓ Colombo practitioners: {len(data)} found")
    
    def test_practitioners_by_city_kandy(self):
        """Test GET /api/practitioners?city=Kandy returns Sri Lankan practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Kandy")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Kandy"
        
        print(f"✓ Kandy practitioners: {len(data)} found")
    
    def test_practitioners_by_city_galle(self):
        """Test GET /api/practitioners?city=Galle returns Sri Lankan practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Galle")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Galle"
        
        print(f"✓ Galle practitioners: {len(data)} found")
    
    def test_practitioners_by_city_jaffna(self):
        """Test GET /api/practitioners?city=Jaffna returns Sri Lankan practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Jaffna")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Jaffna"
        
        print(f"✓ Jaffna practitioners: {len(data)} found")
    
    def test_practitioners_by_city_pune(self):
        """Test GET /api/practitioners?city=Pune returns Indian practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Pune")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Pune"
        
        print(f"✓ Pune practitioners: {len(data)} found")
    
    def test_practitioners_by_city_ahmedabad(self):
        """Test GET /api/practitioners?city=Ahmedabad returns Indian practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Ahmedabad")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Ahmedabad"
        
        print(f"✓ Ahmedabad practitioners: {len(data)} found")
    
    def test_practitioners_by_city_kolkata(self):
        """Test GET /api/practitioners?city=Kolkata returns Indian practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Kolkata")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Kolkata"
        
        print(f"✓ Kolkata practitioners: {len(data)} found")
    
    def test_practitioners_by_city_lucknow(self):
        """Test GET /api/practitioners?city=Lucknow returns Indian practitioner"""
        response = requests.get(f"{BASE_URL}/api/practitioners?city=Lucknow")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one practitioner in Lucknow"
        
        print(f"✓ Lucknow practitioners: {len(data)} found")


class TestSymptoms:
    """Tests for symptoms API"""
    
    def test_get_all_symptoms(self):
        """Test GET /api/symptoms returns symptoms list"""
        response = requests.get(f"{BASE_URL}/api/symptoms")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least some symptoms"
        
        print(f"✓ Symptoms API returned {len(data)} symptoms")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
