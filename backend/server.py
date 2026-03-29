from fastapi import FastAPI, APIRouter, HTTPException, Response, Request, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== MODELS ====================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionRequest(BaseModel):
    session_id: str


class Medicine(BaseModel):
    model_config = ConfigDict(extra="ignore")
    medicine_id: str
    name: str
    sanskrit_name: Optional[str] = None
    description: str
    usage: str
    dosage: str
    ingredients: List[str]
    precautions: List[str]
    contraindications: List[str]
    preparation_method: Optional[str] = None
    image_url: Optional[str] = None
    illness_categories: List[str]
    symptoms: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IllnessCategory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    category_id: str
    name: str
    description: str
    icon: str
    image_url: Optional[str] = None


class SymptomCheckRequest(BaseModel):
    symptoms: List[str]


class Practitioner(BaseModel):
    model_config = ConfigDict(extra="ignore")
    practitioner_id: str
    name: str
    title: str
    specializations: List[str]
    experience_years: int
    qualifications: List[str]
    clinic_name: str
    address: str
    city: str
    state: str
    phone: Optional[str] = None
    email: Optional[str] = None
    consultation_fee: Optional[str] = None
    available_days: List[str]
    rating: float = 0.0
    reviews_count: int = 0
    image_url: Optional[str] = None
    bio: Optional[str] = None


# Booking Model
class BookingCreate(BaseModel):
    practitioner_id: str
    date: str  # YYYY-MM-DD format
    time_slot: str  # e.g., "10:00 AM"
    reason: Optional[str] = None


class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    booking_id: str
    user_id: str
    practitioner_id: str
    practitioner_name: str
    date: str
    time_slot: str
    reason: Optional[str] = None
    status: str = "confirmed"  # confirmed, cancelled, completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Review Model
class ReviewCreate(BaseModel):
    practitioner_id: str
    rating: int  # 1-5
    comment: str


class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str
    user_id: str
    user_name: str
    user_picture: Optional[str] = None
    practitioner_id: str
    rating: int
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Favorites Model
class FavoriteCreate(BaseModel):
    item_type: str  # "medicine" or "practitioner"
    item_id: str


class Favorite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    favorite_id: str
    user_id: str
    item_type: str
    item_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== AUTH HELPERS ====================

async def get_current_user(request: Request) -> User:
    """Get current user from session token in cookies or Authorization header"""
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)


# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/session")
async def create_session(request: SessionRequest, response: Response):
    """Exchange session_id from Emergent Auth for session token"""
    try:
        async with httpx.AsyncClient() as client_http:
            auth_response = await client_http.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": request.session_id}
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session_id")
            
            auth_data = auth_response.json()
    except httpx.RequestError as e:
        logger.error(f"Auth request failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication service unavailable")
    
    email = auth_data.get("email")
    name = auth_data.get("name")
    picture = auth_data.get("picture")
    session_token = auth_data.get("session_token")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": email}, {"_id": 0})
    
    if existing_user:
        user_id = existing_user["user_id"]
        # Update user info if needed
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture}}
        )
    else:
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(new_user)
    
    # Create session
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    session_doc = {
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Remove old sessions for this user
    await db.user_sessions.delete_many({"user_id": user_id})
    await db.user_sessions.insert_one(session_doc)
    
    # Set cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )
    
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user_doc


@api_router.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info"""
    return user.model_dump()


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}


# ==================== ILLNESS CATEGORIES ====================

@api_router.get("/categories", response_model=List[IllnessCategory])
async def get_categories():
    """Get all illness categories"""
    categories = await db.illness_categories.find({}, {"_id": 0}).to_list(100)
    return categories


@api_router.get("/categories/{category_id}")
async def get_category(category_id: str):
    """Get a specific category with its medicines"""
    category = await db.illness_categories.find_one(
        {"category_id": category_id},
        {"_id": 0}
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    medicines = await db.medicines.find(
        {"illness_categories": category_id},
        {"_id": 0}
    ).to_list(100)
    
    return {"category": category, "medicines": medicines}


# ==================== MEDICINES ====================

@api_router.get("/medicines", response_model=List[Medicine])
async def get_medicines(search: Optional[str] = None, category: Optional[str] = None):
    """Get medicines with optional search and category filter"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"symptoms": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["illness_categories"] = category
    
    medicines = await db.medicines.find(query, {"_id": 0}).to_list(100)
    return medicines


@api_router.get("/medicines/{medicine_id}")
async def get_medicine(medicine_id: str):
    """Get a specific medicine"""
    medicine = await db.medicines.find_one(
        {"medicine_id": medicine_id},
        {"_id": 0}
    )
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine


# ==================== SYMPTOM CHECKER ====================

@api_router.get("/symptoms")
async def get_all_symptoms():
    """Get all unique symptoms"""
    medicines = await db.medicines.find({}, {"symptoms": 1, "_id": 0}).to_list(100)
    symptoms_set = set()
    for med in medicines:
        symptoms_set.update(med.get("symptoms", []))
    return sorted(list(symptoms_set))


@api_router.post("/symptom-check")
async def check_symptoms(request: SymptomCheckRequest):
    """Get medicine recommendations based on symptoms"""
    if not request.symptoms:
        return {"medicines": [], "message": "Please select at least one symptom"}
    
    # Find medicines that match any of the symptoms
    medicines = await db.medicines.find(
        {"symptoms": {"$in": request.symptoms}},
        {"_id": 0}
    ).to_list(100)
    
    # Sort by number of matching symptoms
    def count_matches(medicine):
        med_symptoms = set(medicine.get("symptoms", []))
        return len(med_symptoms.intersection(set(request.symptoms)))
    
    medicines_sorted = sorted(medicines, key=count_matches, reverse=True)
    
    return {
        "medicines": medicines_sorted,
        "matched_count": len(medicines_sorted),
        "message": f"Found {len(medicines_sorted)} remedies for your symptoms"
    }


# ==================== PRACTITIONERS ====================

@api_router.get("/practitioners", response_model=List[Practitioner])
async def get_practitioners(
    city: Optional[str] = None,
    specialization: Optional[str] = None,
    search: Optional[str] = None
):
    """Get practitioners with optional filters"""
    query = {}
    
    if city:
        query["city"] = {"$regex": city, "$options": "i"}
    
    if specialization:
        query["specializations"] = {"$regex": specialization, "$options": "i"}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"clinic_name": {"$regex": search, "$options": "i"}},
            {"specializations": {"$regex": search, "$options": "i"}}
        ]
    
    practitioners = await db.practitioners.find(query, {"_id": 0}).to_list(100)
    return practitioners


