import axiosInstance from './axios';

export interface MyReputationResponse {
  user_id: number;
  username: string;
  reputation_score: number;
  rank_tier: 'Fresher' | 'Sophomore' | 'Senior' | 'Campus Legend';
  level: number;
  xp_for_next_level: number;
  total_upvotes_received: number;
  total_downvotes_received: number;
  privileges: string[];
  last_tier_update: string | null;
}

export interface VoteResult {
  success: boolean;
  vote_type: 'upvote' | 'downvote' | null;
  error?: string;
  ranking_data?: {
    upvotes: number;
    downvotes: number;
    total_votes: number;
    wilson_score: number;
    upvote_percentage: number;
  };
  reputation_update?: Record<string, unknown>;
}

export const reputationApi = {
  getMyReputation: async (): Promise<MyReputationResponse> => {
    const response = await axiosInstance.get('/api/reputation/api/user/me/');
    return response.data;
  },

  vote: async (messageId: string, voteType: 'upvote' | 'downvote'): Promise<VoteResult> => {
    const response = await axiosInstance.post('/api/reputation/api/vote/', {
      message_id: messageId,
      vote_type: voteType,
    });
    return response.data;
  },

  removeVote: async (messageId: string): Promise<VoteResult> => {
    const response = await axiosInstance.delete(`/api/reputation/api/vote/${messageId}/`);
    return response.data;
  },
};
