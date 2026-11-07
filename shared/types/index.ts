/**
 * LPU GoCart - Shared TypeScript Types and Data Contracts
 * Used across Student App, Driver App, and Admin Dashboard.
 */

// User and Profile Roles
export type UserRole = 'STUDENT' | 'DRIVER' | 'ADMIN';

export interface UserProfile {
  id: string;
  email: string;
  fullName: string;
  phoneNumber?: string;
  role: UserRole;
  avatarUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface StudentProfile {
  id: string; // Foreign key to profiles.id
  registrationNumber: string; // e.g., "12104567"
  department?: string;
  hostelBlock?: string;
}

export interface DriverProfile {
  id: string; // Foreign key to profiles.id
  licenseNumber: string;
  isAvailable: boolean;
  assignedCartId?: string;
}

// Cart Models
export type CartStatus = 'ACTIVE' | 'MAINTENANCE' | 'OFFLINE' | 'CHARGING';

export interface Cart {
  id: string;
  cartNumber: string; // e.g., "CART-01"
  model: string;
  totalSeats: number;
  batteryPercentage: number;
  status: CartStatus;
  currentRouteId?: string;
  hasCctv: boolean;
  cctvDeviceId?: string;
  createdAt: string;
}

export interface CartSeat {
  id: string;
  cartId: string;
  seatNumber: number; // 1 to totalSeats
  seatLabel: string; // "S1", "S2", etc.
  isAccessible: boolean; // Accessible for disabled students
}

// Routes and Stops
export interface CampusStop {
  id: string;
  routeId: string;
  name: string; // e.g. "Main Gate", "Block 34", "UniMall"
  latitude: number;
  longitude: number;
  sequenceOrder: number;
  estimatedMinutesFromStart: number;
}

export interface CampusRoute {
  id: string;
  name: string; // e.g., "North Campus Loop"
  code: string; // "ROUTE-A"
  description: string;
  fareAmount: number; // In INR, e.g., 10.00
  isActive: boolean;
  stops?: CampusStop[];
}

// Trip and GPS Tracking
export type TripStatus = 'SCHEDULED' | 'IN_TRANSIT' | 'COMPLETED' | 'CANCELLED';

export interface Trip {
  id: string;
  cartId: string;
  driverId: string;
  routeId: string;
  status: TripStatus;
  startTime?: string;
  endTime?: string;
  currentStopId?: string;
}

export interface GPSLocationUpdate {
  cartId: string;
  driverId: string;
  tripId?: string;
  latitude: number;
  longitude: number;
  speed?: number;
  heading?: number; // Compass heading in degrees
  accuracy?: number;
  batteryLevel?: number;
  timestamp: string;
}

// Bookings and Seat Locking
export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'CANCELLED' | 'BOARDED' | 'EXPIRED';
export type PaymentStatus = 'PENDING' | 'COMPLETED' | 'FAILED' | 'REFUNDED';

export interface SeatLock {
  id: string;
  cartId: string;
  tripId: string;
  seatNumber: number;
  studentId: string;
  lockedAt: string;
  expiresAt: string;
  isReleased: boolean;
}

export interface Booking {
  id: string;
  studentId: string;
  cartId: string;
  tripId: string;
  seatNumber: number;
  pickupStopId: string;
  dropStopId: string;
  fareAmount: number;
  status: BookingStatus;
  bookingCode: string;
  qrToken?: string;
  createdAt: string;
}

export interface PaymentTransaction {
  id: string;
  bookingId: string;
  studentId: string;
  amount: number;
  currency: string;
  gateway: 'demo' | 'razorpay';
  gatewayTransactionId?: string;
  status: PaymentStatus;
  createdAt: string;
  completedAt?: string;
}

// CCTV Integration
export interface CCTVDevice {
  id: string;
  cartId: string;
  cameraName: string;
  streamProtocol: 'RTSP' | 'HLS' | 'WEBRTC';
  isOnline: boolean;
  resolution: string;
  lastPingAt?: string;
}

