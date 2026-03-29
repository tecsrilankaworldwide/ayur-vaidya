import { Link } from "react-router-dom";
import { ChevronRight, Pill } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export const MedicineCard = ({ medicine }) => {
  return (
    <Link 
      to={`/medicine/${medicine.medicine_id}`}
      className="group block"
      data-testid={`medicine-card-${medicine.medicine_id}`}
    >
      <div className="medicine-card h-full">
        {/* Image */}
        <div className="relative h-40 overflow-hidden">
          <img
            src={medicine.image_url || "https://images.unsplash.com/photo-1768700439764-9ec0ba31ae75"}
            alt={medicine.name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          {medicine.sanskrit_name && (
            <div className="absolute top-3 left-3">
              <Badge variant="secondary" className="bg-white/90 text-text-secondary text-xs font-sans">
                {medicine.sanskrit_name}
              </Badge>
            </div>
          )}
        </div>
        
        {/* Content */}
        <div className="p-4">
          <div className="flex items-start gap-3 mb-2">
            <div className="w-8 h-8 rounded-full bg-surface-alt flex items-center justify-center flex-shrink-0">
              <Pill className="w-4 h-4 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-serif text-lg font-semibold text-text-primary group-hover:text-primary transition-colors truncate">
                {medicine.name}
              </h3>
              <p className="text-xs text-text-secondary font-sans mt-0.5">
                {medicine.dosage}
              </p>
            </div>
          </div>
          
          <p className="text-sm text-text-secondary font-sans line-clamp-2 mb-3">
            {medicine.description}
          </p>
          
          {/* Symptoms tags */}
          <div className="flex flex-wrap gap-1.5 mb-3">
            {medicine.symptoms?.slice(0, 3).map((symptom, index) => (
              <span 
                key={index}
                className="tag text-xs"
              >
                {symptom}
              </span>
            ))}
            {medicine.symptoms?.length > 3 && (
              <span className="tag text-xs">
                +{medicine.symptoms.length - 3}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-1 text-primary text-sm font-sans font-medium group-hover:gap-2 transition-all">
            <span>View details</span>
            <ChevronRight className="w-4 h-4" />
          </div>
        </div>
      </div>
    </Link>
  );
};

export default MedicineCard;
