import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Header } from "@/components/Header";
import { MedicineCard } from "@/components/MedicineCard";
import { getMedicines } from "@/services/api";
import { toast } from "sonner";
import { 
  Search,
  ChevronLeft,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";

const SearchResults = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (query) {
      searchMedicines();
    } else {
      setMedicines([]);
      setLoading(false);
    }
  }, [query]);

  const searchMedicines = async () => {
    try {
      setLoading(true);
      const data = await getMedicines({ search: query });
      setMedicines(data);
    } catch (error) {
      console.error("Search failed:", error);
      toast.error("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background" data-testid="search-results-page">
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

        {/* Search Header */}
        <div className="mb-8 animate-fadeIn">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Search className="w-6 h-6 text-primary" />
            </div>
            <div>
              <span className="text-xs uppercase tracking-[0.2em] font-sans font-semibold text-primary">
                Search Results
              </span>
              <h1 className="font-serif text-3xl sm:text-4xl font-semibold text-text-primary">
                "{query}"
              </h1>
            </div>
          </div>
          <p className="text-text-secondary font-sans mt-2">
            {loading 
              ? "Searching..." 
              : `Found ${medicines.length} ${medicines.length === 1 ? 'remedy' : 'remedies'}`
            }
          </p>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="loading-spinner"></div>
          </div>
        ) : medicines.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 animate-fadeIn">
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
          <div className="empty-state bg-surface rounded-2xl border border-border py-16">
            <div className="empty-state-icon">
              <AlertCircle className="w-10 h-10 text-text-secondary" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
              No Results Found
            </h3>
            <p className="text-text-secondary font-sans mb-6 max-w-md mx-auto">
              We couldn't find any remedies matching "{query}". Try using different keywords or browse by category.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/dashboard">
                <Button className="btn-secondary" data-testid="browse-categories-button">
                  Browse Categories
                </Button>
              </Link>
              <Link to="/symptom-checker">
                <Button className="btn-primary" data-testid="try-symptom-checker-button">
                  Try Symptom Checker
                </Button>
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default SearchResults;
