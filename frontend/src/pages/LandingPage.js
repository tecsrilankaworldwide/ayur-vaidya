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

      {/* Ancient Heritage Section - Puskola Potha */}
      <section className="py-24 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Image */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-xl">
                <img
                  src="https://images.unsplash.com/photo-1676115388797-5f448ad78e44?crop=entropy&cs=srgb&fm=jpg&q=85"
                  alt="Ancient palm leaf manuscript (Puskola Potha)"
                  className="w-full h-80 object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
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
