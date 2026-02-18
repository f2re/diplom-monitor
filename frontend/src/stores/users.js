import { defineStore } from 'pinia';
import axios from 'axios';
import { API_URL } from '../config';

export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    loading: false,
    error: null,
  }),
  actions: {
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await axios.get(`${API_URL}/users/`);
        this.users = response.data;
      } catch (err) {
        this.error = 'Ошибка загрузки списка пользователей';
      } finally {
        this.loading = false;
      }
    }
  }
});
