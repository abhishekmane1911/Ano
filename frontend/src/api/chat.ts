import axiosInstance from './axios';
import type { Chatroom, Message } from '../stores/chatStore';

const API_BASE = '/api/chat';

export const chatApi = {
  // Chatroom operations
  getChatrooms: async (): Promise<Chatroom[]> => {
    const response = await axiosInstance.get(`${API_BASE}/chatrooms/`);
    return response.data;
  },

  getChatroom: async (chatroomId: string): Promise<Chatroom> => {
    const response = await axiosInstance.get(`${API_BASE}/chatrooms/${chatroomId}/`);
    return response.data;
  },

  getChatroomMessages: async (
    chatroomId: string,
    page: number = 1,
    pageSize: number = 50,
    ordering: string = 'created_at'
  ): Promise<{ results: Message[]; count: number; next: string | null; previous: string | null }> => {
    const response = await axiosInstance.get(
      `${API_BASE}/chatrooms/${chatroomId}/messages/`,
      {
        params: { page, page_size: pageSize, ordering },
      }
    );
    return response.data;
  },

  sendMessage: async (
    chatroomId: string,
    content: string,
    messageType: string = 'text',
    mediaUrl: string = ''
  ): Promise<Message> => {
    const response = await axiosInstance.post(
      `${API_BASE}/chatrooms/${chatroomId}/send_message/`,
      {
        content,
        message_type: messageType,
        media_url: mediaUrl,
      }
    );
    return response.data;
  },

  // Message operations
  editMessage: async (messageId: string, content: string): Promise<Message> => {
    const response = await axiosInstance.put(`${API_BASE}/messages/${messageId}/`, {
      content,
    });
    return response.data;
  },

  deleteMessage: async (messageId: string): Promise<void> => {
    await axiosInstance.delete(`${API_BASE}/messages/${messageId}/`);
  },

  reactToMessage: async (messageId: string, emoji: string): Promise<void> => {
    await axiosInstance.post(`${API_BASE}/messages/${messageId}/react/`, {
      emoji,
    });
  },

  pinMessage: async (messageId: string, duration_hours?: number): Promise<Message> => {
    const response = await axiosInstance.post(`${API_BASE}/messages/${messageId}/pin/`, {
      duration_hours,
    });
    return response.data;
  },

  uploadMedia: async (chatroomId: string, file: File): Promise<{ media_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axiosInstance.post(
      `${API_BASE}/chatrooms/${chatroomId}/upload_media/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  // Search operations
  searchMessages: async (query: string): Promise<{
    query: string;
    count: number;
    results: Array<{
      id: string;
      chatroom: string | null;
      chatroom_name: string | null;
      match_id: string | null;
      sender_id: string;
      content: string;
      highlighted_content: string;
      message_type: string;
      is_pinned: boolean;
      created_at: string;
    }>;
  }> => {
    const response = await axiosInstance.get(`${API_BASE}/search/`, {
      params: { q: query },
    });
    return response.data;
  },
};
