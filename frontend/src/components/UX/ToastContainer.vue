<script setup>
import { useToast } from '../../composables/useToast';
import { X, CheckCircle2, AlertTriangle, Info, XCircle } from 'lucide-vue-next';

const { toasts, remove } = useToast();

const getIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircle2;
    case 'warning': return AlertTriangle;
    case 'error': return XCircle;
    default: return Info;
  }
};

const getClasses = (type) => {
  const base = "flex items-start gap-3 p-4 rounded-xl shadow-lg border backdrop-blur-md transition-all duration-300 transform translate-y-0 opacity-100 max-w-sm w-full pointer-events-auto";
  switch (type) {
    case 'success': return `${base} bg-green-50/90 border-green-200 text-green-800`;
    case 'warning': return `${base} bg-amber-50/90 border-amber-200 text-amber-800`;
    case 'error': return `${base} bg-red-50/90 border-red-200 text-red-800`;
    default: return `${base} bg-blue-50/90 border-blue-200 text-blue-800`;
  }
};
</script>

<template>
  <div class="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup 
      enter-active-class="transition ease-out duration-300"
      enter-from-class="transform translate-y-2 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        :class="getClasses(toast.type)"
      >
        <component :is="getIcon(toast.type)" class="w-5 h-5 mt-0.5 shrink-0" />
        <div class="flex-1 text-sm font-medium leading-tight pt-0.5">{{ toast.message }}</div>
        <button @click="remove(toast.id)" class="text-current opacity-60 hover:opacity-100 transition-opacity">
          <X class="w-4 h-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
