<script setup>
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useGridStore } from '../stores/grid';
import WeekCell from './WeekCell.vue';
import { X, Save, Calendar, Clock, CheckCircle2 } from 'lucide-vue-next';

const authStore = useAuthStore();
const gridStore = useGridStore();

const weeks = computed(() => {
  if (!authStore.user?.start_date || !authStore.user?.deadline) return [];
  
  const start = new Date(authStore.user.start_date);
  const end = new Date(authStore.user.deadline);
  
  const weeksList = [];
  let current = new Date(start);
  let index = 0;
  
  while (current <= end) {
    weeksList.push({
      index,
      startDate: current.toISOString().split('T')[0]
    });
    current.setDate(current.getDate() + 7);
    index++;
  }
  
  return weeksList;
});

const totalWeeks = computed(() => weeks.value.length);

const currentWeekIndex = computed(() => {
  if (!authStore.user?.start_date) return -1;
  const start = new Date(authStore.user.start_date);
  const now = new Date();
  const diffTime = now - start;
  if (diffTime < 0) return -1;
  return Math.floor(diffTime / (1000 * 60 * 60 * 24 * 7));
});

const completedWeeks = computed(() => {
  return gridStore.weeks.filter(w => w.is_completed).length;
});

const progressPercentage = computed(() => {
  if (totalWeeks.value === 0) return 0;
  return Math.round((completedWeeks.value / totalWeeks.value) * 100);
});

// Modal state
const selectedWeekDate = ref(null);
const selectedWeekNumber = ref(null);
const editForm = ref({
  is_completed: true,
  note: ''
});

const openEditModal = (startDate, weekNumber) => {
  const existing = gridStore.getWeekByDate(startDate);
  selectedWeekDate.value = startDate;
  selectedWeekNumber.value = weekNumber;
  editForm.value = existing ? { ...existing } : {
    is_completed: true,
    note: ''
  };
};

const closeEditModal = () => {
  selectedWeekDate.value = null;
  selectedWeekNumber.value = null;
};

const saveWeekProgress = async () => {
  const success = await gridStore.updateWeek(
    selectedWeekDate.value,
    editForm.value.is_completed,
    editForm.value.note
  );
  if (success) closeEditModal();
};

onMounted(() => {
  gridStore.fetchGridData();
});
</script>

