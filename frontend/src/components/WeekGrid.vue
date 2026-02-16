<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useGridStore } from '../stores/grid';
import { useUsersStore } from '../stores/users';
import WeekCell from './WeekCell.vue';
import SkeletonLoader from './UX/SkeletonLoader.vue';
import { X, Save, Calendar, Clock, CheckCircle2, Users, User as UserIcon, Loader2 } from 'lucide-vue-next';
import axios from 'axios';

const authStore = useAuthStore();
const gridStore = useGridStore();
const usersStore = useUsersStore();

const selectedUserId = ref(null);
const targetUser = ref(null);
const loadingUser = ref(false);

const isOwnGrid = computed(() => !selectedUserId.value || selectedUserId.value === authStore.user?.id);

// Получение профиля целевого пользователя
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
    console.error('Не удалось загрузить профиль пользователя', err);
  } finally {
    loadingUser.value = false;
  }
};

const weeks = computed(() => {
  const config = gridStore.config;
  if (!config?.start_date || !config?.deadline) return [];
  
  // Use YYYY, MM, DD to avoid timezone shifts when parsing
  const parseDate = (dateStr) => {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d);
  };

  const formatDate = (date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };
  
  const start = parseDate(config.start_date);
  const end = parseDate(config.deadline);
  
  const weeksList = [];
  let current = new Date(start);
  let index = 0;
  
  while (current <= end) {
    const y = current.getFullYear();
    const m = String(current.getMonth() + 1).padStart(2, '0');
    const d = String(current.getDate()).padStart(2, '0');
    const dateStr = `${y}-${m}-${d}`;

    weeksList.push({
      index,
      startDate: dateStr
    });
    current.setDate(current.getDate() + 7);
    index++;
  }
  
  return weeksList;
});

const totalWeeks = computed(() => weeks.value.length);

