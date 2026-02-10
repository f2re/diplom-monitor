<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useGridStore } from '../stores/grid';
import { useUsersStore } from '../stores/users';
import WeekCell from './WeekCell.vue';
import { X, Save, Calendar, Clock, CheckCircle2, Users, User as UserIcon, Loader2 } from 'lucide-vue-next';
import axios from 'axios';

const authStore = useAuthStore();
const gridStore = useGridStore();
const usersStore = useUsersStore();

const selectedUserId = ref(null);
const targetUser = ref(null);
const loadingUser = ref(false);

const isOwnGrid = computed(() => !selectedUserId.value || selectedUserId.value === authStore.user?.id);

// Fetch target user profile (dates)
const fetchTargetUser = async (userId) => {
  if (!userId || userId === authStore.user?.id) {
    targetUser.value = authStore.user;
    return;
  }
  loadingUser.value = true;
  try {
    const response = await axios.get(`http://localhost:8000/users/${userId}`);
    targetUser.value = response.data;
  } catch (err) {
    console.error('Failed to fetch user profile', err);
  } finally {
    loadingUser.value = false;
  }
};

const weeks = computed(() => {
  const user = targetUser.value;
  if (!user?.start_date || !user?.deadline) return [];
  
  const start = new Date(user.start_date);
  const end = new Date(user.deadline);
  
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

const currentWeekStart = computed(() => {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1); // Monday
  const monday = new Date(today.setDate(diff));
  return monday.toISOString().split('T')[0];
});

const currentWeekIndex = computed(() => {
    const user = targetUser.value;
    if (!user?.start_date) return -1;
    const start = new Date(user.start_date);
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
  // Allow edit only for own grid AND current week
  if (!isOwnGrid.value) return;
  if (startDate !== currentWeekStart.value) return;

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

onMounted(async () => {
  selectedUserId.value = authStore.user?.id;
  targetUser.value = authStore.user;
  await Promise.all([
    gridStore.fetchGridData(),
    usersStore.fetchUsers()
  ]);
});

watch(selectedUserId, async (newId) => {
  await fetchTargetUser(newId);
  await gridStore.fetchGridData(newId);
});
</script>

<template>
  <div class="space-y-8 max-w-6xl mx-auto px-4 py-8">
    <!-- User Selector -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
        <div class="flex items-center gap-3">
            <div class="bg-indigo-100 p-2 rounded-lg">
                <Users class="w-5 h-5 text-indigo-600" />
            </div>
            <span class="font-bold text-gray-700">View Grid:</span>
            <select 
                v-model="selectedUserId"
                class="bg-gray-50 border border-gray-200 rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
            >
                <option :value="authStore.user?.id">My Private Grid</option>
                <optgroup label="Public Grids">
                    <option v-for="user in usersStore.users.filter(u => u.id !== authStore.user?.id)" :key="user.id" :value="user.id">
                        {{ user.emoji }} {{ user.full_name }}
                    </option>
                </optgroup>
            </select>
        </div>
        
        <div v-if="!isOwnGrid" class="flex items-center gap-2 px-4 py-2 bg-amber-50 text-amber-700 rounded-xl text-sm font-bold border border-amber-100">
            <Clock class="w-4 h-4" />
            Read-only Mode
        </div>
    </div>

    <!-- Empty state if dates not set -->
    <div v-if="!targetUser?.start_date || !targetUser?.deadline" class="bg-blue-50 border-2 border-blue-200 rounded-3xl p-12 text-center">
        <Loader2 v-if="loadingUser" class="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
        <template v-else>
            <h2 class="text-2xl font-black text-blue-900 mb-4">Dates not set 🗓️</h2>
            <p class="text-blue-700 font-medium max-w-md mx-auto mb-8">
                {{ isOwnGrid ? 'Please set your start date and deadline in settings.' : 'This user hasn\'t set their diploma dates yet.' }}
            </p>
        </template>
    </div>

    <template v-else>
        <!-- Header/Dashboard -->
        <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-8 items-center justify-between transition-all">
          <div class="space-y-2 text-center md:text-left">
            <div class="flex items-center justify-center md:justify-start gap-3">
                <span class="text-4xl">{{ targetUser?.emoji }}</span>
                <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">
                    {{ isOwnGrid ? 'Your Progress' : targetUser?.full_name }}
                </h1>
            </div>
            <p class="text-gray-500 font-medium flex items-center gap-2 justify-center md:justify-start">
              <Calendar class="w-4 h-4" />
              {{ totalWeeks }} weeks journey
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
              <div class="flex items-center gap-2 text-slate-800 font-bold">
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
              :is-current="week.startDate === currentWeekStart"
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
                <div class="w-4 h-4 bg-slate-900 rounded shadow-sm text-white flex items-center justify-center text-[10px]">✕</div>
                <span>Missed</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-blue-50 border border-blue-400 rounded shadow-sm"></div>
              <span>Current Week</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-amber-100 border border-amber-300 rounded shadow-sm"></div>
              <span>Special Period</span>
            </div>
          </div>
          <div v-if="isOwnGrid" class="mt-4 text-xs text-gray-400 italic">
            * You can only mark progress for the current week.
          </div>
        </div>
    </template>

    <!-- Edit Modal (same as before) -->
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
@media (min-width: 1280px) {
  .xl\:grid-cols-15 {
    grid-template-columns: repeat(15, minmax(0, 1fr));
  }
}
</style>
