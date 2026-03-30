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
        },
        {
            "category_id": "diabetes",
            "name": "Diabetes Care",
            "description": "Blood sugar management and metabolic health",
            "icon": "Activity",
            "image_url": "https://images.unsplash.com/photo-1579684385127-1ef15d508118"
        },
        {
            "category_id": "joints",
            "name": "Joint & Bone Health",
            "description": "Arthritis, joint pain, and bone strengthening",
            "icon": "Bone",
            "image_url": "https://images.unsplash.com/photo-1559757175-7cb036e0e82a"
        },
        {
            "category_id": "general",
            "name": "General Wellness",
            "description": "Daily health tonics and immunity boosters",
            "icon": "Shield",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571"
        },
        {
            "category_id": "hair",
            "name": "Hair Health",
            "description": "Hair fall, premature greying, and scalp health",
            "icon": "Scissors",
            "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e"
        },
        {
            "category_id": "eyes",
            "name": "Eye Care",
            "description": "Vision health, eye strain, and eye disorders",
            "icon": "Eye",
            "image_url": "https://images.unsplash.com/photo-1494869042583-f6c911f04b4c"
        },
        {
            "category_id": "heart",
            "name": "Heart Health",
            "description": "Cardiovascular health and blood circulation",
            "icon": "HeartPulse",
            "image_url": "https://images.unsplash.com/photo-1559757175-5700dde675bc"
        },
        {
            "category_id": "liver",
            "name": "Liver & Kidney",
            "description": "Detoxification and organ health",
            "icon": "Droplets",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71"
        },
        {
            "category_id": "women",
            "name": "Women's Health",
            "description": "PCOS, menstrual health, and hormonal balance",
            "icon": "Flower",
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b"
        },
        {
            "category_id": "men",
            "name": "Men's Health",
            "description": "Vitality, stamina, and reproductive health",
            "icon": "Dumbbell",
            "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b"
        },
        {
            "category_id": "children",
            "name": "Children's Health",
            "description": "Immunity, growth, and common childhood ailments",
            "icon": "Baby",
            "image_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9"
        },
        {
            "category_id": "weight",
            "name": "Weight Management",
            "description": "Healthy weight loss and weight gain",
            "icon": "Scale",
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b"
        },
        {
            "category_id": "bp",
            "name": "Blood Pressure",
            "description": "Hypertension and blood pressure management",
            "icon": "Gauge",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef"
        },
        {
            "category_id": "cholesterol",
            "name": "Cholesterol Care",
            "description": "Lipid management and arterial health",
            "icon": "Droplet",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71"
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
        },
        # Diabetes Care
        {
            "medicine_id": "gudmar-churna",
            "name": "Gudmar Churna",
            "sanskrit_name": "Gymnema Sylvestre",
            "description": "Known as 'Sugar Destroyer', helps regulate blood sugar levels",
            "usage": "Take 1/2 teaspoon with warm water before meals twice daily.",
            "dosage": "1/2 teaspoon, twice daily before meals",
            "ingredients": ["Gudmar (Gymnema sylvestre) leaf powder"],
            "precautions": ["Monitor blood sugar regularly", "May enhance effect of diabetes medications"],
            "contraindications": ["Hypoglycemia", "Surgery (stop 2 weeks before)"],
            "preparation_method": "Gudmar leaves are shade-dried and finely powdered.",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
            "illness_categories": ["diabetes"],
            "symptoms": ["high blood sugar", "sugar cravings", "frequent urination", "excessive thirst", "diabetes management"]
        },
        {
            "medicine_id": "karela-jamun-juice",
            "name": "Karela Jamun Juice",
            "sanskrit_name": "Momordica & Syzygium",
            "description": "Bitter gourd and Indian blackberry combination for diabetes",
            "usage": "Take 20-30ml with equal water on empty stomach in morning.",
            "dosage": "20-30ml with water, morning empty stomach",
            "ingredients": ["Karela (Bitter Gourd) juice", "Jamun (Indian Blackberry) juice"],
            "precautions": ["Very bitter taste", "Start with smaller dose"],
            "contraindications": ["Hypoglycemia", "Pregnancy", "G6PD deficiency"],
            "preparation_method": "Fresh karela and jamun are juiced and blended in specific proportions.",
            "image_url": "https://images.unsplash.com/photo-1622042914579-f5d10cf8ea4d",
            "illness_categories": ["diabetes"],
            "symptoms": ["high blood sugar", "diabetes", "metabolic syndrome", "insulin resistance"]
        },
        {
            "medicine_id": "nisha-amalaki",
            "name": "Nisha Amalaki",
            "sanskrit_name": "Nisha Amalaki",
            "description": "Classical combination of turmeric and amla for diabetes",
            "usage": "Take 1 teaspoon with warm water twice daily.",
            "dosage": "1 teaspoon, twice daily",
            "ingredients": ["Haridra (Turmeric)", "Amalaki (Indian Gooseberry)"],
            "precautions": ["May stain teeth temporarily"],
            "contraindications": ["Bile duct obstruction", "Gallstones"],
            "preparation_method": "Equal parts of turmeric and amla are powdered and mixed.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["diabetes", "skin"],
            "symptoms": ["high blood sugar", "prediabetes", "skin issues", "inflammation"]
        },
        {
            "medicine_id": "chandraprabha-vati",
            "name": "Chandraprabha Vati",
            "sanskrit_name": "Chandraprabha Vati",
            "description": "Classical formulation for urinary and metabolic disorders",
            "usage": "Take 2 tablets with warm water twice daily.",
            "dosage": "2 tablets, twice daily",
            "ingredients": ["Shilajit", "Guggulu", "Triphala", "Trikatu", "Loha Bhasma", "37 herbs"],
            "precautions": ["Use under practitioner guidance"],
            "contraindications": ["Pregnancy", "Severe kidney disease"],
            "preparation_method": "Multiple herbs are processed and formed into tablets as per classical texts.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["diabetes", "general"],
            "symptoms": ["frequent urination", "urinary disorders", "diabetes", "general weakness"]
        },
        {
            "medicine_id": "vijaysar-wood",
            "name": "Vijaysar Wood Tumbler",
            "sanskrit_name": "Pterocarpus Marsupium",
            "description": "Water kept overnight in Vijaysar wood tumbler helps manage blood sugar",
            "usage": "Fill tumbler with water at night, drink in morning on empty stomach.",
            "dosage": "1 glass (200ml) morning, empty stomach",
            "ingredients": ["Vijaysar (Indian Kino Tree) wood"],
            "precautions": ["Change tumbler every 2-3 months when water stops turning color"],
            "contraindications": ["None known"],
            "preparation_method": "Tumbler is carved from Vijaysar heartwood. Water extracts active compounds overnight.",
            "image_url": "https://images.unsplash.com/photo-1544787219-7f47ccb76574",
            "illness_categories": ["diabetes"],
            "symptoms": ["high blood sugar", "diabetes type 2", "metabolic disorders"]
        },
        # Joint & Bone Health
        {
            "medicine_id": "yograj-guggulu",
            "name": "Yograj Guggulu",
            "sanskrit_name": "Yograj Guggulu",
            "description": "Classical formula for joint pain and arthritis",
            "usage": "Take 2 tablets with warm water twice daily after meals.",
            "dosage": "2 tablets, twice daily after meals",
            "ingredients": ["Guggulu", "Chitraka", "Pippali", "Vidanga", "Triphala", "28 herbs"],
            "precautions": ["May cause mild gastric irritation initially"],
            "contraindications": ["Pregnancy", "Hyperthyroidism", "Acute kidney disease"],
            "preparation_method": "Herbs are processed with purified guggulu resin as per Ayurvedic protocols.",
            "image_url": "https://images.unsplash.com/photo-1559757175-7cb036e0e82a",
            "illness_categories": ["joints"],
            "symptoms": ["joint pain", "arthritis", "rheumatism", "stiffness", "muscle pain", "sciatica"]
        },
        {
            "medicine_id": "maharasnadi-kwath",
            "name": "Maharasnadi Kwath",
            "sanskrit_name": "Maharasnadi Kashayam",
            "description": "Powerful decoction for joint disorders and Vata imbalances",
            "usage": "Take 15-20ml with equal warm water twice daily before meals.",
            "dosage": "15-20ml with warm water, twice daily",
            "ingredients": ["Rasna", "Devdaru", "Guduchi", "Ashwagandha", "Shatavari", "25+ herbs"],
            "precautions": ["Bitter taste, can mix with honey"],
            "contraindications": ["Pregnancy", "Acute fever"],
            "preparation_method": "Herbs are boiled until reduced to 1/4th, then strained.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["joints", "stress"],
            "symptoms": ["joint pain", "arthritis", "paralysis", "sciatica", "Vata disorders", "numbness"]
        },
        {
            "medicine_id": "shallaki-capsules",
            "name": "Shallaki Capsules",
            "sanskrit_name": "Boswellia Serrata",
            "description": "Indian Frankincense for joint inflammation and pain",
            "usage": "Take 1-2 capsules with warm water twice daily.",
            "dosage": "1-2 capsules, twice daily",
            "ingredients": ["Shallaki (Boswellia serrata) extract"],
            "precautions": ["May cause mild stomach upset in some"],
            "contraindications": ["Pregnancy", "Breastfeeding"],
            "preparation_method": "Boswellia gum resin is extracted and encapsulated.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["joints"],
            "symptoms": ["joint inflammation", "osteoarthritis", "rheumatoid arthritis", "joint swelling"]
        },
        {
            "medicine_id": "lakshadi-guggulu",
            "name": "Lakshadi Guggulu",
            "sanskrit_name": "Lakshadi Guggulu",
            "description": "For bone fractures, osteoporosis, and calcium deficiency",
            "usage": "Take 2 tablets with warm milk twice daily.",
            "dosage": "2 tablets with warm milk, twice daily",
            "ingredients": ["Laksha (Lac)", "Arjuna", "Ashwagandha", "Nagabala", "Guggulu"],
            "precautions": ["Best taken with milk for calcium absorption"],
            "contraindications": ["Hypercalcemia"],
            "preparation_method": "Herbs are processed with purified guggulu and formed into tablets.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["joints"],
            "symptoms": ["bone weakness", "fracture healing", "osteoporosis", "calcium deficiency", "bone pain"]
        },
        {
            "medicine_id": "maha-vishgarbha-oil",
            "name": "Maha Vishgarbha Oil",
            "sanskrit_name": "Maha Vishgarbha Taila",
            "description": "Medicated oil for external application on joints",
            "usage": "Warm the oil and massage gently on affected joints. Leave for 30 mins.",
            "dosage": "External use - massage twice daily",
            "ingredients": ["Sesame oil base", "Nirgundi", "Rasna", "Ashwagandha", "Bala", "50+ herbs"],
            "precautions": ["For external use only", "Do patch test first"],
            "contraindications": ["Open wounds", "Skin infections"],
            "preparation_method": "Herbs are slowly cooked in sesame oil for days following traditional methods.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["joints"],
            "symptoms": ["joint pain", "muscle stiffness", "arthritis", "body pain", "paralysis"]
        },
        # General Wellness - Common Indian Remedies
        {
            "medicine_id": "amla-churna",
            "name": "Amla Churna",
            "sanskrit_name": "Amalaki Churna",
            "description": "Indian Gooseberry powder - richest natural source of Vitamin C",
            "usage": "Take 1 teaspoon with warm water or honey twice daily.",
            "dosage": "1 teaspoon, twice daily",
            "ingredients": ["Amla (Emblica officinalis) powder"],
            "precautions": ["May cause loose stools initially"],
            "contraindications": ["Diarrhea"],
            "preparation_method": "Fresh amla fruits are dried in shade and finely powdered.",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
            "illness_categories": ["general", "skin", "digestive"],
            "symptoms": ["low immunity", "vitamin C deficiency", "hair fall", "premature greying", "weak digestion"]
        },
        {
            "medicine_id": "haldi-doodh",
            "name": "Haldi Doodh (Golden Milk)",
            "sanskrit_name": "Haridra Ksheera",
            "description": "Traditional turmeric milk for immunity and healing",
            "usage": "Add 1/2 teaspoon turmeric to warm milk with black pepper. Drink at bedtime.",
            "dosage": "1 cup at bedtime",
            "ingredients": ["Haldi (Turmeric)", "Warm Milk", "Black Pepper", "Honey (optional)"],
            "precautions": ["Use black pepper for better absorption"],
            "contraindications": ["Gallstones", "Bile duct obstruction"],
            "preparation_method": "Turmeric is added to warm milk with a pinch of black pepper.",
            "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5",
            "illness_categories": ["general", "respiratory", "joints"],
            "symptoms": ["low immunity", "cough", "cold", "inflammation", "joint pain", "sleep issues"]
        },
        {
            "medicine_id": "kadha",
            "name": "Ayurvedic Kadha",
            "sanskrit_name": "Kwath",
            "description": "Traditional immunity booster decoction popular across India",
            "usage": "Boil ingredients in 2 cups water until reduced to 1 cup. Drink warm.",
            "dosage": "1 cup, once or twice daily",
            "ingredients": ["Tulsi", "Ginger", "Black Pepper", "Cinnamon", "Cloves", "Jaggery"],
            "precautions": ["Adjust sweetness as needed", "Can be strong for some"],
            "contraindications": ["Acidity", "Pitta aggravation"],
            "preparation_method": "All ingredients are boiled together until water reduces by half.",
            "image_url": "https://images.unsplash.com/photo-1622042914579-f5d10cf8ea4d",
            "illness_categories": ["general", "respiratory", "fever"],
            "symptoms": ["low immunity", "cold", "cough", "seasonal illness", "weakness"]
        },
        {
            "medicine_id": "ajwain-water",
            "name": "Ajwain Water",
            "sanskrit_name": "Yavani Jala",
            "description": "Carom seed water for digestive health",
            "usage": "Soak 1 teaspoon ajwain in water overnight. Strain and drink in morning.",
            "dosage": "1 glass in morning, empty stomach",
            "ingredients": ["Ajwain (Carom seeds)", "Water"],
            "precautions": ["Start with small quantity"],
            "contraindications": ["Pregnancy (large doses)", "Bleeding disorders"],
            "preparation_method": "Ajwain seeds are soaked overnight and water is consumed next morning.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["digestive", "general"],
            "symptoms": ["indigestion", "gas", "bloating", "acidity", "stomach pain", "weight management"]
        },
        {
            "medicine_id": "methi-dana",
            "name": "Methi Dana Water",
            "sanskrit_name": "Methika Jala",
            "description": "Fenugreek seed water for diabetes and digestion",
            "usage": "Soak 1 teaspoon methi in water overnight. Eat seeds and drink water in morning.",
            "dosage": "1 teaspoon seeds + water, morning empty stomach",
            "ingredients": ["Methi Dana (Fenugreek seeds)", "Water"],
            "precautions": ["Bitter taste", "May lower blood sugar significantly"],
            "contraindications": ["Pregnancy", "Hormone-sensitive conditions"],
            "preparation_method": "Fenugreek seeds are soaked overnight and consumed with the water.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["diabetes", "digestive", "general"],
            "symptoms": ["high blood sugar", "diabetes", "cholesterol", "digestive issues", "hair health"]
        },
        {
            "medicine_id": "saunf-water",
            "name": "Saunf Water",
            "sanskrit_name": "Mishreya Jala",
            "description": "Fennel seed water for cooling and digestion",
            "usage": "Soak 1 teaspoon saunf in water overnight or boil for 5 mins. Drink throughout day.",
            "dosage": "2-3 glasses throughout the day",
            "ingredients": ["Saunf (Fennel seeds)", "Water"],
            "precautions": ["Safe for most people"],
            "contraindications": ["Estrogen-sensitive conditions"],
            "preparation_method": "Fennel seeds are soaked or lightly boiled in water.",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
            "illness_categories": ["digestive", "general"],
            "symptoms": ["acidity", "bloating", "bad breath", "cooling", "eye health", "weight management"]
        },
        {
            "medicine_id": "jeera-water",
            "name": "Jeera Water",
            "sanskrit_name": "Jiraka Jala",
            "description": "Cumin water for metabolism and weight management",
            "usage": "Boil 1 teaspoon cumin in water for 5 mins. Strain and drink warm.",
            "dosage": "1-2 glasses, morning and evening",
            "ingredients": ["Jeera (Cumin seeds)", "Water"],
            "precautions": ["May increase bleeding during menstruation"],
            "contraindications": ["Heavy menstrual bleeding"],
            "preparation_method": "Cumin seeds are dry roasted and boiled in water.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["digestive", "general"],
            "symptoms": ["slow metabolism", "weight gain", "bloating", "gas", "water retention"]
        },
        # Phlegm & Wheeze (Respiratory)
        {
            "medicine_id": "vasavaleha",
            "name": "Vasavaleha",
            "sanskrit_name": "Vasavaleha",
            "description": "Herbal jam made from Vasa (Adhatoda) for cough, phlegm and wheezing",
            "usage": "Take 1-2 teaspoons with warm water or milk twice daily.",
            "dosage": "1-2 teaspoons, twice daily",
            "ingredients": ["Vasa (Adhatoda vasica)", "Honey", "Pippali", "Ghee", "Sugar"],
            "precautions": ["Diabetics use sugar-free version"],
            "contraindications": ["Pregnancy", "Bleeding disorders"],
            "preparation_method": "Vasa leaves are processed with honey and ghee to form a herbal jam.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["respiratory"],
            "symptoms": ["phlegm", "cough", "wheezing", "bronchitis", "chronic cough", "chest congestion"]
        },
        {
            "medicine_id": "kantakari-avaleha",
            "name": "Kantakari Avaleha",
            "sanskrit_name": "Kantakari Avaleha",
            "description": "Classical preparation for asthma, wheezing and respiratory allergies",
            "usage": "Take 1 teaspoon with warm water twice daily.",
            "dosage": "1 teaspoon, twice daily",
            "ingredients": ["Kantakari (Solanum xanthocarpum)", "Pippali", "Honey", "Ghee"],
            "precautions": ["May cause mild stomach warmth"],
            "contraindications": ["Hyperacidity", "Pregnancy"],
            "preparation_method": "Kantakari is processed into a herbal jam with honey and spices.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["respiratory", "allergies"],
            "symptoms": ["wheezing", "asthma", "breathlessness", "allergic cough", "phlegm"]
        },
        {
            "medicine_id": "agastya-haritaki",
            "name": "Agastya Haritaki Rasayana",
            "sanskrit_name": "Agastya Haritaki",
            "description": "Powerful rasayana for chronic respiratory conditions and phlegm",
            "usage": "Take 1-2 teaspoons with warm water twice daily.",
            "dosage": "1-2 teaspoons, twice daily",
            "ingredients": ["Haritaki", "Dashamoola", "Chaturjata", "Bilva", "Vasa", "Guduchi", "30+ herbs"],
            "precautions": ["Use under practitioner guidance for chronic conditions"],
            "contraindications": ["Pregnancy", "Severe debility"],
            "preparation_method": "Multiple herbs are processed into a rasayana (rejuvenative jam).",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["respiratory"],
            "symptoms": ["chronic cough", "phlegm", "asthma", "bronchitis", "COPD", "wheezing", "breathlessness"]
        },
        {
            "medicine_id": "kaphaketu-ras",
            "name": "Kaphaketu Ras",
            "sanskrit_name": "Kaphaketu Ras",
            "description": "Classical medicine to dissolve phlegm and clear respiratory passages",
            "usage": "Take 1 tablet with honey twice daily.",
            "dosage": "1 tablet with honey, twice daily",
            "ingredients": ["Shuddha Parada", "Shuddha Gandhaka", "Maricha", "Pippali", "Shunthi"],
            "precautions": ["Use only under practitioner supervision"],
            "contraindications": ["Pregnancy", "Pitta disorders", "Gastritis"],
            "preparation_method": "Minerals and herbs processed through Ayurvedic purification methods.",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            "illness_categories": ["respiratory"],
            "symptoms": ["phlegm", "kapha congestion", "thick mucus", "sinus congestion", "cold"]
        },
        {
            "medicine_id": "lavangadi-vati",
            "name": "Lavangadi Vati",
            "sanskrit_name": "Lavangadi Vati",
            "description": "Clove-based tablets for cough, phlegm and throat irritation",
            "usage": "Chew or suck 1-2 tablets 3-4 times daily.",
            "dosage": "1-2 tablets, 3-4 times daily",
            "ingredients": ["Lavanga (Clove)", "Karpura (Camphor)", "Pippali", "Maricha", "Tvak (Cinnamon)"],
            "precautions": ["Chew slowly for best effect"],
            "contraindications": ["Children under 5"],
            "preparation_method": "Clove and spices are powdered and formed into dissolvable tablets.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["respiratory"],
            "symptoms": ["cough", "sore throat", "phlegm", "throat irritation", "hoarse voice"]
        },
        {
            "medicine_id": "shwaskuthar-ras",
            "name": "Shwaskuthar Ras",
            "sanskrit_name": "Shwaskuthar Ras",
            "description": "Classical medicine specifically for asthma and breathing difficulties",
            "usage": "Take 1 tablet with honey and ginger juice twice daily.",
            "dosage": "1 tablet with honey & ginger, twice daily",
            "ingredients": ["Parada", "Gandhaka", "Tankana", "Manashila", "Vatsanabha", "Pippali"],
            "precautions": ["Must be taken under practitioner supervision"],
            "contraindications": ["Pregnancy", "Heart disease", "Children"],
            "preparation_method": "Metallic and herbal preparation following strict Ayurvedic protocols.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["respiratory"],
            "symptoms": ["asthma", "wheezing", "breathlessness", "bronchospasm", "severe cough"]
        },
        {
            "medicine_id": "yashtimadhu-churna",
            "name": "Yashtimadhu Churna",
            "sanskrit_name": "Glycyrrhiza Glabra",
            "description": "Licorice powder for soothing throat and reducing phlegm",
            "usage": "Take 1/2 teaspoon with honey twice daily.",
            "dosage": "1/2 teaspoon with honey, twice daily",
            "ingredients": ["Yashtimadhu (Licorice root) powder"],
            "precautions": ["Not for long-term use", "May raise blood pressure"],
            "contraindications": ["Hypertension", "Kidney disease", "Pregnancy"],
            "preparation_method": "Licorice root is dried and finely powdered.",
            "image_url": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71",
            "illness_categories": ["respiratory", "digestive"],
            "symptoms": ["sore throat", "dry cough", "phlegm", "acidity", "voice problems"]
        },
        {
            "medicine_id": "trikatu-churna",
            "name": "Trikatu Churna",
            "sanskrit_name": "Trikatu",
            "description": "Three pungent herbs to clear phlegm and boost digestion",
            "usage": "Take 1/4 teaspoon with honey before meals.",
            "dosage": "1/4 teaspoon with honey, before meals",
            "ingredients": ["Shunthi (Dry Ginger)", "Maricha (Black Pepper)", "Pippali (Long Pepper)"],
            "precautions": ["Very heating - use small doses"],
            "contraindications": ["Hyperacidity", "Gastritis", "Bleeding disorders", "Pregnancy"],
            "preparation_method": "Equal parts of three pungent herbs are powdered and mixed.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["respiratory", "digestive"],
            "symptoms": ["phlegm", "congestion", "slow digestion", "cold", "kapha disorders", "sinus"]
        },
        {
            "medicine_id": "ginger-honey",
            "name": "Adrak Shahad (Ginger Honey)",
            "sanskrit_name": "Ardraka Madhu",
            "description": "Simple home remedy for cough, cold and phlegm",
            "usage": "Mix 1 teaspoon ginger juice with 1 teaspoon honey. Take 3-4 times daily.",
            "dosage": "1 teaspoon each, 3-4 times daily",
            "ingredients": ["Adrak (Fresh Ginger) juice", "Shahad (Honey)"],
            "precautions": ["Use fresh ginger juice"],
            "contraindications": ["Children under 1 year (honey)", "Severe acidity"],
            "preparation_method": "Fresh ginger is grated and juice extracted, mixed with equal honey.",
            "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5",
            "illness_categories": ["respiratory", "general"],
            "symptoms": ["cough", "cold", "phlegm", "sore throat", "congestion", "nausea"]
        },
        {
            "medicine_id": "steam-inhalation",
            "name": "Herbal Steam Inhalation",
            "sanskrit_name": "Swedana",
            "description": "Steam therapy with eucalyptus, ajwain and tulsi for congestion",
            "usage": "Add herbs to boiling water, cover head with towel and inhale steam for 10 mins.",
            "dosage": "10-15 minutes, 2-3 times daily",
            "ingredients": ["Eucalyptus leaves/oil", "Ajwain (Carom seeds)", "Tulsi leaves", "Pudina (Mint)"],
            "precautions": ["Keep safe distance from hot water", "Not for very young children"],
            "contraindications": ["Facial burns", "Severe asthma attack (consult doctor)"],
            "preparation_method": "Add herbs to a pot of boiling water and inhale the medicated steam.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["respiratory"],
            "symptoms": ["nasal congestion", "sinus", "phlegm", "blocked nose", "cold", "headache"]
        },
        # Hair Health
        {
            "medicine_id": "bhringraj-oil",
            "name": "Bhringraj Oil",
            "sanskrit_name": "Bhringaraj Taila",
            "description": "King of herbs for hair - prevents hair fall and premature greying",
            "usage": "Massage into scalp 30 mins before bath, 2-3 times weekly.",
            "dosage": "External use - scalp massage",
            "ingredients": ["Bhringraj", "Amla", "Brahmi", "Sesame oil", "Coconut oil"],
            "precautions": ["For external use only"],
            "contraindications": ["Scalp infections"],
            "preparation_method": "Herbs are slowly cooked in oil for days following traditional methods.",
            "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",
            "illness_categories": ["hair"],
            "symptoms": ["hair fall", "premature greying", "dandruff", "dry scalp", "hair thinning"]
        },
        {
            "medicine_id": "neelibhringadi-oil",
            "name": "Neelibhringadi Oil",
            "sanskrit_name": "Neelibhringadi Keram",
            "description": "Kerala traditional oil for luxuriant black hair",
            "usage": "Apply to scalp and hair, leave overnight. Wash in morning.",
            "dosage": "External use - overnight application",
            "ingredients": ["Neeli (Indigo)", "Bhringraj", "Amla", "Coconut oil"],
            "precautions": ["May stain pillow - use old cloth"],
            "contraindications": ["None known"],
            "preparation_method": "Traditional Kerala preparation with 100+ boiling cycles.",
            "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",
            "illness_categories": ["hair"],
            "symptoms": ["grey hair", "hair fall", "hair growth", "scalp health"]
        },
        {
            "medicine_id": "kesh-king-churna",
            "name": "Keshya Churna",
            "sanskrit_name": "Keshya Churna",
            "description": "Internal herbs for hair nourishment from within",
            "usage": "Take 1 teaspoon with warm water or milk twice daily.",
            "dosage": "1 teaspoon, twice daily",
            "ingredients": ["Bhringraj", "Amla", "Brahmi", "Ashwagandha", "Shatavari"],
            "precautions": ["Best results with external oil application too"],
            "contraindications": ["Pregnancy"],
            "preparation_method": "Hair-nourishing herbs are powdered and mixed.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["hair"],
            "symptoms": ["hair fall", "weak hair", "slow hair growth", "brittle hair"]
        },
        # Eye Care
        {
            "medicine_id": "triphala-ghrita",
            "name": "Triphala Ghrita",
            "sanskrit_name": "Triphala Ghrita",
            "description": "Medicated ghee for eye health and vision improvement",
            "usage": "Take 1 teaspoon with warm water at bedtime.",
            "dosage": "1 teaspoon at bedtime",
            "ingredients": ["Triphala", "Cow ghee", "Honey"],
            "precautions": ["Not for external eye use without guidance"],
            "contraindications": ["High cholesterol", "Obesity"],
            "preparation_method": "Triphala is cooked in ghee following classical methods.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["eyes"],
            "symptoms": ["weak eyesight", "eye strain", "dry eyes", "computer vision syndrome"]
        },
        {
            "medicine_id": "saptamrit-lauh",
            "name": "Saptamrit Lauh",
            "sanskrit_name": "Saptamrit Lauh",
            "description": "Iron preparation for eye diseases and anemia",
            "usage": "Take 1-2 tablets with honey or ghee twice daily.",
            "dosage": "1-2 tablets, twice daily",
            "ingredients": ["Triphala", "Yashtimadhu", "Loha Bhasma", "Ghee", "Honey"],
            "precautions": ["Use under practitioner guidance"],
            "contraindications": ["Hemochromatosis"],
            "preparation_method": "Classical preparation with purified iron and herbs.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["eyes", "general"],
            "symptoms": ["eye diseases", "night blindness", "anemia", "weak vision"]
        },
        {
            "medicine_id": "rose-water-eyes",
            "name": "Gulab Jal (Rose Water)",
            "sanskrit_name": "Shatapatri Jala",
            "description": "Natural rose water for cooling and soothing tired eyes",
            "usage": "Soak cotton pads and place on closed eyes for 10-15 minutes.",
            "dosage": "External use - eye compress",
            "ingredients": ["Pure rose water (Rosa damascena)"],
            "precautions": ["Use only pure, food-grade rose water"],
            "contraindications": ["Eye infections (consult doctor)"],
            "preparation_method": "Rose petals are steam-distilled to extract pure rose water.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["eyes", "skin"],
            "symptoms": ["tired eyes", "eye redness", "eye irritation", "dark circles"]
        },
        # Heart Health
        {
            "medicine_id": "arjuna-churna",
            "name": "Arjuna Churna",
            "sanskrit_name": "Arjuna",
            "description": "Terminalia Arjuna bark for heart strength and blood pressure",
            "usage": "Take 1/2 teaspoon with warm milk twice daily.",
            "dosage": "1/2 teaspoon with milk, twice daily",
            "ingredients": ["Arjuna (Terminalia arjuna) bark powder"],
            "precautions": ["Monitor if on heart medications"],
            "contraindications": ["Low blood pressure", "Constipation"],
            "preparation_method": "Arjuna bark is dried and finely powdered.",
            "image_url": "https://images.unsplash.com/photo-1559757175-5700dde675bc",
            "illness_categories": ["heart", "bp"],
            "symptoms": ["heart weakness", "high blood pressure", "chest pain", "palpitations"]
        },
        {
            "medicine_id": "hridayarnava-ras",
            "name": "Hridayarnava Ras",
            "sanskrit_name": "Hridayarnava Ras",
            "description": "Classical heart tonic for cardiovascular strength",
            "usage": "Take 1 tablet with Arjuna decoction twice daily.",
            "dosage": "1 tablet, twice daily",
            "ingredients": ["Swarna Bhasma", "Abhrak Bhasma", "Mukta Pishti", "Arjuna"],
            "precautions": ["Use only under practitioner supervision"],
            "contraindications": ["Pregnancy", "Children"],
            "preparation_method": "Precious metals and herbs processed through Ayurvedic calcination.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["heart"],
            "symptoms": ["heart disease", "angina", "cardiac weakness", "irregular heartbeat"]
        },
        # Liver & Kidney
        {
            "medicine_id": "liv-52",
            "name": "Arogyavardhini Vati",
            "sanskrit_name": "Arogyavardhini Vati",
            "description": "Classical liver protective and detoxifying formula",
            "usage": "Take 2 tablets with warm water twice daily.",
            "dosage": "2 tablets, twice daily",
            "ingredients": ["Kutki", "Triphala", "Shilajit", "Guggulu", "Loha Bhasma"],
            "precautions": ["May cause loose stools initially"],
            "contraindications": ["Pregnancy", "Severe liver disease"],
            "preparation_method": "Herbs and minerals processed as per classical texts.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["liver"],
            "symptoms": ["liver disorders", "fatty liver", "hepatitis", "jaundice", "detox"]
        },
        {
            "medicine_id": "punarnava-mandur",
            "name": "Punarnava Mandur",
            "sanskrit_name": "Punarnava Mandur",
            "description": "For kidney health, edema, and anemia",
            "usage": "Take 2 tablets with buttermilk twice daily.",
            "dosage": "2 tablets, twice daily",
            "ingredients": ["Punarnava", "Mandur Bhasma", "Triphala", "Trikatu", "Vidanga"],
            "precautions": ["Monitor kidney function"],
            "contraindications": ["Severe kidney failure"],
            "preparation_method": "Iron oxide processed with Punarnava and other herbs.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["liver", "general"],
            "symptoms": ["kidney problems", "water retention", "edema", "anemia", "swelling"]
        },
        {
            "medicine_id": "gokshuradi-guggulu",
            "name": "Gokshuradi Guggulu",
            "sanskrit_name": "Gokshuradi Guggulu",
            "description": "For urinary tract and kidney stone prevention",
            "usage": "Take 2 tablets with warm water twice daily.",
            "dosage": "2 tablets, twice daily",
            "ingredients": ["Gokshura", "Guggulu", "Triphala", "Trikatu", "Musta"],
            "precautions": ["Drink plenty of water"],
            "contraindications": ["Pregnancy"],
            "preparation_method": "Herbs processed with purified guggulu resin.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["liver", "men"],
            "symptoms": ["kidney stones", "UTI", "painful urination", "prostate issues"]
        },
        # Women's Health
        {
            "medicine_id": "shatavari-churna",
            "name": "Shatavari Churna",
            "sanskrit_name": "Shatavari",
            "description": "Queen of herbs for women - hormonal balance and vitality",
            "usage": "Take 1 teaspoon with warm milk twice daily.",
            "dosage": "1 teaspoon with milk, twice daily",
            "ingredients": ["Shatavari (Asparagus racemosus) root powder"],
            "precautions": ["May increase breast milk production"],
            "contraindications": ["Estrogen-sensitive conditions", "Kidney disease"],
            "preparation_method": "Shatavari roots are dried and finely powdered.",
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "illness_categories": ["women", "general"],
            "symptoms": ["hormonal imbalance", "menopause", "low libido", "lactation", "PCOS"]
        },
        {
            "medicine_id": "ashokarishta",
            "name": "Ashokarishta",
            "sanskrit_name": "Ashokarishta",
            "description": "Fermented tonic for menstrual disorders",
            "usage": "Take 15-20ml with equal water after meals.",
            "dosage": "15-20ml with water, after meals",
            "ingredients": ["Ashoka bark", "Dhataki", "Musta", "Haritaki", "Jaggery"],
            "precautions": ["Contains self-generated alcohol"],
            "contraindications": ["Pregnancy", "Heavy bleeding"],
            "preparation_method": "Ashoka bark fermented naturally for 30+ days.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["women"],
            "symptoms": ["irregular periods", "heavy bleeding", "menstrual pain", "PCOS", "leucorrhea"]
        },
        {
            "medicine_id": "kumaryasava",
            "name": "Kumaryasava",
            "sanskrit_name": "Kumaryasava",
            "description": "Aloe vera based tonic for digestive and menstrual health",
            "usage": "Take 15-20ml with equal water after meals.",
            "dosage": "15-20ml with water, after meals",
            "ingredients": ["Kumari (Aloe vera)", "Loha Bhasma", "Triphala", "Trikatu"],
            "precautions": ["Contains self-generated alcohol"],
            "contraindications": ["Pregnancy", "Liver disease"],
            "preparation_method": "Aloe vera and herbs fermented traditionally.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["women", "digestive"],
            "symptoms": ["menstrual disorders", "anemia", "liver problems", "constipation"]
        },
        {
            "medicine_id": "lodhra-churna",
            "name": "Lodhra Churna",
            "sanskrit_name": "Lodhra",
            "description": "For PCOS, hormonal acne, and uterine health",
            "usage": "Take 1/2 teaspoon with warm water twice daily.",
            "dosage": "1/2 teaspoon, twice daily",
            "ingredients": ["Lodhra (Symplocos racemosa) bark powder"],
            "precautions": ["Best used with practitioner guidance"],
            "contraindications": ["Pregnancy"],
            "preparation_method": "Lodhra bark is dried and finely powdered.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["women", "skin"],
            "symptoms": ["PCOS", "hormonal acne", "irregular periods", "excess facial hair"]
        },
        # Men's Health
        {
            "medicine_id": "shilajit-capsules",
            "name": "Shilajit Capsules",
            "sanskrit_name": "Shilajit",
            "description": "Himalayan mineral pitch for strength and vitality",
            "usage": "Take 1-2 capsules with warm milk at bedtime.",
            "dosage": "1-2 capsules at bedtime",
            "ingredients": ["Purified Shilajit (mineral pitch)"],
            "precautions": ["Use only purified Shilajit"],
            "contraindications": ["Gout", "High uric acid"],
            "preparation_method": "Raw Shilajit is purified through traditional methods.",
            "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
            "illness_categories": ["men", "general"],
            "symptoms": ["low energy", "weakness", "low stamina", "aging", "sexual weakness"]
        },
        {
            "medicine_id": "ashwagandha-capsules",
            "name": "Ashwagandha Capsules",
            "sanskrit_name": "Ashwagandha",
            "description": "Indian Ginseng for strength, stress, and stamina",
            "usage": "Take 1-2 capsules with warm milk twice daily.",
            "dosage": "1-2 capsules, twice daily",
            "ingredients": ["Ashwagandha (Withania somnifera) root extract"],
            "precautions": ["May increase thyroid hormone"],
            "contraindications": ["Hyperthyroidism", "Pregnancy"],
            "preparation_method": "Ashwagandha roots are extracted and encapsulated.",
            "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
            "illness_categories": ["men", "stress"],
            "symptoms": ["stress", "anxiety", "low stamina", "muscle weakness", "insomnia"]
        },
        {
            "medicine_id": "safed-musli",
            "name": "Safed Musli Churna",
            "sanskrit_name": "Shweta Musli",
            "description": "Natural aphrodisiac and energy booster",
            "usage": "Take 1/2 teaspoon with warm milk at bedtime.",
            "dosage": "1/2 teaspoon with milk, at bedtime",
            "ingredients": ["Safed Musli (Chlorophytum borivilianum) root powder"],
            "precautions": ["May take 4-6 weeks for full effect"],
            "contraindications": ["Diabetes (monitor sugar)"],
            "preparation_method": "Musli roots are dried and powdered.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["men"],
            "symptoms": ["low libido", "weakness", "low sperm count", "erectile dysfunction"]
        },
        # Children's Health
        {
            "medicine_id": "bala-chaturbhadra",
            "name": "Bala Chaturbhadra",
            "sanskrit_name": "Bala Chaturbhadra",
            "description": "Classical formula for children's fever and digestive issues",
            "usage": "Give 125-250mg with honey 2-3 times daily based on age.",
            "dosage": "125-250mg based on age",
            "ingredients": ["Musta", "Pippali", "Ativisha", "Karkatashringi"],
            "precautions": ["Adjust dose by age and weight"],
            "contraindications": ["None when used appropriately"],
            "preparation_method": "Child-safe herbs powdered in specific proportions.",
            "image_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9",
            "illness_categories": ["children", "fever"],
            "symptoms": ["children fever", "colic", "indigestion in children", "diarrhea"]
        },
        {
            "medicine_id": "swarna-prashana",
            "name": "Swarna Prashana",
            "sanskrit_name": "Swarna Prashana",
            "description": "Gold-based immunity drops for children",
            "usage": "Give 2-4 drops on empty stomach, preferably on Pushya Nakshatra day.",
            "dosage": "2-4 drops, traditionally monthly",
            "ingredients": ["Swarna Bhasma (Gold ash)", "Honey", "Ghee", "Brahmi", "Vacha"],
            "precautions": ["Get from authentic Ayurvedic center"],
            "contraindications": ["None when authentic"],
            "preparation_method": "Purified gold processed with brain-boosting herbs.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["children", "general"],
            "symptoms": ["low immunity in children", "poor memory", "frequent illness", "growth"]
        },
        {
            "medicine_id": "vidangarishta",
            "name": "Vidangarishta",
            "sanskrit_name": "Vidangarishta",
            "description": "For intestinal worms in children",
            "usage": "Give 5-15ml (age-based) with equal water after meals.",
            "dosage": "5-15ml based on age, after meals",
            "ingredients": ["Vidanga", "Pippali", "Chitraka", "Dhataki", "Jaggery"],
            "precautions": ["Give for limited duration"],
            "contraindications": ["Children under 2 years"],
            "preparation_method": "Fermented preparation of anti-parasitic herbs.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["children", "digestive"],
            "symptoms": ["worms", "loss of appetite in children", "teeth grinding", "stomach pain"]
        },
        # Weight Management
        {
            "medicine_id": "medohar-guggulu",
            "name": "Medohar Guggulu",
            "sanskrit_name": "Medohar Guggulu",
            "description": "Classical formula for weight loss and fat metabolism",
            "usage": "Take 2 tablets with warm water twice daily before meals.",
            "dosage": "2 tablets, twice daily before meals",
            "ingredients": ["Guggulu", "Triphala", "Trikatu", "Vidanga", "Musta"],
            "precautions": ["Exercise and diet changes needed too"],
            "contraindications": ["Pregnancy", "Hyperthyroidism"],
            "preparation_method": "Herbs processed with purified guggulu resin.",
            "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b",
            "illness_categories": ["weight", "cholesterol"],
            "symptoms": ["obesity", "high cholesterol", "slow metabolism", "stubborn fat"]
        },
        {
            "medicine_id": "garcinia-cambogia",
            "name": "Vrikshamla Capsules",
            "sanskrit_name": "Vrikshamla",
            "description": "Garcinia for appetite control and fat blocking",
            "usage": "Take 1 capsule before meals twice daily.",
            "dosage": "1 capsule before meals, twice daily",
            "ingredients": ["Vrikshamla (Garcinia cambogia) extract"],
            "precautions": ["Don't exceed recommended dose"],
            "contraindications": ["Liver disease", "Pregnancy", "Diabetes medications"],
            "preparation_method": "Garcinia fruit rind is extracted and standardized.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["weight"],
            "symptoms": ["weight gain", "overeating", "sugar cravings", "fat accumulation"]
        },
        {
            "medicine_id": "ashwagandha-weight",
            "name": "Ashwagandha for Weight Gain",
            "sanskrit_name": "Ashwagandha",
            "description": "For healthy weight gain and muscle building",
            "usage": "Take 1 teaspoon with warm milk and ghee twice daily.",
            "dosage": "1 teaspoon with milk & ghee, twice daily",
            "ingredients": ["Ashwagandha powder", "Milk", "Ghee"],
            "precautions": ["Combine with protein-rich diet"],
            "contraindications": ["Hyperthyroidism"],
            "preparation_method": "Ashwagandha taken with anabolic carriers (milk, ghee).",
            "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
            "illness_categories": ["weight", "men"],
            "symptoms": ["underweight", "muscle wasting", "weakness", "poor appetite"]
        },
        # Blood Pressure
        {
            "medicine_id": "sarpagandha-vati",
            "name": "Sarpagandha Vati",
            "sanskrit_name": "Sarpagandha",
            "description": "Classical medicine for high blood pressure",
            "usage": "Take 1 tablet twice daily under practitioner supervision.",
            "dosage": "1 tablet, twice daily",
            "ingredients": ["Sarpagandha (Rauwolfia serpentina)", "Jatamansi", "Bhringaraj"],
            "precautions": ["Must monitor BP regularly", "Use only under supervision"],
            "contraindications": ["Low BP", "Depression", "Pregnancy"],
            "preparation_method": "Sarpagandha processed with supportive herbs.",
            "image_url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef",
            "illness_categories": ["bp", "stress"],
            "symptoms": ["high blood pressure", "hypertension", "anxiety", "insomnia"]
        },
        {
            "medicine_id": "brahmi-bp",
            "name": "Brahmi for BP",
            "sanskrit_name": "Brahmi",
            "description": "Calming herb for stress-related blood pressure",
            "usage": "Take 1/2 teaspoon with warm water twice daily.",
            "dosage": "1/2 teaspoon, twice daily",
            "ingredients": ["Brahmi (Bacopa monnieri) powder"],
            "precautions": ["May cause drowsiness"],
            "contraindications": ["Bradycardia", "Low BP"],
            "preparation_method": "Whole brahmi plant is shade-dried and powdered.",
            "image_url": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d",
            "illness_categories": ["bp", "stress"],
            "symptoms": ["stress-related BP", "anxiety", "mental tension", "headache"]
        },
        # Cholesterol
        {
            "medicine_id": "guggulu-cholesterol",
            "name": "Triphala Guggulu",
            "sanskrit_name": "Triphala Guggulu",
            "description": "For cholesterol management and arterial health",
            "usage": "Take 2 tablets with warm water twice daily after meals.",
            "dosage": "2 tablets, twice daily after meals",
            "ingredients": ["Triphala", "Guggulu", "Pippali"],
            "precautions": ["May thin blood slightly"],
            "contraindications": ["Bleeding disorders", "Pre-surgery"],
            "preparation_method": "Triphala processed with purified guggulu.",
            "image_url": "https://images.unsplash.com/photo-1587049352851-8d4e89133924",
            "illness_categories": ["cholesterol", "weight"],
            "symptoms": ["high cholesterol", "high triglycerides", "arterial blockage", "obesity"]
        },
        {
            "medicine_id": "lasuna-capsules",
            "name": "Lasuna Capsules",
            "sanskrit_name": "Lasuna",
            "description": "Garlic capsules for heart and cholesterol health",
            "usage": "Take 1-2 capsules after meals twice daily.",
            "dosage": "1-2 capsules, twice daily after meals",
            "ingredients": ["Lasuna (Garlic) extract"],
            "precautions": ["May cause garlic breath", "Avoid before surgery"],
            "contraindications": ["Bleeding disorders", "Pre-surgery"],
            "preparation_method": "Garlic is processed to reduce odor while retaining benefits.",
            "image_url": "https://images.unsplash.com/photo-1556228578-0d85b1a4d571",
            "illness_categories": ["cholesterol", "heart", "bp"],
            "symptoms": ["high cholesterol", "high BP", "heart disease", "poor circulation"]
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
        },
        {
            "practitioner_id": "dr-wickramasinghe-colombo",
            "name": "Dr. Dinesh Wickramasinghe",
            "title": "BAMS, MD (Kayachikitsa)",
            "specializations": ["Panchakarma", "Diabetes Management", "Chronic Diseases"],
            "experience_years": 24,
            "qualifications": ["BAMS - University of Colombo", "MD Kayachikitsa - Institute of Indigenous Medicine"],
            "clinic_name": "Lanka Ayurveda Bhavan",
            "address": "42, Bauddhaloka Mawatha, Colombo 07",
            "city": "Colombo",
            "state": "Western Province",
            "phone": "+94 11 269 4455",
            "email": "dr.dinesh@lankaayurveda.lk",
            "consultation_fee": "Rs. 2500",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "rating": 4.9,
            "reviews_count": 378,
            "image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d",
            "bio": "Dr. Wickramasinghe is one of Sri Lanka's most respected Ayurvedic physicians, combining traditional Hela Wedakama with classical Ayurvedic Panchakarma therapies."
        },
        {
            "practitioner_id": "dr-rajapaksha-kandy",
            "name": "Dr. Thilini Rajapaksha",
            "title": "BAMS, MSc (Clinical Ayurveda)",
            "specializations": ["Women's Health", "Fertility", "Skin Disorders", "Rasayana"],
            "experience_years": 16,
            "qualifications": ["BAMS - University of Kelaniya", "MSc Clinical Ayurveda - Gampaha Wickramarachchi University"],
            "clinic_name": "Kandyan Ayurveda Wellness",
            "address": "15, Peradeniya Road, Near Dalada Maligawa",
            "city": "Kandy",
            "state": "Central Province",
            "phone": "+94 81 222 3344",
            "email": "dr.thilini@kandyanayurveda.lk",
            "consultation_fee": "Rs. 2000",
            "available_days": ["Monday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "rating": 4.8,
            "reviews_count": 212,
            "image_url": "https://images.unsplash.com/photo-1594824476967-48c8b964273f",
            "bio": "Dr. Rajapaksha specializes in women's health and fertility using traditional Sri Lankan Ayurvedic remedies passed down through generations of healers in the hill country."
        },
        {
            "practitioner_id": "dr-jayawardena-galle",
            "name": "Dr. Chaminda Jayawardena",
            "title": "BAMS, MD (Shalya Tantra)",
            "specializations": ["Joint Disorders", "Pain Management", "Marma Therapy"],
            "experience_years": 20,
            "qualifications": ["BAMS - University of Ruhuna", "MD Shalya - Institute of Indigenous Medicine, Colombo"],
            "clinic_name": "Galle Fort Ayurveda Center",
            "address": "68, Lighthouse Street, Galle Fort",
            "city": "Galle",
            "state": "Southern Province",
            "phone": "+94 91 223 4567",
            "email": "info@galleayurveda.lk",
            "consultation_fee": "Rs. 1800",
            "available_days": ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "rating": 4.7,
            "reviews_count": 156,
            "image_url": "https://images.unsplash.com/photo-1537368910025-700350fe46c7",
            "bio": "Practicing within the historic Galle Fort, Dr. Jayawardena is renowned for his Marma therapy and traditional bone-setting techniques from the Southern Sri Lankan tradition."
        },
        {
            "practitioner_id": "dr-sivarajah-jaffna",
            "name": "Dr. Vasanthi Sivarajah",
            "title": "BAMS, MD (Dravyaguna)",
            "specializations": ["Herbal Medicine", "Respiratory Disorders", "Siddha-Ayurveda"],
            "experience_years": 19,
            "qualifications": ["BAMS - University of Jaffna", "MD Dravyaguna - University of Colombo"],
            "clinic_name": "Nallur Ayurveda Vaithiyasalai",
            "address": "23, Temple Road, Near Nallur Kovil",
            "city": "Jaffna",
            "state": "Northern Province",
            "phone": "+94 21 222 8899",
            "email": "dr.vasanthi@nallurhealing.lk",
            "consultation_fee": "Rs. 1500",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Friday", "Saturday"],
            "rating": 4.8,
            "reviews_count": 143,
            "image_url": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2",
            "bio": "Dr. Sivarajah uniquely integrates Siddha and Ayurvedic traditions, drawing on the rich Tamil medicinal heritage of Northern Sri Lanka for respiratory and herbal treatments."
        },
        {
            "practitioner_id": "dr-kulkarni-pune",
            "name": "Dr. Anita Kulkarni",
            "title": "BAMS, MD (Prasuti Tantra)",
            "specializations": ["Women's Health", "Pregnancy Care", "Pediatric Ayurveda"],
            "experience_years": 21,
            "qualifications": ["BAMS - Tilak Ayurveda Mahavidyalaya, Pune", "MD Prasuti Tantra - Pune University"],
            "clinic_name": "Sahaja Ayurveda Clinic",
            "address": "12, FC Road, Shivajinagar",
            "city": "Pune",
            "state": "Maharashtra",
            "phone": "+91 20 2553 4455",
            "email": "dr.anita@sahajaayurveda.com",
            "consultation_fee": "₹800",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Saturday"],
            "rating": 4.7,
            "reviews_count": 234,
            "image_url": "https://images.unsplash.com/photo-1651008376811-b90baee60c1f",
            "bio": "Dr. Kulkarni is a leading practitioner in prenatal and postnatal Ayurvedic care, helping mothers and children through gentle, time-tested herbal protocols."
        },
        {
            "practitioner_id": "dr-trivedi-ahmedabad",
            "name": "Dr. Harsh Trivedi",
            "title": "BAMS, MD (Rasashastra)",
            "specializations": ["Diabetes", "Metabolic Disorders", "Detoxification"],
            "experience_years": 23,
            "qualifications": ["BAMS - Gujarat Ayurved University, Jamnagar", "MD Rasashastra - IPGT&RA, Jamnagar"],
            "clinic_name": "Arogya Ayurveda Hospital",
            "address": "SG Highway, Near Vastrapur Lake",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "phone": "+91 79 2685 1234",
            "email": "dr.trivedi@arogyaayurveda.in",
            "consultation_fee": "₹700",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "rating": 4.8,
            "reviews_count": 267,
            "image_url": "https://images.unsplash.com/photo-1622253692010-333f2da6031d",
            "bio": "Trained at the prestigious Gujarat Ayurved University in Jamnagar, Dr. Trivedi brings deep expertise in mineral-based Ayurvedic preparations for metabolic and lifestyle disorders."
        },
        {
            "practitioner_id": "dr-mukherjee-kolkata",
            "name": "Dr. Sanjay Mukherjee",
            "title": "BAMS, PhD (Kayachikitsa)",
            "specializations": ["Digestive Disorders", "Liver Health", "Chronic Diseases"],
            "experience_years": 26,
            "qualifications": ["BAMS - J.B. Roy State Ayurvedic College, Kolkata", "PhD Kayachikitsa - BHU"],
            "clinic_name": "Bengal Ayurveda Chikitsalaya",
            "address": "8/2, Gariahat Road, Ballygunge",
            "city": "Kolkata",
            "state": "West Bengal",
            "phone": "+91 33 2461 7890",
            "email": "dr.mukherjee@bengalayurveda.com",
            "consultation_fee": "₹600",
            "available_days": ["Monday", "Tuesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "rating": 4.7,
            "reviews_count": 198,
            "image_url": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d",
            "bio": "With a PhD from BHU, Dr. Mukherjee combines rigorous academic research with Bengal's rich tradition of Ayurvedic gastroenterology and liver care."
        },
        {
            "practitioner_id": "dr-mishra-lucknow",
            "name": "Dr. Priya Mishra",
            "title": "BAMS, MD (Swasthavritta)",
            "specializations": ["Preventive Care", "Weight Management", "Yoga Therapy"],
            "experience_years": 14,
            "qualifications": ["BAMS - State Ayurvedic College, Lucknow", "MD Swasthavritta - Rishikul Govt. Ayurvedic College"],
            "clinic_name": "Awadh Ayurveda Wellness",
            "address": "Hazratganj, Near Sahara Ganj Mall",
            "city": "Lucknow",
            "state": "Uttar Pradesh",
            "phone": "+91 522 400 5566",
            "email": "dr.priya@awadhayurveda.in",
            "consultation_fee": "₹500",
            "available_days": ["Monday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "rating": 4.6,
            "reviews_count": 145,
            "image_url": "https://images.unsplash.com/photo-1594824476967-48c8b964273f",
            "bio": "Dr. Mishra integrates Yoga therapy with Ayurvedic preventive care, specializing in lifestyle modifications and weight management programs rooted in classical Swasthavritta principles."
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
