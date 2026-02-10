import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

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
        const response = await axios.get(`${API_URL}/users`);
        this.users = response.data;
      } catch (err) {
        this.error = 'Failed to load users';
      } finally {
        this.loading = false;
      }
    }
  }
});
