import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    loading: false, saving: false,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    init() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
      }
    },
    async login(email, password) {
      this.loading = true;
      this.error = null;
      try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await axios.post(`${API_URL}/auth/login`, formData);
        this.token = response.data.access_token;
        localStorage.setItem('token', this.token);
        this.init();
        await this.fetchCurrentUser();
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка входа';
        return false;
      } finally {
        this.loading = false;
      }
    },
    async loginWithTelegram(telegramData) {
        this.loading = true;
        this.error = null;
        try {
            const response = await axios.post(`${API_URL}/auth/telegram`, telegramData);
            this.token = response.data.access_token;
            localStorage.setItem('token', this.token);
            this.init();
            await this.fetchCurrentUser();
            return true;
        } catch (err) {
            this.error = err.response?.data?.detail || 'Ошибка входа через Telegram';
            return false;
        } finally {
            this.loading = false;
        }
    },
    async register(userData) {
      this.loading = true;
      this.error = null;
      try {
        await axios.post(`${API_URL}/auth/register`, userData);
        return await this.login(userData.email, userData.password);
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка регистрации';
        return false;
      } finally {
        this.loading = false;
      }
    },
    async fetchCurrentUser() {
      if (!this.token) return;
      try {
        if (!axios.defaults.headers.common['Authorization']) {
            this.init();
        }
        const response = await axios.get(`${API_URL}/users/me`);
        this.user = response.data;
      } catch (err) {
        if (err.response && err.response.status === 401) {
            this.logout();
        }
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    },
    async updateProfile(profileData) {
        this.loading = true;
        try {
            const response = await axios.put(`${API_URL}/users/me`, profileData);
            this.user = response.data;
            return true;
        } catch (err) {
            this.error = err.response?.data?.detail || 'Ошибка обновления профиля';
            return false;
        } finally {
            this.loading = false;
        }
    }
  },
});
