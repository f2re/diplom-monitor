<script setup>
import { computed } from 'vue';

const props = defineProps({
  weekNumber: { type: Number, required: true },
  startDate: { type: String, required: true },
  progress: { type: Object, default: null },
  completions: { type: Array, default: () => [] },
  specialPeriod: { type: Object, default: null },
  isCurrent: { type: Boolean, default: false }
});

const emit = defineEmits(['click']);

const isPast = computed(() => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const day = today.getDay();
  const diff = today.getDate() - (day === 0 ? 6 : day - 1);
  const currentMonday = new Date(today.getFullYear(), today.getMonth(), diff);
  const [y, m, d] = props.startDate.split('-').map(Number);
  return new Date(y, m - 1, d) < currentMonday;
});

const isMissed = computed(() =>
  isPast.value && (!props.progress || !props.progress.is_completed)
);

const completedCount = computed(() =>
  props.completions.filter(u => u.is_completed).length
);

const cellClasses = computed(() => {
  const base = 'relative w-full aspect-square rounded-xl border-2 flex items-center justify-center transition-all duration-200 text-xs font-bold shadow-sm overflow-visible cursor-pointer hover:shadow-lg hover:scale-105 active:scale-95 group';
  let state = '';
  if (props.progress?.is_completed) {
    state = 'bg-green-500 border-green-600 text-white';
  } else if (isMissed.value) {
    state = 'bg-slate-800 border-slate-900 text-white';
  } else if (props.specialPeriod) {
    state = 'bg-amber-100 border-amber-300 text-amber-700';
  } else if (props.isCurrent) {
    state = 'bg-blue-50 border-blue-300 text-blue-600';
  } else {
    state = 'bg-white border-gray-100 text-gray-300';
  }
  const ring = props.isCurrent
    ? 'ring-4 ring-blue-400/60 ring-offset-1 z-20 shadow-blue-100 shadow-lg'
    : 'z-10';
  return `${base} ${state} ${ring}`;
});
</script>

<template>
  <div :class="cellClasses" @click="emit('click', startDate, weekNumber)">

    <!-- Tooltip при наведении -->
    <div
      class="absolute bottom-[calc(100%+10px)] left-1/2 -translate-x-1/2
             w-56 bg-slate-900 text-white text-[11px] rounded-2xl p-3
             shadow-2xl border border-slate-700/60
             opacity-0 scale-95 pointer-events-none
             group-hover:opacity-100 group-hover:scale-100
             transition-all duration-200 ease-out origin-bottom z-[100]"
    >
      <!-- Заголовок -->
      <div class="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-700/60">
        <span class="font-black text-white">Неделя {{ weekNumber + 1 }}</span>
        <span class="text-slate-400 text-[10px]">{{ startDate }}</span>
      </div>

      <!-- Список участников -->
      <div v-if="completions.length === 0" class="text-slate-400 italic text-center py-1">Нет участников</div>
      <div v-else class="flex flex-col gap-1.5">
        <div
          v-for="user in completions"
          :key="user.user_id"
          class="flex flex-col gap-0.5"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-1.5 min-w-0">
              <span class="text-sm leading-none flex-shrink-0">{{ user.emoji }}</span>
              <span class="font-semibold truncate" :class="user.is_completed ? 'text-white' : 'text-slate-400'">{{ user.full_name }}</span>
            </div>
            <span
              :class="[
                'flex-shrink-0 text-[10px] font-black px-1.5 py-0.5 rounded-full',
                user.is_completed
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-slate-700 text-slate-400'
              ]"
            >{{ user.is_completed ? '✓ да' : '✗ нет' }}</span>
          </div>
          <div v-if="user.note" class="text-slate-400 italic text-[9px] pl-6 leading-tight line-clamp-2">
            "{{ user.note }}"
          </div>
        </div>
      </div>

      <!-- Итого -->
      <div class="mt-2 pt-1.5 border-t border-slate-700/60 flex justify-between text-[10px]">
        <span class="text-green-400 font-bold">✓ {{ completedCount }} отметились</span>
        <span class="text-slate-400">{{ completions.length - completedCount }} нет</span>
      </div>

      <!-- Стрелка вниз -->
      <div class="absolute top-full left-1/2 -translate-x-1/2 border-[6px] border-transparent border-t-slate-900"></div>
    </div>

    <!-- Номер недели — всегда виден в углу -->
    <span
      class="absolute top-0.5 left-1 text-[9px] font-black leading-none pointer-events-none select-none"
      :class="(props.progress?.is_completed || isMissed) ? 'text-white/60' : 'text-gray-400'"
    >{{ weekNumber + 1 }}</span>

    <!-- Эмодзи участников внутри клетки -->
    <div class="grid grid-cols-2 gap-0.5 p-1 w-full h-full content-center justify-items-center">
      <span
        v-for="user in completions"
        :key="user.user_id"
        class="text-[10px] sm:text-[11px] leading-none transition-all"
        :class="user.is_completed ? 'opacity-100 drop-shadow-sm' : 'opacity-20 grayscale'"
        :title="user.full_name"
      >{{ user.emoji }}</span>
    </div>

    <!-- Текущая неделя — синяя полоска сверху -->
    <div v-if="isCurrent" class="absolute top-0 left-0 w-full h-1 bg-blue-500 rounded-t-xl animate-pulse"></div>

    <!-- Спец. период — оранжевая точка -->
    <div v-if="specialPeriod" class="absolute -top-1 -right-1 z-30">
      <div class="w-3 h-3 bg-amber-500 rounded-full border border-white shadow-sm animate-pulse"></div>
    </div>
  </div>
</template>
