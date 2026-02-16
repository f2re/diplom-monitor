<template>
  <div class="animate-pulse bg-slate-200 dark:bg-slate-700 rounded" :style="{ height, width }"></div>
</template>

<script setup>
defineProps({
  height: { type: String, default: '1rem' },
  width: { type: String, default: '100%' }
})
</script>
