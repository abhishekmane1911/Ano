import axiosInstance from './axios';

export interface Report {
  id: string;
  reporter_id: string;
  reason: 'harassment' | 'spam' | 'inappropriate' | 'other';
  description: string;
  status: 'pending' | 'reviewed' | 'resolved';
  created_at: string;
  reviewed_at: string | null;
}

export interface Block {
  id: string;
  blocker_id: string;
  anonymous_id: string;
  blocked_at: string;
}

export interface CreateReportData {
  reported_id: string;
  reason: 'harassment' | 'spam' | 'inappropriate' | 'other';
  description: string;
}

export interface CreateBlockData {
  blocked_id: string;
}

export const reportsAPI = {
  // Create a report
  createReport: async (data: CreateReportData): Promise<Report> => {
    const response = await axiosInstance.post('/api/reports/', data);
    return response.data;
  },

  // Block a user
  blockUser: async (data: CreateBlockData): Promise<Block> => {
    const response = await axiosInstance.post('/api/reports/block/', data);
    return response.data;
  },

  // Get blocked users list
  getBlockedUsers: async (): Promise<Block[]> => {
    console.log('API: Making request to /api/reports/blocked/');
    const response = await axiosInstance.get('/api/reports/blocked/');
    console.log('API: Response status:', response.status);
    console.log('API: Response data:', response.data);
    
    // Handle paginated response format
    if (response.data && response.data.results && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    
    // Fallback for direct array response
    return Array.isArray(response.data) ? response.data : [];
  },

  // Unblock a user
  unblockUser: async (anonymousId: string): Promise<void> => {
    await axiosInstance.delete(`/api/reports/block/${anonymousId}/`);
  },
};
