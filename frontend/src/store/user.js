import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../api/request.js';

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));
  const token = ref(localStorage.getItem('token') || '');

  const isLoggedIn = computed(() => !!token.value);

  function setUser(data) {
    user.value = data.user;
    token.value = data.token;
    localStorage.setItem('user', JSON.stringify(data.user));
    localStorage.setItem('token', data.token);
  }

  function logout() {
    user.value = null;
    token.value = '';
    localStorage.removeItem('user');
    localStorage.removeItem('token');
  }

  async function fetchUserInfo() {
    const res = await api.get('/user/info');
    if (res.code === 200) {
      user.value = res.data;
      localStorage.setItem('user', JSON.stringify(res.data));
    }
    return res;
  }

  return { user, token, isLoggedIn, setUser, logout, fetchUserInfo };
});
