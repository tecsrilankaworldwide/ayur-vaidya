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
    
    # Insert new data
    await db.illness_categories.insert_many(categories)
    await db.medicines.insert_many(medicines)
    
    return {
        "message": "Database seeded successfully",
        "categories_count": len(categories),
        "medicines_count": len(medicines)
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
