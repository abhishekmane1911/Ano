import { create } from 'zustand';

export interface Message {
  id: string;
  chatroom_id: string | null;
  sender_id: string;
  sender_tier?: string;
  content: string;
  message_type: 'text' | 'image' | 'voice' | 'system';
  media_url: string;
  is_edited: boolean;
  is_deleted: boolean;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
  reactions?: MessageReaction[];
  reaction_count?: Record<string, number>;
  upvotes?: number;
  downvotes?: number;
  wilson_score?: number;
  user_vote?: 'upvote' | 'downvote' | null;
  ranking?: {
    upvotes: number;
    downvotes: number;
    wilson_score: number;
    user_vote: 'upvote' | 'downvote' | null;
  };
}

export interface MessageReaction {
  id: string;
  emoji: string;
  profile_id: string;
  created_at: string;
}

export interface Chatroom {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  member_count: number;
  unread_count?: number;
}

interface TypingUser {
  profile_id: string;
  timestamp: number;
}

interface ChatState {
  chatrooms: Chatroom[];
  currentChatroom: Chatroom | null;
  messages: Record<string, Message[]>;
  typingUsers: Record<string, TypingUser[]>;
  onlineUsers: Record<string, string[]>;
  ws: WebSocket | null;
  isConnected: boolean;
  blockedUsers: string[];

