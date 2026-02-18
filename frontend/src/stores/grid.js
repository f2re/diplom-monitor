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
    getWeekByDate: (state) => (weekStartDate) => {
      return state.weeks.find(w => w.week_start_date === weekStartDate) || null
    },
    getCompletionsByDate: (state) => (weekStartDate) => {
      return state.allProgress
        .filter(p => p.completions.some(c => c.date === weekStartDate))
        .map(p => ({
          emoji: p.emoji,
          note: p.completions.find(c => c.date === weekStartDate)?.note || null
        }))
    },
    isSpecialPeriod: (state) => (weekStartDate) => {
      if (!state.specialPeriods.length) return null
      const weekDate = new Date(weekStartDate)
      return state.specialPeriods.find(period => {
        const start = new Date(period.start_date)
        const end = new Date(period.end_date)
        return weekDate >= start && weekDate <= end
      }) || null
    },
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
    async fetchGridData(userId = null) {
      this.loading = true
      this.error = null
      try {
        await Promise.all([
          this.fetchConfig(),
          this.fetchAllProgress(),
        ])
        if (userId) {
          await Promise.all([
            this.fetchWeeks(userId),
            this.fetchStats(userId),
            this.fetchSpecialPeriods(userId),
          ])
        }
      } catch (err) {
        this.error = 'Не удалось загрузить данные'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async fetchConfig() {
      try {
        const response = await axios.get(`${API_URL}/grid/config`)
        this.config = response.data
      } catch (err) {
        this.error = 'Не удалось загрузить конфигурацию'
        console.error(err)
      }
    },
    async fetchWeeks(userId) {
      try {
        const response = await axios.get(`${API_URL}/grid/weeks/${userId}`)
        this.weeks = response.data
      } catch (err) {
        this.error = 'Не удалось загрузить прогресс'
        console.error(err)
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
    // POST (не PUT!) — так ожидает backend
    async updateWeek(weekStartDate, isCompleted, note) {
      this.saving = true
      try {
        await axios.post(`${API_URL}/grid/weeks`, {
          week_start_date: weekStartDate,
          is_completed: isCompleted,
          note: note,
        })
        const existing = this.weeks.find(w => w.week_start_date === weekStartDate)
        if (existing) {
          existing.is_completed = isCompleted
          existing.note = note
        } else {
          this.weeks.push({ week_start_date: weekStartDate, is_completed: isCompleted, note })
        }
        return true
      } catch (err) {
        this.error = 'Не удалось сохранить прогресс'
        console.error(err)
        return false
      } finally {
        this.saving = false
      }
    },
    async toggleWeek(weekStartDate) {
      const week = this.weeks.find(w => w.week_start_date === weekStartDate)
      const newStatus = week ? !week.is_completed : true
      return await this.updateWeek(weekStartDate, newStatus, week?.note || null)
    },
    async updateWeekNote(weekStartDate, note) {
      const week = this.weeks.find(w => w.week_start_date === weekStartDate)
      return await this.updateWeek(weekStartDate, week?.is_completed || false, note)
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
