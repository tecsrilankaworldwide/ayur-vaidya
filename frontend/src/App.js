import { useEffect, useRef } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";

// Pages
import LoginPage from "@/pages/LoginPage";
import Dashboard from "@/pages/Dashboard";
import SymptomChecker from "@/pages/SymptomChecker";
import CategoryPage from "@/pages/CategoryPage";
import MedicineDetail from "@/pages/MedicineDetail";
import SearchResults from "@/pages/SearchResults";

// Auth callback component
const AuthCallback = () => {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);
  const { login } = useAuth();

  useEffect(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash;
    const sessionIdMatch = hash.match(/session_id=([^&]+)/);
    
    if (sessionIdMatch) {
      const sessionId = sessionIdMatch[1];
      login(sessionId).then((success) => {
        if (success) {
          navigate("/dashboard", { replace: true });
        } else {
          navigate("/", { replace: true });
        }
      });
    } else {
      navigate("/", { replace: true });
    }
  }, [navigate, login]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="loading-spinner mx-auto mb-4"></div>
        <p className="text-text-secondary font-sans">Authenticating...</p>
      </div>
    </div>
  );
};

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  const { user, loading, checkAuth } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Skip if we have user from AuthCallback
    if (location.state?.user) return;
    
    // CRITICAL: If returning from OAuth callback, skip the /me check
    if (window.location.hash?.includes('session_id=')) {
      return;
    }

    if (!loading && !user) {
      checkAuth().then((authenticated) => {
        if (!authenticated) {
          navigate("/", { replace: true });
        }
      });
    }
  }, [user, loading, checkAuth, navigate, location.state]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return children;
};

// App router component
const AppRouter = () => {
  const location = useLocation();

  // Check URL fragment for session_id synchronously during render
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/symptom-checker"
        element={
          <ProtectedRoute>
            <SymptomChecker />
          </ProtectedRoute>
        }
      />
      <Route
        path="/category/:categoryId"
        element={
          <ProtectedRoute>
            <CategoryPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/medicine/:medicineId"
        element={
          <ProtectedRoute>
            <MedicineDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/search"
        element={
          <ProtectedRoute>
            <SearchResults />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <AppRouter />
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
