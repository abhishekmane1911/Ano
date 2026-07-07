import { create } from 'zustand';
import type { MyReputationResponse } from '../api/reputation';

export type RankTier = 'Fresher' | 'Sophomore' | 'Senior' | 'Campus Legend';

interface RankUpEvent {
  newTier: RankTier;
  newLevel: number;
}

interface ReputationState {
  myReputation: MyReputationResponse | null;
  rankUpEvent: RankUpEvent | null;
  setMyReputation: (data: MyReputationResponse) => void;
  applyReputationUpdate: (data: Partial<MyReputationResponse>) => void;
  applyTierUpdate: (newTier: RankTier, newLevel: number) => void;
  clearRankUpEvent: () => void;
}

export const useReputationStore = create<ReputationState>((set, get) => ({
  myReputation: null,
  rankUpEvent: null,

  setMyReputation: (data) => set({ myReputation: data }),

  applyReputationUpdate: (data) => {
    const current = get().myReputation;
    if (!current) return;
    set({ myReputation: { ...current, ...data } });
  },

  applyTierUpdate: (newTier, newLevel) => {
    const current = get().myReputation;
    if (current && current.rank_tier !== newTier) {
      set({ rankUpEvent: { newTier, newLevel } });
    }
    if (current) {
      set({ myReputation: { ...current, rank_tier: newTier, level: newLevel } });
    }
  },

  clearRankUpEvent: () => set({ rankUpEvent: null }),
}));
