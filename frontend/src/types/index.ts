/**
 * SANJOG - Community Food Rescue Network
 * Core TypeScript Domain Types & Interfaces
 */

export interface SurplusBatch {
  id: string;
  donorName: string;
  foodTitle: string;
  foodType: string;
  servings: number;
  dietary: string;
  prepTime: string;
  shelfLife: string;
  slaUrgency: 'URGENT' | 'HIGH' | 'NORMAL';
  slaColor: string;
  safetyCleared: boolean;
  fssaiVerified: boolean;
  location: string;
}

export interface MealDemand {
  id: string;
  receiverName: string;
  mealsNeeded: number;
  beneficiaries: string;
  dietaryPreference: string;
  targetTime: string;
  urgency: 'CRITICAL' | 'HIGH' | 'MODERATE';
  storage: string;
  darpanVerified: boolean;
  location: string;
}

export interface CourierMission {
  missionId: string;
  donor: string;
  receiver: string;
  volunteerName: string;
  vehicle: string;
  servings: number;
  status: 'EN_ROUTE_PICKUP' | 'IN_TRANSIT' | 'DELIVERED';
  statusDisplay: string;
  donorOtp: string;
  receiverOtp: string;
  pickupVerified: boolean;
  deliveryVerified: boolean;
  eta: string;
  distance: string;
}

export interface TelemetryMetrics {
  totalMealsRescued: number;
  co2SavedKg: number;
  activeCouriers: number;
  activeKitchens: number;
  partnerShelters: number;
  complianceRate: number;
}

export interface FoodPassportData {
  passportId: string;
  batchTitle: string;
  kitchenName: string;
  fssaiLicense: string;
  cookingTimestamp: string;
  safeTempCelsius: number;
  transitVehicle: string;
  courierName: string;
  destinationShelter: string;
  darpanId: string;
  qrPayload: string;
  blockchainHash: string;
}
