<template>
  <Transition
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="transform translate-y-2 opacity-0"
    enter-to-class="transform translate-y-0 opacity-100"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="saving || showSaved" class="fixed bottom-4 right-4 flex items-center space-x-2 px-4 py-2 bg-white dark:bg-slate-800 rounded-full shadow-lg border border-slate-200 dark:border-slate-700 z-50">
      <div v-if="saving" class="flex items-center space-x-2">
        <div class="animate-spin rounded-full h-4 w-4 border-2 border-indigo-600 border-t-transparent"></div>
        <span class="text-sm font-medium text-slate-600 dark:text-slate-300">Сохранение...</span>
      </div>
      <div v-else-if="showSaved" class="flex items-center space-x-2 text-green-600">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm font-medium">Сохранено</span>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  saving: Boolean
})

const showSaved = ref(false)
let timeout = null

watch(() => props.saving, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    showSaved.ref = true
    showSaved.value = true
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => {
      showSaved.value = false
    }, 2000)
  }
})
</script>
