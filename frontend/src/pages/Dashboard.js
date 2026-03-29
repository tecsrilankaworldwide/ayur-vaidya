import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Header } from "@/components/Header";
import { CategoryCard } from "@/components/CategoryCard";
import { getCategories, seedDatabase } from "@/services/api";
import { toast } from "sonner";
import { 
  Stethoscope, 
  ArrowRight, 
  Leaf,
  RefreshCw,
  UserCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";

const Dashboard = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await getCategories();
      setCategories(data);
    } catch (error) {
      console.error("Failed to load categories:", error);
      toast.error("Failed to load categories");
    } finally {
      setLoading(false);
    }
  };

  const handleSeed = async () => {
    try {
      setSeeding(true);
      await seedDatabase();
      toast.success("Database seeded successfully!");
      loadCategories();
    } catch (error) {
      console.error("Failed to seed database:", error);
      toast.error("Failed to seed database");
    } finally {
      setSeeding(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  const firstName = user?.name?.split(" ")[0] || "there";

  return (
    <div className="min-h-screen bg-background" data-testid="dashboard">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="relative rounded-2xl overflow-hidden mb-10 animate-fadeIn">
          <img
            src="https://images.pexels.com/photos/7615621/pexels-photo-7615621.jpeg"
            alt="Herbal supplements"
            className="w-full h-48 sm:h-56 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-text-primary/90 via-text-primary/70 to-transparent" />
          <div className="absolute inset-0 flex items-center px-6 sm:px-10">
            <div>
              <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary-foreground/70 mb-2 block">
                {getGreeting()}
              </span>
              <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-semibold text-white mb-2">
                Welcome, {firstName}
              </h1>
              <p className="text-white/80 font-sans text-sm sm:text-base max-w-md">
                Discover traditional Ayurvedic remedies for everyday wellness
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          {/* Symptom Checker Card */}
          <Link 
            to="/symptom-checker"
            className="group block animate-fadeIn delay-100"
            data-testid="symptom-checker-link"
          >
            <div className="bg-primary rounded-2xl p-6 h-full transition-all hover:shadow-lg hover:-translate-y-1">
              <div className="flex items-start justify-between mb-4">
                <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center">
                  <Stethoscope className="w-7 h-7 text-white" />
                </div>
                <ArrowRight className="w-5 h-5 text-white/60 group-hover:text-white group-hover:translate-x-1 transition-all" />
              </div>
              <h2 className="font-serif text-2xl font-semibold text-white mb-2">
                Symptom Checker
              </h2>
              <p className="text-white/80 font-sans text-sm">
                Tell us your symptoms and get personalized remedy recommendations
              </p>
            </div>
          </Link>

          {/* Browse Remedies Card */}
          <div className="bg-surface rounded-2xl border border-border p-6 animate-fadeIn delay-200">
            <div className="flex items-start justify-between mb-4">
              <div className="w-14 h-14 rounded-full bg-accent/10 flex items-center justify-center">
                <Leaf className="w-7 h-7 text-accent" />
              </div>
              {categories.length === 0 && !loading && (
                <Button
                  onClick={handleSeed}
                  disabled={seeding}
                  size="sm"
                  variant="outline"
                  className="text-xs border-border hover:bg-surface-alt"
                  data-testid="seed-database-button"
                >
                  {seeding ? (
                    <>
                      <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    "Load Sample Data"
                  )}
                </Button>
              )}
            </div>
            <h2 className="font-serif text-2xl font-semibold text-text-primary mb-2">
              Browse by Category
            </h2>
            <p className="text-text-secondary font-sans text-sm">
              Explore our collection of {categories.length > 0 ? categories.length : "7"} illness categories and natural remedies
            </p>
          </div>

          {/* Find Practitioners Card */}
          <Link 
            to="/practitioners"
            className="group block animate-fadeIn delay-300"
            data-testid="practitioners-link"
          >
            <div className="bg-surface rounded-2xl border border-border p-6 h-full transition-all hover:shadow-lg hover:-translate-y-1 hover:border-primary/30">
              <div className="flex items-start justify-between mb-4">
                <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center">
                  <UserCircle className="w-7 h-7 text-primary" />
                </div>
                <ArrowRight className="w-5 h-5 text-text-secondary group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </div>
              <h2 className="font-serif text-2xl font-semibold text-text-primary mb-2">
                Find Practitioners
              </h2>
              <p className="text-text-secondary font-sans text-sm">
                Connect with experienced Ayurvedic doctors near you for consultations
              </p>
            </div>
          </Link>
        </div>

        {/* Categories Grid */}
        <section className="animate-fadeIn delay-300">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-serif text-2xl sm:text-3xl font-semibold text-text-primary">
              Illness Categories
            </h2>
            {categories.length === 0 && !loading && (
              <span className="text-sm text-text-secondary font-sans">
                Click "Load Sample Data" above to get started
              </span>
            )}
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="loading-spinner"></div>
            </div>
          ) : categories.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {categories.map((category, index) => (
                <div 
                  key={category.category_id}
                  className="animate-fadeIn"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <CategoryCard category={category} />
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">
                <Leaf className="w-10 h-10 text-text-secondary" />
              </div>
              <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
                No Categories Yet
              </h3>
              <p className="text-text-secondary font-sans mb-4">
                Load sample data to explore Ayurvedic remedies
              </p>
              <Button
                onClick={handleSeed}
                disabled={seeding}
                className="btn-primary"
                data-testid="seed-database-button-empty"
              >
                {seeding ? "Loading..." : "Load Sample Data"}
              </Button>
            </div>
          )}
        </section>

        {/* Disclaimer */}
        <div className="mt-12 p-4 bg-surface-alt rounded-xl border border-border">
          <p className="text-xs text-text-secondary font-sans text-center">
            <strong className="text-text-primary">Disclaimer:</strong> The information provided is for educational purposes only and should not replace professional medical advice. Always consult a qualified healthcare practitioner before starting any treatment.
          </p>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
