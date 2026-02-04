import { create } from 'zustand';
import type { Profile } from '../api/profile';
import type { Match, MatchMessage } from '../api/matchmaking';

interface TypingUser {
  profile_id: string;
  timestamp: number;
}

interface MatchmakingState {
  profiles: Profile[];
  currentProfileIndex: number;
  matches: Match[];
  currentMatch: Match | null;
  matchMessages: Record<string, MatchMessage[]>;
  typingUsers: Record<string, TypingUser[]>;
  ws: WebSocket | null;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setProfiles: (profiles: Profile[]) => void;
  nextProfile: () => void;
  removeCurrentProfile: () => void;
  setMatches: (matches: Match[]) => void;
  addMatch: (match: Match) => void;
  setCurrentMatch: (match: Match | null) => void;
  addMatchMessage: (matchId: string, message: MatchMessage) => void;
  updateMatchMessage: (matchId: string, message: MatchMessage) => void;
  setMatchMessages: (matchId: string, messages: MatchMessage[]) => void;
  prependMatchMessages: (matchId: string, messages: MatchMessage[]) => void;
  addTypingUser: (matchId: string, profileId: string) => void;
  removeTypingUser: (matchId: string, profileId: string) => void;
  setWebSocket: (ws: WebSocket | null) => void;
  setConnected: (connected: boolean) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useMatchmakingStore = create<MatchmakingState>((set) => ({
  profiles: [],
  currentProfileIndex: 0,
  matches: [],
  currentMatch: null,
  matchMessages: {},
  typingUsers: {},
  ws: null,
  isConnected: false,
  isLoading: false,
  error: null,

  setProfiles: (profiles) => set({ profiles, currentProfileIndex: 0 }),

  nextProfile: () =>
    set((state) => ({
      currentProfileIndex: Math.min(state.currentProfileIndex + 1, state.profiles.length - 1),
    })),

  removeCurrentProfile: () =>
    set((state) => ({
      profiles: state.profiles.filter((_, index) => index !== state.currentProfileIndex),
      currentProfileIndex: Math.min(state.currentProfileIndex, state.profiles.length - 2),
    })),

  setMatches: (matches) => set({ matches }),

  addMatch: (match) =>
    set((state) => ({
      matches: [match, ...state.matches],
    })),

  setCurrentMatch: (match) => set({ currentMatch: match }),

  addMatchMessage: (matchId, message) =>
    set((state) => {
      const existingMessages = state.matchMessages[matchId] || [];
      // Check if message already exists
      if (existingMessages.some((m) => m.id === message.id)) {
        return state; // Don't add duplicate
      }
      return {
        matchMessages: {
          ...state.matchMessages,
          [matchId]: [...existingMessages, message],
        },
      };
    }),

  updateMatchMessage: (matchId, message) =>
    set((state) => ({
      matchMessages: {
        ...state.matchMessages,
        [matchId]: (state.matchMessages[matchId] || []).map((m) =>
          m.id === message.id ? message : m
        ),
      },
    })),

  setMatchMessages: (matchId, messages) =>
    set((state) => ({
      matchMessages: {
        ...state.matchMessages,
        [matchId]: messages,
      },
    })),

  prependMatchMessages: (matchId, messages) =>
    set((state) => ({
      matchMessages: {
        ...state.matchMessages,
        [matchId]: [...messages, ...(state.matchMessages[matchId] || [])],
      },
    })),

  addTypingUser: (matchId, profileId) =>
    set((state) => {
      const existing = state.typingUsers[matchId] || [];
      const filtered = existing.filter((u) => u.profile_id !== profileId);
      return {
        typingUsers: {
          ...state.typingUsers,
          [matchId]: [...filtered, { profile_id: profileId, timestamp: Date.now() }],
        },
      };
    }),

  removeTypingUser: (matchId, profileId) =>
    set((state) => ({
      typingUsers: {
        ...state.typingUsers,
        [matchId]: (state.typingUsers[matchId] || []).filter((u) => u.profile_id !== profileId),
      },
    })),

  setWebSocket: (ws) => set({ ws }),

  setConnected: (connected) => set({ isConnected: connected }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  reset: () =>
    set({
      profiles: [],
      currentProfileIndex: 0,
      matches: [],
      currentMatch: null,
      matchMessages: {},
      typingUsers: {},
      ws: null,
      isConnected: false,
      isLoading: false,
      error: null,
    }),
}));
