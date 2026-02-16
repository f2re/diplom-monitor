<script setup>
import { useToast } from '../../composables/useToast';
import { X, CheckCircle, AlertTriangle, Info, AlertCircle } from 'lucide-vue-next';

const { toasts, remove } = useToast();

const getIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircle;
    case 'warning': return AlertTriangle;
    case 'error': return AlertCircle;
    default: return Info;
  }
};

const getClasses = (type) => {
  const base = 'pointer-events-auto w-full max-w-sm overflow-hidden rounded-xl shadow-lg ring-1 ring-black ring-opacity-5 transition-all transform';
  const colors = {
    success: 'bg-white border-l-4 border-green-500',
    warning: 'bg-white border-l-4 border-amber-500',
    error: 'bg-white border-l-4 border-red-500',
    info: 'bg-white border-l-4 border-blue-500',
  };
  return `${base} ${colors[type] || colors.info}`;
};
</script>

<template>
  <div aria-live="assertive" class="pointer-events-none fixed inset-0 flex items-end px-4 py-6 sm:items-start sm:p-6 z-[100]">
    <div class="flex w-full flex-col items-center space-y-4 sm:items-end">
      <TransitionGroup
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-for="toast in toasts" :key="toast.id" :class="getClasses(toast.type)">
          <div class="p-4">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <component 
                  :is="getIcon(toast.type)" 
                  class="h-6 w-6" 
                  :class="{
                    'text-green-400': toast.type === 'success',
                    'text-amber-400': toast.type === 'warning',
                    'text-red-400': toast.type === 'error',
                    'text-blue-400': toast.type === 'info'
                  }" 
                />
              </div>
              <div class="ml-3 w-0 flex-1 pt-0.5">
                <p class="text-sm font-medium text-gray-900">{{ toast.message }}</p>
              </div>
              <div class="ml-4 flex flex-shrink-0">
                <button 
                  type="button" 
                  @click="remove(toast.id)"
                  class="inline-flex rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  <span class="sr-only">Close</span>
                  <X class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>
