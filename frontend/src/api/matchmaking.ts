import axiosInstance from './axios';
import type { Profile } from './profile';

export interface Swipe {
  id: string;
  swiper: string;
  swiped: string;
  direction: 'left' | 'right';
  created_at: string;
}

export interface Match {
  id: string;
  profile1: Profile;
  profile2: Profile;
  other_profile: Profile;
  matched_at: string;
  is_active: boolean;
}

export interface MatchMessage {
  id: string;
  match: string;
  sender: string;
  sender_anonymous_id: string;
  content: string;
  message_type: 'text' | 'image' | 'voice' | 'system';
  media_url: string;
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  is_own_message: boolean;
}

export interface SwipeResponse {
  swipe: Swipe;
  is_match: boolean;
  match?: Match;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const matchmakingAPI = {
  getProfiles: async (): Promise<Profile[]> => {
    const response = await axiosInstance.get('/api/matchmaking/profiles/');
    return response.data;
  },

  swipe: async (swipedId: string, direction: 'left' | 'right'): Promise<SwipeResponse> => {
    const response = await axiosInstance.post('/api/matchmaking/swipe/', {
      swiped: swipedId,
      direction,
    });
    return response.data;
  },

  getMatches: async (): Promise<Match[]> => {
    const response = await axiosInstance.get('/api/matchmaking/matches/');
    return response.data;
  },

  getMatchDetail: async (matchId: string): Promise<Match> => {
    const response = await axiosInstance.get(`/api/matchmaking/matches/${matchId}/`);
    return response.data;
  },

  getMatchMessages: async (
    matchId: string,
    page: number = 1
  ): Promise<PaginatedResponse<MatchMessage>> => {
    const response = await axiosInstance.get(
      `/api/matchmaking/matches/${matchId}/messages/`,
      {
        params: { page },
      }
    );
    return response.data;
  },

  sendMatchMessage: async (matchId: string, content: string, messageType: string = 'text', mediaUrl: string = ''): Promise<MatchMessage> => {
    const response = await axiosInstance.post(
      `/api/matchmaking/matches/${matchId}/messages/send/`,
      {
        content,
        message_type: messageType,
        media_url: mediaUrl,
      }
    );
    return response.data;
  },

  uploadMatchMedia: async (matchId: string, file: File): Promise<{ media_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axiosInstance.post(
      `/api/matchmaking/matches/${matchId}/messages/upload/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};
