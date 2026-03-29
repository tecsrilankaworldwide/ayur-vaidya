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

## What's Been Implemented (March 29, 2026)

### Backend Features
- Google OAuth integration with Emergent Auth
- 7 Illness categories (Respiratory, Digestive, Fever, Headache, Skin, Stress, Allergies)
- 21 Ayurvedic medicines with comprehensive info
- Symptom checker API (71 unique symptoms)
- Search functionality
- Medicine detail API
- Category-based browsing
- **Practitioner Directory API** - 8 practitioners across 8 cities
- Practitioner search/filter by city and specialization
- **Booking System** - create/view/cancel appointments, available time slots
- **Reviews System** - create reviews, view practitioner reviews, auto-update ratings
- **Favorites System** - add/remove favorites for medicines and practitioners
- Health check endpoint

### Frontend Features
- **Beautiful Landing Page** with "Ayur Vaidya - Nature's Way of Healing" branding
- Login page with Google OAuth
- Dashboard with welcome banner, quick actions (Symptom Checker, Browse, Find Practitioners)
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

### Design System
- Theme: Organic & Earthy (Light)
- Primary Color: #2C4C3B (Moss Green)
- Accent Color: #E07A5F (Terracotta)
- Background: #F9F6F0 (Warm Sand)
- Typography: Cormorant Garamond (headings), Outfit (body)

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Google OAuth authentication
- [x] Browse medicines by category
- [x] Symptom checker
- [x] Medicine details page
- [x] Landing page with branding
- [x] Practitioner booking/appointments
- [x] Reviews and ratings system
- [x] Favorites for medicines and practitioners

### P1 (High Priority)
- [ ] Email/SMS appointment reminders
- [ ] Appointment rescheduling
- [ ] Print medicine information
- [ ] Practitioner availability calendar management

### P2 (Medium Priority)
- [ ] User notes on medicines
- [ ] Dosage calculator based on age/weight
- [ ] Medicine comparison feature
- [ ] Share medicine info via social/email

### P3 (Low Priority)
- [ ] Dark mode theme
- [ ] Multi-language support (Sanskrit, Hindi)
- [ ] Community reviews/experiences
- [ ] Practitioner directory

## Next Tasks
1. Add user favorites feature
2. Implement recently viewed medicines
3. Add print functionality for medicine details
4. Consider PWA for offline access
