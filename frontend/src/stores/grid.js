import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';
import { useUsersStore } from './users';

const API_URL = '/api';

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
    loading: false, saving: false,
    error: null,
    config: {
      start_date: null,
      deadline: null
    },
    allProgress: [] // Array of { user_id, emoji, completions: [{ date: 'YYYY-MM-DD', note: '...' }] }
  }),
  getters: {
    getWeekByDate: (state) => (dateString) => {
      return state.weeks.find(w => w.week_start_date === dateString);
    },
    getCompletionsByDate: (state) => (dateString) => {
      const usersStore = useUsersStore();
      return state.allProgress.map(up => {
        const completion = up.completions.find(c => c.date === dateString);
        const user = usersStore.users.find(u => u.id === up.user_id);
        
        return {
          user_id: up.user_id,
          emoji: up.emoji,
          full_name: user?.full_name || 'Unknown',
          is_completed: !!completion,
          note: completion?.note
        };
      });
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
      const authStore = useAuthStore();
      const targetId = userId || authStore.user?.id;
      
      if (!targetId) {
        // Still fetch global config even if no user is logged in yet
        await this.fetchGlobalConfig();
        return;
      }

      this.loading = true;
      try {
        // Fetch everything including user-specific data
        const [config, progress, periods, stats, weeks] = await Promise.all([
          this.fetchGlobalConfig(),
          this.fetchAllProgress(),
          axios.get(`${API_URL}/grid/special-periods/${targetId}`),
          axios.get(`${API_URL}/grid/stats/${targetId}`),
          axios.get(`${API_URL}/grid/weeks/${targetId}`)
        ]);

        this.specialPeriods = periods.data;
        this.stats = stats.data;
        this.weeks = weeks.data;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка загрузки данных сетки';
      } finally {
        this.loading = false;
      }
    },
    async updateWeek(weekStartDate, isCompleted, note = null) {
      this.saving = true;
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

        // Update allProgress for reactivity
        const authStore = useAuthStore();
        if (authStore.user?.id) {
            // Update local state for immediate UI feedback
            const userProgress = this.allProgress.find(p => p.user_id === authStore.user.id);
            if (userProgress) {
                if (isCompleted) {
                    const existing = userProgress.completions.find(c => c.date === weekStartDate);
                    if (!existing) {
                        userProgress.completions.push({ date: weekStartDate, note });
                    } else {
                        existing.note = note;
                    }
                } else {
                    userProgress.completions = userProgress.completions.filter(c => c.date !== weekStartDate);
                }
            }
        }
        
        // Refresh stats after updating week
        if (authStore.user?.id) {
          const statsRes = await axios.get(`${API_URL}/grid/stats/${authStore.user.id}`);
          this.stats = statsRes.data;
        }
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка обновления недели';
        return false;
      } finally {
        this.saving = false;
      }
    },
    async addSpecialPeriod(periodData) {
      this.saving = true;
      try {
        const response = await axios.post(`${API_URL}/grid/special-periods`, periodData);
        this.specialPeriods.push(response.data);
        // Refresh stats
        const authStore = useAuthStore();
        if (authStore.user?.id) {
          const statsRes = await axios.get(`${API_URL}/grid/stats/${authStore.user.id}`);
          this.stats = statsRes.data;
        }
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка добавления периода';
        return false;
      } finally {
        this.saving = false;
      }
    },
    async deleteSpecialPeriod(periodId) {
      this.saving = true;
      try {
        await axios.delete(`${API_URL}/grid/special-periods/${periodId}`);
        this.specialPeriods = this.specialPeriods.filter(p => p.id !== periodId);
        // Refresh stats
        const authStore = useAuthStore();
        if (authStore.user?.id) {
          const statsRes = await axios.get(`${API_URL}/grid/stats/${authStore.user.id}`);
          this.stats = statsRes.data;
        }
        return true;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка удаления периода';
        return false;
      } finally {
        this.saving = false;
      }
    }
  }
});
