import axiosInstance from './axios';

export interface AdminReport {
  id: string;
  reporter_anonymous_id: string;
  reported_anonymous_id: string;
  reason: 'harassment' | 'spam' | 'inappropriate' | 'other';
  description: string;
  status: 'pending' | 'reviewed' | 'resolved';
  created_at: string;
  reviewed_by_email: string | null;
  reviewed_at: string | null;
}

export interface AdminReportUpdateData {
  status: 'pending' | 'reviewed' | 'resolved';
}

export interface AdminUserDetail {
  anonymous_id: string;
  age: number;
  interests: string[];
  hobbies: string[];
  relationship_intent: string;
  personality_tags: string[];
  bio: string;
  reports_received_count: number;
  reports_made_count: number;
  messages_sent_count: number;
  matches_count: number;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface AdminBanUserData {
  reason?: string;
}

export interface AdminBroadcastData {
  content: string;
  chatroom_id?: string;
}

export interface AdminPlatformMetrics {
  active_users_today: number;
  active_users_week: number;
  total_users: number;
  total_profiles: number;
  total_messages_today: number;
  total_messages_week: number;
  total_messages: number;
  total_matches: number;
  total_reports_pending: number;
  total_reports: number;
  total_chatrooms: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const adminAPI = {
  // List reports with filtering
  listReports: async (
    status?: 'pending' | 'reviewed' | 'resolved',
    ordering?: string,
    page?: number
  ): Promise<PaginatedResponse<AdminReport>> => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (ordering) params.append('ordering', ordering);
    if (page) params.append('page', page.toString());

    const response = await axiosInstance.get(`/api/admin/reports/?${params.toString()}`);
    return response.data;
  },

  // Update report status
  updateReport: async (reportId: string, data: AdminReportUpdateData): Promise<AdminReport> => {
    const response = await axiosInstance.put(`/api/admin/reports/${reportId}/`, data);
    return response.data;
  },

  // Get user details by anonymous ID
  getUserDetail: async (anonymousId: string): Promise<AdminUserDetail> => {
    const response = await axiosInstance.get(`/api/admin/users/${anonymousId}/`);
    return response.data;
  },

  // Ban user
  banUser: async (anonymousId: string, data: AdminBanUserData): Promise<{ message: string }> => {
    const response = await axiosInstance.post(`/api/admin/users/${anonymousId}/ban/`, data);
    return response.data;
  },

  // Send broadcast message
  broadcastMessage: async (data: AdminBroadcastData): Promise<{ message: string }> => {
    const response = await axiosInstance.post('/api/admin/broadcast/', data);
    return response.data;
  },

  // Get platform metrics
  getPlatformMetrics: async (): Promise<AdminPlatformMetrics> => {
    const response = await axiosInstance.get('/api/admin/metrics/');
    return response.data;
  },
};
