import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance
const apiClient = axios.create({
  baseURL: API,
  withCredentials: true,
});

// Categories
export const getCategories = async () => {
  const response = await apiClient.get("/categories");
  return response.data;
};

export const getCategoryWithMedicines = async (categoryId) => {
  const response = await apiClient.get(`/categories/${categoryId}`);
  return response.data;
};

// Medicines
export const getMedicines = async (params = {}) => {
  const response = await apiClient.get("/medicines", { params });
  return response.data;
};

export const getMedicineById = async (medicineId) => {
  const response = await apiClient.get(`/medicines/${medicineId}`);
  return response.data;
};

// Symptoms
export const getAllSymptoms = async () => {
  const response = await apiClient.get("/symptoms");
  return response.data;
};

export const checkSymptoms = async (symptoms) => {
  const response = await apiClient.post("/symptom-check", { symptoms });
  return response.data;
};

// Seed database
export const seedDatabase = async () => {
  const response = await apiClient.post("/seed");
  return response.data;
};

// Health check
export const healthCheck = async () => {
  const response = await apiClient.get("/health");
  return response.data;
};

// Practitioners
export const getPractitioners = async (params = {}) => {
  const response = await apiClient.get("/practitioners", { params });
  return response.data;
};

export const getPractitionerById = async (practitionerId) => {
  const response = await apiClient.get(`/practitioners/${practitionerId}`);
  return response.data;
};

export const getPractitionerCities = async () => {
  const response = await apiClient.get("/practitioners/cities");
  return response.data;
};

export const getPractitionerSpecializations = async () => {
  const response = await apiClient.get("/practitioners/specializations");
  return response.data;
};

// Bookings
export const createBooking = async (bookingData) => {
  const response = await apiClient.post("/bookings", bookingData);
  return response.data;
};

export const getUserBookings = async () => {
  const response = await apiClient.get("/bookings");
  return response.data;
};

export const cancelBooking = async (bookingId) => {
  const response = await apiClient.delete(`/bookings/${bookingId}`);
  return response.data;
};

export const getAvailableSlots = async (practitionerId, date) => {
  const response = await apiClient.get(`/practitioners/${practitionerId}/slots`, {
    params: { date }
  });
  return response.data;
};

// Reviews
export const createReview = async (reviewData) => {
  const response = await apiClient.post("/reviews", reviewData);
  return response.data;
};

export const getPractitionerReviews = async (practitionerId) => {
  const response = await apiClient.get(`/practitioners/${practitionerId}/reviews`);
  return response.data;
};

// Favorites
export const addFavorite = async (itemType, itemId) => {
  const response = await apiClient.post("/favorites", { item_type: itemType, item_id: itemId });
  return response.data;
};

export const removeFavorite = async (itemType, itemId) => {
  const response = await apiClient.delete(`/favorites/${itemType}/${itemId}`);
  return response.data;
};

export const getFavorites = async () => {
  const response = await apiClient.get("/favorites");
  return response.data;
};

export const checkFavorite = async (itemType, itemId) => {
  const response = await apiClient.get(`/favorites/check/${itemType}/${itemId}`);
  return response.data;
};
