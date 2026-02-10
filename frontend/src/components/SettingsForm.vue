<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { Save, Calendar, User, Smile, Loader2 } from 'lucide-vue-next';

const authStore = useAuthStore();
const emit = defineEmits(['close']);

const form = ref({
  full_name: authStore.user?.full_name || '',
  start_date: authStore.user?.start_date || '',
  deadline: authStore.user?.deadline || '',
  emoji: authStore.user?.emoji || '🎓'
});

const emojis = ['🎓', '📚', '💻', '🧪', '🎨', '🧬', '⚖️', '🏗️'];

const handleSubmit = async () => {
  const success = await authStore.updateProfile(form.value);
  if (success) {
    emit('close');
  }
};
</script>

<template>
  <div class="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 max-w-2xl mx-auto animate-in">
    <div class="flex items-center gap-4 mb-8">
      <div class="bg-blue-100 p-3 rounded-2xl">
        <User class="w-6 h-6 text-blue-600" />
      </div>
      <div>
        <h2 class="text-2xl font-black text-gray-900">Profile Settings</h2>
        <p class="text-gray-500 font-medium">Customize your diploma journey</p>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div class="space-y-2">
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Full Name</label>
        <div class="relative">
          <input 
            v-model="form.full_name" 
            type="text" 
            placeholder="John Doe"
            class="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
          />
          <User class="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-2">
          <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Start Date</label>
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
          <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Deadline</label>
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
        <label class="block text-sm font-bold text-gray-700 uppercase tracking-wider">Your Spirit Emoji</label>
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

      <div v-if="authStore.error" class="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm font-bold text-center">
        {{ authStore.error }}
      </div>

      <div class="flex gap-4 pt-4">
        <button 
          type="button"
          @click="emit('close')"
          class="flex-1 px-6 py-4 border border-gray-200 bg-white text-gray-600 font-black rounded-2xl hover:bg-gray-50 transition-all active:scale-95"
        >
          Cancel
        </button>
        <button 
          type="submit"
          :disabled="authStore.loading"
          class="flex-1 px-6 py-4 bg-blue-600 text-white font-black rounded-2xl hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 active:scale-95 disabled:opacity-50"
        >
          <Loader2 v-if="authStore.loading" class="w-5 h-5 animate-spin" />
          <Save v-else class="w-5 h-5" />
          Save Settings
        </button>
      </div>
    </form>
  </div>
</template>