@api_router.get("/practitioners/cities")
async def get_practitioner_cities():
    """Get unique cities with practitioners"""
    practitioners = await db.practitioners.find({}, {"city": 1, "_id": 0}).to_list(100)
    cities = list(set(p.get("city") for p in practitioners if p.get("city")))
    return sorted(cities)


@api_router.get("/practitioners/specializations")
async def get_practitioner_specializations():
    """Get unique specializations"""
    practitioners = await db.practitioners.find({}, {"specializations": 1, "_id": 0}).to_list(100)
    specs = set()
    for p in practitioners:
        specs.update(p.get("specializations", []))
    return sorted(list(specs))


@api_router.get("/practitioners/{practitioner_id}")
async def get_practitioner(practitioner_id: str):
    """Get a specific practitioner"""
    practitioner = await db.practitioners.find_one(
        {"practitioner_id": practitioner_id},
        {"_id": 0}
    )
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    return practitioner


# ==================== BOOKINGS ====================

@api_router.post("/bookings", status_code=201)
async def create_booking(booking: BookingCreate, user: User = Depends(get_current_user)):
    """Create a new booking"""
    # Verify practitioner exists
    practitioner = await db.practitioners.find_one(
        {"practitioner_id": booking.practitioner_id},
        {"_id": 0}
    )
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    
    # Check if slot is already booked
    existing = await db.bookings.find_one({
        "practitioner_id": booking.practitioner_id,
        "date": booking.date,
        "time_slot": booking.time_slot,
        "status": {"$ne": "cancelled"}
    })
    if existing:
        raise HTTPException(status_code=400, detail="This time slot is already booked")
    
    booking_id = f"booking_{uuid.uuid4().hex[:12]}"
    booking_doc = {
        "booking_id": booking_id,
        "user_id": user.user_id,
        "practitioner_id": booking.practitioner_id,
        "practitioner_name": practitioner["name"],
        "date": booking.date,
        "time_slot": booking.time_slot,
        "reason": booking.reason,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.bookings.insert_one(booking_doc)
    # Remove MongoDB's _id field for JSON serialization
    booking_doc.pop("_id", None)
    return {"message": "Booking confirmed", "booking": booking_doc}


@api_router.get("/bookings")
async def get_user_bookings(user: User = Depends(get_current_user)):
    """Get user's bookings"""
    bookings = await db.bookings.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).sort("date", -1).to_list(100)
    return bookings


