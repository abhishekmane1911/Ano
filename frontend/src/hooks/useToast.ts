import { create } from 'zustand';
import type { Toast, ToastType, ToastAction } from '../components/common/Toast';

interface ToastStore {
  toasts: Toast[];
  addToast: (message: string, type: ToastType, duration?: number, action?: ToastAction) => void;
  removeToast: (id: string) => void;
  clearAll: () => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (message, type, duration, action) => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    const toast: Toast = { id, message, type, duration, action };
    set((state) => ({ toasts: [...state.toasts, toast] }));
  },
  removeToast: (id) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },
  clearAll: () => set({ toasts: [] }),
}));

export const useToast = () => {
  const { addToast } = useToastStore();

  return {
    success: (message: string, duration?: number, action?: ToastAction) => 
      addToast(message, 'success', duration, action),
    error: (message: string, duration?: number, action?: ToastAction) => 
      addToast(message, 'error', duration, action),
    warning: (message: string, duration?: number, action?: ToastAction) => 
      addToast(message, 'warning', duration, action),
    info: (message: string, duration?: number, action?: ToastAction) => 
      addToast(message, 'info', duration, action),
    reputation: (message: string, duration?: number, action?: ToastAction) => 
      addToast(message, 'reputation', duration, action),
    moderation: (message: string, duration?: number, action?: ToastAction) => 
      addToast(message, 'moderation', duration, action),
  };
};
