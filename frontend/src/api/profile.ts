import axiosInstance from './axios';

export interface Profile {
  anonymous_id: string;
  bio: string;
  avatar: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdateData {
  bio?: string;
}

export const profileAPI = {
  getMyProfile: async (): Promise<Profile> => {
    const response = await axiosInstance.get('/api/profiles/me/');
    return response.data;
  },

  updateMyProfile: async (data: ProfileUpdateData): Promise<Profile> => {
    const response = await axiosInstance.put('/api/profiles/me/', data);
    return response.data;
  },

  getProfileByAnonymousId: async (anonymousId: string): Promise<Profile> => {
    const response = await axiosInstance.get(`/api/profiles/${anonymousId}/`);
    return response.data;
  },

  uploadAvatar: async (file: File): Promise<Profile> => {
    const formData = new FormData();
    formData.append('avatar', file);
    const response = await axiosInstance.post('/api/profiles/avatar/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
