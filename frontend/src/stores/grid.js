import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

const API_URL = 'http://localhost:8000';

export const useGridStore = defineStore('grid', {
  state: () => ({
    weeks: [],
    specialPeriods: [],
    stats: {
      total_weeks: 0,
      special_weeks: 0,
      effective_weeks: 0,
      completed_weeks: 0,
      remaining_weeks: 0
    },
    loading: false,
    error: null,
    config: {
      start_date: null,
      deadline: null
    },
    allProgress: [] // Array of { user_id, emoji, completions: [week_start_dates] }
  }),
  getters: {
    getWeekByDate: (state) => (dateString) => {
      return state.weeks.find(w => w.week_start_date === dateString);
    },
    getCompletionsByDate: (state) => (dateString) => {
      return state.allProgress.map(up => ({
        user_id: up.user_id,
        emoji: up.emoji,
        is_completed: up.completions.includes(dateString)
      }));
    },
    isSpecialPeriod: (state) => (dateString) => {
      const weekDate = new Date(dateString);
      
      return state.specialPeriods.find(p => {
        const start = new Date(p.start_date);
        const end = new Date(p.end_date);
        return weekDate >= start && weekDate <= end;
      });
    }
  },
  actions: {
    async fetchGlobalConfig() {
      try {
        const response = await axios.get(`${API_URL}/grid/config`);
        this.config = response.data;
        return this.config;
      } catch (err) {
        console.error('Error fetching global config', err);
      }
    },
    async fetchAllProgress() {
      try {
        const response = await axios.get(`${API_URL}/grid/all-progress`);
        this.allProgress = response.data;
      } catch (err) {
        console.error('Error fetching all progress', err);
      }
    },
    async fetchGridData(userId = null) {
      this.loading = true;
      try {
        const authStore = useAuthStore();
        const targetId = userId || authStore.user?.id;
        
        // Fetch config and all progress in parallel with user data
        const promises = [
          this.fetchGlobalConfig(),
          this.fetchAllProgress(),
          axios.get(`${API_URL}/grid/special-periods/${targetId}`),
          axios.get(`${API_URL}/grid/stats/${targetId}`)
        ];

        if (targetId) {
          promises.push(axios.get(`${API_URL}/grid/weeks/${targetId}`));
        }

        const results = await Promise.all(promises);
        
        // results indices: 0:config, 1:allProgress, 2:periods, 3:stats, 4:weeks (if targetId)
        this.specialPeriods = results[2].data;
        this.stats = results[3].data;
        if (targetId && results[4]) {
          this.weeks = results[4].data;
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка загрузки данных сетки';
      } finally {
        this.loading = false;
      }
    },
    async updateWeek(weekStartDate, isCompleted, note = null) {
      try {
        const response = await axios.post(`${API_URL}/grid/weeks`, {
          week_start_date: weekStartDate,
          is_completed: isCompleted,
          note
        });
        
        const index = this.weeks.findIndex(w => w.week_start_date === weekStartDate);
        if (index !== -1) {
          this.weeks[index] = response.data;
        } else {
          this.weeks.push(response.data);
        }
        // Refresh stats after updating week
        const authStore = useAuthStore();
        const statsRes = await axios.get(`${API_URL}/grid/stats/${authStore.user.id}`);
        this.stats = statsRes.data;
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка обновления недели';
        return false;
      }
    },
    async addSpecialPeriod(periodData) {
      try {
        const response = await axios.post(`${API_URL}/grid/special-periods`, periodData);
        this.specialPeriods.push(response.data);
        // Refresh stats
        const authStore = useAuthStore();
        const statsRes = await axios.get(`${API_URL}/grid/stats/${authStore.user.id}`);
        this.stats = statsRes.data;
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка добавления периода';
        return false;
      }
    },
    async deleteSpecialPeriod(periodId) {
      try {
        await axios.delete(`${API_URL}/grid/special-periods/${periodId}`);
        this.specialPeriods = this.specialPeriods.filter(p => p.id !== periodId);
        // Refresh stats
        const authStore = useAuthStore();
        const statsRes = await axios.get(`${API_URL}/grid/stats/${authStore.user.id}`);
        this.stats = statsRes.data;
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка удаления периода';
        return false;
      }
    }
  }
});