  setChatrooms: (chatrooms: Chatroom[]) => void;
  setCurrentChatroom: (chatroom: Chatroom | null) => void;
  addMessage: (chatroomId: string, message: Message) => void;
  updateMessage: (chatroomId: string, message: Message) => void;
  deleteMessage: (chatroomId: string, messageId: string) => void;
  setMessages: (chatroomId: string, messages: Message[]) => void;
  prependMessages: (chatroomId: string, messages: Message[]) => void;
  addReaction: (chatroomId: string, messageId: string, emoji: string, profileId: string, reactionId: string) => void;
  removeReaction: (chatroomId: string, messageId: string, emoji: string, profileId: string) => void;
  updateVote: (chatroomId: string, messageId: string, upvotes: number, downvotes: number, userVote: 'upvote' | 'downvote' | null) => void;
  addTypingUser: (chatroomId: string, profileId: string) => void;
  removeTypingUser: (chatroomId: string, profileId: string) => void;
  addOnlineUser: (chatroomId: string, profileId: string) => void;
  removeOnlineUser: (chatroomId: string, profileId: string) => void;
  setWebSocket: (ws: WebSocket | null) => void;
  setConnected: (connected: boolean) => void;
  incrementUnreadCount: (chatroomId: string) => void;
  resetUnreadCount: (chatroomId: string) => void;
  setBlockedUsers: (userIds: string[]) => void;
  addBlockedUser: (userId: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  chatrooms: [],
  currentChatroom: null,
  messages: {},
  typingUsers: {},
  onlineUsers: {},
  ws: null,
  isConnected: false,
  blockedUsers: [],

  setChatrooms: (chatrooms) => set({ chatrooms }),

  setCurrentChatroom: (chatroom) => set({ currentChatroom: chatroom }),

  addMessage: (chatroomId, message) =>
    set((state) => {
      // Ignore messages from blocked users
      if (state.blockedUsers.includes(message.sender_id)) {
        return state;
      }
      const existingMessages = state.messages[chatroomId] || [];
      // Prevent duplicates by checking if message ID already exists
      const isDuplicate = existingMessages.some((m) => m.id === message.id);
      if (isDuplicate) {
        return state;
      }
      return {
        messages: {
          ...state.messages,
          [chatroomId]: [...existingMessages, message],
        },
      };
    }),

  updateMessage: (chatroomId, message) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [chatroomId]: (state.messages[chatroomId] || []).map((m) =>
          m.id === message.id ? message : m
        ),
      },
    })),

  deleteMessage: (chatroomId, messageId) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [chatroomId]: (state.messages[chatroomId] || []).map((m) =>
          m.id === messageId ? { ...m, is_deleted: true, content: '[Message deleted]' } : m
        ),
      },
    })),

  setMessages: (chatroomId, messages) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [chatroomId]: messages.filter(m => !state.blockedUsers.includes(m.sender_id)),
      },
    })),

  prependMessages: (chatroomId, newMessages) =>
    set((state) => {
      const existingMessages = state.messages[chatroomId] || [];

      // Filter out messages from blocked users
      const allowedNewMessages = newMessages.filter(m => !state.blockedUsers.includes(m.sender_id));

      // Filter out duplicates
      const uniqueNewMessages = allowedNewMessages.filter(
        (newMsg) => !existingMessages.some((existingMsg) => existingMsg.id === newMsg.id)
      );

      return {
        messages: {
          ...state.messages,
          [chatroomId]: [...uniqueNewMessages, ...existingMessages],
        },
      };
    }),

  addReaction: (chatroomId, messageId, emoji, profileId, reactionId) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [chatroomId]: (state.messages[chatroomId] || []).map((m) => {
          if (m.id === messageId) {
            const reactions = m.reactions || [];
            const newReaction = { id: reactionId, emoji, profile_id: profileId, created_at: new Date().toISOString() };
            return {
              ...m,
              reactions: [...reactions, newReaction],
              reaction_count: {
                ...m.reaction_count,
                [emoji]: (m.reaction_count?.[emoji] || 0) + 1,
              },
            };
          }
          return m;
        }),
      },
    })),

  updateVote: (chatroomId, messageId, upvotes, downvotes, userVote) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [chatroomId]: (state.messages[chatroomId] || []).map((m) =>
          m.id === messageId
            ? {
              ...m,
              upvotes,
              downvotes,
              user_vote: userVote,
              ranking: m.ranking ? {
                ...m.ranking,
                upvotes,
                downvotes,
                user_vote: userVote
              } : undefined
            }
            : m
        ),
      },
    })),

  removeReaction: (chatroomId, messageId, emoji, profileId) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [chatroomId]: (state.messages[chatroomId] || []).map((m) => {
          if (m.id === messageId) {
            const reactions = (m.reactions || []).filter(
              (r) => !(r.emoji === emoji && r.profile_id === profileId)
            );
            const newCount = Math.max(0, (m.reaction_count?.[emoji] || 0) - 1);
            const reactionCount = { ...m.reaction_count };

            if (newCount === 0) {
              delete reactionCount[emoji];
            } else {
              reactionCount[emoji] = newCount;
            }

            return {
              ...m,
              reactions,
              reaction_count: reactionCount,
            };
          }
          return m;
        }),
      },
    })),

  addTypingUser: (chatroomId, profileId) =>
    set((state) => {
      const existing = state.typingUsers[chatroomId] || [];
      const filtered = existing.filter((u) => u.profile_id !== profileId);
      return {
        typingUsers: {
          ...state.typingUsers,
          [chatroomId]: [...filtered, { profile_id: profileId, timestamp: Date.now() }],
        },
      };
    }),

  removeTypingUser: (chatroomId, profileId) =>
    set((state) => ({
      typingUsers: {
        ...state.typingUsers,
        [chatroomId]: (state.typingUsers[chatroomId] || []).filter(
          (u) => u.profile_id !== profileId
        ),
      },
    })),

  addOnlineUser: (chatroomId, profileId) =>
    set((state) => {
      const existing = state.onlineUsers[chatroomId] || [];
      if (!existing.includes(profileId)) {
        return {
          onlineUsers: {
            ...state.onlineUsers,
            [chatroomId]: [...existing, profileId],
          },
        };
      }
      return state;
    }),

  removeOnlineUser: (chatroomId, profileId) =>
    set((state) => ({
      onlineUsers: {
        ...state.onlineUsers,
        [chatroomId]: (state.onlineUsers[chatroomId] || []).filter(
          (id) => id !== profileId
        ),
      },
    })),

  setWebSocket: (ws) => set({ ws }),

  setConnected: (connected) => set({ isConnected: connected }),

  incrementUnreadCount: (chatroomId) =>
    set((state) => ({
      chatrooms: state.chatrooms.map((room) =>
        room.id === chatroomId
          ? { ...room, unread_count: (room.unread_count || 0) + 1 }
          : room
      ),
    })),

  resetUnreadCount: (chatroomId) =>
    set((state) => ({
      chatrooms: state.chatrooms.map(c =>
        c.id === chatroomId ? { ...c, unread_count: 0 } : c
      )
    })),

  setBlockedUsers: (userIds) => set({ blockedUsers: userIds }),

  addBlockedUser: (userId) =>
    set((state) => ({
      blockedUsers: [...state.blockedUsers, userId],
      // Remove any existing messages from this newly blocked user
      messages: Object.fromEntries(
        Object.entries(state.messages).map(([roomId, msgs]) => [
          roomId,
          msgs.filter(m => m.sender_id !== userId)
        ])
      )
    })),
}));
