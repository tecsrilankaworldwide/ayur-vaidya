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
  Star
} from "lucide-react";
import { Button } from "@/components/ui/button";

const LandingPage = () => {
  const { user, checkAuth, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Skip if returning from OAuth
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
        {/* Background Image - Traditional Ayurvedic Herbs & Spices */}
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1677599082447-6549af4c5454?crop=entropy&cs=srgb&fm=jpg&q=85"
            alt="Traditional Ayurvedic herbs and spices in wooden bowls"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#1A2421]/95 via-[#1A2421]/80 to-[#1A2421]/40" />
        </div>

        {/* Header */}
        <header className="absolute top-0 left-0 right-0 z-20 px-6 py-6">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                <Leaf className="w-6 h-6 text-primary-foreground" />
              </div>
              <span className="font-serif text-2xl font-semibold text-white">
                Ayur Vaidya
              </span>
            </div>
            <Link to="/login">
              <Button 
                variant="outline" 
                className="border-white/30 text-white hover:bg-white/10 hover:text-white rounded-full px-6"
                data-testid="header-login-button"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </header>

        {/* Hero Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 py-32">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-6 animate-fadeIn">
              <Sparkles className="w-4 h-4 text-accent" />
              <span className="text-sm font-sans text-white/90">
                Ancient Wisdom, Modern Wellness
              </span>
            </div>

            <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl font-semibold text-white leading-tight mb-4 animate-fadeIn delay-100">
              Ayur Vaidya
            </h1>
            
            <p className="font-serif text-2xl sm:text-3xl text-white/80 mb-6 animate-fadeIn delay-200">
              Nature's Way of Healing
            </p>

            <p className="text-lg text-white/70 font-sans leading-relaxed mb-8 max-w-lg animate-fadeIn delay-300">
              Discover the ancient science of Ayurveda. Find natural remedies for everyday ailments, 
              connect with experienced practitioners, and embrace holistic wellness.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 animate-fadeIn delay-400">
              <Link to="/login">
                <Button 
                  className="btn-accent text-lg py-6 px-8 rounded-full group"
                  data-testid="get-started-button"
                >
                  Get Started
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <a href="#features">
                <Button 
                  variant="outline" 
                  className="border-white/30 text-white hover:bg-white/10 hover:text-white text-lg py-6 px-8 rounded-full"
                >
                  Learn More
                </Button>
              </a>
            </div>

            {/* Stats */}
            <div className="flex flex-wrap gap-8 mt-12 animate-fadeIn delay-500">
              <div>
                <p className="font-serif text-3xl font-semibold text-white">21+</p>
                <p className="text-sm text-white/60 font-sans">Natural Remedies</p>
              </div>
              <div>
                <p className="font-serif text-3xl font-semibold text-white">8+</p>
                <p className="text-sm text-white/60 font-sans">Expert Practitioners</p>
              </div>
              <div>
                <p className="font-serif text-3xl font-semibold text-white">71+</p>
                <p className="text-sm text-white/60 font-sans">Symptoms Covered</p>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <a href="#features" className="text-white/50 hover:text-white/80 transition-colors">
            <ChevronRight className="w-8 h-8 rotate-90" />
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-3 block">
              Why Choose Us
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-semibold text-text-primary mb-4">
              Your Path to Natural Wellness
            </h2>
            <p className="text-text-secondary font-sans max-w-2xl mx-auto">
              Ayur Vaidya combines traditional Ayurvedic knowledge with modern technology 
              to bring you personalized health recommendations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-surface rounded-2xl border border-border p-8 hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
                <Leaf className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-serif text-2xl font-semibold text-text-primary mb-3">
                Natural Remedies
              </h3>
              <p className="text-text-secondary font-sans">
                Access a comprehensive database of Ayurvedic medicines with detailed 
                information on usage, dosage, and preparation methods.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-surface rounded-2xl border border-border p-8 hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center mb-6">
                <Heart className="w-8 h-8 text-accent" />
              </div>
              <h3 className="font-serif text-2xl font-semibold text-text-primary mb-3">
                Symptom Checker
              </h3>
              <p className="text-text-secondary font-sans">
                Tell us your symptoms and get personalized recommendations for 
                natural remedies tailored to your needs.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-surface rounded-2xl border border-border p-8 hover:shadow-lg transition-shadow">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
                <Users className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-serif text-2xl font-semibold text-text-primary mb-3">
                Expert Practitioners
              </h3>
              <p className="text-text-secondary font-sans">
                Connect with experienced Ayurvedic practitioners, book appointments, 
                and get personalized consultations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Tridosha Section - Vata, Pitta, Kapha */}
      <section className="py-24 px-6 bg-surface">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-3 block">
              The Foundation of Ayurveda
            </span>
            <h2 className="font-serif text-4xl sm:text-5xl font-semibold text-text-primary mb-4">
              The Three Doshas
            </h2>
            <p className="text-text-secondary font-sans max-w-2xl mx-auto">
              According to Ayurveda, the universe is composed of five elements, which combine to form three fundamental energies or doshas that govern all physical and mental processes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Vata */}
            <div className="relative group">
              <div className="bg-gradient-to-br from-sky-50 to-blue-100 rounded-3xl p-8 border border-sky-200 hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="w-20 h-20 rounded-full bg-sky-500/20 flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-10 h-10 text-sky-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" strokeLinecap="round"/>
                    <path d="M8 12c0-2.21 1.79-4 4-4M16 12c0 2.21-1.79 4-4 4" strokeLinecap="round"/>
                    <path d="M12 8v8M8 12h8" strokeLinecap="round" opacity="0.5"/>
                  </svg>
                </div>
                <h3 className="font-serif text-2xl font-semibold text-sky-800 text-center mb-2">
                  Vata
                </h3>
                <p className="text-sky-600 text-sm font-sans text-center mb-4">
                  Air + Space
                </p>
                <p className="text-sky-700/80 font-sans text-sm text-center mb-4">
                  Controls movement, breathing, circulation, and nervous system functions.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-sans text-sky-700">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>Qualities: Light, dry, cold, mobile</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-sky-700">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>Season: Autumn & Early Winter</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-sky-700">
                    <span className="w-2 h-2 rounded-full bg-sky-500"></span>
                    <span>Time: 2-6 AM & 2-6 PM</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Pitta */}
            <div className="relative group">
              <div className="bg-gradient-to-br from-orange-50 to-red-100 rounded-3xl p-8 border border-orange-200 hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="w-20 h-20 rounded-full bg-orange-500/20 flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-10 h-10 text-orange-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2c1.5 2 3 4 3 7 0 3.5-2.5 6-6 6s-6-2.5-6-6c0-3 1.5-5 3-7" strokeLinecap="round"/>
                    <path d="M12 22v-4M8 18l4 4 4-4" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="11" r="2" fill="currentColor" opacity="0.5"/>
                  </svg>
                </div>
                <h3 className="font-serif text-2xl font-semibold text-orange-800 text-center mb-2">
                  Pitta
                </h3>
                <p className="text-orange-600 text-sm font-sans text-center mb-4">
                  Fire + Water
                </p>
                <p className="text-orange-700/80 font-sans text-sm text-center mb-4">
                  Governs digestion, metabolism, intelligence, and body temperature.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-sans text-orange-700">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Qualities: Hot, sharp, oily, intense</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-orange-700">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Season: Summer</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-orange-700">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Time: 10-2 AM & 10-2 PM</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Kapha */}
            <div className="relative group">
              <div className="bg-gradient-to-br from-emerald-50 to-green-100 rounded-3xl p-8 border border-emerald-200 hover:shadow-xl transition-all hover:-translate-y-1">
                <div className="w-20 h-20 rounded-full bg-emerald-500/20 flex items-center justify-center mb-6 mx-auto">
                  <svg className="w-10 h-10 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2C8 2 4 6 4 10c0 6 8 12 8 12s8-6 8-12c0-4-4-8-8-8z" strokeLinecap="round"/>
                    <circle cx="12" cy="10" r="3" fill="currentColor" opacity="0.3"/>
                  </svg>
                </div>
                <h3 className="font-serif text-2xl font-semibold text-emerald-800 text-center mb-2">
                  Kapha
                </h3>
                <p className="text-emerald-600 text-sm font-sans text-center mb-4">
                  Earth + Water
                </p>
                <p className="text-emerald-700/80 font-sans text-sm text-center mb-4">
                  Maintains structure, stability, lubrication, and immune system.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-sans text-emerald-700">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Qualities: Heavy, slow, cool, stable</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-emerald-700">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Season: Late Winter & Spring</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs font-sans text-emerald-700">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Time: 6-10 AM & 6-10 PM</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <p className="text-text-secondary font-sans text-sm max-w-2xl mx-auto">
              Balance of these three doshas leads to health, while imbalance leads to disease. 
              Ayurvedic treatments aim to restore this natural balance through diet, lifestyle, and herbal remedies.
            </p>
          </div>
        </div>
      </section>

      {/* Ancient Heritage Section - Puskola Potha */}
      <section className="py-24 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Image - Using user's Puskola Potha */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-xl bg-surface-alt p-8">
                <img
                  src="https://customer-assets.emergentagent.com/job_wellness-vaid/artifacts/juudcf3h_image.png"
                  alt="Puskola Potha - Ancient palm leaf manuscript"
                  className="w-full h-72 object-contain"
                />
              </div>
              <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-accent rounded-full flex items-center justify-center shadow-lg">
                <span className="font-serif text-white text-center text-xs leading-tight px-2">
                  5000+<br />Years
                </span>
              </div>
            </div>

            {/* Content */}
            <div>
              <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-3 block">
                Ancient Heritage
              </span>
              <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-text-primary mb-6 leading-tight">
                Wisdom Preserved in<br />
                <span className="text-primary">Puskola Potha</span>
              </h2>
              <p className="text-text-secondary font-sans leading-relaxed mb-6">
                For millennia, Ayurvedic medicinal knowledge has been carefully inscribed on 
                <strong> Puskola Potha</strong> (boiled palmyra leaves). These ancient palm leaf manuscripts 
                contain the wisdom of generations of healers, preserving remedies and treatments 
                that continue to benefit humanity today.
              </p>
              <p className="text-text-secondary font-sans leading-relaxed mb-6">
                Our database draws from these time-tested traditions, bringing you authentic 
                Ayurvedic knowledge in a modern, accessible format.
              </p>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Leaf className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="font-serif text-lg font-semibold text-text-primary">Traditional Authenticity</p>
                  <p className="text-sm text-text-secondary font-sans">Rooted in ancient Vedic scriptures</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Traditional Elements Section - Oil Lamps & Tulsi */}
      <section className="py-20 px-6 bg-surface">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-3 block">
              Sacred Elements
            </span>
            <h2 className="font-serif text-3xl sm:text-4xl font-semibold text-text-primary">
              The Pillars of Ayurvedic Healing
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Oil Lamp - Pahana */}
            <div className="group text-center">
              <div className="relative rounded-2xl overflow-hidden mb-6 shadow-lg">
                <img
                  src="https://images.pexels.com/photos/8818748/pexels-photo-8818748.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                  alt="Traditional oil lamp (Pahana)"
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 text-left">
                  <h3 className="font-serif text-xl font-semibold text-white">Pahana</h3>
                  <p className="text-white/80 text-sm font-sans">Sacred Oil Lamp</p>
                </div>
              </div>
              <p className="text-text-secondary font-sans text-sm px-4">
                The sacred oil lamp symbolizes the light of knowledge, dispelling darkness and ignorance in healing practices.
              </p>
            </div>

            {/* Tulsi */}
            <div className="group text-center">
              <div className="relative rounded-2xl overflow-hidden mb-6 shadow-lg">
                <img
                  src="https://images.pexels.com/photos/32112349/pexels-photo-32112349.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                  alt="Sacred Tulsi (Holy Basil) plant"
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 text-left">
                  <h3 className="font-serif text-xl font-semibold text-white">Tulsi</h3>
                  <p className="text-white/80 text-sm font-sans">Holy Basil</p>
                </div>
              </div>
              <p className="text-text-secondary font-sans text-sm px-4">
                Known as the "Queen of Herbs," Tulsi is revered for its healing properties and spiritual significance.
              </p>
            </div>

            {/* Brass Vessels */}
            <div className="group text-center">
              <div className="relative rounded-2xl overflow-hidden mb-6 shadow-lg">
                <img
                  src="https://images.unsplash.com/photo-1644341129459-aa473f26d313?crop=entropy&cs=srgb&fm=jpg&q=85"
                  alt="Traditional brass vessels for medicine preparation"
                  className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <div className="absolute bottom-4 left-4 right-4 text-left">
                  <h3 className="font-serif text-xl font-semibold text-white">Kumbha</h3>
                  <p className="text-white/80 text-sm font-sans">Brass Vessels</p>
                </div>
              </div>
              <p className="text-text-secondary font-sans text-sm px-4">
                Traditional brass vessels enhance medicinal properties and are used in preparation of Ayurvedic remedies.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section className="py-24 px-6 bg-surface-alt">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center gap-1 mb-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <Star key={i} className="w-6 h-6 text-yellow-500 fill-yellow-500" />
            ))}
          </div>
          <blockquote className="font-serif text-2xl sm:text-3xl text-text-primary mb-8 leading-relaxed">
            "Ayurveda is not just a system of medicine, it's a way of life. 
            Let nature guide you towards balance and wellness."
          </blockquote>
          <p className="text-text-secondary font-sans">— Ancient Ayurvedic Wisdom</p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 bg-primary">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-serif text-4xl sm:text-5xl font-semibold text-white mb-4">
            Begin Your Healing Journey
          </h2>
          <p className="text-white/80 font-sans text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of people who have discovered the power of natural healing. 
            Sign up today and take the first step towards holistic wellness.
          </p>
          <Link to="/login">
            <Button 
              className="bg-white text-primary hover:bg-white/90 text-lg py-6 px-10 rounded-full group"
              data-testid="cta-get-started-button"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 bg-text-primary">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <Leaf className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-serif text-lg font-semibold text-white">
              Ayur Vaidya
            </span>
          </div>
          <p className="text-white/50 text-sm font-sans text-center">
            © 2024 Ayur Vaidya. For educational purposes only. Consult a healthcare professional before use.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
