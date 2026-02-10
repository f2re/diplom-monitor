import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

const API_URL = 'http://localhost:8000';

export const useGridStore = defineStore('grid', {
  state: () => ({
    weeks: [],
    specialPeriods: [],
    loading: false,
    error: null,
  }),
  getters: {
    getWeekByDate: (state) => (dateString) => {
      return state.weeks.find(w => w.week_start_date === dateString);
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
    async fetchGridData(userId = null) {
      this.loading = true;
      try {
        const authStore = useAuthStore();
        const targetId = userId || authStore.user?.id;
        
        if (!targetId) return;

        const [weeksRes, periodsRes] = await Promise.all([
          axios.get(`${API_URL}/grid/weeks/${targetId}`),
          axios.get(`${API_URL}/grid/special-periods/${targetId}`)
        ]);
        this.weeks = weeksRes.data;
        this.specialPeriods = periodsRes.data;
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
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка обновления недели';
        return false;
      }
    }
  }
});