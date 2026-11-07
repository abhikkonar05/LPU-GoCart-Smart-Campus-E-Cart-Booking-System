/**
 * LPU GoCart - Shared Campus Constants
 * Lovely Professional University (LPU), Phagwara, Punjab, India
 */

// LPU Campus Coordinates & Geofencing Center
export const LPU_CAMPUS_COORDINATES = {
  latitude: 31.2536,
  longitude: 75.7037,
  latitudeDelta: 0.015,
  longitudeDelta: 0.015,
};

// Known Campus Key Landmarks & Stops
export const LPU_CAMPUS_STOPS = [
  { id: 'stop-01', name: 'Main Gate (Gate 1)', latitude: 31.2538, longitude: 75.7012 },
  { id: 'stop-02', name: 'Block 32 (Engineering)', latitude: 31.2545, longitude: 75.7040 },
  { id: 'stop-03', name: 'UniMall & Food Court', latitude: 31.2529, longitude: 75.7048 },
  { id: 'stop-04', name: 'Central Library / Block 34', latitude: 31.2552, longitude: 75.7058 },
  { id: 'stop-05', name: 'Girls Hostel (GH-1 to GH-6)', latitude: 31.2515, longitude: 75.7075 },
  { id: 'stop-06', name: 'Boys Hostel (BH-1 to BH-8)', latitude: 31.2568, longitude: 75.7082 },
  { id: 'stop-07', name: 'Indoor Sports Stadium & Baldev Raj Mittal Unipolis', latitude: 31.2530, longitude: 75.7025 },
  { id: 'stop-08', name: 'Gate 4 / Residential Area', latitude: 31.2510, longitude: 75.7005 }
];

// Fare & Business Constants
export const BUSINESS_RULES = {
  DEFAULT_SEAT_FARE_INR: 10.0,
  SEAT_LOCK_DURATION_SECONDS: 300, // 5 minutes
  GPS_POLL_INTERVAL_MS: 3000, // 3 seconds
  MAX_SEATS_PER_CART: 8,
  STUDENT_EMAIL_DOMAIN: 'lpu.in',
};

// Application Theme Colors
export const LPU_BRAND_COLORS = {
  primary: '#1D4ED8',      // Deep Royal Blue
  primaryDark: '#1E3A8A',  // Navy
  accent: '#10B981',       // Subtle Green (Eco-friendly E-Cart)
  warning: '#F59E0B',      // Amber
  danger: '#EF4444',       // Crimson
  background: '#F8FAFC',   // Off-white
  card: '#FFFFFF',         // White
  textPrimary: '#0F172A',  // Slate 900
  textSecondary: '#64748B',// Slate 500
};

