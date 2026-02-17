<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { Mail, Lock, User, Loader2, ArrowRight, Github } from 'lucide-vue-next';

const authStore = useAuthStore();
const isLogin = ref(true);

const form = ref({
  email: '',
  password: '',
  full_name: ''
});

const handleSubmit = async () => {
  if (isLogin.value) {
    await authStore.login(form.value.email, form.value.password);
  } else {
    await authStore.register(form.value);
  }
};

// Telegram Login Integration
onMounted(() => {
  window.onTelegramAuth = async (user) => {
    await authStore.loginWithTelegram(user);
  };

  if (authStore.telegramBotName) {
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', authStore.telegramBotName);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-radius', '12');
    script.setAttribute('data-onauth', 'onTelegramAuth(user)');
    script.setAttribute('data-request-access', 'write');
    
    const container = document.getElementById('telegram-login-container');
    if (container) container.appendChild(script);
  }
});

onUnmounted(() => {
  delete window.onTelegramAuth;
});
</script>

<template>
  <div class="w-full max-w-md animate-in fade-in zoom-in duration-500">
    <div class="bg-white rounded-[2.5rem] p-10 shadow-2xl shadow-blue-100 border border-slate-100">
      <div class="text-center mb-10">
        <h2 class="text-4xl font-black text-slate-900 mb-3 tracking-tight">
          {{ isLogin ? 'С возвращением!' : 'Создать аккаунт' }}
        </h2>
        <p class="text-slate-500 font-medium">
          {{ isLogin ? 'Рады видеть вас снова' : 'Начните отслеживать свой прогресс сегодня' }}
        </p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-5">
        <div v-if="!isLogin" class="space-y-2">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Полное имя</label>
          <div class="relative group">
            <input 
              v-model="form.full_name" 
              type="text" 
              required
              class="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-blue-500 focus:bg-white outline-none transition-all font-medium"
              placeholder="Иван Иванов"
            />
            <User class="absolute left-4 top-4 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
          </div>
        </div>

        <div class="space-y-2">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Email адрес</label>
          <div class="relative group">
            <input 
              v-model="form.email" 
              type="email" 
              required
              class="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-blue-500 focus:bg-white outline-none transition-all font-medium"
              placeholder="name@example.com"
            />
            <Mail class="absolute left-4 top-4 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
          </div>
        </div>

        <div class="space-y-2">
          <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest ml-1">Пароль</label>
          <div class="relative group">
            <input 
              v-model="form.password" 
              type="password" 
              required
              class="w-full pl-12 pr-4 py-4 bg-slate-50 border-2 border-transparent rounded-2xl focus:border-blue-500 focus:bg-white outline-none transition-all font-medium"
              placeholder="••••••••"
            />
            <Lock class="absolute left-4 top-4 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
          </div>
        </div>

        <button 
          type="submit" 
          :disabled="authStore.loading"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-2xl shadow-lg shadow-blue-200 transition-all flex items-center justify-center gap-2 group active:scale-[0.98] disabled:opacity-70"
        >
          <Loader2 v-if="authStore.loading" class="w-5 h-5 animate-spin" />
          <template v-else>
            {{ isLogin ? 'Войти' : 'Зарегистрироваться' }}
            <ArrowRight class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </template>
        </button>
      </form>

      <div class="relative my-8">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-100"></div></div>
        <div class="relative flex justify-center text-xs uppercase"><span class="bg-white px-4 text-slate-400 font-bold tracking-widest">Или через</span></div>
      </div>

      <!-- Telegram Login -->
      <div class="flex justify-center min-h-[40px]" id="telegram-login-container"></div>

      <div v-if="authStore.error" class="mt-6 p-4 bg-red-50 border border-red-100 rounded-2xl text-red-600 text-sm font-bold text-center">
        {{ authStore.error }}
      </div>

      <p class="text-center mt-8 text-slate-500 font-medium">
        {{ isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
        <button 
          @click="isLogin = !isLogin" 
          class="text-blue-600 font-bold hover:underline ml-1"
        >
          {{ isLogin ? 'Создать' : 'Войти' }}
        </button>
      </p>
    </div>
  </div>
</template>