@api_router.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: str, user: User = Depends(get_current_user)):
    """Cancel a booking"""
    result = await db.bookings.update_one(
        {"booking_id": booking_id, "user_id": user.user_id},
        {"$set": {"status": "cancelled"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled"}


@api_router.get("/practitioners/{practitioner_id}/slots")
async def get_available_slots(practitioner_id: str, date: str):
    """Get available time slots for a practitioner on a specific date"""
    practitioner = await db.practitioners.find_one(
        {"practitioner_id": practitioner_id},
        {"_id": 0}
    )
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    
    # Define all possible slots
    all_slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
        "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
        "05:00 PM", "05:30 PM"
    ]
    
    # Get booked slots for this date
    booked = await db.bookings.find(
        {"practitioner_id": practitioner_id, "date": date, "status": {"$ne": "cancelled"}},
        {"time_slot": 1, "_id": 0}
    ).to_list(100)
    booked_slots = [b["time_slot"] for b in booked]
    
    # Return available slots
    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    return {"date": date, "available_slots": available_slots, "booked_slots": booked_slots}


# ==================== REVIEWS ====================

@api_router.post("/reviews")
async def create_review(review: ReviewCreate, user: User = Depends(get_current_user)):
    """Create a review for a practitioner"""
    # Verify practitioner exists
    practitioner = await db.practitioners.find_one(
        {"practitioner_id": review.practitioner_id},
        {"_id": 0}
    )
    if not practitioner:
        raise HTTPException(status_code=404, detail="Practitioner not found")
    
    # Check if user already reviewed this practitioner
    existing = await db.reviews.find_one({
        "user_id": user.user_id,
        "practitioner_id": review.practitioner_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this practitioner")
    
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    review_id = f"review_{uuid.uuid4().hex[:12]}"
    review_doc = {
        "review_id": review_id,
        "user_id": user.user_id,
        "user_name": user.name,
        "user_picture": user.picture,
        "practitioner_id": review.practitioner_id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.reviews.insert_one(review_doc)
    
    # Update practitioner's rating
    all_reviews = await db.reviews.find(
        {"practitioner_id": review.practitioner_id},
        {"rating": 1, "_id": 0}
    ).to_list(1000)
    
    avg_rating = sum(r["rating"] for r in all_reviews) / len(all_reviews)
    await db.practitioners.update_one(
        {"practitioner_id": review.practitioner_id},
        {"$set": {"rating": round(avg_rating, 1), "reviews_count": len(all_reviews)}}
    )
    
    # Remove MongoDB's _id field for JSON serialization
    review_doc.pop("_id", None)
    return {"message": "Review submitted", "review": review_doc}


@api_router.get("/practitioners/{practitioner_id}/reviews")
async def get_practitioner_reviews(practitioner_id: str):
    """Get reviews for a practitioner"""
    reviews = await db.reviews.find(
        {"practitioner_id": practitioner_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return reviews


# ==================== FAVORITES ====================

@api_router.post("/favorites")
async def add_favorite(favorite: FavoriteCreate, user: User = Depends(get_current_user)):
    """Add an item to favorites"""
    if favorite.item_type not in ["medicine", "practitioner"]:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    # Check if already favorited
    existing = await db.favorites.find_one({
        "user_id": user.user_id,
        "item_type": favorite.item_type,
        "item_id": favorite.item_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    favorite_id = f"fav_{uuid.uuid4().hex[:12]}"
    favorite_doc = {
        "favorite_id": favorite_id,
        "user_id": user.user_id,
        "item_type": favorite.item_type,
        "item_id": favorite.item_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.favorites.insert_one(favorite_doc)
    # Remove MongoDB's _id field for JSON serialization
    favorite_doc.pop("_id", None)
    return {"message": "Added to favorites", "favorite": favorite_doc}


@api_router.delete("/favorites/{item_type}/{item_id}")
async def remove_favorite(item_type: str, item_id: str, user: User = Depends(get_current_user)):
    """Remove an item from favorites"""
    result = await db.favorites.delete_one({
        "user_id": user.user_id,
        "item_type": item_type,
        "item_id": item_id
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}


@api_router.get("/favorites")
async def get_favorites(user: User = Depends(get_current_user)):
    """Get user's favorites with item details"""
    favorites = await db.favorites.find(
        {"user_id": user.user_id},
        {"_id": 0}
    ).to_list(100)
    
    # Enrich with item details
    result = {"medicines": [], "practitioners": []}
    
    for fav in favorites:
        if fav["item_type"] == "medicine":
            medicine = await db.medicines.find_one(
                {"medicine_id": fav["item_id"]},
                {"_id": 0}
            )
            if medicine:
                result["medicines"].append(medicine)
        elif fav["item_type"] == "practitioner":
            practitioner = await db.practitioners.find_one(
                {"practitioner_id": fav["item_id"]},
                {"_id": 0}
            )
            if practitioner:
                result["practitioners"].append(practitioner)
    
    return result


@api_router.get("/favorites/check/{item_type}/{item_id}")
async def check_favorite(item_type: str, item_id: str, user: User = Depends(get_current_user)):
    """Check if an item is favorited"""
    favorite = await db.favorites.find_one({
        "user_id": user.user_id,
        "item_type": item_type,
        "item_id": item_id
    })
    return {"is_favorited": favorite is not None}


# ==================== SEED DATABASE ====================

@api_router.post("/seed")
async def seed_database():
    """Seed the database with initial data"""
    
    # Illness Categories
    categories = [
        {
            "category_id": "respiratory",
            "name": "Respiratory Issues",
            "description": "Common cold, cough, congestion, and breathing problems",
            "icon": "Wind",
            "image_url": "https://images.unsplash.com/photo-1584362917165-526a968579e8"
        },
        {
            "category_id": "digestive",
            "name": "Digestive Health",
            "description": "Indigestion, acidity, constipation, and stomach issues",
            "icon": "Apple",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71"
        },
        {
            "category_id": "fever",
            "name": "Fever & Immunity",
            "description": "Fever, weakness, and immune system support",
            "icon": "Thermometer",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef"
        },
        {
            "category_id": "headache",
            "name": "Headache & Pain",
            "description": "Headaches, migraines, and body pain",
            "icon": "Brain",
            "image_url": "https://images.unsplash.com/photo-1616391182219-e080b4d1043a"
        },
        {
            "category_id": "skin",
            "name": "Skin Health",
            "description": "Skin issues, rashes, and allergies",
            "icon": "Sparkles",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571"
        },
        {
            "category_id": "stress",
            "name": "Stress & Anxiety",
            "description": "Mental wellness, stress relief, and sleep issues",
            "icon": "Heart",
            "image_url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773"
        },
        {
            "category_id": "allergies",
            "name": "Allergies",
            "description": "Seasonal allergies, hay fever, and allergic reactions",
            "icon": "Flower2",
            "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946"
        }
    ]
    
    # Medicines
    medicines = [
        # Respiratory
        {
            "medicine_id": "tulsi-drops",
            "name": "Tulsi Drops",
            "sanskrit_name": "Ocimum Sanctum",
            "description": "Holy Basil extract for respiratory health and immunity",
            "usage": "Add 2-3 drops to warm water or tea. Can be taken 2-3 times daily.",
            "dosage": "2-3 drops, 2-3 times daily",
            "ingredients": ["Tulsi (Holy Basil) extract", "Distilled water"],
            "precautions": ["Consult doctor if pregnant", "Not for children under 2"],
            "contraindications": ["Blood thinning medications", "Pregnancy"],
            "preparation_method": "Fresh tulsi leaves are steam-distilled to extract the essential oil and mixed with purified water.",
            "image_url": "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
            "illness_categories": ["respiratory", "fever"],
            "symptoms": ["cough", "cold", "sore throat", "congestion", "fever", "low immunity"]
        },
        {
            "medicine_id": "sitopaladi-churna",
            "name": "Sitopaladi Churna",
            "sanskrit_name": "Sitopaladi Churna",
            "description": "Classical Ayurvedic formula for respiratory disorders",
            "usage": "Mix 1/2 teaspoon with honey and take after meals.",
            "dosage": "1/2 teaspoon with honey, twice daily",
            "ingredients": ["Mishri (Rock sugar)", "Vamshalochana (Bamboo manna)", "Pippali (Long pepper)", "Ela (Cardamom)", "Twak (Cinnamon)"],
            "precautions": ["Diabetics should use with caution due to sugar content"],
            "contraindications": ["Diabetes (use sugar-free version)"],
            "preparation_method": "All ingredients are dried, powdered, and mixed in specific proportions as per classical texts.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["respiratory"],
            "symptoms": ["cough", "cold", "bronchitis", "phlegm", "chest congestion"]
        },
        {
            "medicine_id": "talisadi-churna",
            "name": "Talisadi Churna",
            "sanskrit_name": "Talisadi Churna",
            "description": "Herbal powder for cough, cold, and digestive issues",
            "usage": "Take 1/4 to 1/2 teaspoon with warm water or honey twice daily.",
            "dosage": "1/4-1/2 teaspoon, twice daily",
            "ingredients": ["Talispatra (Abies webbiana)", "Maricha (Black pepper)", "Shunthi (Ginger)", "Pippali (Long pepper)", "Vamshalochana", "Ela (Cardamom)", "Twak (Cinnamon)"],
            "precautions": ["May cause mild gastric irritation in sensitive individuals"],
            "contraindications": ["Gastritis", "Peptic ulcer"],
            "preparation_method": "Herbs are carefully dried, ground to fine powder, and blended in traditional proportions.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["respiratory", "digestive"],
            "symptoms": ["cough", "cold", "indigestion", "loss of appetite", "bronchitis"]
        },
        # Digestive
        {
            "medicine_id": "triphala-churna",
            "name": "Triphala Churna",
            "sanskrit_name": "Triphala",
            "description": "Three-fruit formula for digestive health and detoxification",
            "usage": "Mix 1 teaspoon in warm water. Take before bedtime for best results.",
            "dosage": "1 teaspoon with warm water, before bedtime",
            "ingredients": ["Amalaki (Indian Gooseberry)", "Bibhitaki (Terminalia bellirica)", "Haritaki (Terminalia chebula)"],
            "precautions": ["Start with lower dose", "May cause loose stools initially"],
            "contraindications": ["Diarrhea", "Pregnancy", "Breastfeeding"],
            "preparation_method": "Equal parts of three fruits are dried, powdered separately, and then mixed together.",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
            "illness_categories": ["digestive"],
            "symptoms": ["constipation", "indigestion", "bloating", "toxin buildup", "irregular bowel"]
        },
        {
            "medicine_id": "hingvastak-churna",
            "name": "Hingvastak Churna",
            "sanskrit_name": "Hingvastak Churna",
            "description": "Digestive powder with asafoetida for gas and bloating",
            "usage": "Take 1/2 teaspoon with warm water before meals.",
            "dosage": "1/2 teaspoon before meals",
            "ingredients": ["Hing (Asafoetida)", "Shunthi (Ginger)", "Pippali (Long pepper)", "Maricha (Black pepper)", "Ajwain (Carom seeds)", "Saindhava lavana (Rock salt)", "Jeera (Cumin)", "Krishna Jeera (Black cumin)"],
            "precautions": ["Not recommended during pregnancy"],
            "contraindications": ["Pregnancy", "High blood pressure (due to salt)"],
            "preparation_method": "All ingredients are roasted lightly, powdered, and mixed in specific ratios.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["digestive"],
            "symptoms": ["gas", "bloating", "indigestion", "loss of appetite", "abdominal pain"]
        },
        {
            "medicine_id": "avipattikar-churna",
            "name": "Avipattikar Churna",
            "sanskrit_name": "Avipattikar Churna",
            "description": "Classical formula for acidity and hyperacidity",
            "usage": "Take 1/2-1 teaspoon with cold water or coconut water after meals.",
            "dosage": "1/2-1 teaspoon after meals",
            "ingredients": ["Trikatu", "Triphala", "Musta", "Vidanga", "Ela", "Lavanga", "Patra", "Mishri"],
            "precautions": ["Diabetics should monitor sugar intake"],
            "contraindications": ["Diabetes (use sugar-free version)", "Hypoglycemia"],
            "preparation_method": "Ingredients are processed as per Ayurvedic texts with specific heating and mixing procedures.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["digestive"],
            "symptoms": ["acidity", "heartburn", "gastritis", "indigestion", "sour burps"]
        },
        # Fever & Immunity
        {
            "medicine_id": "giloy-satva",
            "name": "Giloy Satva",
            "sanskrit_name": "Guduchi Satva",
            "description": "Tinospora cordifolia extract for immunity and fever",
            "usage": "Mix 250-500mg with warm water or honey twice daily.",
            "dosage": "250-500mg, twice daily",
            "ingredients": ["Giloy (Tinospora cordifolia) starch extract"],
            "precautions": ["May lower blood sugar levels"],
            "contraindications": ["Autoimmune diseases", "Pre-surgery (stop 2 weeks before)"],
            "preparation_method": "Fresh Giloy stems are crushed, soaked in water, and the starch is extracted and dried.",
            "image_url": "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
            "illness_categories": ["fever"],
            "symptoms": ["fever", "low immunity", "weakness", "recurring infections", "chronic fever"]
        },
        {
            "medicine_id": "sudarshan-ghana-vati",
            "name": "Sudarshan Ghana Vati",
            "sanskrit_name": "Sudarshan Churna",
            "description": "Multi-herb tablet for all types of fever",
            "usage": "Take 2 tablets with warm water twice daily.",
            "dosage": "2 tablets, twice daily",
            "ingredients": ["Chirata", "Kutki", "Giloy", "Haritaki", "Triphala", "Neem", "40+ herbs"],
            "precautions": ["May cause slight gastric discomfort initially"],
            "contraindications": ["Pregnancy", "Liver disease"],
            "preparation_method": "Herbs are decocted, concentrated, and formed into tablets as per Ayurvedic pharmacopoeia.",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            "illness_categories": ["fever"],
            "symptoms": ["fever", "intermittent fever", "malaria-type fever", "weakness", "body ache"]
        },
        {
            "medicine_id": "chyawanprash",
            "name": "Chyawanprash",
            "sanskrit_name": "Chyawanprash",
            "description": "Immunity-boosting herbal jam with Amla",
            "usage": "Take 1-2 teaspoons daily, preferably with warm milk.",
            "dosage": "1-2 teaspoons daily",
            "ingredients": ["Amla", "Ashwagandha", "Pippali", "Guduchi", "Shatavari", "40+ herbs", "Honey", "Ghee"],
            "precautions": ["Diabetics should consult doctor due to sugar content"],
            "contraindications": ["Diabetes (use sugar-free version)"],
            "preparation_method": "Amla is cooked with ghee, then herbs are added and cooked with sugar and honey to create a jam.",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
            "illness_categories": ["fever", "respiratory"],
            "symptoms": ["low immunity", "weakness", "recurring infections", "fatigue", "seasonal illness"]
        },
        # Headache & Pain
        {
            "medicine_id": "pathyadi-kwath",
            "name": "Pathyadi Kwath",
            "sanskrit_name": "Pathyadi Kwath",
            "description": "Herbal decoction for headaches and migraines",
            "usage": "Take 15-20ml twice daily before meals.",
            "dosage": "15-20ml, twice daily",
            "ingredients": ["Haritaki", "Amalaki", "Bibhitaki", "Neem", "Guduchi", "Nimba"],
            "precautions": ["Bitter taste, can be mixed with honey"],
            "contraindications": ["Pregnancy", "Low blood pressure"],
            "preparation_method": "Herbs are boiled in water until reduced to 1/4th the original volume.",
            "image_url": "https://images.unsplash.com/photo-1616391182219-e080b4d1043a",
            "illness_categories": ["headache"],
            "symptoms": ["headache", "migraine", "tension headache", "sinus headache"]
        },
        {
            "medicine_id": "godanti-bhasma",
            "name": "Godanti Bhasma",
            "sanskrit_name": "Godanti Bhasma",
            "description": "Calcified gypsum for headaches and fever",
            "usage": "Take 125-250mg with honey or warm water twice daily.",
            "dosage": "125-250mg, twice daily",
            "ingredients": ["Godanti (Gypsum) - purified and calcified"],
            "precautions": ["Use only under practitioner guidance"],
            "contraindications": ["Kidney disease", "Hypercalcemia"],
            "preparation_method": "Gypsum is purified, heated to high temperatures, and reduced to ash (bhasma) through multiple cycles.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["headache", "fever"],
            "symptoms": ["headache", "migraine", "fever", "chronic headache"]
        },
        {
            "medicine_id": "brahmi-vati",
            "name": "Brahmi Vati",
            "sanskrit_name": "Brahmi Vati",
            "description": "Brain tonic for mental clarity and headache relief",
            "usage": "Take 1-2 tablets with warm milk or water twice daily.",
            "dosage": "1-2 tablets, twice daily",
            "ingredients": ["Brahmi", "Shankhpushpi", "Ashwagandha", "Jatamansi", "Swarna Bhasma"],
            "precautions": ["May cause drowsiness in some"],
            "contraindications": ["Low thyroid function"],
            "preparation_method": "Herbs are processed with specific juices and metals as per traditional methods.",
            "image_url": "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
            "illness_categories": ["headache", "stress"],
            "symptoms": ["headache", "mental fatigue", "poor concentration", "anxiety-related headache"]
        },
        # Skin Health
        {
            "medicine_id": "neem-capsules",
            "name": "Neem Capsules",
            "sanskrit_name": "Nimba",
            "description": "Blood purifier for skin health and infections",
            "usage": "Take 1-2 capsules with water twice daily after meals.",
            "dosage": "1-2 capsules, twice daily",
            "ingredients": ["Neem leaf extract"],
            "precautions": ["May lower blood sugar"],
            "contraindications": ["Pregnancy", "Trying to conceive", "Diabetes (monitor closely)"],
            "preparation_method": "Neem leaves are dried, powdered, and encapsulated for easy consumption.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["skin"],
            "symptoms": ["acne", "skin rash", "eczema", "blood impurities", "boils", "skin infection"]
        },
        {
            "medicine_id": "manjistha-capsules",
            "name": "Manjistha Capsules",
            "sanskrit_name": "Manjistha",
            "description": "Blood purifier and skin brightening herb",
            "usage": "Take 1-2 capsules with warm water twice daily.",
            "dosage": "1-2 capsules, twice daily",
            "ingredients": ["Manjistha (Rubia cordifolia) extract"],
            "precautions": ["May cause reddish discoloration of urine (harmless)"],
            "contraindications": ["Pregnancy", "Breastfeeding"],
            "preparation_method": "Manjistha roots are extracted and standardized for active compounds.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["skin"],
            "symptoms": ["pigmentation", "uneven skin tone", "acne scars", "skin inflammation", "eczema"]
        },
        {
            "medicine_id": "khadirarishta",
            "name": "Khadirarishta",
            "sanskrit_name": "Khadirarishta",
            "description": "Fermented herbal tonic for skin diseases",
            "usage": "Take 15-20ml with equal water after meals.",
            "dosage": "15-20ml with water, after meals",
            "ingredients": ["Khadira (Acacia catechu)", "Devdaru", "Triphala", "Daruhaldi", "Natural fermentation agents"],
            "precautions": ["Contains self-generated alcohol from fermentation"],
            "contraindications": ["Alcohol intolerance", "Liver disease"],
            "preparation_method": "Herbs are fermented naturally for 30-90 days to produce a medicinal wine.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["skin", "allergies"],
            "symptoms": ["chronic skin disease", "psoriasis", "eczema", "skin allergies", "itching"]
        },
        # Stress & Anxiety
        {
            "medicine_id": "ashwagandha-churna",
            "name": "Ashwagandha Churna",
            "sanskrit_name": "Ashwagandha",
            "description": "Adaptogenic herb for stress and energy",
            "usage": "Mix 1/2 teaspoon with warm milk at bedtime.",
            "dosage": "1/2 teaspoon with warm milk, at bedtime",
            "ingredients": ["Ashwagandha root powder"],
            "precautions": ["May increase thyroid hormone levels"],
            "contraindications": ["Hyperthyroidism", "Pregnancy"],
            "preparation_method": "Ashwagandha roots are carefully dried and ground to a fine powder.",
            "image_url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
            "illness_categories": ["stress"],
            "symptoms": ["stress", "anxiety", "fatigue", "insomnia", "weakness", "low energy"]
        },
        {
            "medicine_id": "brahmi-churna",
            "name": "Brahmi Churna",
            "sanskrit_name": "Brahmi",
            "description": "Memory enhancer and stress reliever",
            "usage": "Take 1/4-1/2 teaspoon with warm water or milk twice daily.",
            "dosage": "1/4-1/2 teaspoon, twice daily",
            "ingredients": ["Brahmi (Bacopa monnieri) powder"],
            "precautions": ["May cause mild digestive upset in some"],
            "contraindications": ["Stomach ulcers", "Bradycardia"],
            "preparation_method": "Whole Brahmi plant is shade-dried and powdered.",
            "image_url": "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
            "illness_categories": ["stress", "headache"],
            "symptoms": ["poor memory", "anxiety", "stress", "mental fatigue", "lack of focus"]
        },
        {
            "medicine_id": "jatamansi-churna",
            "name": "Jatamansi Churna",
            "sanskrit_name": "Jatamansi",
            "description": "Calming herb for sleep and anxiety",
            "usage": "Take 1/4 teaspoon with warm water at bedtime.",
            "dosage": "1/4 teaspoon at bedtime",
            "ingredients": ["Jatamansi (Nardostachys jatamansi) powder"],
            "precautions": ["May cause drowsiness"],
            "contraindications": ["Operating machinery", "Sedative medications"],
            "preparation_method": "Jatamansi rhizomes are cleaned, dried, and powdered.",
            "image_url": "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
            "illness_categories": ["stress"],
            "symptoms": ["insomnia", "anxiety", "restlessness", "palpitations", "nervous tension"]
        },
        # Allergies
        {
            "medicine_id": "haridra-khand",
            "name": "Haridra Khand",
            "sanskrit_name": "Haridra Khand",
            "description": "Turmeric-based formula for allergies",
            "usage": "Take 1 teaspoon with warm milk twice daily.",
            "dosage": "1 teaspoon with warm milk, twice daily",
            "ingredients": ["Haridra (Turmeric)", "Mishri (Rock sugar)", "Ghee", "Milk", "Trikatu"],
            "precautions": ["Diabetics should use with caution"],
            "contraindications": ["Diabetes (uncontrolled)", "Bile duct obstruction"],
            "preparation_method": "Turmeric is cooked with milk, ghee, and sugar to form a sweet granular preparation.",
            "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946",
            "illness_categories": ["allergies", "skin"],
            "symptoms": ["allergies", "skin allergies", "urticaria", "hives", "seasonal allergies"]
        },
        {
            "medicine_id": "tribhuvan-kirti-ras",
            "name": "Tribhuvan Kirti Ras",
            "sanskrit_name": "Tribhuvan Kirti Ras",
            "description": "Classical medicine for allergic cold and fever",
            "usage": "Take 1 tablet with honey and ginger juice twice daily.",
            "dosage": "1 tablet with honey, twice daily",
            "ingredients": ["Shuddha Hingula", "Shuddha Vatsanabha", "Pippali", "Shunthi", "Maricha", "Tankana"],
            "precautions": ["Should be taken only under practitioner supervision"],
            "contraindications": ["Pregnancy", "Pitta constitution", "Gastritis"],
            "preparation_method": "Metals and herbs are processed through Ayurvedic purification and calcination methods.",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            "illness_categories": ["allergies", "respiratory", "fever"],
            "symptoms": ["allergic rhinitis", "sneezing", "running nose", "cold with fever", "body ache"]
        },
        {
            "medicine_id": "lakshmi-vilas-ras",
            "name": "Lakshmi Vilas Ras",
            "sanskrit_name": "Lakshmi Vilas Ras",
            "description": "Respiratory and skin allergy medicine",
            "usage": "Take 1 tablet with warm water twice daily.",
            "dosage": "1 tablet, twice daily",
            "ingredients": ["Abhrak Bhasma", "Gandhak", "Maricha", "Pippali", "Various purified metals"],
            "precautions": ["Use only under medical supervision"],
            "contraindications": ["Pregnancy", "Children under 12"],
            "preparation_method": "Complex metallic preparation following strict Ayurvedic protocols.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["allergies", "skin", "respiratory"],
            "symptoms": ["skin allergies", "respiratory allergies", "asthma", "eczema", "chronic cold"]
        }
    ]
    
    # Clear existing data
    await db.illness_categories.delete_many({})
    await db.medicines.delete_many({})
    await db.practitioners.delete_many({})
    
    # Practitioners data
    practitioners = [
        {
            "practitioner_id": "dr-sharma-delhi",
            "name": "Dr. Rajesh Sharma",
            "title": "BAMS, MD (Ayurveda)",
            "specializations": ["Panchakarma", "Chronic Diseases", "Skin Disorders"],
            "experience_years": 25,
            "qualifications": ["BAMS - Gujarat Ayurved University", "MD Kayachikitsa - BHU"],
            "clinic_name": "Vedic Ayurveda Clinic",
            "address": "45, Hauz Khas Village, Near Deer Park",
            "city": "New Delhi",
            "state": "Delhi",
            "phone": "+91 98765 43210",
            "email": "dr.sharma@vedicayurveda.com",
            "consultation_fee": "₹800",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "rating": 4.8,
            "reviews_count": 342,
            "image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d",
            "bio": "Dr. Sharma is a renowned Ayurvedic physician with over 25 years of experience in treating chronic diseases through traditional Panchakarma therapies."
        },
        {
            "practitioner_id": "dr-patel-mumbai",
            "name": "Dr. Meera Patel",
            "title": "BAMS, MS (Shalya Tantra)",
            "specializations": ["Women's Health", "Fertility", "Digestive Disorders"],
            "experience_years": 18,
            "qualifications": ["BAMS - Maharashtra University", "MS Shalya - Pune University"],
            "clinic_name": "Ayur Shakti Wellness Center",
            "address": "12, Linking Road, Bandra West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "phone": "+91 98123 45678",
            "email": "dr.meera@ayurshakti.in",
            "consultation_fee": "₹1000",
            "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "rating": 4.9,
            "reviews_count": 287,
            "image_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2",
            "bio": "Dr. Patel specializes in women's health and fertility treatments using authentic Ayurvedic protocols combined with modern diagnostic techniques."
        },
        {
            "practitioner_id": "dr-krishnan-bangalore",
            "name": "Dr. Venkat Krishnan",
            "title": "BAMS, PhD (Dravyaguna)",
            "specializations": ["Respiratory Disorders", "Allergies", "Immunity"],
            "experience_years": 22,
            "qualifications": ["BAMS - RGUHS Bangalore", "PhD - SDM College of Ayurveda"],
            "clinic_name": "Prakriti Ayurveda Hospital",
            "address": "78, JP Nagar 6th Phase",
            "city": "Bangalore",
            "state": "Karnataka",
            "phone": "+91 80 2658 9900",
            "email": "info@prakritiayurveda.org",
            "consultation_fee": "₹750",
            "available_days": ["Monday", "Tuesday", "Thursday", "Friday", "Saturday"],
            "rating": 4.7,
            "reviews_count": 198,
            "image_url": "https://images.unsplash.com/photo-1537368910025-700350fe46c7",
            "bio": "With a PhD in Dravyaguna (Ayurvedic Pharmacology), Dr. Krishnan brings scientific rigor to traditional treatments for respiratory and immune disorders."
        },
        {
            "practitioner_id": "dr-nair-kerala",
            "name": "Dr. Lakshmi Nair",
            "title": "BAMS, MD (Panchakarma)",
            "specializations": ["Panchakarma", "Rejuvenation", "Stress Management"],
            "experience_years": 30,
            "qualifications": ["BAMS - Kerala University", "MD - Govt. Ayurveda College, Trivandrum"],
            "clinic_name": "Kerala Ayurveda Traditions",
            "address": "Near Padmanabhaswamy Temple, East Fort",
            "city": "Thiruvananthapuram",
            "state": "Kerala",
            "phone": "+91 471 233 4455",
            "email": "appointments@keralaayurvedatraditions.com",
            "consultation_fee": "₹600",
            "available_days": ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "rating": 4.9,
            "reviews_count": 456,
            "image_url": "https://images.unsplash.com/photo-1594824476967-48c8b964273f",
            "bio": "Dr. Nair is a third-generation Ayurvedic physician from Kerala, specializing in authentic Panchakarma and rejuvenation therapies."
        },
        {
            "practitioner_id": "dr-gupta-jaipur",
            "name": "Dr. Anil Gupta",
            "title": "BAMS, MD (Rasashastra)",
            "specializations": ["Joint Disorders", "Arthritis", "Pain Management"],
            "experience_years": 20,
            "qualifications": ["BAMS - NIA Jaipur", "MD Rasashastra - NIA Jaipur"],
            "clinic_name": "Jaipur Ayurveda Sansthan",
            "address": "C-Scheme, Near Statue Circle",
            "city": "Jaipur",
            "state": "Rajasthan",
            "phone": "+91 141 256 7890",
            "email": "drgupta@jaipurayurveda.com",
            "consultation_fee": "₹700",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"],
            "rating": 4.6,
            "reviews_count": 167,
            "image_url": "https://images.unsplash.com/photo-1622253692010-333f2da6031d",
            "bio": "Dr. Gupta specializes in treating joint disorders and chronic pain using traditional mineral-based Ayurvedic preparations (Rasaushadhis)."
        },
        {
            "practitioner_id": "dr-devi-hyderabad",
            "name": "Dr. Sunita Devi",
            "title": "BAMS, MD (Kaumarbhritya)",
            "specializations": ["Pediatrics", "Child Development", "Digestive Issues in Children"],
            "experience_years": 15,
            "qualifications": ["BAMS - NTRUHS", "MD Kaumarbhritya - Dr. NTR University"],
            "clinic_name": "Bala Ayurveda Clinic",
            "address": "Jubilee Hills, Road No. 36",
            "city": "Hyderabad",
            "state": "Telangana",
            "phone": "+91 40 2355 6677",
            "email": "balaayurveda@gmail.com",
            "consultation_fee": "₹500",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Friday", "Saturday"],
            "rating": 4.8,
            "reviews_count": 234,
            "image_url": "https://images.unsplash.com/photo-1651008376811-b90baee60c1f",
            "bio": "Dr. Devi is a pediatric Ayurveda specialist, dedicated to providing gentle, natural treatments for children's health issues."
        },
        {
            "practitioner_id": "dr-singh-varanasi",
            "name": "Dr. Pradeep Singh",
            "title": "BAMS, MD (Swasthavritta)",
            "specializations": ["Lifestyle Disorders", "Diabetes Management", "Preventive Care"],
            "experience_years": 28,
            "qualifications": ["BAMS - BHU", "MD Swasthavritta - BHU"],
            "clinic_name": "Kashi Ayurveda Kendra",
            "address": "Assi Ghat, Near Tulsi Manas Temple",
            "city": "Varanasi",
            "state": "Uttar Pradesh",
            "phone": "+91 542 245 6789",
            "email": "kashiayurveda@bhu.ac.in",
            "consultation_fee": "₹400",
            "available_days": ["Monday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "rating": 4.7,
            "reviews_count": 312,
            "image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d",
            "bio": "Teaching at BHU and practicing in the spiritual city of Varanasi, Dr. Singh combines ancient wisdom with lifestyle medicine for modern health challenges."
        },
        {
            "practitioner_id": "dr-rao-chennai",
            "name": "Dr. Kamala Rao",
            "title": "BAMS, MD (Manasroga)",
            "specializations": ["Mental Health", "Anxiety", "Sleep Disorders", "Stress"],
            "experience_years": 17,
            "qualifications": ["BAMS - Tamil Nadu MGR University", "MD Manasroga - AVS Coimbatore"],
            "clinic_name": "Manas Ayurveda Center",
            "address": "T. Nagar, Near Pondy Bazaar",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "phone": "+91 44 2434 5566",
            "email": "dr.rao@manasayurveda.in",
            "consultation_fee": "₹900",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "rating": 4.8,
            "reviews_count": 189,
            "image_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2",
            "bio": "Dr. Rao specializes in Ayurvedic psychiatry (Manasroga), offering holistic treatments for anxiety, depression, and sleep disorders."
        }
    ]
    
    # Insert new data
    await db.illness_categories.insert_many(categories)
    await db.medicines.insert_many(medicines)
    await db.practitioners.insert_many(practitioners)
    
    return {
        "message": "Database seeded successfully",
        "categories_count": len(categories),
        "medicines_count": len(medicines),
        "practitioners_count": len(practitioners)
    }


# ==================== HEALTH CHECK ====================

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
