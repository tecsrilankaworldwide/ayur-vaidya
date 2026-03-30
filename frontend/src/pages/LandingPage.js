import { useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { 
  Leaf, 
  ArrowRight, 
  Sparkles, 
  Heart, 
  Users,
  ChevronRight,
  Star,
  Shield,
  Search,
  BookOpen,
  Calendar,
  MapPin,
  Quote
} from "lucide-react";
import { Button } from "@/components/ui/button";

const LandingPage = () => {
  const { user, checkAuth, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (window.location.hash?.includes('session_id=')) {
      return;
    }
    
    checkAuth().then((authenticated) => {
      if (authenticated) {
        navigate("/dashboard", { replace: true });
      }
    });
  }, [checkAuth, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background overflow-hidden" data-testid="landing-page">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1677599082447-6549af4c5454?crop=entropy&cs=srgb&fm=jpg&q=85"
            alt="Traditional Ayurvedic herbs and spices in wooden bowls"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0D1B16]/97 via-[#0D1B16]/90 to-[#0D1B16]/60" />
        </div>

        <header className="absolute top-0 left-0 right-0 z-20 px-6 py-6">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#E07A5F] rounded-full flex items-center justify-center shadow-lg shadow-[#E07A5F]/30">
                <Leaf className="w-6 h-6 text-white" />
              </div>
              <span className="font-serif text-2xl font-semibold text-white tracking-wide">
                Ayur Vaidya
              </span>
            </div>
            <Link to="/login">
              <Button 
                variant="outline" 
                className="border-white/40 text-white hover:bg-white/15 hover:text-white rounded-full px-6 backdrop-blur-sm"
                data-testid="header-login-button"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </header>

        <div className="relative z-10 max-w-7xl mx-auto px-6 py-32">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 bg-[#E07A5F]/20 backdrop-blur-sm border border-[#E07A5F]/30 px-5 py-2.5 rounded-full mb-8 animate-fadeIn">
              <Sparkles className="w-4 h-4 text-[#E07A5F]" />
              <span className="text-sm font-sans text-white font-medium tracking-wide">
                Ancient Wisdom, Modern Wellness
              </span>
            </div>

            <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl font-bold text-white leading-[1.1] mb-5 animate-fadeIn delay-100">
              Ayur <span className="text-[#E07A5F]">Vaidya</span>
            </h1>
            
            <p className="font-serif text-2xl sm:text-3xl text-[#A8C5B0] mb-6 animate-fadeIn delay-200 italic">
              Nature's Way of Healing
            </p>

            <p className="text-base sm:text-lg text-white/80 font-sans leading-relaxed mb-10 max-w-lg animate-fadeIn delay-300">
              Discover the ancient science of Ayurveda. Find natural remedies for everyday ailments, 
              connect with experienced practitioners, and embrace holistic wellness.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 animate-fadeIn delay-400">
              <Link to="/login">
                <Button 
                  className="bg-[#E07A5F] hover:bg-[#C96A52] text-white text-lg py-6 px-8 rounded-full group shadow-lg shadow-[#E07A5F]/30 transition-all hover:shadow-xl hover:shadow-[#E07A5F]/40"
                  data-testid="get-started-button"
                >
                  Get Started
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <a href="#features">
                <Button 
                  variant="outline" 
                  className="border-white/40 text-white hover:bg-white/15 hover:text-white text-lg py-6 px-8 rounded-full backdrop-blur-sm"
                >
                  Learn More
                </Button>
              </a>
            </div>

            <div className="flex flex-wrap gap-10 mt-14 animate-fadeIn delay-500">
              <div>
                <p className="font-serif text-4xl font-bold text-white">65+</p>
                <p className="text-sm text-[#A8C5B0] font-sans mt-1">Natural Remedies</p>
              </div>
              <div className="w-px bg-white/20 self-stretch"></div>
              <div>
                <p className="font-serif text-4xl font-bold text-white">16+</p>
                <p className="text-sm text-[#A8C5B0] font-sans mt-1">Expert Practitioners</p>
              </div>
              <div className="w-px bg-white/20 self-stretch"></div>
              <div>
                <p className="font-serif text-4xl font-bold text-white">20</p>
                <p className="text-sm text-[#A8C5B0] font-sans mt-1">Health Categories</p>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <a href="#features" className="text-white/50 hover:text-white/80 transition-colors">
            <ChevronRight className="w-8 h-8 rotate-90" />
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-28 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
              Why Choose Us
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-bold text-[#1A2421] mb-5">
              Your Path to Natural Wellness
            </h2>
            <p className="text-[#4A5D52] font-sans max-w-2xl mx-auto text-base leading-relaxed">
              Ayur Vaidya combines traditional Ayurvedic knowledge with modern technology 
              to bring you personalized health recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            <div className="bg-white rounded-2xl border border-[#D4C8B8]/50 p-10 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 group" data-testid="feature-remedies">
              <div className="w-16 h-16 rounded-2xl bg-[#2C4C3B]/10 flex items-center justify-center mb-7 group-hover:bg-[#2C4C3B] transition-colors">
                <Leaf className="w-8 h-8 text-[#2C4C3B] group-hover:text-white transition-colors" />
              </div>
              <h3 className="font-serif text-2xl font-bold text-[#1A2421] mb-3">
                Natural Remedies
              </h3>
              <p className="text-[#4A5D52] font-sans leading-relaxed">
                Access 65+ Ayurvedic medicines with detailed 
                information on usage, dosage, and preparation methods.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[#D4C8B8]/50 p-10 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 group" data-testid="feature-symptom-checker">
              <div className="w-16 h-16 rounded-2xl bg-[#E07A5F]/10 flex items-center justify-center mb-7 group-hover:bg-[#E07A5F] transition-colors">
                <Search className="w-8 h-8 text-[#E07A5F] group-hover:text-white transition-colors" />
              </div>
              <h3 className="font-serif text-2xl font-bold text-[#1A2421] mb-3">
                Symptom Checker
              </h3>
              <p className="text-[#4A5D52] font-sans leading-relaxed">
                Tell us your symptoms and get personalized recommendations for 
                natural remedies tailored to your needs.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[#D4C8B8]/50 p-10 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 group" data-testid="feature-practitioners">
              <div className="w-16 h-16 rounded-2xl bg-[#2C4C3B]/10 flex items-center justify-center mb-7 group-hover:bg-[#2C4C3B] transition-colors">
                <Users className="w-8 h-8 text-[#2C4C3B] group-hover:text-white transition-colors" />
              </div>
              <h3 className="font-serif text-2xl font-bold text-[#1A2421] mb-3">
                Expert Practitioners
              </h3>
              <p className="text-[#4A5D52] font-sans leading-relaxed">
                Connect with 16+ experienced Ayurvedic practitioners across India and Sri Lanka, and book consultations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-6 bg-[#F4EDE4]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
              Simple Process
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-bold text-[#1A2421] mb-5">
              How It Works
            </h2>
            <p className="text-[#4A5D52] font-sans max-w-2xl mx-auto text-base">
              Start your Ayurvedic wellness journey in three simple steps
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="relative text-center" data-testid="step-1">
              <div className="w-20 h-20 rounded-full bg-[#2C4C3B] flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Search className="w-9 h-9 text-white" />
              </div>
              <div className="absolute top-10 left-[60%] right-0 hidden md:block">
                <div className="border-t-2 border-dashed border-[#2C4C3B]/30 w-full"></div>
              </div>
              <span className="inline-block bg-[#E07A5F] text-white text-xs font-bold px-3 py-1 rounded-full mb-4">Step 1</span>
              <h3 className="font-serif text-xl font-bold text-[#1A2421] mb-2">Describe Symptoms</h3>
              <p className="text-[#4A5D52] font-sans text-sm leading-relaxed max-w-xs mx-auto">
                Select your symptoms from our comprehensive list or browse by health category
              </p>
            </div>

            <div className="relative text-center" data-testid="step-2">
              <div className="w-20 h-20 rounded-full bg-[#E07A5F] flex items-center justify-center mx-auto mb-6 shadow-lg">
                <BookOpen className="w-9 h-9 text-white" />
              </div>
              <div className="absolute top-10 left-[60%] right-0 hidden md:block">
                <div className="border-t-2 border-dashed border-[#2C4C3B]/30 w-full"></div>
              </div>
              <span className="inline-block bg-[#E07A5F] text-white text-xs font-bold px-3 py-1 rounded-full mb-4">Step 2</span>
              <h3 className="font-serif text-xl font-bold text-[#1A2421] mb-2">Get Remedies</h3>
              <p className="text-[#4A5D52] font-sans text-sm leading-relaxed max-w-xs mx-auto">
                Receive personalized Ayurvedic medicine recommendations with dosage and preparation info
              </p>
            </div>

            <div className="relative text-center" data-testid="step-3">
              <div className="w-20 h-20 rounded-full bg-[#2C4C3B] flex items-center justify-center mx-auto mb-6 shadow-lg">
                <Calendar className="w-9 h-9 text-white" />
              </div>
              <span className="inline-block bg-[#E07A5F] text-white text-xs font-bold px-3 py-1 rounded-full mb-4">Step 3</span>
              <h3 className="font-serif text-xl font-bold text-[#1A2421] mb-2">Consult Expert</h3>
              <p className="text-[#4A5D52] font-sans text-sm leading-relaxed max-w-xs mx-auto">
                Book an appointment with an experienced Ayurvedic practitioner near you
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Tridosha Section */}
      <section className="py-28 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
              The Foundation of Ayurveda
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-bold text-[#1A2421] mb-5">
              The Three Doshas
            </h2>
            <p className="text-[#4A5D52] font-sans max-w-2xl mx-auto text-base leading-relaxed">
              According to Ayurveda, the universe is composed of five elements, which combine to form three fundamental energies that govern all physical and mental processes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="relative group" data-testid="dosha-vata">
              <div className="bg-gradient-to-br from-sky-50 to-blue-100 rounded-3xl p-8 border border-sky-200/80 hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="w-20 h-20 rounded-full bg-sky-500/20 flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-10 h-10 text-sky-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" strokeLinecap="round"/>
                    <path d="M8 12c0-2.21 1.79-4 4-4M16 12c0 2.21-1.79 4-4 4" strokeLinecap="round"/>
                    <path d="M12 8v8M8 12h8" strokeLinecap="round" opacity="0.5"/>
                  </svg>
                </div>
                <h3 className="font-serif text-2xl font-bold text-sky-900 text-center mb-2">Vata</h3>
                <p className="text-sky-700 text-sm font-sans font-semibold text-center mb-4">Air + Space</p>
                <p className="text-sky-800/80 font-sans text-sm text-center mb-4">
                  Controls movement, breathing, circulation, and nervous system functions.
                </p>
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2 text-xs font-sans text-sky-800">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>Qualities: Light, dry, cold, mobile</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-sky-800">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>Season: Autumn & Early Winter</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-sky-800">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>Time: 2-6 AM & 2-6 PM</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative group" data-testid="dosha-pitta">
              <div className="bg-gradient-to-br from-orange-50 to-red-100 rounded-3xl p-8 border border-orange-200/80 hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="w-20 h-20 rounded-full bg-orange-500/20 flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-10 h-10 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2c1.5 2 3 4 3 7 0 3.5-2.5 6-6 6s-6-2.5-6-6c0-3 1.5-5 3-7" strokeLinecap="round"/>
                    <path d="M12 22v-4M8 18l4 4 4-4" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="11" r="2" fill="currentColor" opacity="0.5"/>
                  </svg>
                </div>
                <h3 className="font-serif text-2xl font-bold text-orange-900 text-center mb-2">Pitta</h3>
                <p className="text-orange-700 text-sm font-sans font-semibold text-center mb-4">Fire + Water</p>
                <p className="text-orange-800/80 font-sans text-sm text-center mb-4">
                  Governs digestion, metabolism, intelligence, and body temperature.
                </p>
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2 text-xs font-sans text-orange-800">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Qualities: Hot, sharp, oily, intense</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-orange-800">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Season: Summer</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-orange-800">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Time: 10-2 AM & 10-2 PM</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="relative group" data-testid="dosha-kapha">
              <div className="bg-gradient-to-br from-emerald-50 to-green-100 rounded-3xl p-8 border border-emerald-200/80 hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-10 h-10 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2C8 2 4 6 4 10c0 6 8 12 8 12s8-6 8-12c0-4-4-8-8-8z" strokeLinecap="round"/>
                    <circle cx="12" cy="10" r="3" fill="currentColor" opacity="0.3"/>
                  </svg>
                </div>
                <h3 className="font-serif text-2xl font-bold text-emerald-900 text-center mb-2">Kapha</h3>
                <p className="text-emerald-700 text-sm font-sans font-semibold text-center mb-4">Earth + Water</p>
                <p className="text-emerald-800/80 font-sans text-sm text-center mb-4">
                  Maintains structure, stability, lubrication, and immune system.
                </p>
                <div className="space-y-2.5">
                  <div className="flex items-center gap-2 text-xs font-sans text-emerald-800">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Qualities: Heavy, slow, cool, stable</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-emerald-800">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Season: Late Winter & Spring</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-emerald-800">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Time: 6-10 AM & 6-10 PM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-14">
            <p className="text-[#4A5D52] font-sans text-sm max-w-2xl mx-auto leading-relaxed">
              Balance of these three doshas leads to health, while imbalance leads to disease. 
              Ayurvedic treatments aim to restore this natural balance through diet, lifestyle, and herbal remedies.
            </p>
          </div>
        </div>
      </section>

      {/* Health Categories Preview */}
      <section className="py-24 px-6 bg-[#F4EDE4]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
              Comprehensive Coverage
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-bold text-[#1A2421] mb-5">
              20 Health Categories
            </h2>
            <p className="text-[#4A5D52] font-sans max-w-2xl mx-auto text-base">
              From respiratory care to mental wellness, we cover a wide range of health needs
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4" data-testid="health-categories-grid">
            {[
              { name: "Respiratory", icon: "Wind" },
              { name: "Digestive", icon: "Apple" },
              { name: "Diabetes", icon: "Activity" },
              { name: "Joint & Bone", icon: "Bone" },
              { name: "Heart Health", icon: "HeartPulse" },
              { name: "Skin Health", icon: "Sparkles" },
              { name: "Hair Health", icon: "Scissors" },
              { name: "Eye Care", icon: "Eye" },
              { name: "Women's Health", icon: "Flower" },
              { name: "Men's Health", icon: "Dumbbell" },
              { name: "Children", icon: "Baby" },
              { name: "Weight Mgmt", icon: "Scale" },
              { name: "Blood Pressure", icon: "Gauge" },
              { name: "Cholesterol", icon: "Droplet" },
              { name: "Liver & Kidney", icon: "Droplets" },
              { name: "Stress", icon: "Heart" },
              { name: "Allergies", icon: "Flower2" },
              { name: "Fever", icon: "Thermometer" },
              { name: "Headache", icon: "Brain" },
              { name: "General", icon: "Shield" },
            ].map((cat, i) => (
              <div 
                key={cat.name}
                className="bg-white rounded-xl p-4 text-center border border-[#D4C8B8]/40 hover:border-[#2C4C3B]/40 hover:shadow-md transition-all cursor-default"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                <div className="w-10 h-10 rounded-full bg-[#2C4C3B]/10 flex items-center justify-center mx-auto mb-2">
                  <Leaf className="w-5 h-5 text-[#2C4C3B]" />
                </div>
                <p className="text-sm font-sans font-semibold text-[#1A2421]">{cat.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Ancient Heritage Section - Puskola Potha */}
      <section className="py-28 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl bg-[#F4EDE4] p-8">
                <img
                  src="https://customer-assets.emergentagent.com/job_wellness-vaid/artifacts/juudcf3h_image.png"
                  alt="Puskola Potha - Ancient palm leaf manuscript"
                  className="w-full h-72 object-contain"
                />
              </div>
              <div className="absolute -bottom-5 -right-5 w-28 h-28 bg-[#E07A5F] rounded-full flex items-center justify-center shadow-xl shadow-[#E07A5F]/30">
                <span className="font-serif text-white text-center text-sm font-bold leading-tight px-2">
                  5000+<br />Years
                </span>
              </div>
            </div>

            <div>
              <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
                Ancient Heritage
              </span>
              <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#1A2421] mb-6 leading-tight">
                Wisdom Preserved in<br />
                <span className="text-[#2C4C3B]">Puskola Potha</span>
              </h2>
              <p className="text-[#4A5D52] font-sans leading-relaxed mb-6">
                For millennia, Ayurvedic medicinal knowledge has been carefully inscribed on 
                <strong className="text-[#1A2421]"> Puskola Potha</strong> (boiled palmyra leaves). These ancient palm leaf manuscripts 
                contain the wisdom of generations of healers, preserving remedies and treatments 
                that continue to benefit humanity today.
              </p>
              <p className="text-[#4A5D52] font-sans leading-relaxed mb-8">
                Our database draws from these time-tested traditions, bringing you authentic 
                Ayurvedic knowledge in a modern, accessible format.
              </p>
              <div className="flex items-center gap-4 bg-[#2C4C3B]/5 rounded-xl p-4">
                <div className="w-12 h-12 rounded-full bg-[#2C4C3B] flex items-center justify-center flex-shrink-0">
                  <Leaf className="w-6 h-6 text-white" />
                </div>
                <div>
                  <p className="font-serif text-lg font-bold text-[#1A2421]">Traditional Authenticity</p>
                  <p className="text-sm text-[#4A5D52] font-sans">Rooted in ancient Vedic scriptures</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Traditional Elements Section */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
              Sacred Elements
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#1A2421]">
              The Pillars of Ayurvedic Healing
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="group text-center" data-testid="element-pahana">
              <div className="relative rounded-2xl overflow-hidden mb-6 shadow-lg">
                <img
                  src="https://images.pexels.com/photos/8818748/pexels-photo-8818748.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                  alt="Traditional oil lamp (Pahana)"
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#1A2421]/80 via-[#1A2421]/20 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 text-left">
                  <h3 className="font-serif text-xl font-bold text-white">Pahana</h3>
                  <p className="text-white/90 text-sm font-sans">Sacred Oil Lamp</p>
                </div>
              </div>
              <p className="text-[#4A5D52] font-sans text-sm px-4 leading-relaxed">
                The sacred oil lamp symbolizes the light of knowledge, dispelling darkness and ignorance in healing practices.
              </p>
            </div>

            <div className="group text-center" data-testid="element-tulsi">
              <div className="relative rounded-2xl overflow-hidden mb-6 shadow-lg">
                <img
                  src="https://images.pexels.com/photos/32112349/pexels-photo-32112349.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                  alt="Sacred Tulsi (Holy Basil) plant"
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#1A2421]/80 via-[#1A2421]/20 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 text-left">
                  <h3 className="font-serif text-xl font-bold text-white">Tulsi</h3>
                  <p className="text-white/90 text-sm font-sans">Holy Basil</p>
                </div>
              </div>
              <p className="text-[#4A5D52] font-sans text-sm px-4 leading-relaxed">
                Known as the "Queen of Herbs," Tulsi is revered for its healing properties and spiritual significance.
              </p>
            </div>

            <div className="group text-center" data-testid="element-kumbha">
              <div className="relative rounded-2xl overflow-hidden mb-6 shadow-lg">
                <img
                  src="https://images.unsplash.com/photo-1644341129459-aa473f26d313?crop=entropy&cs=srgb&fm=jpg&q=85"
                  alt="Traditional brass vessels for medicine preparation"
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#1A2421]/80 via-[#1A2421]/20 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 text-left">
                  <h3 className="font-serif text-xl font-bold text-white">Kumbha</h3>
                  <p className="text-white/90 text-sm font-sans">Brass Vessels</p>
                </div>
              </div>
              <p className="text-[#4A5D52] font-sans text-sm px-4 leading-relaxed">
                Traditional brass vessels enhance medicinal properties and are used in preparation of Ayurvedic remedies.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Practitioner Locations Section */}
      <section className="py-24 px-6 bg-[#F4EDE4]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs uppercase tracking-[0.25em] font-sans font-bold text-[#E07A5F] mb-4 block">
              India & Sri Lanka
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-bold text-[#1A2421] mb-5">
              Find Practitioners Near You
            </h2>
            <p className="text-[#4A5D52] font-sans max-w-2xl mx-auto text-base">
              Our network of certified Ayurvedic practitioners spans across major cities in India and Sri Lanka
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl p-8 border border-[#D4C8B8]/50" data-testid="locations-india">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-[#E07A5F]/10 flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-[#E07A5F]" />
                </div>
                <h3 className="font-serif text-2xl font-bold text-[#1A2421]">India</h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {["New Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Jaipur", "Varanasi", "Pune", "Ahmedabad", "Kolkata", "Lucknow", "Kerala"].map(city => (
                  <div key={city} className="flex items-center gap-2 py-2 px-3 rounded-lg bg-[#F9F6F0]">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#2C4C3B]"></div>
                    <span className="text-sm font-sans text-[#1A2421] font-medium">{city}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-2xl p-8 border border-[#D4C8B8]/50" data-testid="locations-srilanka">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-[#2C4C3B]/10 flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-[#2C4C3B]" />
                </div>
                <h3 className="font-serif text-2xl font-bold text-[#1A2421]">Sri Lanka</h3>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {["Colombo", "Kandy", "Galle", "Jaffna"].map(city => (
                  <div key={city} className="flex items-center gap-2 py-2 px-3 rounded-lg bg-[#F9F6F0]">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#E07A5F]"></div>
                    <span className="text-sm font-sans text-[#1A2421] font-medium">{city}</span>
                  </div>
                ))}
              </div>
              <p className="text-sm text-[#4A5D52] font-sans mt-6 leading-relaxed">
                Sri Lanka carries a rich tradition of Hela Wedakama (indigenous medicine) that complements classical Ayurveda. Our practitioners bridge both traditions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial / Quote Section */}
      <section className="py-28 px-6 bg-[#1A2421]">
        <div className="max-w-4xl mx-auto text-center">
          <Quote className="w-12 h-12 text-[#E07A5F]/50 mx-auto mb-8" />
          <blockquote className="font-serif text-2xl sm:text-3xl lg:text-4xl text-white mb-8 leading-relaxed font-medium">
            "Ayurveda is not just a system of medicine, it's a way of life. 
            Let nature guide you towards balance and wellness."
          </blockquote>
          <div className="w-16 h-0.5 bg-[#E07A5F] mx-auto mb-6"></div>
          <p className="text-[#A8C5B0] font-sans text-lg">Ancient Ayurvedic Wisdom</p>
        </div>
      </section>

      {/* Trust / Safety Section */}
      <section className="py-20 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex items-start gap-4 p-6" data-testid="trust-authentic">
              <div className="w-12 h-12 rounded-xl bg-[#2C4C3B]/10 flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6 text-[#2C4C3B]" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-[#1A2421] mb-1">Authentic Remedies</h4>
                <p className="text-sm text-[#4A5D52] font-sans leading-relaxed">All medicines sourced from classical Ayurvedic texts and verified traditions</p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-6" data-testid="trust-verified">
              <div className="w-12 h-12 rounded-xl bg-[#E07A5F]/10 flex items-center justify-center flex-shrink-0">
                <Star className="w-6 h-6 text-[#E07A5F]" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-[#1A2421] mb-1">Verified Practitioners</h4>
                <p className="text-sm text-[#4A5D52] font-sans leading-relaxed">All practitioners hold recognized BAMS/MD qualifications with years of experience</p>
              </div>
            </div>
            <div className="flex items-start gap-4 p-6" data-testid="trust-educational">
              <div className="w-12 h-12 rounded-xl bg-[#2C4C3B]/10 flex items-center justify-center flex-shrink-0">
                <BookOpen className="w-6 h-6 text-[#2C4C3B]" />
              </div>
              <div>
                <h4 className="font-serif text-lg font-bold text-[#1A2421] mb-1">Educational Resource</h4>
                <p className="text-sm text-[#4A5D52] font-sans leading-relaxed">Detailed information on dosage, preparation methods, and precautions for each remedy</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-28 px-6 bg-[#2C4C3B]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-serif text-4xl sm:text-5xl font-bold text-white mb-5">
            Begin Your Healing Journey
          </h2>
          <p className="text-white/80 font-sans text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
            Join thousands of people who have discovered the power of natural healing. 
            Sign up today and take the first step towards holistic wellness.
          </p>
          <Link to="/login">
            <Button 
              className="bg-[#E07A5F] hover:bg-[#C96A52] text-white text-lg py-7 px-12 rounded-full group shadow-xl shadow-[#E07A5F]/30 transition-all hover:shadow-2xl"
              data-testid="cta-get-started-button"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 px-6 bg-[#0D1B16]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#2C4C3B] rounded-full flex items-center justify-center">
              <Leaf className="w-4 h-4 text-white" />
            </div>
            <span className="font-serif text-lg font-semibold text-white">
              Ayur Vaidya
            </span>
          </div>
          <p className="text-white/40 text-sm font-sans text-center">
            © 2026 Ayur Vaidya. For educational purposes only. Consult a healthcare professional before use.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
