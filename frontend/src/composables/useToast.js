import { ref } from 'vue';

const toasts = ref([]);

export function useToast() {
  /**
   * Add a new toast notification.
   * @param {string} message - The message to display.
   * @param {'info' | 'success' | 'warning' | 'error'} type - The type of notification.
   * @param {number} duration - Duration in ms before auto-dismissing.
   */
  const add = (message, type = 'info', duration = 3000) => {
    const id = Date.now();
    toasts.value.push({ id, message, type });
    
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }
  };

  const remove = (id) => {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  };

  return {
    toasts,
    add,
    remove
  };
}
