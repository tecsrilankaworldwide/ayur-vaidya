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
- Health check endpoint

### Frontend Features
- Beautiful login page with Google OAuth
- Dashboard with welcome banner and category grid
- Symptom checker with multi-select symptoms
- Category pages with medicine listings
- Medicine detail pages with full information
- Search functionality
- **Practitioner Directory** with search, city/specialization filters
- **Practitioner detail modal** with contact info (call/email)
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

### P1 (High Priority)
- [ ] User favorites/bookmarks
- [ ] Recently viewed medicines
- [ ] Print medicine information
- [ ] Practitioner booking integration
- [ ] Practitioner reviews system

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
