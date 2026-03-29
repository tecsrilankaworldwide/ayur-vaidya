import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Leaf, ArrowRight, Shield, Heart, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const LoginPage = () => {
  const { user, checkAuth, handleGoogleLogin, loading } = useAuth();
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
    <div className="min-h-screen login-bg flex flex-col" data-testid="login-page">
      {/* Header */}
      <header className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center gap-2">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
            <Leaf className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="font-serif text-xl font-semibold text-text-primary">
            Ayur Vaidya
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-lg">
          {/* Hero Section */}
          <div className="text-center mb-10 animate-fadeIn">
            <span className="inline-block text-xs sm:text-sm uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-4">
              Ancient Wisdom, Modern Wellness
            </span>
            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl tracking-tight leading-none text-text-primary mb-4">
              Discover Natural Healing
            </h1>
            <p className="text-base leading-relaxed font-sans text-text-secondary max-w-md mx-auto">
              Find Ayurvedic remedies for common ailments with our symptom checker and comprehensive medicine guide.
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-surface rounded-2xl border border-border p-8 shadow-sm animate-fadeIn delay-200">
            <h2 className="font-serif text-2xl font-semibold text-text-primary text-center mb-2">
              Welcome Back
            </h2>
            <p className="text-text-secondary text-sm font-sans text-center mb-6">
              Sign in to access your personalized recommendations
            </p>

            <Button
              onClick={handleGoogleLogin}
              className="w-full bg-primary hover:bg-primary-hover text-primary-foreground rounded-full py-6 text-base font-sans font-medium transition-all hover:shadow-lg"
              data-testid="google-login-button"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </Button>

            <p className="text-xs text-text-secondary text-center mt-4 font-sans">
              By signing in, you agree to our Terms of Service and Privacy Policy
            </p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-3 gap-4 mt-8 animate-fadeIn delay-300">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-surface flex items-center justify-center border border-border">
                <Shield className="w-5 h-5 text-primary" />
              </div>
              <p className="text-xs font-sans text-text-secondary">Trusted Remedies</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-surface flex items-center justify-center border border-border">
                <Heart className="w-5 h-5 text-accent" />
              </div>
              <p className="text-xs font-sans text-text-secondary">Natural Healing</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-surface flex items-center justify-center border border-border">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>
              <p className="text-xs font-sans text-text-secondary">Expert Guidance</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-6 py-4 text-center">
        <p className="text-xs text-text-secondary font-sans">
          © 2024 Ayur Vaidya. For educational purposes only. Consult a healthcare professional before use.
        </p>
      </footer>
    </div>
  );
};

export default LoginPage;
