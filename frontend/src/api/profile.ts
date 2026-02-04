import axiosInstance from './axios';

export interface Profile {
  anonymous_id: string;
  age: number;
  interests: string[];
  hobbies: string[];
  relationship_intent: 'friendship' | 'dating' | 'casual';
  personality_tags: string[];
  bio: string;
  avatar: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileCreateData {
  age: number;
  interests: string[];
  hobbies: string[];
  relationship_intent: 'friendship' | 'dating' | 'casual';
  personality_tags: string[];
  bio?: string;
}

export interface ProfileUpdateData {
  age?: number;
  interests?: string[];
  hobbies?: string[];
  relationship_intent?: 'friendship' | 'dating' | 'casual';
  personality_tags?: string[];
  bio?: string;
}

export const profileAPI = {
  createProfile: async (data: ProfileCreateData): Promise<Profile> => {
    const response = await axiosInstance.post('/api/profiles/', data);
    return response.data;
  },

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
