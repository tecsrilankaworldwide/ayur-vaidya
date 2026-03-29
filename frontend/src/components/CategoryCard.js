import { Link } from "react-router-dom";
import { 
  Wind, 
  Apple, 
  Thermometer, 
  Brain, 
  Sparkles, 
  Heart, 
  Flower2,
  ChevronRight 
} from "lucide-react";

const iconMap = {
  Wind,
  Apple,
  Thermometer,
  Brain,
  Sparkles,
  Heart,
  Flower2,
};

export const CategoryCard = ({ category }) => {
  const IconComponent = iconMap[category.icon] || Sparkles;

  return (
    <Link 
      to={`/category/${category.category_id}`}
      className="group block"
      data-testid={`category-card-${category.category_id}`}
    >
      <div className="relative h-48 rounded-2xl overflow-hidden card-hover">
        {/* Background Image */}
        <img
          src={category.image_url || "https://images.unsplash.com/photo-1768700439764-9ec0ba31ae75"}
          alt={category.name}
          className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        
        {/* Overlay */}
        <div className="absolute inset-0 category-card-overlay" />
        
        {/* Content */}
        <div className="absolute inset-0 p-5 flex flex-col justify-end">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
              <IconComponent className="w-5 h-5 text-white" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-white">
              {category.name}
            </h3>
          </div>
          <p className="text-white/80 text-sm font-sans line-clamp-2">
            {category.description}
          </p>
          <div className="flex items-center gap-1 mt-3 text-white/60 text-xs font-sans group-hover:text-white transition-colors">
            <span>View remedies</span>
            <ChevronRight className="w-3 h-3 transition-transform group-hover:translate-x-1" />
          </div>
        </div>
      </div>
    </Link>
  );
};

export default CategoryCard;
