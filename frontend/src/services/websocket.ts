import { useChatStore, type Message } from '../stores/chatStore';
import { useAuthStore } from '../stores/authStore';
import { useReputationStore } from '../stores/reputationStore';
import { useToastStore } from '../hooks/useToast';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/ws';

export class ChatWebSocketService {
  private ws: WebSocket | null = null;
  private chatroomId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: number | null = null;
  private typingTimeout: number | null = null;

  connect(chatroomId: string): void {
    // Check if already connected or connecting to this chatroom
    if (this.ws) {
      if (this.chatroomId === chatroomId) {
        if (this.ws.readyState === WebSocket.OPEN) {
          return; // Already connected
        }
        if (this.ws.readyState === WebSocket.CONNECTING) {
          return; // Already connecting
        }
      }
      this.disconnect(); // Disconnect from previous chatroom
    }

    this.chatroomId = chatroomId;
    const accessToken = useAuthStore.getState().accessToken;
    
    if (!accessToken) {
      console.error('No access token available for WebSocket connection');
      return;
    }
    
    // Connect to WebSocket with JWT token in URL
    const wsUrl = `${WS_BASE_URL}/chat/${chatroomId}/?token=${accessToken}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onclose = this.handleClose.bind(this);

    useChatStore.getState().setWebSocket(this.ws);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.chatroomId = null;
      useChatStore.getState().setWebSocket(null);
      useChatStore.getState().setConnected(false);
    }

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
      this.typingTimeout = null;
    }
  }

  private handleOpen(): void {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    useChatStore.getState().setConnected(true);

    // Start heartbeat to keep connection alive
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Every 30 seconds
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      const { type } = data;

      switch (type) {
        case 'message.receive':
          this.handleMessageReceive(data.message);
          break;
        case 'message.edit':
          this.handleMessageEdit(data.message);
          break;
        case 'message.delete':
          this.handleMessageDelete(data.message_id);
          break;
        case 'message.react':
          this.handleMessageReact(data);
          break;
        case 'message.unreact':
          this.handleMessageUnreact(data);
          break;
        case 'typing.start':
          this.handleTypingStart(data.profile_id);
          break;
        case 'typing.stop':
          this.handleTypingStop(data.profile_id);
          break;
        case 'user.join':
          this.handleUserJoin(data.profile_id);
          break;
        case 'user.leave':
          this.handleUserLeave(data.profile_id);
          break;
        case 'read.receipt':
          this.handleReadReceipt(data);
          break;
        case 'vote_update':
          this.handleVoteUpdate(data);
          break;
        case 'reputation_update':
          this.handleReputationUpdate(data);
          break;
        case 'tier_update':
          this.handleTierUpdate(data);
          break;
        case 'error':
          useToastStore.getState().addToast(
            data.message || 'An error occurred',
            data.spam_detected ? 'moderation' : 'error'
          );
          break;
        default:
          break;
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    useChatStore.getState().setConnected(false);

    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    // Don't reconnect on certain error codes
    const noReconnectCodes = [1000, 4001, 4003, 4004]; // Normal closure, auth errors, not found
    
    // Attempt to reconnect if not a normal closure or specific error
    if (!noReconnectCodes.includes(event.code) && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => {
        if (this.chatroomId) {
          this.connect(this.chatroomId);
        }
      }, delay);
    } else if (noReconnectCodes.includes(event.code) && event.code !== 1000) {
      console.error('WebSocket connection failed:', this.getCloseReason(event.code));
    }
  }

  private getCloseReason(code: number): string {
    switch (code) {
      case 4001:
        return 'Authentication failed - please log in again';
      case 4003:
        return 'Profile not found';
      case 4004:
        return 'Chatroom not found';
      case 1006:
        return 'Connection closed abnormally - server may be offline';
      default:
        return `Connection closed with code ${code}`;
    }
  }

  // Event handlers
  private handleMessageReceive(message: Message): void {
    if (this.chatroomId) {
      useChatStore.getState().addMessage(this.chatroomId, message);
      
      // Increment unread count if not in current chatroom
      const currentChatroom = useChatStore.getState().currentChatroom;
      if (!currentChatroom || currentChatroom.id !== this.chatroomId) {
        useChatStore.getState().incrementUnreadCount(this.chatroomId);
      }
    }
  }

  private handleMessageEdit(message: Message): void {
    if (this.chatroomId) {
      useChatStore.getState().updateMessage(this.chatroomId, message);
    }
  }

  private handleMessageDelete(messageId: string): void {
    if (this.chatroomId) {
      useChatStore.getState().deleteMessage(this.chatroomId, messageId);
    }
  }

  private handleMessageReact(data: {
    message_id: string;
    emoji: string;
    profile_id: string;
    reaction_id: string;
  }): void {
    if (this.chatroomId) {
      useChatStore.getState().addReaction(
        this.chatroomId,
        data.message_id,
        data.emoji,
        data.profile_id,
        data.reaction_id
      );
    }
  }

  private handleMessageUnreact(data: {
    message_id: string;
    emoji: string;
    profile_id: string;
  }): void {
    if (this.chatroomId) {
      useChatStore.getState().removeReaction(
        this.chatroomId,
        data.message_id,
        data.emoji,
        data.profile_id
      );
    }
  }

  private handleTypingStart(profileId: string): void {
    if (this.chatroomId) {
      useChatStore.getState().addTypingUser(this.chatroomId, profileId);
    }
  }

  private handleTypingStop(profileId: string): void {
    if (this.chatroomId) {
      useChatStore.getState().removeTypingUser(this.chatroomId, profileId);
    }
  }

  private handleUserJoin(profileId: string): void {
    if (this.chatroomId) {
      useChatStore.getState().addOnlineUser(this.chatroomId, profileId);
    }
  }

  private handleUserLeave(profileId: string): void {
    if (this.chatroomId) {
      useChatStore.getState().removeOnlineUser(this.chatroomId, profileId);
    }
  }

  private handleReadReceipt(_data: { message_id: string; profile_id: string }): void {
    // Read receipts are informational only; no store update needed currently
  }

  private handleVoteUpdate(data: {
    message_id: string;
    chatroom_id: string;
    upvotes: number;
    downvotes: number;
    user_vote: 'upvote' | 'downvote' | null;
  }): void {
    const chatroomId = data.chatroom_id || this.chatroomId;
    if (chatroomId) {
      useChatStore.getState().updateVote(
        chatroomId,
        data.message_id,
        data.upvotes,
        data.downvotes,
        data.user_vote
      );
    }
  }

  private handleReputationUpdate(data: {
    reputation_score?: number;
    level?: number;
    rank_tier?: string;
    total_upvotes_received?: number;
    total_downvotes_received?: number;
  }): void {
    useReputationStore.getState().applyReputationUpdate(data as any);
  }

  private handleTierUpdate(data: { new_tier: string; new_level: number }): void {
    const tier = data.new_tier as any;
    useReputationStore.getState().applyTierUpdate(tier, data.new_level);
    useToastStore.getState().addToast(
      `🎉 Rank up! You're now ${data.new_tier}`,
      'reputation',
      5000
    );
  }

  // Send methods
  sendMessage(content: string, messageType: string = 'text', mediaUrl: string = ''): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'message.send',
          content,
          message_type: messageType,
          media_url: mediaUrl,
        })
      );
    }
  }

  editMessage(messageId: string, content: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'message.edit',
          message_id: messageId,
          content,
        })
      );
    }
  }

  deleteMessage(messageId: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'message.delete',
          message_id: messageId,
        })
      );
    }
  }

  reactToMessage(messageId: string, emoji: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'message.react',
          message_id: messageId,
          emoji,
        })
      );
    }
  }

  startTyping(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'typing.start' }));

      // Auto-stop typing after 3 seconds
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout);
      }
      this.typingTimeout = setTimeout(() => {
        this.stopTyping();
      }, 3000);
    }
  }

  stopTyping(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'typing.stop' }));
    }
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
      this.typingTimeout = null;
    }
  }

  sendReadReceipt(messageId: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'read.receipt',
          message_id: messageId,
        })
      );
    }
  }
}

// Singleton instance
export const chatWebSocket = new ChatWebSocketService();
