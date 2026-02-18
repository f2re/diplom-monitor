<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useGridStore } from '../stores/grid';
import { useUsersStore } from '../stores/users';
import { useToast } from '../composables/useToast';
import WeekCell from './WeekCell.vue';
import SkeletonLoader from './UX/SkeletonLoader.vue';
import { X, Save, Calendar, Clock, CheckCircle2, Users, Loader2, LayoutGrid } from 'lucide-vue-next';
import axios from 'axios';
import { API_URL } from '../config';

const authStore = useAuthStore();
const gridStore = useGridStore();
const usersStore = useUsersStore();
const { add: addToast } = useToast();

// null = своя сетка, -1 = сводная, число = чужой userId
const selectedUserId = ref(null);
const targetUser = ref(null);
const loadingUser = ref(false);

const isOwnGrid = computed(() =>
  !selectedUserId.value || selectedUserId.value === authStore.user?.id
);
const isSummary = computed(() => selectedUserId.value === -1);

const fetchTargetUser = async (userId) => {
  if (!userId || userId === authStore.user?.id || userId === -1) {
    targetUser.value = authStore.user;
    return;
  }
  loadingUser.value = true;
  try {
    const res = await axios.get(`${API_URL}/users/${userId}`);
    targetUser.value = res.data;
  } catch (err) {
    console.error('Не удалось загрузить профиль', err);
  } finally {
    loadingUser.value = false;
  }
};

const weeks = computed(() => {
  const config = gridStore.config;
  if (!config?.start_date || !config?.deadline) return [];
  const parseDate = (s) => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
  const start = parseDate(config.start_date);
  const end   = parseDate(config.deadline);
  const list = [];
  let cur = new Date(start), i = 0;
  while (cur <= end) {
    const y = cur.getFullYear();
    const m = String(cur.getMonth() + 1).padStart(2, '0');
    const d = String(cur.getDate()).padStart(2, '0');
    list.push({ index: i, startDate: `${y}-${m}-${d}` });
    cur.setDate(cur.getDate() + 7);
    i++;
  }
  return list;
});

const totalWeeks = computed(() => weeks.value.length);

