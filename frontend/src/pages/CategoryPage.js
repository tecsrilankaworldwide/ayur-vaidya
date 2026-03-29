import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Header } from "@/components/Header";
import { MedicineCard } from "@/components/MedicineCard";
import { getCategoryWithMedicines } from "@/services/api";
import { toast } from "sonner";
import { 
  ChevronLeft,
  Wind, 
  Apple, 
  Thermometer, 
  Brain, 
  Sparkles, 
  Heart, 
  Flower2,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";

const iconMap = {
  Wind,
  Apple,
  Thermometer,
  Brain,
  Sparkles,
  Heart,
  Flower2,
};

const CategoryPage = () => {
  const { categoryId } = useParams();
  const [category, setCategory] = useState(null);
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategory();
  }, [categoryId]);

  const loadCategory = async () => {
    try {
      setLoading(true);
      const data = await getCategoryWithMedicines(categoryId);
      setCategory(data.category);
      setMedicines(data.medicines);
    } catch (error) {
      console.error("Failed to load category:", error);
      toast.error("Failed to load category");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="flex items-center justify-center py-32">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (!category) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="empty-state">
            <div className="empty-state-icon">
              <AlertCircle className="w-10 h-10 text-text-secondary" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
              Category Not Found
            </h3>
            <p className="text-text-secondary font-sans mb-4">
              The category you're looking for doesn't exist
            </p>
            <Link to="/dashboard">
              <Button className="btn-secondary">
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const IconComponent = iconMap[category.icon] || Sparkles;

  return (
    <div className="min-h-screen bg-background" data-testid="category-page">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link 
          to="/dashboard"
          className="inline-flex items-center gap-1 text-text-secondary hover:text-primary font-sans text-sm font-medium mb-6 transition-colors"
          data-testid="back-to-dashboard"
        >
          <ChevronLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>

        {/* Hero Section */}
        <div className="relative rounded-2xl overflow-hidden mb-10 animate-fadeIn">
          <img
            src={category.image_url || "https://images.unsplash.com/photo-1768700439764-9ec0ba31ae75"}
            alt={category.name}
            className="w-full h-64 sm:h-80 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-text-primary/90 via-text-primary/50 to-transparent" />
          <div className="absolute inset-0 flex items-end p-6 sm:p-10">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <IconComponent className="w-6 h-6 text-white" />
                </div>
                <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-white/70">
                  {medicines.length} Remedies
                </span>
              </div>
              <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-semibold text-white mb-2">
                {category.name}
              </h1>
              <p className="text-white/80 font-sans text-base max-w-2xl">
                {category.description}
              </p>
            </div>
          </div>
        </div>

        {/* Medicines Grid */}
        <section className="animate-fadeIn delay-100">
          <h2 className="font-serif text-2xl font-semibold text-text-primary mb-6">
            Available Remedies
          </h2>

          {medicines.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {medicines.map((medicine, index) => (
                <div 
                  key={medicine.medicine_id}
                  className="animate-fadeIn"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <MedicineCard medicine={medicine} />
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state bg-surface rounded-2xl border border-border">
              <div className="empty-state-icon">
                <AlertCircle className="w-10 h-10 text-text-secondary" />
              </div>
              <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
                No Remedies Yet
              </h3>
              <p className="text-text-secondary font-sans">
                No remedies are available in this category yet
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

export default CategoryPage;
