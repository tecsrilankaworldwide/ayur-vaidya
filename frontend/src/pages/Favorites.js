import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Header } from "@/components/Header";
import { MedicineCard } from "@/components/MedicineCard";
import { getFavorites, removeFavorite } from "@/services/api";
import { toast } from "sonner";
import { 
  Heart,
  Pill,
  UserCircle,
  Star,
  MapPin,
  Award,
  Trash2,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const Favorites = () => {
  const [favorites, setFavorites] = useState({ medicines: [], practitioners: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      setLoading(true);
      const data = await getFavorites();
      setFavorites(data);
    } catch (error) {
      console.error("Failed to load favorites:", error);
      toast.error("Failed to load favorites");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (itemType, itemId) => {
    try {
      await removeFavorite(itemType, itemId);
      toast.success("Removed from favorites");
      loadFavorites();
    } catch (error) {
      console.error("Failed to remove favorite:", error);
      toast.error("Failed to remove from favorites");
    }
  };

  const totalFavorites = favorites.medicines.length + favorites.practitioners.length;

  return (
    <div className="min-h-screen bg-background" data-testid="favorites-page">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 animate-fadeIn">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center">
              <Heart className="w-6 h-6 text-accent" />
            </div>
            <div>
              <h1 className="font-serif text-3xl sm:text-4xl font-semibold text-text-primary">
                My Favorites
              </h1>
              <p className="text-text-secondary font-sans">
                {totalFavorites} saved item{totalFavorites !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="loading-spinner"></div>
          </div>
        ) : totalFavorites > 0 ? (
          <Tabs defaultValue="medicines" className="animate-fadeIn">
            <TabsList className="bg-surface-alt border border-border mb-6">
              <TabsTrigger 
                value="medicines" 
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              >
                <Pill className="w-4 h-4 mr-2" />
                Medicines ({favorites.medicines.length})
              </TabsTrigger>
              <TabsTrigger 
                value="practitioners"
                className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
              >
                <UserCircle className="w-4 h-4 mr-2" />
                Practitioners ({favorites.practitioners.length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="medicines">
              {favorites.medicines.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {favorites.medicines.map((medicine, index) => (
                    <div 
                      key={medicine.medicine_id} 
                      className="relative animate-fadeIn"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <button
                        onClick={() => handleRemoveFavorite("medicine", medicine.medicine_id)}
                        className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-white shadow-md flex items-center justify-center text-accent hover:bg-accent hover:text-white transition-colors"
                        data-testid={`remove-medicine-${medicine.medicine_id}`}
                      >
                        <Heart className="w-4 h-4 fill-current" />
                      </button>
                      <MedicineCard medicine={medicine} />
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState 
                  icon={Pill}
                  title="No Favorite Medicines"
                  description="Browse remedies and save your favorites"
                  linkTo="/dashboard"
                  linkText="Browse Medicines"
                />
              )}
            </TabsContent>

            <TabsContent value="practitioners">
              {favorites.practitioners.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {favorites.practitioners.map((practitioner, index) => (
                    <div 
                      key={practitioner.practitioner_id}
                      className="relative animate-fadeIn"
                      style={{ animationDelay: `${index * 100}ms` }}
                    >
                      <button
                        onClick={() => handleRemoveFavorite("practitioner", practitioner.practitioner_id)}
                        className="absolute top-3 right-3 z-10 w-8 h-8 rounded-full bg-white shadow-md flex items-center justify-center text-accent hover:bg-accent hover:text-white transition-colors"
                        data-testid={`remove-practitioner-${practitioner.practitioner_id}`}
                      >
                        <Heart className="w-4 h-4 fill-current" />
                      </button>
                      <PractitionerFavoriteCard practitioner={practitioner} />
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState 
                  icon={UserCircle}
                  title="No Favorite Practitioners"
                  description="Find practitioners and save your favorites"
                  linkTo="/practitioners"
                  linkText="Find Practitioners"
                />
              )}
            </TabsContent>
          </Tabs>
        ) : (
          <div className="empty-state bg-surface rounded-2xl border border-border py-16">
            <div className="empty-state-icon">
              <Heart className="w-10 h-10 text-text-secondary" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
              No Favorites Yet
            </h3>
            <p className="text-text-secondary font-sans mb-6 max-w-md mx-auto">
              Save your favorite medicines and practitioners for quick access
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link to="/dashboard">
                <Button className="btn-secondary">
                  Browse Medicines
                </Button>
              </Link>
              <Link to="/practitioners">
                <Button className="btn-primary">
                  Find Practitioners
                </Button>
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

const PractitionerFavoriteCard = ({ practitioner }) => {
  return (
    <Link 
      to="/practitioners"
      className="block bg-surface rounded-2xl border border-border p-5 hover:shadow-lg transition-all"
    >
      <div className="flex gap-4">
        <div className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0">
          <img
            src={practitioner.image_url || "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d"}
            alt={practitioner.name}
            className="w-full h-full object-cover"
          />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="font-serif text-lg font-semibold text-text-primary truncate">
              {practitioner.name}
            </h3>
            <div className="flex items-center gap-1 flex-shrink-0">
              <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
              <span className="text-sm font-sans font-medium text-text-primary">{practitioner.rating}</span>
            </div>
          </div>
          
          <p className="text-sm text-text-secondary font-sans mb-2">
            {practitioner.title}
          </p>

          <div className="flex items-center gap-1 text-sm text-text-secondary font-sans mb-2">
            <MapPin className="w-3.5 h-3.5" />
            <span className="truncate">{practitioner.city}</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {practitioner.specializations?.slice(0, 2).map((spec, index) => (
              <Badge 
                key={index} 
                variant="secondary"
                className="bg-primary/10 text-primary text-xs border-0"
              >
                {spec}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    </Link>
  );
};

const EmptyState = ({ icon: Icon, title, description, linkTo, linkText }) => {
  return (
    <div className="text-center py-16 bg-surface-alt rounded-2xl border border-border">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-surface flex items-center justify-center border border-border">
        <Icon className="w-8 h-8 text-text-secondary" />
      </div>
      <h3 className="font-serif text-lg font-semibold text-text-primary mb-2">
        {title}
      </h3>
      <p className="text-text-secondary font-sans mb-4">
        {description}
      </p>
      <Link to={linkTo}>
        <Button className="btn-secondary">
          {linkText}
        </Button>
      </Link>
    </div>
  );
};

export default Favorites;
