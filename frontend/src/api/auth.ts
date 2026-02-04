import axiosInstance from './axios';

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
}

export interface LoginData {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface VerifyEmailData {
  token: string;
}

export interface PasswordResetRequestData {
  email: string;
}

export interface PasswordResetConfirmData {
  token: string;
  password: string;
  password_confirm: string;
}

export const authAPI = {
  register: async (data: RegisterData) => {
    const response = await axiosInstance.post('/api/auth/register/', data);
    return response.data;
  },

  verifyEmail: async (data: VerifyEmailData) => {
    const response = await axiosInstance.post('/api/auth/verify-email/', data);
    return response.data;
  },

  login: async (data: LoginData) => {
    const response = await axiosInstance.post('/api/auth/login/', data);
    return response.data;
  },

  logout: async () => {
    const response = await axiosInstance.post('/api/auth/logout/');
    return response.data;
  },

  refreshToken: async () => {
    const response = await axiosInstance.post('/api/auth/refresh/');
    return response.data;
  },

  requestPasswordReset: async (data: PasswordResetRequestData) => {
    const response = await axiosInstance.post('/api/auth/password-reset/', data);
    return response.data;
  },

  confirmPasswordReset: async (data: PasswordResetConfirmData) => {
    const response = await axiosInstance.post('/api/auth/password-reset-confirm/', data);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await axiosInstance.get('/api/auth/me/');
    return response.data;
  },
};
