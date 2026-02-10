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
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1);
  const currentMonday = new Date(today.setDate(diff));
  currentMonday.setHours(0, 0, 0, 0);
  
  const weekStart = new Date(props.startDate);
  return weekStart < currentMonday;
});

const isMissed = computed(() => {
  return isPast.value && (!props.progress || !props.progress.is_completed);
});

const cellClasses = computed(() => {
  const base = 'relative w-full aspect-square rounded-lg border-2 flex items-center justify-center transition-all duration-200 cursor-pointer text-xs font-bold shadow-sm hover:shadow-md hover:scale-110 active:scale-95 z-10 overflow-hidden';
  
  if (props.progress?.is_completed) {
    return `${base} bg-green-500 border-green-600 text-white hover:bg-green-600`;
  }

  if (isMissed.value) {
    return `${base} bg-slate-900 border-slate-950 text-white hover:bg-black`;
  }
  
  if (props.specialPeriod) {
    return `${base} bg-amber-100 border-amber-300 text-amber-700 hover:bg-amber-200`;
  }
  
  if (props.isCurrent) {
    return `${base} bg-blue-50 border-blue-400 text-blue-600 ring-2 ring-blue-400 ring-offset-2`;
  }
  
  return `${base} bg-white border-gray-100 text-gray-300 hover:border-gray-300`;
});
</script>

<template>
  <div 
    :class="cellClasses"
    @click="emit('click', startDate, weekNumber)"
    :title="`Неделя ${weekNumber + 1} (${startDate})`"
  >
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
                !user.is_completed ? 'grayscale opacity-30 brightness-50' : 'opacity-100'
            ]"
            :title="user.is_completed ? 'Выполнено' : 'Не выполнено'"
        >
            {{ user.emoji }}
        </div>
    </div>
    
    <div v-if="specialPeriod" class="absolute -top-1 -right-1 z-30">
      <div class="w-3 h-3 bg-amber-500 rounded-full animate-pulse border border-white shadow-sm"></div>
    </div>
  </div>
</template>