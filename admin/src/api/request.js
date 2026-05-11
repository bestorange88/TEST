import axios from 'axios';
import router from '../router/index.js';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('admin_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  response => {
    const data = response.data;
    if (data.code === 401) {
      localStorage.removeItem('admin_token');
      router.push('/login');
    }
    return data;
  },
  error => Promise.reject(error)
);

export default api;
