import { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { 
  getPractitioners, 
  getPractitionerCities, 
  getPractitionerSpecializations,
  getAvailableSlots,
  createBooking,
  getPractitionerReviews,
  createReview,
  addFavorite,
  removeFavorite,
  checkFavorite
} from "@/services/api";
import { toast } from "sonner";
import { 
  Search,
  MapPin,
  Star,
  Phone,
  Mail,
  Clock,
  Award,
  GraduationCap,
  Stethoscope,
  ChevronRight,
  Filter,
  X,
  Calendar,
  Heart,
  MessageSquare,
  Send
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { format } from "date-fns";

const PractitionersPage = () => {
  const [practitioners, setPractitioners] = useState([]);
  const [cities, setCities] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState("");
  const [selectedSpec, setSelectedSpec] = useState("");
  const [selectedPractitioner, setSelectedPractitioner] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadPractitioners();
  }, [selectedCity, selectedSpec]);

  const loadInitialData = async () => {
    try {
      const [citiesData, specsData] = await Promise.all([
        getPractitionerCities(),
        getPractitionerSpecializations()
      ]);
      setCities(citiesData);
      setSpecializations(specsData);
    } catch (error) {
      console.error("Failed to load filter data:", error);
    }
  };

  const loadPractitioners = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedCity) params.city = selectedCity;
      if (selectedSpec) params.specialization = selectedSpec;
      if (searchQuery) params.search = searchQuery;
      
      const data = await getPractitioners(params);
      setPractitioners(data);
    } catch (error) {
      console.error("Failed to load practitioners:", error);
      toast.error("Failed to load practitioners");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadPractitioners();
  };

  const clearFilters = () => {
    setSelectedCity("");
    setSelectedSpec("");
    setSearchQuery("");
  };

  const hasActiveFilters = selectedCity || selectedSpec || searchQuery;

  return (
    <div className="min-h-screen bg-background" data-testid="practitioners-page">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="relative rounded-2xl overflow-hidden mb-8 animate-fadeIn">
          <img
            src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d"
            alt="Ayurvedic consultation"
            className="w-full h-48 sm:h-64 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-text-primary/90 via-text-primary/70 to-transparent" />
          <div className="absolute inset-0 flex items-center px-6 sm:px-10">
            <div>
              <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary-foreground/70 mb-2 block">
                Find Expert Care
              </span>
              <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-semibold text-white mb-2">
                Practitioner Directory
              </h1>
              <p className="text-white/80 font-sans text-sm sm:text-base max-w-lg">
                Connect with experienced Ayurvedic practitioners for personalized consultations
              </p>
            </div>
          </div>
        </div>

        {/* Search & Filters */}
        <div className="bg-surface rounded-2xl border border-border p-4 sm:p-6 mb-8 animate-fadeIn delay-100">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-4">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
              <input
                type="text"
                placeholder="Search by name, clinic, or specialization..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input pl-12 w-full"
                data-testid="practitioner-search-input"
              />
            </div>

            {/* Desktop Filters */}
            <div className="hidden md:flex items-center gap-3">
              <Select value={selectedCity || "all"} onValueChange={(val) => setSelectedCity(val === "all" ? "" : val)}>
                <SelectTrigger className="w-[180px] bg-surface-alt border-border" data-testid="city-filter">
                  <MapPin className="w-4 h-4 mr-2 text-text-secondary" />
                  <SelectValue placeholder="All Cities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Cities</SelectItem>
                  {cities.map((city) => (
                    <SelectItem key={city} value={city}>{city}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedSpec || "all"} onValueChange={(val) => setSelectedSpec(val === "all" ? "" : val)}>
                <SelectTrigger className="w-[200px] bg-surface-alt border-border" data-testid="specialization-filter">
                  <Stethoscope className="w-4 h-4 mr-2 text-text-secondary" />
                  <SelectValue placeholder="All Specializations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Specializations</SelectItem>
                  {specializations.map((spec) => (
                    <SelectItem key={spec} value={spec}>{spec}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button type="submit" className="btn-primary" data-testid="search-practitioners-button">
                Search
              </Button>
            </div>

            {/* Mobile Filter Toggle */}
            <div className="flex md:hidden gap-2">
              <Button 
                type="button" 
                variant="outline" 
                className="flex-1 border-border"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
                {hasActiveFilters && (
                  <Badge className="ml-2 bg-primary text-primary-foreground text-xs">
                    {[selectedCity, selectedSpec].filter(Boolean).length}
                  </Badge>
                )}
              </Button>
              <Button type="submit" className="btn-primary">
                Search
              </Button>
            </div>
          </form>

          {/* Mobile Filters Panel */}
          {showFilters && (
            <div className="md:hidden mt-4 pt-4 border-t border-border space-y-3 animate-fadeIn">
              <Select value={selectedCity || "all"} onValueChange={(val) => setSelectedCity(val === "all" ? "" : val)}>
                <SelectTrigger className="w-full bg-surface-alt border-border">
                  <MapPin className="w-4 h-4 mr-2 text-text-secondary" />
                  <SelectValue placeholder="All Cities" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Cities</SelectItem>
                  {cities.map((city) => (
                    <SelectItem key={city} value={city}>{city}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={selectedSpec || "all"} onValueChange={(val) => setSelectedSpec(val === "all" ? "" : val)}>
                <SelectTrigger className="w-full bg-surface-alt border-border">
                  <Stethoscope className="w-4 h-4 mr-2 text-text-secondary" />
                  <SelectValue placeholder="All Specializations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Specializations</SelectItem>
                  {specializations.map((spec) => (
                    <SelectItem key={spec} value={spec}>{spec}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Active Filters */}
          {hasActiveFilters && (
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
              <span className="text-xs text-text-secondary font-sans">Active filters:</span>
              {selectedCity && (
                <Badge variant="secondary" className="bg-primary/10 text-primary">
                  {selectedCity}
                  <button onClick={() => setSelectedCity("")} className="ml-1">
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              )}
              {selectedSpec && (
                <Badge variant="secondary" className="bg-primary/10 text-primary">
                  {selectedSpec}
                  <button onClick={() => setSelectedSpec("")} className="ml-1">
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              )}
              <button 
                onClick={clearFilters}
                className="text-xs text-accent hover:text-accent/80 font-sans font-medium ml-auto"
              >
                Clear all
              </button>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-serif text-xl font-semibold text-text-primary">
            {loading ? "Searching..." : `${practitioners.length} Practitioner${practitioners.length !== 1 ? 's' : ''} Found`}
          </h2>
        </div>

        {/* Practitioners Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="loading-spinner"></div>
          </div>
        ) : practitioners.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {practitioners.map((practitioner, index) => (
              <div 
                key={practitioner.practitioner_id}
                className="animate-fadeIn"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <PractitionerCard 
                  practitioner={practitioner} 
                  onClick={() => setSelectedPractitioner(practitioner)}
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state bg-surface rounded-2xl border border-border py-16">
            <div className="empty-state-icon">
              <Stethoscope className="w-10 h-10 text-text-secondary" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
              No Practitioners Found
            </h3>
            <p className="text-text-secondary font-sans mb-4">
              Try adjusting your search criteria or filters
            </p>
            <Button onClick={clearFilters} className="btn-secondary">
              Clear Filters
            </Button>
          </div>
        )}

        {/* Practitioner Detail Modal */}
        <Dialog open={!!selectedPractitioner} onOpenChange={() => setSelectedPractitioner(null)}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-surface border-border">
            {selectedPractitioner && (
              <PractitionerDetailEnhanced 
                practitioner={selectedPractitioner} 
                onClose={() => setSelectedPractitioner(null)}
              />
            )}
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
};

// Practitioner Card Component
const PractitionerCard = ({ practitioner, onClick }) => {
  return (
    <div 
      className="bg-surface rounded-2xl border border-border p-5 hover:shadow-lg transition-all cursor-pointer card-hover"
      onClick={onClick}
      data-testid={`practitioner-card-${practitioner.practitioner_id}`}
    >
      <div className="flex gap-4">
        {/* Avatar */}
        <div className="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0">
          <img
            src={practitioner.image_url || "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d"}
            alt={practitioner.name}
            className="w-full h-full object-cover"
          />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="font-serif text-lg font-semibold text-text-primary truncate">
              {practitioner.name}
            </h3>
            <div className="flex items-center gap-1 flex-shrink-0">
              <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
              <span className="text-sm font-sans font-medium text-text-primary">{practitioner.rating}</span>
              <span className="text-xs text-text-secondary">({practitioner.reviews_count})</span>
            </div>
          </div>
          
          <p className="text-sm text-text-secondary font-sans mb-2">
            {practitioner.title}
          </p>

          <div className="flex items-center gap-1 text-sm text-text-secondary font-sans mb-2">
            <MapPin className="w-3.5 h-3.5" />
            <span className="truncate">{practitioner.clinic_name}, {practitioner.city}</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {practitioner.specializations?.slice(0, 3).map((spec, index) => (
              <Badge 
                key={index} 
                variant="secondary"
                className="bg-primary/10 text-primary text-xs border-0"
              >
                {spec}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
        <div className="flex items-center gap-4 text-sm text-text-secondary font-sans">
          <span className="flex items-center gap-1">
            <Award className="w-4 h-4" />
            {practitioner.experience_years} yrs exp
          </span>
          <span className="font-medium text-primary">
            {practitioner.consultation_fee}
          </span>
        </div>
        <ChevronRight className="w-5 h-5 text-text-secondary" />
      </div>
    </div>
  );
};

// Practitioner Detail Component
const PractitionerDetail = ({ practitioner }) => {
  return (
    <>
      <DialogHeader>
        <div className="flex gap-4">
          <div className="w-24 h-24 rounded-xl overflow-hidden flex-shrink-0">
            <img
              src={practitioner.image_url || "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d"}
              alt={practitioner.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div>
            <DialogTitle className="font-serif text-2xl font-semibold text-text-primary mb-1">
              {practitioner.name}
            </DialogTitle>
            <p className="text-text-secondary font-sans">{practitioner.title}</p>
            <div className="flex items-center gap-2 mt-2">
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                <span className="font-sans font-medium">{practitioner.rating}</span>
              </div>
              <span className="text-text-secondary text-sm">({practitioner.reviews_count} reviews)</span>
            </div>
          </div>
        </div>
      </DialogHeader>

      <div className="space-y-6 mt-4">
        {/* Bio */}
        {practitioner.bio && (
          <p className="text-text-secondary font-sans text-sm leading-relaxed">
            {practitioner.bio}
          </p>
        )}

        {/* Specializations */}
        <div>
          <h4 className="font-serif text-lg font-semibold text-text-primary mb-2 flex items-center gap-2">
            <Stethoscope className="w-5 h-5 text-primary" />
            Specializations
          </h4>
          <div className="flex flex-wrap gap-2">
            {practitioner.specializations?.map((spec, index) => (
              <Badge 
                key={index} 
                variant="secondary"
                className="bg-primary/10 text-primary border-0"
              >
                {spec}
              </Badge>
            ))}
          </div>
        </div>

        {/* Qualifications */}
        <div>
          <h4 className="font-serif text-lg font-semibold text-text-primary mb-2 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-primary" />
            Qualifications
          </h4>
          <ul className="space-y-1">
            {practitioner.qualifications?.map((qual, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-text-secondary font-sans">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                {qual}
              </li>
            ))}
          </ul>
        </div>

        <Separator className="bg-border" />

        {/* Contact & Location */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-surface-alt rounded-xl p-4 border border-border">
            <h4 className="font-serif font-semibold text-text-primary mb-3 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-accent" />
              Location
            </h4>
            <p className="text-sm font-sans font-medium text-text-primary mb-1">
              {practitioner.clinic_name}
            </p>
            <p className="text-sm text-text-secondary font-sans">
              {practitioner.address}<br />
              {practitioner.city}, {practitioner.state}
            </p>
          </div>

          <div className="bg-surface-alt rounded-xl p-4 border border-border">
            <h4 className="font-serif font-semibold text-text-primary mb-3 flex items-center gap-2">
              <Clock className="w-5 h-5 text-accent" />
              Availability
            </h4>
            <p className="text-sm text-text-secondary font-sans">
              {practitioner.available_days?.join(", ")}
            </p>
            <p className="text-sm font-medium text-primary mt-2">
              Consultation: {practitioner.consultation_fee}
            </p>
          </div>
        </div>

        {/* Contact Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          {practitioner.phone && (
            <a 
              href={`tel:${practitioner.phone}`}
              className="btn-primary flex items-center justify-center gap-2 flex-1"
              data-testid="call-practitioner-button"
            >
              <Phone className="w-4 h-4" />
              Call Now
            </a>
          )}
          {practitioner.email && (
            <a 
              href={`mailto:${practitioner.email}`}
              className="btn-secondary flex items-center justify-center gap-2 flex-1"
              data-testid="email-practitioner-button"
            >
              <Mail className="w-4 h-4" />
              Send Email
            </a>
          )}
        </div>
      </div>
    </>
  );
};

// Enhanced Practitioner Detail with Booking & Reviews
const PractitionerDetailEnhanced = ({ practitioner, onClose }) => {
  const [activeTab, setActiveTab] = useState("info");
  const [selectedDate, setSelectedDate] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [bookingReason, setBookingReason] = useState("");
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [newReview, setNewReview] = useState({ rating: 5, comment: "" });
  const [submittingReview, setSubmittingReview] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);

  useEffect(() => {
    loadReviews();
    checkIfFavorited();
  }, [practitioner.practitioner_id]);

  useEffect(() => {
    if (selectedDate) {
      loadSlots();
    }
  }, [selectedDate]);

  const loadSlots = async () => {
    try {
      setLoadingSlots(true);
      const dateStr = format(selectedDate, "yyyy-MM-dd");
      const data = await getAvailableSlots(practitioner.practitioner_id, dateStr);
      setAvailableSlots(data.available_slots);
    } catch (error) {
      console.error("Failed to load slots:", error);
      toast.error("Failed to load available slots");
    } finally {
      setLoadingSlots(false);
    }
  };

  const loadReviews = async () => {
    try {
      setLoadingReviews(true);
      const data = await getPractitionerReviews(practitioner.practitioner_id);
      setReviews(data);
    } catch (error) {
      console.error("Failed to load reviews:", error);
    } finally {
      setLoadingReviews(false);
    }
  };

  const checkIfFavorited = async () => {
    try {
      const data = await checkFavorite("practitioner", practitioner.practitioner_id);
      setIsFavorited(data.is_favorited);
    } catch (error) {
      console.error("Failed to check favorite:", error);
    }
  };

  const toggleFavorite = async () => {
    try {
      setFavoriteLoading(true);
      if (isFavorited) {
        await removeFavorite("practitioner", practitioner.practitioner_id);
        toast.success("Removed from favorites");
      } else {
        await addFavorite("practitioner", practitioner.practitioner_id);
        toast.success("Added to favorites");
      }
      setIsFavorited(!isFavorited);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update favorites");
    } finally {
      setFavoriteLoading(false);
    }
  };

  const handleBooking = async () => {
    if (!selectedDate || !selectedSlot) {
      toast.error("Please select a date and time slot");
      return;
    }

    try {
      setBookingLoading(true);
      await createBooking({
        practitioner_id: practitioner.practitioner_id,
        date: format(selectedDate, "yyyy-MM-dd"),
        time_slot: selectedSlot,
        reason: bookingReason || null
      });
      toast.success("Appointment booked successfully!");
      setSelectedDate(null);
      setSelectedSlot(null);
      setBookingReason("");
      setActiveTab("info");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to book appointment");
    } finally {
      setBookingLoading(false);
    }
  };

  const handleSubmitReview = async () => {
    if (!newReview.comment.trim()) {
      toast.error("Please write a review comment");
      return;
    }

    try {
      setSubmittingReview(true);
      await createReview({
        practitioner_id: practitioner.practitioner_id,
        rating: newReview.rating,
        comment: newReview.comment
      });
      toast.success("Review submitted successfully!");
      setNewReview({ rating: 5, comment: "" });
      loadReviews();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to submit review");
    } finally {
      setSubmittingReview(false);
    }
  };

  return (
    <>
      <DialogHeader>
        <div className="flex gap-4">
          <div className="w-20 h-20 rounded-xl overflow-hidden flex-shrink-0">
            <img
              src={practitioner.image_url || "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d"}
              alt={practitioner.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1">
            <div className="flex items-start justify-between">
              <DialogTitle className="font-serif text-xl font-semibold text-text-primary mb-1">
                {practitioner.name}
              </DialogTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleFavorite}
                disabled={favoriteLoading}
                className={isFavorited ? "text-accent" : "text-text-secondary"}
                data-testid="favorite-practitioner-button"
              >
                <Heart className={`w-5 h-5 ${isFavorited ? "fill-current" : ""}`} />
              </Button>
            </div>
            <p className="text-text-secondary font-sans text-sm">{practitioner.title}</p>
            <div className="flex items-center gap-2 mt-1">
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                <span className="font-sans font-medium text-sm">{practitioner.rating}</span>
              </div>
              <span className="text-text-secondary text-xs">({practitioner.reviews_count} reviews)</span>
              <span className="text-primary font-medium text-sm ml-auto">{practitioner.consultation_fee}</span>
            </div>
          </div>
        </div>
      </DialogHeader>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
        <TabsList className="w-full bg-surface-alt border border-border">
          <TabsTrigger value="info" className="flex-1 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            Info
          </TabsTrigger>
          <TabsTrigger value="book" className="flex-1 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            <Calendar className="w-4 h-4 mr-1" />
            Book
          </TabsTrigger>
          <TabsTrigger value="reviews" className="flex-1 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
            <MessageSquare className="w-4 h-4 mr-1" />
            Reviews
          </TabsTrigger>
        </TabsList>

        {/* Info Tab */}
        <TabsContent value="info" className="space-y-4 mt-4">
          {practitioner.bio && (
            <p className="text-text-secondary font-sans text-sm leading-relaxed">
              {practitioner.bio}
            </p>
          )}

          <div>
            <h4 className="font-serif font-semibold text-text-primary mb-2 flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-primary" />
              Specializations
            </h4>
            <div className="flex flex-wrap gap-2">
              {practitioner.specializations?.map((spec, index) => (
                <Badge key={index} variant="secondary" className="bg-primary/10 text-primary text-xs border-0">
                  {spec}
                </Badge>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-serif font-semibold text-text-primary mb-2 flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-primary" />
              Qualifications
            </h4>
            <ul className="space-y-1">
              {practitioner.qualifications?.map((qual, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-text-secondary font-sans">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                  {qual}
                </li>
              ))}
            </ul>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-surface-alt rounded-xl p-3 border border-border">
              <div className="flex items-center gap-2 mb-2">
                <MapPin className="w-4 h-4 text-accent" />
                <span className="font-sans font-medium text-sm text-text-primary">Location</span>
              </div>
              <p className="text-xs text-text-secondary font-sans">
                {practitioner.clinic_name}<br />
                {practitioner.city}, {practitioner.state}
              </p>
            </div>
            <div className="bg-surface-alt rounded-xl p-3 border border-border">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-accent" />
                <span className="font-sans font-medium text-sm text-text-primary">Available</span>
              </div>
              <p className="text-xs text-text-secondary font-sans">
                {practitioner.available_days?.slice(0, 3).join(", ")}
                {practitioner.available_days?.length > 3 && "..."}
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            {practitioner.phone && (
              <a href={`tel:${practitioner.phone}`} className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm py-2">
                <Phone className="w-4 h-4" /> Call
              </a>
            )}
            {practitioner.email && (
              <a href={`mailto:${practitioner.email}`} className="btn-secondary flex-1 flex items-center justify-center gap-2 text-sm py-2">
                <Mail className="w-4 h-4" /> Email
              </a>
            )}
          </div>
        </TabsContent>

        {/* Booking Tab */}
        <TabsContent value="book" className="mt-4">
          <div className="space-y-4">
            <div>
              <h4 className="font-serif font-semibold text-text-primary mb-2">Select Date</h4>
              <div className="border border-border rounded-xl p-2 bg-surface-alt">
                <CalendarComponent
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  disabled={(date) => date < new Date() || date > new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)}
                  className="mx-auto"
                />
              </div>
            </div>

            {selectedDate && (
              <div className="animate-fadeIn">
                <h4 className="font-serif font-semibold text-text-primary mb-2">
                  Available Slots for {format(selectedDate, "MMM d, yyyy")}
                </h4>
                {loadingSlots ? (
                  <div className="flex justify-center py-4">
                    <div className="loading-spinner w-6 h-6"></div>
                  </div>
                ) : availableSlots.length > 0 ? (
                  <div className="grid grid-cols-3 gap-2">
                    {availableSlots.map((slot) => (
                      <button
                        key={slot}
                        onClick={() => setSelectedSlot(slot)}
                        className={`p-2 text-sm rounded-lg border transition-colors ${
                          selectedSlot === slot
                            ? "bg-primary text-primary-foreground border-primary"
                            : "bg-surface border-border hover:border-primary"
                        }`}
                        data-testid={`slot-${slot}`}
                      >
                        {slot}
                      </button>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-text-secondary font-sans text-sm py-4">
                    No slots available for this date
                  </p>
                )}
              </div>
            )}

            {selectedSlot && (
              <div className="animate-fadeIn">
                <h4 className="font-serif font-semibold text-text-primary mb-2">Reason for Visit (Optional)</h4>
                <Textarea
                  value={bookingReason}
                  onChange={(e) => setBookingReason(e.target.value)}
                  placeholder="Describe your symptoms or reason for consultation..."
                  className="bg-surface-alt border-border"
                />
              </div>
            )}

            <Button
              onClick={handleBooking}
              disabled={!selectedDate || !selectedSlot || bookingLoading}
              className="w-full btn-accent"
              data-testid="confirm-booking-button"
            >
              {bookingLoading ? "Booking..." : `Book Appointment - ${practitioner.consultation_fee}`}
            </Button>
          </div>
        </TabsContent>

        {/* Reviews Tab */}
        <TabsContent value="reviews" className="mt-4">
          <div className="space-y-4">
            {/* Write Review */}
            <div className="bg-surface-alt rounded-xl p-4 border border-border">
              <h4 className="font-serif font-semibold text-text-primary mb-3">Write a Review</h4>
              <div className="flex gap-1 mb-3">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setNewReview({ ...newReview, rating: star })}
                    className="p-1"
                  >
                    <Star 
                      className={`w-6 h-6 ${
                        star <= newReview.rating 
                          ? "text-yellow-500 fill-yellow-500" 
                          : "text-gray-300"
                      }`} 
                    />
                  </button>
                ))}
              </div>
              <Textarea
                value={newReview.comment}
                onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
                placeholder="Share your experience..."
                className="bg-surface border-border mb-3"
                rows={3}
              />
              <Button
                onClick={handleSubmitReview}
                disabled={submittingReview || !newReview.comment.trim()}
                className="btn-primary"
                data-testid="submit-review-button"
              >
                {submittingReview ? "Submitting..." : "Submit Review"}
                <Send className="w-4 h-4 ml-2" />
              </Button>
            </div>

            {/* Reviews List */}
            <div className="space-y-3">
              <h4 className="font-serif font-semibold text-text-primary">
                Patient Reviews ({reviews.length})
              </h4>
              {loadingReviews ? (
                <div className="flex justify-center py-4">
                  <div className="loading-spinner w-6 h-6"></div>
                </div>
              ) : reviews.length > 0 ? (
                reviews.map((review) => (
                  <div key={review.review_id} className="bg-surface rounded-xl p-4 border border-border">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        {review.user_picture ? (
                          <img src={review.user_picture} alt="" className="w-full h-full rounded-full object-cover" />
                        ) : (
                          <span className="text-primary font-semibold text-sm">
                            {review.user_name?.charAt(0) || "U"}
                          </span>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-sans font-medium text-sm text-text-primary">
                            {review.user_name}
                          </span>
                          <div className="flex items-center gap-0.5">
                            {[1, 2, 3, 4, 5].map((star) => (
                              <Star
                                key={star}
                                className={`w-3 h-3 ${
                                  star <= review.rating
                                    ? "text-yellow-500 fill-yellow-500"
                                    : "text-gray-300"
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        <p className="text-text-secondary font-sans text-sm">{review.comment}</p>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center text-text-secondary font-sans text-sm py-4">
                  No reviews yet. Be the first to review!
                </p>
              )}
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </>
  );
};

export default PractitionersPage;
