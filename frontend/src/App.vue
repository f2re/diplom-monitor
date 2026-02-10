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
    <!-- Navigation -->
    <nav class="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2.5 cursor-pointer" @click="showSettings = false">
          <div class="bg-blue-600 p-2 rounded-xl shadow-lg shadow-blue-200">
            <GraduationCap class="w-6 h-6 text-white" />
          </div>
          <span class="text-xl font-black tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            DiplomMonitor
          </span>
        </div>

        <div v-if="authStore.isAuthenticated" class="flex items-center gap-2 sm:gap-4">
          <div class="hidden sm:block text-right mr-2">
            <p class="text-sm font-bold text-slate-900 leading-none">{{ authStore.user?.full_name }}</p>
            <p class="text-xs font-medium text-slate-500">{{ authStore.user?.email }}</p>
          </div>
          
          <button 
            @click="toggleSettings" 
            :class="[
                'p-2.5 rounded-xl transition-all',
                showSettings ? 'bg-blue-50 text-blue-600' : 'text-slate-500 hover:text-blue-600 hover:bg-blue-50'
            ]"
            title="Settings"
          >
            <SettingsIcon class="w-5 h-5" />
          </button>

          <button 
            @click="authStore.logout()" 
            class="p-2.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
            title="Logout"
          >
            <LogOut class="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="py-12 flex-grow">
      <div v-if="!authStore.isAuthenticated" class="flex flex-col items-center justify-center min-h-[calc(100vh-12rem)] px-4">
        <AuthForm />
      </div>
      <div v-else class="max-w-7xl mx-auto px-4">
        <SettingsForm v-if="showSettings" @close="showSettings = false" />
        <WeekGrid v-else />
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-8 border-t border-slate-200 bg-white">
      <div class="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4 text-slate-500 text-sm font-medium">
        <p>© 2026 DiplomMonitor. Built for students with ❤️</p>
        <div class="flex items-center gap-6">
          <a href="#" class="hover:text-blue-600 transition-colors">Documentation</a>
          <a href="#" class="hover:text-blue-600 transition-colors">Privacy</a>
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
/* Custom animations */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-in {
  animation: fade-in 0.4s ease-out forwards;
}

@keyframes zoom-in-95 {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.zoom-in-95 {
  animation: zoom-in-95 0.2s ease-out forwards;
}
</style>
