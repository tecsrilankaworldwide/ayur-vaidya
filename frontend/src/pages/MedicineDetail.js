import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Header } from "@/components/Header";
import { getMedicineById, addFavorite, removeFavorite, checkFavorite } from "@/services/api";
import { toast } from "sonner";
import { 
  ChevronLeft,
  Pill,
  Clock,
  Beaker,
  AlertTriangle,
  ShieldX,
  BookOpen,
  AlertCircle,
  Heart
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const MedicineDetail = () => {
  const { medicineId } = useParams();
  const [medicine, setMedicine] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);

  useEffect(() => {
    loadMedicine();
    checkIfFavorited();
  }, [medicineId]);

  const loadMedicine = async () => {
    try {
      setLoading(true);
      const data = await getMedicineById(medicineId);
      setMedicine(data);
    } catch (error) {
      console.error("Failed to load medicine:", error);
      toast.error("Failed to load medicine details");
    } finally {
      setLoading(false);
    }
  };

  const checkIfFavorited = async () => {
    try {
      const data = await checkFavorite("medicine", medicineId);
      setIsFavorited(data.is_favorited);
    } catch (error) {
      console.error("Failed to check favorite:", error);
    }
  };

  const toggleFavorite = async () => {
    try {
      setFavoriteLoading(true);
      if (isFavorited) {
        await removeFavorite("medicine", medicineId);
        toast.success("Removed from favorites");
      } else {
        await addFavorite("medicine", medicineId);
        toast.success("Added to favorites");
      }
      setIsFavorited(!isFavorited);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to update favorites");
    } finally {
      setFavoriteLoading(false);
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

  if (!medicine) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="empty-state">
            <div className="empty-state-icon">
              <AlertCircle className="w-10 h-10 text-text-secondary" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
              Medicine Not Found
            </h3>
            <p className="text-text-secondary font-sans mb-4">
              The medicine you're looking for doesn't exist
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

  return (
    <div className="min-h-screen bg-background" data-testid="medicine-detail-page">
      <Header />
      
      {/* Hero Image */}
      <div className="medicine-hero">
        <img
          src={medicine.image_url || "https://images.unsplash.com/photo-1768700439764-9ec0ba31ae75"}
          alt={medicine.name}
        />
        <div className="medicine-hero-overlay" />
        
        {/* Back Button */}
        <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between">
          <Link 
            to="/dashboard"
            className="inline-flex items-center gap-1 bg-white/20 backdrop-blur-sm text-white px-3 py-2 rounded-full text-sm font-sans font-medium hover:bg-white/30 transition-colors"
            data-testid="back-button"
          >
            <ChevronLeft className="w-4 h-4" />
            Back
          </Link>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleFavorite}
            disabled={favoriteLoading}
            className={`bg-white/20 backdrop-blur-sm hover:bg-white/30 ${isFavorited ? "text-accent" : "text-white"}`}
            data-testid="favorite-medicine-button"
          >
            <Heart className={`w-5 h-5 ${isFavorited ? "fill-current" : ""}`} />
          </Button>
        </div>

        {/* Hero Content */}
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-10 z-10">
          <div className="max-w-7xl mx-auto">
            {medicine.sanskrit_name && (
              <Badge variant="secondary" className="bg-white/20 text-white border-0 mb-3">
                {medicine.sanskrit_name}
              </Badge>
            )}
            <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-semibold text-white mb-2">
              {medicine.name}
            </h1>
            <p className="text-white/80 font-sans text-base max-w-2xl">
              {medicine.description}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="content-overlap max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="bg-surface rounded-t-3xl -mt-8 pt-8 px-4 sm:px-8 lg:px-12 pb-8 border border-border border-b-0">
          
          {/* Quick Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 animate-fadeIn">
            <div className="bg-surface-alt rounded-xl p-5 border border-border">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-serif text-lg font-semibold text-text-primary">Dosage</h3>
              </div>
              <p className="text-text-secondary font-sans text-sm">{medicine.dosage}</p>
            </div>
            <div className="bg-surface-alt rounded-xl p-5 border border-border">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
                  <Pill className="w-5 h-5 text-accent" />
                </div>
                <h3 className="font-serif text-lg font-semibold text-text-primary">Usage</h3>
              </div>
              <p className="text-text-secondary font-sans text-sm">{medicine.usage}</p>
            </div>
          </div>

          {/* Symptoms */}
          <div className="mb-8 animate-fadeIn delay-100">
            <h2 className="font-serif text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <span className="w-1 h-6 bg-primary rounded-full"></span>
              Helpful For
            </h2>
            <div className="flex flex-wrap gap-2">
              {medicine.symptoms?.map((symptom, index) => (
                <Badge 
                  key={index} 
                  variant="secondary"
                  className="bg-primary/10 text-primary border-0 font-sans"
                >
                  {symptom}
                </Badge>
              ))}
            </div>
          </div>

          <Separator className="my-8 bg-border" />

          {/* Detailed Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Ingredients */}
            <div className="animate-fadeIn delay-200" data-testid="ingredients-section">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <Beaker className="w-5 h-5 text-primary" />
                </div>
                <h2 className="font-serif text-xl font-semibold text-text-primary">Ingredients</h2>
              </div>
              <ul className="space-y-2">
                {medicine.ingredients?.map((ingredient, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span className="text-text-secondary font-sans text-sm">{ingredient}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Preparation Method */}
            {medicine.preparation_method && (
              <div className="animate-fadeIn delay-300" data-testid="preparation-section">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-accent" />
                  </div>
                  <h2 className="font-serif text-xl font-semibold text-text-primary">Preparation Method</h2>
                </div>
                <p className="text-text-secondary font-sans text-sm leading-relaxed">
                  {medicine.preparation_method}
                </p>
              </div>
            )}
          </div>

          <Separator className="my-8 bg-border" />

          {/* Precautions & Contraindications */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Precautions */}
            <div className="animate-fadeIn delay-400" data-testid="precautions-section">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-yellow-600" />
                </div>
                <h2 className="font-serif text-xl font-semibold text-text-primary">Precautions</h2>
              </div>
              <ul className="space-y-2">
                {medicine.precautions?.map((precaution, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-yellow-500 mt-2 flex-shrink-0"></span>
                    <span className="text-text-secondary font-sans text-sm">{precaution}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contraindications */}
            <div className="animate-fadeIn delay-500" data-testid="contraindications-section">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                  <ShieldX className="w-5 h-5 text-red-600" />
                </div>
                <h2 className="font-serif text-xl font-semibold text-text-primary">Contraindications</h2>
              </div>
              <ul className="space-y-2">
                {medicine.contraindications?.map((contraindication, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-2 flex-shrink-0"></span>
                    <span className="text-text-secondary font-sans text-sm">{contraindication}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="mt-10 p-6 bg-surface-alt rounded-xl border border-border animate-fadeIn delay-600">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-5 h-5 text-accent" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-semibold text-text-primary mb-1">
                  Medical Disclaimer
                </h3>
                <p className="text-sm text-text-secondary font-sans">
                  This information is provided for educational purposes only and is not intended as medical advice. 
                  Always consult with a qualified Ayurvedic practitioner or healthcare provider before using any 
                  herbal remedies, especially if you are pregnant, nursing, taking medication, or have a medical condition.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MedicineDetail;
