import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Header } from "@/components/Header";
import { MedicineCard } from "@/components/MedicineCard";
import { getAllSymptoms, checkSymptoms } from "@/services/api";
import { toast } from "sonner";
import { 
  Stethoscope, 
  Search,
  X,
  ChevronRight,
  Pill,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const SymptomChecker = () => {
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    loadSymptoms();
  }, []);

  const loadSymptoms = async () => {
    try {
      setLoading(true);
      const data = await getAllSymptoms();
      setSymptoms(data);
    } catch (error) {
      console.error("Failed to load symptoms:", error);
      toast.error("Failed to load symptoms. Please try loading sample data from dashboard.");
    } finally {
      setLoading(false);
    }
  };

  const toggleSymptom = (symptom) => {
    setSelectedSymptoms(prev => {
      if (prev.includes(symptom)) {
        return prev.filter(s => s !== symptom);
      }
      return [...prev, symptom];
    });
    setResults(null);
  };

  const clearSelection = () => {
    setSelectedSymptoms([]);
    setResults(null);
  };

  const handleCheck = async () => {
    if (selectedSymptoms.length === 0) {
      toast.error("Please select at least one symptom");
      return;
    }

    try {
      setChecking(true);
      const data = await checkSymptoms(selectedSymptoms);
      setResults(data);
      if (data.medicines.length === 0) {
        toast.info("No remedies found for these symptoms. Try selecting different symptoms.");
      }
    } catch (error) {
      console.error("Failed to check symptoms:", error);
      toast.error("Failed to get recommendations");
    } finally {
      setChecking(false);
    }
  };

  const filteredSymptoms = symptoms.filter(symptom =>
    symptom.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groupedSymptoms = filteredSymptoms.reduce((acc, symptom) => {
    const firstLetter = symptom.charAt(0).toUpperCase();
    if (!acc[firstLetter]) {
      acc[firstLetter] = [];
    }
    acc[firstLetter].push(symptom);
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-background" data-testid="symptom-checker-page">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
          {/* Left - Content */}
          <div className="animate-fadeIn">
            <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-3 block">
              Symptom Checker
            </span>
            <h1 className="font-serif text-4xl sm:text-5xl tracking-tight leading-none text-text-primary mb-4">
              Find Your Natural Remedy
            </h1>
            <p className="text-text-secondary font-sans text-base leading-relaxed mb-6">
              Select your symptoms below and we'll recommend traditional Ayurvedic medicines that may help. 
              Our database includes comprehensive remedies for common ailments.
            </p>

            {/* Selected Symptoms */}
            {selectedSymptoms.length > 0 && (
              <div className="mb-6 p-4 bg-surface rounded-xl border border-border animate-scaleIn">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-sans font-medium text-text-primary">
                    Selected Symptoms ({selectedSymptoms.length})
                  </span>
                  <button
                    onClick={clearSelection}
                    className="text-xs text-accent hover:text-accent/80 font-sans font-medium flex items-center gap-1"
                    data-testid="clear-symptoms-button"
                  >
                    <X className="w-3 h-3" />
                    Clear all
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedSymptoms.map((symptom) => (
                    <Badge
                      key={symptom}
                      variant="secondary"
                      className="bg-primary text-primary-foreground cursor-pointer hover:bg-primary-hover transition-colors"
                      onClick={() => toggleSymptom(symptom)}
                      data-testid={`selected-symptom-${symptom}`}
                    >
                      {symptom}
                      <X className="w-3 h-3 ml-1" />
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Check Button */}
            <Button
              onClick={handleCheck}
              disabled={selectedSymptoms.length === 0 || checking}
              className="btn-primary w-full sm:w-auto"
              data-testid="check-symptoms-button"
            >
              {checking ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Finding Remedies...
                </>
              ) : (
                <>
                  <Stethoscope className="w-4 h-4 mr-2" />
                  Find Remedies
                  <ChevronRight className="w-4 h-4 ml-1" />
                </>
              )}
            </Button>
          </div>

          {/* Right - Image */}
          <div className="hidden lg:block animate-fadeIn delay-200">
            <img
              src="https://images.unsplash.com/photo-1684713745382-4d18b6be39a9?crop=entropy&cs=srgb&fm=jpg&q=85"
              alt="Traditional Ayurvedic spices and herbs"
              className="w-full h-80 object-cover rounded-2xl"
            />
          </div>
        </div>

        {/* Results Section */}
        {results && (
          <section className="mb-10 animate-fadeIn" data-testid="symptom-results">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center">
                <Pill className="w-5 h-5 text-accent" />
              </div>
              <div>
                <h2 className="font-serif text-2xl font-semibold text-text-primary">
                  Recommended Remedies
                </h2>
                <p className="text-sm text-text-secondary font-sans">
                  {results.message}
                </p>
              </div>
            </div>

            {results.medicines.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {results.medicines.map((medicine, index) => (
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
              <div className="text-center py-12 bg-surface rounded-2xl border border-border">
                <AlertCircle className="w-12 h-12 text-text-secondary mx-auto mb-4" />
                <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
                  No Remedies Found
                </h3>
                <p className="text-text-secondary font-sans">
                  Try selecting different or additional symptoms
                </p>
              </div>
            )}
          </section>
        )}

        {/* Symptoms Selection */}
        <section className="animate-fadeIn delay-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-serif text-2xl font-semibold text-text-primary">
              Select Your Symptoms
            </h2>
            <span className="text-sm text-text-secondary font-sans">
              {symptoms.length} symptoms available
            </span>
          </div>

          {/* Search */}
          <div className="relative mb-6">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-secondary" />
            <input
              type="text"
              placeholder="Search symptoms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input pl-12"
              data-testid="symptom-search-input"
            />
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="loading-spinner"></div>
            </div>
          ) : symptoms.length > 0 ? (
            <div className="bg-surface rounded-2xl border border-border p-6">
              {Object.keys(groupedSymptoms).sort().map((letter) => (
                <div key={letter} className="mb-6 last:mb-0">
                  <h3 className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary mb-3">
                    {letter}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {groupedSymptoms[letter].map((symptom) => (
                      <button
                        key={symptom}
                        onClick={() => toggleSymptom(symptom)}
                        className={`symptom-chip ${
                          selectedSymptoms.includes(symptom) ? 'active' : ''
                        }`}
                        data-testid={`symptom-chip-${symptom}`}
                      >
                        {symptom}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">
                <AlertCircle className="w-10 h-10 text-text-secondary" />
              </div>
              <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
                No Symptoms Available
              </h3>
              <p className="text-text-secondary font-sans mb-4">
                Please load sample data from the dashboard first
              </p>
              <Link to="/dashboard">
                <Button className="btn-secondary" data-testid="go-to-dashboard-button">
                  Go to Dashboard
                </Button>
              </Link>
            </div>
          )}
        </section>

        {/* Info Box */}
        <div className="mt-10 p-6 bg-surface-alt rounded-2xl border border-border animate-fadeIn delay-300">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-serif text-lg font-semibold text-text-primary mb-1">
                Important Note
              </h3>
              <p className="text-sm text-text-secondary font-sans">
                This symptom checker provides general guidance based on traditional Ayurvedic knowledge. 
                The recommendations are for educational purposes only and should not replace professional medical advice. 
                Always consult a qualified healthcare practitioner for proper diagnosis and treatment.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SymptomChecker;