<template>
  <div class="space-y-8 max-w-6xl mx-auto px-4 py-8">
    <!-- Empty state if dates not set -->
    <div v-if="!authStore.user?.start_date || !authStore.user?.deadline" class="bg-blue-50 border-2 border-blue-200 rounded-3xl p-12 text-center">
        <h2 class="text-2xl font-black text-blue-900 mb-4">Set your dates to begin tracking! 🗓️</h2>
        <p class="text-blue-700 font-medium max-w-md mx-auto mb-8">
            To generate your diploma progress grid, we need to know your start date and defense deadline.
        </p>
        <!-- For now just a message, we'll add SettingsForm soon -->
        <p class="text-sm text-blue-500 italic">Profile settings coming soon...</p>
    </div>

    <template v-else>
        <!-- Header/Dashboard -->
        <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-8 items-center justify-between">
          <div class="space-y-2 text-center md:text-left">
            <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">
              Hello, {{ authStore.user?.full_name || 'Student' }}! 👋
            </h1>
            <p class="text-gray-500 font-medium flex items-center gap-2 justify-center md:justify-start">
              <Calendar class="w-4 h-4" />
              {{ totalWeeks }} weeks in your journey
            </p>
          </div>

          <div class="flex gap-6 items-center">
            <div class="text-center">
              <p class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Progress</p>
              <div class="relative flex items-center justify-center">
                 <svg class="w-20 h-20 transform -rotate-90">
                    <circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="8" fill="transparent" class="text-gray-100" />
                    <circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="8" fill="transparent" :stroke-dasharray="226.19" :stroke-dashoffset="226.19 * (1 - progressPercentage / 100)" class="text-blue-500 transition-all duration-1000" />
                 </svg>
                 <span class="absolute text-lg font-black text-gray-700">{{ progressPercentage }}%</span>
              </div>
            </div>
            
            <div class="space-y-1">
              <div class="flex items-center gap-2 text-green-600 font-bold">
                <CheckCircle2 class="w-5 h-5" />
                <span>{{ completedWeeks }} completed</span>
              </div>
              <div class="flex items-center gap-2 text-blue-600 font-bold">
                <Clock class="w-5 h-5" />
                <span>{{ totalWeeks - completedWeeks }} remaining</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Grid -->
        <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
          <div class="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-10 lg:grid-cols-12 xl:grid-cols-15 gap-3">
            <WeekCell 
              v-for="week in weeks" 
              :key="week.startDate" 
              :week-number="week.index"
              :start-date="week.startDate"
              :progress="gridStore.getWeekByDate(week.startDate)"
              :special-period="gridStore.isSpecialPeriod(week.startDate)"
              :is-current="week.index === currentWeekIndex"
              @click="openEditModal"
            />
          </div>
          
          <!-- Legend -->
          <div class="mt-8 pt-6 border-t border-gray-100 flex flex-wrap gap-6 text-sm font-medium text-gray-500">
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-green-500 rounded shadow-sm"></div>
              <span>Completed</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-blue-50 border border-blue-400 rounded shadow-sm"></div>
              <span>Current Week</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-amber-100 border border-amber-300 rounded shadow-sm"></div>
              <span>Special Period</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-white border border-gray-100 rounded shadow-sm"></div>
              <span>Future Week</span>
            </div>
          </div>
        </div>
    </template>

    <!-- Edit Modal -->
    <div v-if="selectedWeekDate !== null" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
        <div class="bg-gray-50 px-8 py-6 flex items-center justify-between border-b">
          <div>
            <h3 class="text-xl font-extrabold text-gray-900">Week {{ selectedWeekNumber + 1 }}</h3>
            <p class="text-sm text-gray-500">Starting on {{ selectedWeekDate }}</p>
          </div>
          <button @click="closeEditModal" class="p-2 hover:bg-gray-200 rounded-full transition-colors">
            <X class="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <div class="p-8 space-y-6">
          <div class="space-y-3">
            <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider text-center">Did you make progress?</label>
            <div class="flex justify-center gap-4">
              <button 
                @click="editForm.is_completed = true"
                :class="[
                  'flex-1 py-4 px-6 rounded-2xl border-2 font-black transition-all text-lg',
                  editForm.is_completed
                    ? 'border-green-500 bg-green-50 text-green-700 shadow-inner' 
                    : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                ]"
              >
                YES! 🚀
              </button>
              <button 
                @click="editForm.is_completed = false"
                :class="[
                  'flex-1 py-4 px-6 rounded-2xl border-2 font-black transition-all text-lg',
                  !editForm.is_completed
                    ? 'border-red-500 bg-red-50 text-red-700 shadow-inner' 
                    : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                ]"
              >
                NOT YET 😴
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Notes (Optional)</label>
            <textarea 
              v-model="editForm.note" 
              rows="3" 
              placeholder="What did you achieve this week?" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            ></textarea>
          </div>
        </div>

        <div class="bg-gray-50 px-8 py-6 flex gap-4">
          <button 
            @click="closeEditModal" 
            class="flex-1 px-6 py-3 border border-gray-200 bg-white text-gray-600 font-bold rounded-xl hover:bg-gray-100 transition-colors"
          >
            Cancel
          </button>
          <button 
            @click="saveWeekProgress" 
            class="flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 active:scale-95"
          >
            <Save class="w-5 h-5" />
            Save Progress
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom grid column count for larger screens */
@media (min-width: 1280px) {
  .xl\:grid-cols-15 {
    grid-template-columns: repeat(15, minmax(0, 1fr));
  }
}

@keyframes zoom-in-95 {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.zoom-in-95 {
  animation: zoom-in-95 0.2s ease-out forwards;
}
</style>