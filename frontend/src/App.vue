<script setup>
import { onMounted, ref } from 'vue';
import { useAuthStore } from './stores/auth';
import AuthForm from './components/AuthForm.vue';
import WeekGrid from './components/WeekGrid.vue';
import SettingsForm from './components/SettingsForm.vue';
import { LogOut, GraduationCap, Github, Settings as SettingsIcon } from 'lucide-vue-next';

const authStore = useAuthStore();
const showSettings = ref(false);

onMounted(async () => {
  if (authStore.token) {
    await authStore.fetchCurrentUser();
  }
});

const toggleSettings = () => {
  showSettings.value = !showSettings.value;
};
</script>

<template>
  <div class="min-h-screen bg-[#F8FAFC] text-slate-900 font-sans antialiased flex flex-col">
    <!-- Навигация -->
    <nav class="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3 cursor-pointer group" @click="showSettings = false">
          <div class="relative">
            <div class="absolute inset-0 bg-blue-400 blur-lg opacity-40 group-hover:opacity-70 transition-opacity"></div>
            <div class="relative bg-gradient-to-br from-blue-600 to-indigo-700 p-2.5 rounded-2xl shadow-xl shadow-blue-200 transform group-hover:scale-110 transition-transform duration-300">
              <GraduationCap class="w-6 h-6 text-white" />
            </div>
          </div>
          <div class="flex flex-col">
            <span class="text-xl font-black tracking-tighter bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient">
              DiplomMonitor
            </span>
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">Management System</span>
          </div>
        </div>

        <div v-if="authStore.isAuthenticated" class="flex items-center gap-2 sm:gap-4">
          <div class="hidden sm:block text-right mr-2">
            <p class="text-sm font-bold text-slate-900 leading-none">{{ authStore.user?.full_name }}</p>
            <p class="text-xs font-medium text-slate-500">{{ authStore.user?.email || 'Telegram User' }}</p>
          </div>
          
          <button 
            @click="toggleSettings" 
            :class="[
                'p-2.5 rounded-xl transition-all',
                showSettings ? 'bg-blue-50 text-blue-600' : 'text-slate-500 hover:text-blue-600 hover:bg-blue-50'
            ]"
            title="Настройки"
          >
            <SettingsIcon class="w-5 h-5" />
          </button>

          <button 
            @click="authStore.logout()" 
            class="p-2.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
            title="Выйти"
          >
            <LogOut class="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>

    <!-- Основной контент -->
    <main class="py-12 flex-grow">
      <div v-if="!authStore.isAuthenticated" class="flex flex-col items-center justify-center min-h-[calc(100vh-12rem)] px-4">
        <AuthForm />
      </div>
      <div v-else class="max-w-7xl mx-auto px-4">
        <SettingsForm v-if="showSettings" @close="showSettings = false" />
        <WeekGrid v-else />
      </div>
    </main>

    <!-- Футер -->
    <footer class="py-8 border-t border-slate-200 bg-white">
      <div class="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4 text-slate-500 text-sm font-medium">
        <p>© 2026 DiplomMonitor. Сделано для студентов с ❤️</p>
        <div class="flex items-center gap-6">
          <a href="#" class="hover:text-blue-600 transition-colors">Документация</a>
          <a href="#" class="hover:text-blue-600 transition-colors">Конфиденциальность</a>
          <a href="https://github.com" target="_blank" class="flex items-center gap-1.5 hover:text-slate-900 transition-colors">
            <Github class="w-4 h-4" />
            GitHub
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.animate-gradient {
  animation: gradient 3s ease infinite;
}
</style>
