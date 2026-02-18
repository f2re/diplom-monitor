import { defineStore } from 'pinia'
import axios from 'axios'
import { API_URL } from '../config'

export const useGridStore = defineStore('grid', {
  state: () => ({
    weeks: [],
    config: null,
    stats: null,
    specialPeriods: [],
    allProgress: [],
    loading: false,
    saving: false,
    error: null,
  }),
  getters: {
    getWeekStatus: (state) => (weekStartDate) => {
      const week = state.weeks.find(w => w.week_start_date === weekStartDate)
      return week ? week.is_completed : false
    },
    getWeekNote: (state) => (weekStartDate) => {
      const week = state.weeks.find(w => w.week_start_date === weekStartDate)
      return week ? week.note : null
    },
  },
  actions: {
    async fetchConfig(userId) {
      this.loading = true
      try {
        const response = await axios.get(`${API_URL}/grid/config`)
        this.config = response.data
      } catch (err) {
        this.error = 'Не удалось загрузить конфигурацию'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async fetchWeeks(userId) {
      this.loading = true
      try {
        const response = await axios.get(`${API_URL}/grid/weeks/${userId}`)
        this.weeks = response.data
      } catch (err) {
        this.error = 'Не удалось загрузить прогресс'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async fetchStats(userId) {
      try {
        const response = await axios.get(`${API_URL}/grid/stats/${userId}`)
        this.stats = response.data
      } catch (err) {
        console.error('Failed to load stats', err)
      }
    },
    async fetchSpecialPeriods(userId) {
      try {
        const response = await axios.get(`${API_URL}/grid/special-periods/${userId}`)
        this.specialPeriods = response.data
      } catch (err) {
        console.error('Failed to load special periods', err)
      }
    },
    async fetchAllProgress() {
      try {
        const response = await axios.get(`${API_URL}/grid/all-progress`)
        this.allProgress = response.data
      } catch (err) {
        console.error('Failed to load all progress', err)
      }
    },
    async toggleWeek(weekStartDate) {
      this.saving = true
      try {
        const week = this.weeks.find(w => w.week_start_date === weekStartDate)
        const newStatus = !week.is_completed
        
        await axios.put(`${API_URL}/grid/weeks`, {
          week_start_date: weekStartDate,
          is_completed: newStatus
        })
        
        week.is_completed = newStatus
      } catch (err) {
        this.error = 'Не удалось обновить статус недели'
        console.error(err)
      } finally {
        this.saving = false
      }
    },
    async updateWeekNote(weekStartDate, note) {
      this.saving = true
      try {
        await axios.put(`${API_URL}/grid/weeks`, {
          week_start_date: weekStartDate,
          note: note
        })
        
        const week = this.weeks.find(w => w.week_start_date === weekStartDate)
        if (week) {
          week.note = note
        }
      } catch (err) {
        this.error = 'Не удалось обновить заметку'
        console.error(err)
      } finally {
        this.saving = false
      }
    },
    async createSpecialPeriod(periodData) {
      this.saving = true
      try {
        await axios.post(`${API_URL}/grid/special-periods`, periodData)
        await this.fetchSpecialPeriods(periodData.user_id)
      } catch (err) {
        this.error = 'Не удалось создать особый период'
        console.error(err)
      } finally {
        this.saving = false
      }
    },
    async deleteSpecialPeriod(periodId, userId) {
      this.saving = true
      try {
        await axios.delete(`${API_URL}/grid/special-periods/${periodId}`)
        await this.fetchSpecialPeriods(userId)
      } catch (err) {
        this.error = 'Не удалось удалить особый период'
        console.error(err)
      } finally {
        this.saving = false
      }
    }
  }
})
