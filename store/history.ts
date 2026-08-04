import { defineStore } from "pinia";
import { getHistoryGamesApi, mockGames, type GameItem } from "@@/apis/history";

export const HistoryStore = defineStore("history", {
  state: () => ({
    games: mockGames as GameItem[],
    loading: false,
    error: null as any,
  }),
  actions: {
    async fetchGames() {
      this.loading = true;
      const { data, error } = await getHistoryGamesApi();
      if (data) {
        this.games = data;
      }
      this.error = error;
      this.loading = false;
    },
  },
});
