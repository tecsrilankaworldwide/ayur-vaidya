import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Header } from "@/components/Header";
import { getUserBookings, cancelBooking } from "@/services/api";
import { toast } from "sonner";
import { 
  Calendar,
  Clock,
  MapPin,
  User,
  X,
  AlertCircle,
  CheckCircle,
  XCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBookings();
  }, []);

  const loadBookings = async () => {
    try {
      setLoading(true);
      const data = await getUserBookings();
      setBookings(data);
    } catch (error) {
      console.error("Failed to load bookings:", error);
      toast.error("Failed to load bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (bookingId) => {
    try {
      await cancelBooking(bookingId);
      toast.success("Booking cancelled successfully");
      loadBookings();
    } catch (error) {
      console.error("Failed to cancel booking:", error);
      toast.error("Failed to cancel booking");
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "confirmed":
        return (
          <Badge className="bg-green-100 text-green-700 border-0">
            <CheckCircle className="w-3 h-3 mr-1" />
            Confirmed
          </Badge>
        );
      case "cancelled":
        return (
          <Badge className="bg-red-100 text-red-700 border-0">
            <XCircle className="w-3 h-3 mr-1" />
            Cancelled
          </Badge>
        );
      case "completed":
        return (
          <Badge className="bg-blue-100 text-blue-700 border-0">
            <CheckCircle className="w-3 h-3 mr-1" />
            Completed
          </Badge>
        );
      default:
        return null;
    }
  };

  const upcomingBookings = bookings.filter(b => b.status === "confirmed");
  const pastBookings = bookings.filter(b => b.status !== "confirmed");

  return (
    <div className="min-h-screen bg-background" data-testid="my-bookings-page">
      <Header />
      
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 animate-fadeIn">
          <h1 className="font-serif text-3xl sm:text-4xl font-semibold text-text-primary mb-2">
            My Appointments
          </h1>
          <p className="text-text-secondary font-sans">
            Manage your upcoming and past appointments with practitioners
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="loading-spinner"></div>
          </div>
        ) : bookings.length > 0 ? (
          <div className="space-y-8">
            {/* Upcoming Bookings */}
            {upcomingBookings.length > 0 && (
              <section className="animate-fadeIn">
                <h2 className="font-serif text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-primary" />
                  Upcoming Appointments
                </h2>
                <div className="space-y-4">
                  {upcomingBookings.map((booking) => (
                    <BookingCard 
                      key={booking.booking_id} 
                      booking={booking} 
                      onCancel={handleCancel}
                      getStatusBadge={getStatusBadge}
                    />
                  ))}
                </div>
              </section>
            )}

            {/* Past Bookings */}
            {pastBookings.length > 0 && (
              <section className="animate-fadeIn delay-100">
                <h2 className="font-serif text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-text-secondary" />
                  Past Appointments
                </h2>
                <div className="space-y-4 opacity-75">
                  {pastBookings.map((booking) => (
                    <BookingCard 
                      key={booking.booking_id} 
                      booking={booking}
                      getStatusBadge={getStatusBadge}
                      isPast
                    />
                  ))}
                </div>
              </section>
            )}
          </div>
        ) : (
          <div className="empty-state bg-surface rounded-2xl border border-border py-16">
            <div className="empty-state-icon">
              <Calendar className="w-10 h-10 text-text-secondary" />
            </div>
            <h3 className="font-serif text-xl font-semibold text-text-primary mb-2">
              No Appointments Yet
            </h3>
            <p className="text-text-secondary font-sans mb-6">
              Book an appointment with an Ayurvedic practitioner
            </p>
            <Link to="/practitioners">
              <Button className="btn-primary" data-testid="find-practitioners-button">
                Find Practitioners
              </Button>
            </Link>
          </div>
        )}
      </main>
    </div>
  );
};

const BookingCard = ({ booking, onCancel, getStatusBadge, isPast = false }) => {
  return (
    <div className="bg-surface rounded-2xl border border-border p-5 hover:shadow-sm transition-shadow">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <User className="w-5 h-5 text-primary" />
            <h3 className="font-serif text-lg font-semibold text-text-primary">
              {booking.practitioner_name}
            </h3>
            {getStatusBadge(booking.status)}
          </div>
          
          <div className="space-y-2 ml-8">
            <div className="flex items-center gap-2 text-sm text-text-secondary font-sans">
              <Calendar className="w-4 h-4" />
              <span>{new Date(booking.date).toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-text-secondary font-sans">
              <Clock className="w-4 h-4" />
              <span>{booking.time_slot}</span>
            </div>
            {booking.reason && (
              <p className="text-sm text-text-secondary font-sans">
                <strong>Reason:</strong> {booking.reason}
              </p>
            )}
          </div>
        </div>

        {!isPast && booking.status === "confirmed" && (
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button 
                variant="outline" 
                className="text-accent border-accent hover:bg-accent/10"
                data-testid={`cancel-booking-${booking.booking_id}`}
              >
                <X className="w-4 h-4 mr-1" />
                Cancel
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent className="bg-surface border-border">
              <AlertDialogHeader>
                <AlertDialogTitle className="font-serif">Cancel Appointment?</AlertDialogTitle>
                <AlertDialogDescription className="font-sans">
                  Are you sure you want to cancel your appointment with {booking.practitioner_name} 
                  on {booking.date} at {booking.time_slot}? This action cannot be undone.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel className="border-border">Keep Appointment</AlertDialogCancel>
                <AlertDialogAction 
                  onClick={() => onCancel(booking.booking_id)}
                  className="bg-accent hover:bg-accent/90"
                >
                  Yes, Cancel
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
      </div>
    </div>
  );
};

export default MyBookings;