const currentWeekStart = computed(() => {
  const today = new Date();
  const day = today.getDay(); // 0 (Sun) to 6 (Sat)
  const diff = today.getDate() - (day === 0 ? 6 : day - 1); // Adjust to get Monday
  const monday = new Date(today.setDate(diff));
  
  const yyyy = monday.getFullYear();
  const mm = String(monday.getMonth() + 1).padStart(2, '0');
  const dd = String(monday.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
});

const currentWeekIndex = computed(() => {
    return weeks.value.findIndex(w => w.startDate === currentWeekStart.value);
});

const completedWeeks = computed(() => {
  return gridStore.weeks.filter(w => w.is_completed).length;
});

const progressPercentage = computed(() => {
  if (totalWeeks.value === 0) return 0;
  return Math.round((completedWeeks.value / totalWeeks.value) * 100);
});

// Состояние модального окна
const selectedWeekDate = ref(null);
const selectedWeekNumber = ref(null);
const editForm = ref({
  is_completed: true,
  note: ''
});

const openEditModal = (startDate, weekNumber) => {
  // Check strict week locking
  if (startDate !== currentWeekStart.value) {
    const isPast = new Date(startDate) < new Date(currentWeekStart.value);
    alert(isPast ? "Эта неделя уже прошла и заблокирована 🔒" : "Эта неделя еще не наступила ⏳");
    return;
  }

  // Разрешить редактирование только для своей сетки
  if (!isOwnGrid.value) return;
  
  // Разрешаем редактирование любых недель, чтобы можно было исправлять ошибки или оставлять заметки
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
    <!-- Выбор пользователя -->
    <div class="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
        <div class="flex items-center gap-3">
            <div class="bg-indigo-100 p-2 rounded-lg">
                <Users class="w-5 h-5 text-indigo-600" />
            </div>
            <span class="font-bold text-gray-700">Просмотр:</span>
            <select 
                v-model="selectedUserId"
                class="bg-gray-50 border border-gray-200 rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-indigo-500 font-medium"
            >
                <option :value="authStore.user?.id">Моя сетка</option>
                <optgroup label="Публичные сетки">
                    <option v-for="user in usersStore.users.filter(u => u.id !== authStore.user?.id)" :key="user.id" :value="user.id">
                        {{ user.emoji }} {{ user.full_name }}
                    </option>
                </optgroup>
            </select>
        </div>
        
        <div v-if="!isOwnGrid" class="flex items-center gap-2 px-4 py-2 bg-amber-50 text-amber-700 rounded-xl text-sm font-bold border border-amber-100">
            <Clock class="w-4 h-4" />
            Режим просмотра
        </div>
    </div>

    <!-- Пустое состояние, если даты не заданы -->
    <div v-if="!gridStore.config?.start_date || !gridStore.config?.deadline" class="bg-blue-50 border-2 border-blue-200 rounded-3xl p-12 text-center">
        <Loader2 v-if="loadingUser" class="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
        <template v-else>
            <h2 class="text-2xl font-black text-blue-900 mb-4">Даты не заданы 🗓️</h2>
            <p class="text-blue-700 font-medium max-w-md mx-auto mb-8">
                {{ authStore.user?.is_superuser ? 'Пожалуйста, укажите дату начала и дедлайн в настройках.' : 'Администратор еще не указал глобальные даты обучения.' }}
            </p>
        </template>
    </div>

    <template v-else>
        <!-- Заголовок/Дашборд -->
        <div v-if="gridStore.loading" class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-8 items-center justify-between">
           <div class="space-y-4 w-full md:w-1/2">
              <SkeletonLoader height="2.5rem" width="70%" />
              <SkeletonLoader height="1.25rem" width="40%" />
           </div>
           <div class="flex gap-6 items-center">
              <SkeletonLoader height="5rem" width="5rem" class="rounded-full" />
              <div class="space-y-2">
                 <SkeletonLoader height="1.25rem" width="100px" />
                 <SkeletonLoader height="1.25rem" width="100px" />
              </div>
           </div>
        </div>
        <div v-else class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-8 items-center justify-between transition-all">
          <div class="space-y-2 text-center md:text-left">
            <div class="flex items-center justify-center md:justify-start gap-3">
                <span class="text-4xl">{{ targetUser?.emoji }}</span>
                <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">
                    {{ isOwnGrid ? 'Ваш прогресс' : targetUser?.full_name }}
                </h1>
            </div>
            <p class="text-gray-500 font-medium flex items-center gap-2 justify-center md:justify-start">
              <Calendar class="w-4 h-4" />
              Путь длиной в {{ totalWeeks }} недель
            </p>
          </div>

          <div class="flex gap-6 items-center">
            <div class="text-center">
              <p class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Прогресс</p>
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
                <span>{{ completedWeeks }} выполнено</span>
              </div>
              <div class="flex items-center gap-2 text-slate-800 font-bold">
                <Clock class="w-5 h-5" />
                <span>{{ totalWeeks - completedWeeks }} осталось</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Сетка -->
        <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
          <div v-if="gridStore.loading" class="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-10 lg:grid-cols-12 xl:grid-cols-15 gap-3">
            <SkeletonLoader v-for="i in 40" :key="i" height="2.5rem" width="100%" />
          </div>
          <div v-else class="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-10 lg:grid-cols-12 xl:grid-cols-15 gap-3">
            <WeekCell 
              v-for="week in weeks" 
              :key="week.startDate" 
              :week-number="week.index"
              :start-date="week.startDate"
              :progress="gridStore.getWeekByDate(week.startDate)"
              :completions="gridStore.getCompletionsByDate(week.startDate)"
              :special-period="gridStore.isSpecialPeriod(week.startDate)"
              :is-current="week.startDate === currentWeekStart"
              @click="openEditModal"
            />
          </div>
          
          <!-- Легенда -->
          <div class="mt-8 pt-6 border-t border-gray-100 flex flex-wrap gap-6 text-sm font-medium text-gray-500">
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-green-500 rounded shadow-sm"></div>
              <span>Выполнено</span>
            </div>
            <div class="flex items-center gap-2">
                <div class="w-4 h-4 bg-slate-900 rounded shadow-sm text-white flex items-center justify-center text-[10px]">✕</div>
                <span>Пропущено</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-white border-2 border-blue-400 ring-2 ring-blue-400 ring-offset-1 rounded shadow-sm"></div>
              <span>Текущая неделя</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 bg-amber-100 border border-amber-300 rounded shadow-sm"></div>
              <span>Спец. период</span>
            </div>
          </div>
          <div v-if="isOwnGrid" class="mt-4 text-xs text-gray-400 italic">
            * Нажмите на неделю, чтобы отметить прогресс или оставить заметку.
          </div>
        </div>
    </template>

    <!-- Модальное окно редактирования -->
    <div v-if="selectedWeekDate !== null" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
        <div class="bg-gray-50 px-8 py-6 flex items-center justify-between border-b">
          <div>
            <h3 class="text-xl font-extrabold text-gray-900">Неделя {{ selectedWeekNumber + 1 }}</h3>
            <p class="text-sm text-gray-500">Начиная с {{ selectedWeekDate }}</p>
          </div>
          <button @click="closeEditModal" class="p-2 hover:bg-gray-200 rounded-full transition-colors">
            <X class="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <div class="p-8 space-y-6">
          <div class="space-y-3">
            <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider text-center">Был ли прогресс?</label>
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
                ДА! 🚀
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
                НЕТ 😴
              </button>
            </div>
          </div>

          <div class="space-y-3">
            <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Заметки (опционально)</label>
            <textarea 
              v-model="editForm.note" 
              rows="3" 
              placeholder="Что было сделано за эту неделю?" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none resize-none"
            ></textarea>
          </div>
        </div>

        <div class="bg-gray-50 px-8 py-6 flex gap-4">
          <button 
            @click="closeEditModal" 
            class="flex-1 px-6 py-3 border border-gray-200 bg-white text-gray-600 font-bold rounded-xl hover:bg-gray-100 transition-colors"
          >
            Отмена
          </button>
          <button 
            @click="saveWeekProgress" 
            class="flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 active:scale-95"
          >
            <Save class="w-5 h-5" />
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
