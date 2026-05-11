import axios from 'axios';
import { useUserStore } from '../store/user.js';
import router from '../router/index.js';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  response => {
    const data = response.data;
    if (data.code === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push('/login');
    }
    return data;
  },
  error => {
    return Promise.reject(error);
  }
);

export default api;
