<script setup>
import { computed } from 'vue';

const props = defineProps({
  weekNumber: {
    type: Number,
    required: true
  },
  startDate: {
    type: String,
    required: true
  },
  progress: {
    type: Object,
    default: null
  },
  completions: {
    type: Array,
    default: () => []
  },
  specialPeriod: {
    type: Object,
    default: null
  },
  isCurrent: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click']);

const isPast = computed(() => {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  // Get Monday of the current week (Monday-Sunday logic)
  const day = today.getDay(); // 0 (Sun) to 6 (Sat)
  const diff = today.getDate() - (day === 0 ? 6 : day - 1);
  const currentMonday = new Date(today.getFullYear(), today.getMonth(), diff);
  
  const [y, m, d] = props.startDate.split('-').map(Number);
  const weekStart = new Date(y, m - 1, d);
  
  return weekStart < currentMonday;
});

const isMissed = computed(() => {
  return isPast.value && (!props.progress || !props.progress.is_completed);
});

const isEditable = computed(() => {
  return props.isCurrent;
});

const cellClasses = computed(() => {
  const base = 'relative w-full aspect-square rounded-lg border-2 flex items-center justify-center transition-all duration-200 text-xs font-bold shadow-sm z-10 overflow-hidden';
  const interactive = 'cursor-pointer hover:shadow-md hover:scale-105 active:scale-95';
  
  let stateClasses = '';
  
  if (props.progress?.is_completed) {
    stateClasses = 'bg-green-500 border-green-600 text-white';
  } else if (isMissed.value) {
    stateClasses = 'bg-slate-900 border-slate-950 text-white';
  } else if (props.specialPeriod) {
    stateClasses = 'bg-amber-100 border-amber-300 text-amber-700';
  } else if (props.isCurrent) {
    stateClasses = 'bg-blue-50 border-blue-200 text-blue-600';
  } else {
    stateClasses = 'bg-white border-gray-100 text-gray-300';
  }

  // Current week gets a persistent highlight ring regardless of state
  let currentClasses = '';
  if (props.isCurrent) {
    currentClasses = 'ring-4 ring-blue-400/50 ring-offset-1 z-20 border-blue-500 shadow-blue-100 shadow-lg';
  }
  
  return `${base} ${stateClasses} ${currentClasses} ${interactive} group`;
});
</script>

<template>
  <div 
    :class="cellClasses"
    @click="emit('click', startDate, weekNumber)"
  >
    <!-- Tooltip -->
    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-[150px] bg-slate-900/95 backdrop-blur text-white text-[10px] rounded-lg p-2 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50 flex flex-col gap-1.5 border border-slate-700">
      <div v-if="!completions || completions.length === 0" class="text-slate-400 italic text-center">Нет участников</div>
      <div v-else v-for="user in completions" :key="user.user_id" class="flex items-center justify-between gap-3 w-full">
        <span class="text-base leading-none drop-shadow-md">{{ user.emoji }}</span>
        <span :class="['font-bold', user.is_completed ? 'text-green-400' : 'text-slate-500']">
          {{ user.is_completed ? 'Сделано' : '—' }}
        </span>
      </div>
      <!-- Triangle pointer -->
      <div class="absolute top-full left-1/2 -translate-x-1/2 border-[6px] border-transparent border-t-slate-900/95"></div>
    </div>

    <!-- Background Number -->
    <span v-if="!progress?.is_completed && !isMissed" class="absolute inset-0 flex items-center justify-center text-[10px] opacity-20 pointer-events-none">
        {{ weekNumber + 1 }}
    </span>

    <!-- Multi-user Emojis -->
    <div class="grid grid-cols-2 gap-0.5 p-0.5 w-full h-full content-center justify-items-center">
        <div 
            v-for="user in completions" 
            :key="user.user_id"
            :class="[
                'text-[10px] sm:text-xs transition-opacity leading-none',
                !user.is_completed 
                  ? 'grayscale opacity-20 brightness-75' 
                  : 'opacity-100 drop-shadow-[0_0_1.5px_rgba(255,255,255,0.7)]'
            ]"
            :title="user.is_completed ? 'Выполнено' : 'Не выполнено'"
        >
            {{ user.emoji }}
        </div>
    </div>
    
    <!-- Current Week Indicator -->
    <div v-if="isCurrent" class="absolute top-0 left-0 w-full h-1 bg-blue-500 animate-pulse"></div>
    
    <div v-if="specialPeriod" class="absolute -top-1 -right-1 z-30">
      <div class="w-3 h-3 bg-amber-500 rounded-full animate-pulse border border-white shadow-sm"></div>
    </div>
  </div>
</template>