const currentWeekStart = computed(() => {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - (day === 0 ? 6 : day - 1);
  const monday = new Date(today.getFullYear(), today.getMonth(), diff);
  const yyyy = monday.getFullYear();
  const mm = String(monday.getMonth() + 1).padStart(2, '0');
  const dd = String(monday.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
});

const completedWeeks = computed(() =>
  gridStore.weeks.filter(w => w.is_completed).length
);

const progressPercentage = computed(() => {
  if (totalWeeks.value === 0) return 0;
  return Math.round((completedWeeks.value / totalWeeks.value) * 100);
});

// Компьютед: completions для каждой ячейки (всегда все пользователи)
const getCompletions = (weekStartDate) =>
  gridStore.getCompletionsByDate(weekStartDate, usersStore.users);

// Модальное окно
const selectedWeekDate = ref(null);
const selectedWeekNumber = ref(null);
const editForm = ref({ is_completed: true, note: '' });

const openEditModal = (startDate, weekNumber) => {
  if (isSummary.value) return; // в сводной не редактируем
  if (startDate !== currentWeekStart.value) {
    const isPast = new Date(startDate) < new Date(currentWeekStart.value);
    addToast(
      isPast ? 'Эта неделя уже прошла и заблокирована 🔒' : 'Эта неделя ещё не наступила ⏳',
      isPast ? 'warning' : 'info'
    );
    return;
  }
  if (!isOwnGrid.value) return;
  const existing = gridStore.getWeekByDate(startDate);
  selectedWeekDate.value  = startDate;
  selectedWeekNumber.value = weekNumber;
  editForm.value = existing
    ? { is_completed: existing.is_completed, note: existing.note || '' }
    : { is_completed: true, note: '' };
};

const closeEditModal = () => {
  selectedWeekDate.value  = null;
  selectedWeekNumber.value = null;
};

const saveWeekProgress = async () => {
  const ok = await gridStore.updateWeek(
    selectedWeekDate.value,
    editForm.value.is_completed,
    editForm.value.note
  );
  if (ok) { closeEditModal(); addToast('Прогресс сохранён! 🚀', 'success'); }
};

onMounted(async () => {
  if (!authStore.user?.id) return;
  selectedUserId.value = authStore.user.id;
  targetUser.value     = authStore.user;
  await Promise.all([
    gridStore.fetchGridData(authStore.user.id),
    usersStore.fetchUsers(),
  ]);
});

watch(selectedUserId, async (newId) => {
  if (newId === -1) {
    // Сводная: перезагружаем allProgress, не меняем weeks
    targetUser.value = authStore.user;
    await gridStore.fetchAllProgress();
    return;
  }
  if (!newId) return;
  await fetchTargetUser(newId);
  await gridStore.fetchGridData(newId);
});
</script>

<template>
  <div class="space-y-8 max-w-6xl mx-auto px-4 py-8">

    <!-- Селектор сетки -->
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
          <!-- Сводная — для всех (особенно удобна админу) -->
          <option :value="-1">📊 Сводная сетка (все участники)</option>
          <optgroup label="Индивидуальные сетки">
            <option
              v-for="user in usersStore.users.filter(u => u.id !== authStore.user?.id)"
              :key="user.id"
              :value="user.id"
            >{{ user.emoji }} {{ user.full_name }}</option>
          </optgroup>
        </select>
      </div>

      <div
        v-if="isSummary"
        class="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-xl text-sm font-bold border border-indigo-100"
      >
        <LayoutGrid class="w-4 h-4" />
        Сводный просмотр
      </div>
      <div
        v-else-if="!isOwnGrid"
        class="flex items-center gap-2 px-4 py-2 bg-amber-50 text-amber-700 rounded-xl text-sm font-bold border border-amber-100"
      >
        <Clock class="w-4 h-4" />
        Режим просмотра
      </div>
    </div>

    <!-- Нет дат -->
    <div
      v-if="!gridStore.config?.start_date || !gridStore.config?.deadline"
      class="bg-blue-50 border-2 border-blue-200 rounded-3xl p-12 text-center"
    >
      <Loader2 v-if="gridStore.loading" class="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
      <template v-else>
        <h2 class="text-2xl font-black text-blue-900 mb-4">Даты не заданы 📅</h2>
        <p class="text-blue-700 font-medium max-w-md mx-auto">
          {{ authStore.user?.is_superuser
            ? 'Укажите дату начала и дедлайн в настройках.'
            : 'Администратор ещё не указал глобальные даты обучения.' }}
        </p>
      </template>
    </div>

    <template v-else>
      <!-- Дашборд -->
      <div
        v-if="gridStore.loading"
        class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-8 items-center justify-between"
      >
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

      <div
        v-else
        class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 flex flex-col md:flex-row gap-8 items-center justify-between"
      >
        <!-- Сводная -->
        <template v-if="isSummary">
          <div class="space-y-2 text-center md:text-left">
            <div class="flex items-center justify-center md:justify-start gap-3">
              <span class="text-4xl">📊</span>
              <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Сводная сетка</h1>
            </div>
            <p class="text-gray-500 font-medium flex items-center gap-2 justify-center md:justify-start">
              <Users class="w-4 h-4" />
              {{ usersStore.users.length }} участников · {{ totalWeeks }} недель
            </p>
          </div>
          <div class="flex flex-wrap gap-3 justify-center">
            <div
              v-for="user in usersStore.users"
              :key="user.id"
              class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-xl border border-gray-100"
            >
              <span class="text-xl">{{ user.emoji || '🎓' }}</span>
              <span class="text-sm font-bold text-gray-700">{{ user.full_name }}</span>
            </div>
          </div>
        </template>

        <!-- Индивидуальная -->
        <template v-else>
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
                  <circle cx="40" cy="40" r="36" stroke="currentColor" stroke-width="8" fill="transparent"
                    :stroke-dasharray="226.19"
                    :stroke-dashoffset="226.19 * (1 - progressPercentage / 100)"
                    class="text-blue-500 transition-all duration-1000" />
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
        </template>
      </div>

      <!-- Сетка -->
      <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
        <div
          v-if="gridStore.loading"
          class="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-10 lg:grid-cols-12 xl:grid-cols-15 gap-3"
        >
          <SkeletonLoader v-for="i in 40" :key="i" height="2.5rem" width="100%" />
        </div>
        <div
          v-else
          class="grid grid-cols-4 sm:grid-cols-7 md:grid-cols-10 lg:grid-cols-12 xl:grid-cols-15 gap-3"
        >
          <WeekCell
            v-for="week in weeks"
            :key="week.startDate"
            :week-number="week.index"
            :start-date="week.startDate"
            :progress="gridStore.getWeekByDate(week.startDate)"
            :completions="getCompletions(week.startDate)"
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
            <div class="w-4 h-4 bg-slate-800 rounded shadow-sm text-white flex items-center justify-center text-[10px]">✕</div>
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
        <div v-if="isOwnGrid && !isSummary" class="mt-4 text-xs text-gray-400 italic">
          * Нажмите на текущую неделю, чтобы отметить прогресс или оставить заметку.
        </div>
      </div>
    </template>

    <!-- Модальное окно -->
    <div
      v-if="selectedWeekDate !== null"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm"
    >
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
                  editForm.is_completed ? 'border-green-500 bg-green-50 text-green-700 shadow-inner' : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                ]"
              >ДА! 🚀</button>
              <button
                @click="editForm.is_completed = false"
                :class="[
                  'flex-1 py-4 px-6 rounded-2xl border-2 font-black transition-all text-lg',
                  !editForm.is_completed ? 'border-red-500 bg-red-50 text-red-700 shadow-inner' : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                ]"
              >НЕТ 😴</button>
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
          >Отмена</button>
          <button
            @click="saveWeekProgress"
            :disabled="gridStore.saving"
            class="flex-1 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 active:scale-95 disabled:opacity-70"
          >
            <Loader2 v-if="gridStore.saving" class="w-5 h-5 animate-spin" />
            <Save v-else class="w-5 h-5" />
            Сохранить
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
