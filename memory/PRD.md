# Ayur Vaidya - Ayurvedic Medicine Recommender PRD

## Original Problem Statement
"Can we develop an ayurvedic program to suggest different ayurvedic medicine for simple illnesses"

## User Personas
1. **Health-Conscious Individual** - Seeks natural remedies for common ailments
2. **Ayurveda Enthusiast** - Wants comprehensive information about traditional medicines
3. **Caregiver** - Looking for safe, natural options for family members

## Core Requirements (Static)
- Browse medicines by illness category
- Comprehensive medicine information (name, usage, dosage, ingredients, precautions, contraindications, preparation method)
- Symptom checker functionality
- Search capability
- Google OAuth authentication
- Mobile-responsive design

## Architecture
- **Frontend**: React 19 with Tailwind CSS, Shadcn UI components
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: Emergent Google OAuth

## What's Been Implemented

### Backend Features
- Google OAuth integration with Emergent Auth
- 20 Illness categories (Respiratory, Digestive, Fever, Headache, Skin, Stress, Allergies, Diabetes, Joints, General, Hair, Eyes, Heart, Liver/Kidney, Women's, Men's, Children's, Weight, BP, Cholesterol)
- 76 Ayurvedic medicines with comprehensive info
- Symptom checker API
- Search functionality
- Medicine detail API
- Category-based browsing
- **Practitioner Directory API** - 16 practitioners across 16 cities (India + Sri Lanka)
- Practitioner search/filter by city and specialization
- **Booking System** - create/view/cancel appointments, available time slots
- **Reviews System** - create reviews, view practitioner reviews, auto-update ratings
- **Favorites System** - add/remove favorites for medicines and practitioners
- Health check endpoint

### Frontend Features
- **Beautiful Landing Page** with "Ayur Vaidya - Nature's Way of Healing" branding
  - Hero with improved contrast (dark overlay, terracotta accent color)
  - "How It Works" 3-step process section
  - Three Doshas (Tridosha) section
  - 20 Health Categories grid
  - Puskola Potha (ancient heritage) section
  - Sacred Elements (Pahana, Tulsi, Kumbha) section
  - Practitioner Locations (India & Sri Lanka) section
  - Trust/Safety indicators
  - CTA section
- Login page with Google OAuth
- Dashboard with welcome banner, quick actions
- Symptom checker with multi-select symptoms
- Category pages with medicine listings
- Medicine detail pages with full information + favorite button
- Search functionality
- **Practitioner Directory** with search, city/specialization filters
- **Practitioner Booking** - calendar picker, time slots, appointment confirmation
- **Reviews & Ratings** - write reviews, view practitioner reviews
- **My Appointments page** - view/cancel bookings
- **My Favorites page** - saved medicines and practitioners with tabs
- **User menu** with Favorites, Appointments, Logout
- Protected routes with authentication
- Responsive design with earthy, organic theme (Cormorant Garamond + Outfit fonts)

### Practitioner Coverage
**India (12 cities):** New Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Jaipur, Varanasi, Pune, Ahmedabad, Kolkata, Lucknow, Kerala (Thiruvananthapuram)
**Sri Lanka (4 cities):** Colombo, Kandy, Galle, Jaffna

### Design System
- Theme: Organic & Earthy (Light)
- Primary Color: #2C4C3B (Moss Green)
- Accent Color: #E07A5F (Terracotta)
- Background: #F9F6F0 (Warm Sand)
- Dark sections: #1A2421, #0D1B16
- Typography: Cormorant Garamond (headings), Outfit (body)

## Prioritized Backlog

### P0 (Critical) - ALL DONE
- [x] Google OAuth authentication
- [x] Browse medicines by category (20 categories)
- [x] Symptom checker
- [x] Medicine details page
- [x] Landing page with branding and improved contrast
- [x] Practitioner booking/appointments
- [x] Reviews and ratings system
- [x] Favorites for medicines and practitioners
- [x] Expanded medicine database (76 medicines)
- [x] Expanded practitioner network (16 practitioners, India + Sri Lanka)
- [x] Landing page new sections (How It Works, Categories, Locations, Trust)

### P1 (High Priority)
- [ ] Email/SMS appointment reminders
- [ ] Appointment rescheduling
- [ ] Print medicine information
- [ ] Practitioner availability calendar management

### P2 (Medium Priority)
- [ ] Refactor seed data out of server.py into separate file
- [ ] User notes on medicines
- [ ] Dosage calculator based on age/weight
- [ ] Medicine comparison feature
- [ ] Share medicine info via social/email

### P3 (Low Priority)
- [ ] Dark mode theme
- [ ] Multi-language support (Sanskrit, Hindi, Tamil, Sinhala)
- [ ] Community reviews/experiences
- [ ] PWA for offline access

## Next Tasks
1. Refactor seed data from server.py to separate seed_data.py file
2. Add print functionality for medicine details
3. Consider PWA for offline access
