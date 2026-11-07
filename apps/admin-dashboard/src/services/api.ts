import axios from 'axios';

const API_BASE = '/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('lpu_admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto redirect on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('lpu_admin_token');
      localStorage.removeItem('lpu_admin_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const AdminAPI = {
  // Auth
  login: async (email: string, password: string) => {
    const res = await api.post('/auth/login', { email, password });
    return res.data;
  },

  getMe: async () => {
    const res = await api.get('/auth/me');
    return res.data;
  },

  // Fleet & Overview Metrics
  getMetrics: async () => {
    const res = await api.get('/admin/metrics');
    return res.data;
  },

  // Carts
  getCarts: async () => {
    const res = await api.get('/carts');
    return res.data;
  },

  getCartDetail: async (cartId: string) => {
    const res = await api.get(`/carts/${cartId}`);
    return res.data;
  },

  updateCart: async (cartId: string, data: any) => {
    const res = await api.put(`/admin/carts/${cartId}`, data);
    return res.data;
  },

  createCart: async (data: any) => {
    const res = await api.post('/admin/carts', data);
    return res.data;
  },

  // Routes
  getRoutes: async () => {
    const res = await api.get('/routes');
    return res.data;
  },

  // CCTV Units
  getCCTVDevices: async () => {
    const res = await api.get('/admin/cctv');
    return res.data;
  },

  // Telemetry
  getActiveTelemetry: async () => {
    const res = await api.get('/tracking/active');
    return res.data;
  },

  sendTelemetryUpdate: async (payload: any) => {
    const res = await api.post('/tracking/update', payload);
    return res.data;
  }
};

