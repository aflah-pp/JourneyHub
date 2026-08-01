import api from "./api";

export const dashboardService = {
  getDashboardData: async () => {
    const [scoreRes, journeysRes, historyRes] = await Promise.all([
      api.get("/score/me/"),
      api.get("/journey/my/"),
      api.get("/score/history/"),
    ]);

    return {
      score: scoreRes.data.data,
      journeys: journeysRes.data.data?.results || [],
      history: historyRes.data.data?.results || [],
    };
  },
};
