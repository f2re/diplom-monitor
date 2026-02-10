<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useGridStore } from '../stores/grid';
import { Save, Calendar, User, Smile, Loader2, Clock, Trash2, Plus, Info } from 'lucide-vue-next';

const authStore = useAuthStore();
const gridStore = useGridStore();
const emit = defineEmits(['close']);

const form = ref({
  full_name: authStore.user?.full_name || '',
  start_date: authStore.user?.start_date || '',
  deadline: authStore.user?.deadline || '',
  emoji: authStore.user?.emoji || '🎓'
});

const newPeriod = ref({
  start_date: '',
  end_date: '',
  period_type: 'vacation',
  description: ''
});

const emojis = ['🎓', '📚', '💻', '🧪', '🎨', '🧬', '⚖️', '🏗️'];

onMounted(async () => {
  await gridStore.fetchGridData();
});

const handleSubmit = async () => {
  const success = await authStore.updateProfile(form.value);
  if (success) {
    emit('close');
  }
};

const handleAddPeriod = async () => {
  if (!newPeriod.value.start_date || !newPeriod.value.end_date) return;
  const success = await gridStore.addSpecialPeriod(newPeriod.value);
  if (success) {
    newPeriod.value = {
      start_date: '',
      end_date: '',
      period_type: 'vacation',
      description: ''
    };
  }
};

const handleDeletePeriod = async (id) => {
  await gridStore.deleteSpecialPeriod(id);
};
</script>

<template>
  <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 max-w-2xl mx-auto animate-in fade-in duration-500">
    <div class="flex items-center gap-4 mb-8">
      <div class="bg-blue-100 p-3 rounded-2xl">
        <User class="w-6 h-6 text-blue-600" />
      </div>
      <div>
        <h2 class="text-2xl font-black text-gray-900">Настройки профиля</h2>
        <p class="text-gray-500 font-medium">Настройте параметры вашего обучения</p>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div class="space-y-2">
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Полное имя</label>
        <div class="relative">
          <input 
            v-model="form.full_name" 
            type="text" 
            placeholder="Иван Иванов"
            class="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          <User class="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-2">
          <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Дата начала</label>
          <div class="relative">
            <input 
              v-model="form.start_date" 
              type="date" 
              class="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
            <Calendar class="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
          </div>
        </div>

        <div class="space-y-2">
          <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Дедлайн защиты</label>
          <div class="relative">
            <input 
              v-model="form.deadline" 
              type="date" 
              class="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
            />
            <Clock class="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
          </div>
        </div>
      </div>

      <div class="space-y-3">
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Ваш эмодзи</label>
        <div class="flex flex-wrap gap-3">
          <button 
            v-for="e in emojis" 
            :key="e"
            type="button"
            @click="form.emoji = e"
            :class="[
              'w-12 h-12 flex items-center justify-center text-2xl rounded-xl border-2 transition-all',
              form.emoji === e ? 'border-blue-500 bg-blue-50 shadow-inner' : 'border-gray-100 bg-gray-50 hover:border-gray-200'
            ]"
          >
            {{ e }}
          </button>
        </div>
      </div>

      <div class="flex gap-4 pt-4 border-b border-gray-100 pb-8">
        <button 
          type="button"
          @click="emit('close')"
          class="flex-1 px-6 py-4 border border-gray-200 text-gray-600 font-bold rounded-2xl hover:bg-gray-50 transition-all"
        >
          Отмена
        </button>
        <button 
          type="submit"
          class="flex-[2] px-6 py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all flex items-center justify-center gap-2"
        >
          <Save class="w-5 h-5" />
          Сохранить профиль
        </button>
      </div>
    </form>

    <!-- Секция управления периодами (Administrator Feature) -->
    <div class="mt-10 space-y-6">
      <div class="flex items-center gap-3">
        <div class="bg-indigo-100 p-2.5 rounded-xl">
          <Calendar class="w-5 h-5 text-indigo-600" />
        </div>
        <h3 class="text-xl font-black text-gray-900">Специальные периоды</h3>
      </div>
      
      <p class="text-sm text-gray-500 font-medium">
        Добавьте отпуска, стажировки или каникулы. Эти недели будут вычтены из общего срока подготовки.
      </p>

      <!-- Список существующих периодов -->
      <div v-if="gridStore.specialPeriods.length > 0" class="space-y-3">
        <div v-for="p in gridStore.specialPeriods" :key="p.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-2xl border border-gray-100">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-gray-900 capitalize">{{ p.period_type }}</span>
              <span class="px-2 py-0.5 bg-indigo-50 text-indigo-600 text-[10px] font-black uppercase rounded-md">Активен</span>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ p.start_date }} — {{ p.end_date }}</p>
            <p v-if="p.description" class="text-xs italic text-gray-400 mt-0.5">{{ p.description }}</p>
          </div>
          <button @click="handleDeletePeriod(p.id)" class="p-2 text-gray-400 hover:text-red-500 transition-colors">
            <Trash2 class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Форма добавления -->
      <div class="p-6 bg-blue-50/50 rounded-3xl border border-blue-100/50 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="text-[10px] font-black text-blue-600 uppercase">С</label>
            <input v-model="newPeriod.start_date" type="date" class="w-full px-3 py-2 bg-white border border-blue-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-black text-blue-600 uppercase">По</label>
            <input v-model="newPeriod.end_date" type="date" class="w-full px-3 py-2 bg-white border border-blue-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <select v-model="newPeriod.period_type" class="px-3 py-2 bg-white border border-blue-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500">
            <option value="vacation">Отпуск</option>
            <option value="internship">Стажировка</option>
            <option value="sick_leave">Больничный</option>
            <option value="other">Другое</option>
          </select>
          <input v-model="newPeriod.description" type="text" placeholder="Описание (необяз.)" class="px-3 py-2 bg-white border border-blue-100 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <button 
          @click="handleAddPeriod"
          class="w-full py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all flex items-center justify-center gap-2"
        >
          <Plus class="w-4 h-4" />
          Добавить период
        </button>
      </div>

      <div class="flex items-start gap-3 p-4 bg-orange-50 rounded-2xl border border-orange-100">
        <Info class="w-5 h-5 text-orange-500 shrink-0 mt-0.5" />
        <p class="text-xs text-orange-700 leading-relaxed font-medium">
          Изменения периодов мгновенно пересчитывают ваш "чистый" прогресс в основной сетке.
        </p>
      </div>
    </div>
  </div>
</template>
