<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { LogIn, UserPlus, Loader2, AlertCircle } from 'lucide-vue-next';

const authStore = useAuthStore();
const isLogin = ref(true);

const form = reactive({
  email: '',
  password: '',
  full_name: '',
  start_date: '',
  deadline: ''
});

const handleSubmit = async () => {
  if (isLogin.value) {
    await authStore.login(form.email, form.password);
  } else {
    await authStore.register(form);
  }
};

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  authStore.error = null;
};

const handleTelegramAuth = async (user) => {
  await authStore.loginWithTelegram(user);
};

onMounted(() => {
  window.onTelegramAuth = handleTelegramAuth;
  
  const script = document.createElement('script');
  script.src = 'https://telegram.org/js/telegram-widget.js?22';
  script.setAttribute('data-telegram-login', 'weeks_until_diploma_bot');
  script.setAttribute('data-size', 'large');
  script.setAttribute('data-radius', '12');
  script.setAttribute('data-onauth', 'onTelegramAuth(user)');
  script.setAttribute('data-request-access', 'write');
  script.async = true;
  
  const container = document.getElementById('telegram-login-container');
  if (container) {
    container.appendChild(script);
  }
});

onUnmounted(() => {
  delete window.onTelegramAuth;
});
</script>

<template>
  <div class="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl transition-all duration-300 hover:shadow-2xl border border-gray-100">
    <div class="text-center mb-8">
      <h2 class="text-3xl font-extrabold text-gray-900 tracking-tight">
        {{ isLogin ? 'Welcome Back' : 'Get Started' }}
      </h2>
      <p class="mt-2 text-gray-500">
        {{ isLogin ? 'Enter your credentials to access your tracker' : 'Create an account to start tracking your progress' }}
      </p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-5">
      <div v-if="authStore.error" class="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 flex items-center gap-3 animate-in fade-in slide-in-from-top-4 duration-300">
        <AlertCircle class="w-5 h-5 flex-shrink-0" />
        <p class="text-sm font-medium">{{ authStore.error }}</p>
      </div>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1.5">Email Address</label>
          <input 
            v-model="form.email" 
            type="email" 
            required 
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
            placeholder="name@example.com"
          />
        </div>

        <div v-if="!isLogin">
          <label class="block text-sm font-semibold text-gray-700 mb-1.5">Full Name</label>
          <input 
            v-model="form.full_name" 
            type="text" 
            required 
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
            placeholder="John Doe"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
          <input 
            v-model="form.password" 
            type="password" 
            required 
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
            placeholder="••••••••"
          />
        </div>

        <template v-if="!isLogin">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Start Date</label>
              <input 
                v-model="form.start_date" 
                type="date" 
                required 
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">Deadline</label>
              <input 
                v-model="form.deadline" 
                type="date" 
                required 
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
              />
            </div>
          </div>
        </template>
      </div>

      <button 
        type="submit" 
        :disabled="authStore.loading"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl transition-all active:scale-[0.98] disabled:opacity-70 disabled:active:scale-100 flex items-center justify-center gap-2 shadow-lg shadow-blue-200"
      >
        <Loader2 v-if="authStore.loading" class="w-5 h-5 animate-spin" />
        <template v-else>
          <component :is="isLogin ? LogIn : UserPlus" class="w-5 h-5" />
          {{ isLogin ? 'Sign In' : 'Create Account' }}
        </template>
      </button>

      <div class="relative py-4">
        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-200"></div></div>
        <div class="relative flex justify-center text-sm uppercase"><span class="bg-white px-2 text-gray-400">Or continue with</span></div>
      </div>

      <div id="telegram-login-container" class="flex justify-center min-h-[40px] transition-all duration-300"></div>

      <div class="pt-4 mt-4 border-t border-gray-50">
        <button 
          type="button" 
          @click="toggleMode"
          class="w-full bg-white hover:bg-gray-50 text-gray-600 font-semibold py-3 rounded-xl border border-gray-200 transition-all"
        >
          {{ isLogin ? 'Need an account? Register' : 'Already have an account? Login' }}
        </button>
      </div>
    </form>
  </div>
</template>