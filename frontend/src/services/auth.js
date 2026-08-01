import { useAuthStore } from "@/store/authStore";
import api from "./api";

export const authService = {
  register: async (data) => {
    const response = await api.post("/accounts/register/", data);
    return response.data;
  },

  verifyEmail: async (token) => {
    const response = await api.post("/accounts/verify-email/", { token });
    return response.data;
  },

  login: async (login, password) => {
    const response = await api.post("/accounts/login/", { login, password });
    const { access, user } = response.data.data;
    useAuthStore.getState().login(user, access);
    return { user, access };
  },

  logout: async () => {
    await api.post("/accounts/logout/");
    useAuthStore.getState().logout();
  },

  refresh: async () => {
    const response = await api.post("/accounts/refresh/");
    const { access } = response.data;
    useAuthStore.getState().setAccessToken(access);
    return access;
  },

  forgotPassword: async (email) => {
    const response = await api.post("/accounts/password/forgot/", { email });
    return response.data;
  },

  resetPassword: async (uidb64, token, password, confirmPassword) => {
    const response = await api.post(`/accounts/password/reset/${uidb64}/${token}/`, {
      password,
      confirm_password: confirmPassword,
    });
    return response.data;
  },

  changePassword: async (oldPassword, newPassword, confirmPassword) => {
    const response = await api.post("/accounts/password/change/", {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    });
    return response.data;
  },

  resendVerification: async (email) => {
    const response = await api.post("/auth/resend-verification/", { email });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get("/accounts/me/");
    return response.data;
  },

  updateProfile: async (data) => {
    const response = await api.patch("/accounts/me/", data);
    return response.data;
  },

  getPublicProfile: async (username) => {
    const response = await api.get(`/accounts/users/${username}/`);
    return response.data;
  },

  searchUsers: async (query) => {
    const response = await api.get(`/accounts/users/search/?q=${encodeURIComponent(query)}`);
    return response.data;
  },

  follow: async (userId) => {
    const response = await api.post(`/accounts/users/${userId}/follow/`);
    return response.data;
  },

  unfollow: async (userId) => {
    const response = await api.delete(`/accounts/users/${userId}/unfollow/`);
    return response.data;
  },

  getPreferences: async () => {
    const response = await api.get("/accounts/preferences/");
    return response.data;
  },

  updatePreferences: async (data) => {
    const response = await api.patch("/accounts/preferences/", data);
    return response.data;
  },

  getUploadSignature: async (folder) => {
    const response = await api.post("/accounts/cloudinary-signature/", { folder });
    return response.data;
  },

  getJourneys: async () => {
    const response = await api.get("/journey/my/");
    return response.data;
  },

  getScore: async () => {
    const response = await api.get("/score/me/");
    return response.data;
  },
  getUserJourneys: async (username, params = {}) => {
    const response = await api.get(`journey/${username}/journeys/`, { params });
    return response.data;
  },

  clearUserData: async (confirm) => {
    const response = await api.post("/accounts/me/clear-data/", { confirm });
    return response.data;
  },

  deleteAccount: async (confirm) => {
    const response = await api.delete("/accounts/me/delete/", { data: { confirm } });
    return response.data;
  },
};

export const journeyService = {
  searchJourneys: async (query, params = {}) => {
    const response = await api.get(`/journey/search/`, {
      params: { search: query, ...params },
    });
    return response.data;
  },

  getJourneys: async (params = {}) => {
    const response = await api.get("/journey/", { params });
    return response.data;
  },

  getJourneyDetail: async (id) => {
    const response = await api.get(`/journey/${id}/`);
    return response.data;
  },

  createJourney: async (data) => {
    const response = await api.post("/journey/create/", data);
    return response.data;
  },

  updateJourney: async (id, data) => {
    const response = await api.patch(`/journey/${id}/update/`, data);
    return response.data;
  },

  deleteJourney: async (id) => {
    const response = await api.delete(`/journey/${id}/delete/`);
    return response.data;
  },

  getJourneyUpdates: async (id, params = {}) => {
    const response = await api.get(`/journey/${id}/updates/`, { params });
    return response.data;
  },
  getUpdateDetail: async (journeyId, updateId) => {
    const response = await api.get(`/journey/${journeyId}/updates/${updateId}/`);
    return response.data;
  },

  createUpdate: async (journeyId, data) => {
    const response = await api.post(`/journey/${journeyId}/updates/create/`, data);
    return response.data;
  },

  updateUpdate: async (journeyId, updateId, data) => {
    const response = await api.patch(`/journey/${journeyId}/updates/${updateId}/update/`, data);
    return response.data;
  },

  deleteUpdate: async (journeyId, updateId) => {
    const response = await api.delete(`/journey/${journeyId}/updates/${updateId}/delete/`);
    return response.data;
  },

  updateUpdateTags: async (journeyId, updateId, tagNames) => {
    const response = await api.patch(`/journey/${journeyId}/updates/${updateId}/tags/`, {
      tags: tagNames,
    });
    return response.data;
  },

  addUpdateImage: async (updateId, imageFile, orderIndex = 0) => {
    const formData = new FormData();
    formData.append("image", imageFile);
    formData.append("order_index", orderIndex);
    const response = await api.post(`journey/updates/${updateId}/images/create/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  deleteUpdateImage: async (updateId, imageId) => {
    const response = await api.delete(`journey/updates/${updateId}/images/${imageId}/delete/`);
    return response.data;
  },

  reorderUpdateImages: async (updateId, orderedIds) => {
    const response = await api.patch(`journey/updates/${updateId}/images/reorder/`, {
      ordered_ids: orderedIds,
    });
    return response.data;
  },

  getTrendingTags: async () => {
    const response = await api.get("/journey/tags/trending/");
    return response.data;
  },

  getTagDetail: async (slug) => {
    const response = await api.get(`/journey/tags/${slug}/`);
    return response.data;
  },
};

export const reactionService = {
  toggleLike: async (updateId) => {
    const response = await api.post(`reaction/updates/${updateId}/like/`);
    return response.data;
  },
  toggleUnLike: async (updateId) => {
    const response = await api.delete(`reaction/updates/${updateId}/unlike/`);
    return response.data;
  },

  toggleSaveJourney: async (journeyId) => {
    const response = await api.post(`reaction/journeys/${journeyId}/save/`);
    return response.data;
  },
  unsaveJourney: async (journeyId) => {
    const response = await api.delete(`/reaction/journeys/${journeyId}/unsave/`);
    return response.data;
  },

  toggleSave: async (updateId) => {
    const response = await api.post(`reaction/updates/${updateId}/save/`);
    return response.data;
  },

  unsaveUpdate: async (updateId) => {
    const response = await api.delete(`/reaction/updates/${updateId}/unsave/`);
    return response.data;
  },
  getComments: async (updateId, cursor = null) => {
    const params = {};
    if (cursor) params.cursor = cursor;
    const response = await api.get(`/reaction/updates/${updateId}/comments/`, { params });
    return response.data;
  },

  createComment: async (updateId, content) => {
    const response = await api.post(`/reaction/updates/${updateId}/comments/create/`, {
      content,
    });
    return response.data;
  },

  updateComment: async (commentId, content) => {
    const response = await api.patch(`/reaction/comments/${commentId}/`, {
      content,
    });
    return response.data;
  },

  deleteComment: async (commentId) => {
    const response = await api.delete(`/reaction/comments/${commentId}/`);
    return response.data;
  },

  getReplies: async (commentId, cursor = null) => {
    const params = {};
    if (cursor) params.cursor = cursor;
    const response = await api.get(`/reaction/comments/${commentId}/replies/`, { params });
    return response.data;
  },

  createReply: async (commentId, content) => {
    const response = await api.post(`/reaction/comments/${commentId}/replies/create/`, {
      content,
    });
    return response.data;
  },

  updateReply: async (replyId, content) => {
    const response = await api.patch(`/reaction/replies/${replyId}/`, {
      content,
    });
    return response.data;
  },

  deleteReply: async (replyId) => {
    const response = await api.delete(`/reaction/replies/${replyId}/`);
    return response.data;
  },

  getAcceptedSolution: async (updateId) => {
    const response = await api.get(`/reaction/updates/${updateId}/accepted-solution/`);
    return response.data;
  },

  acceptSolution: async (updateId, commentId) => {
    const response = await api.post(`/reaction/updates/${updateId}/accept-solution/`, {
      comment_id: commentId,
    });
    return response.data;
  },

  removeAcceptedSolution: async (updateId) => {
    const response = await api.delete(`/reaction/updates/${updateId}/remove-accepted/`);
    return response.data;
  },
};

export const feedService = {
  latestFeed: async (cursor = null, pageSize = 30) => {
    const params = { page_size: pageSize };
    if (cursor) {
      params.cursor = cursor;
    }
    const response = await api.get("/feed/latest/", { params });
    return response.data;
  },

  followingFeed: async (cursor = null, pageSize = 30) => {
    const params = { page_size: pageSize };
    if (cursor) {
      params.cursor = cursor;
    }
    const response = await api.get("/feed/following/", { params });
    return response.data;
  },

  trendingFeed: async (cursor = null, pageSize = 30) => {
    const params = { page_size: pageSize };
    if (cursor) {
      params.cursor = cursor;
    }
    const response = await api.get("/feed/trending/", { params });
    return response.data;
  },

  helpNeededFeed: async (cursor = null, pageSize = 30) => {
    const params = { page_size: pageSize };
    if (cursor) {
      params.cursor = cursor;
    }
    const response = await api.get("/feed/help-needed/", { params });
    return response.data;
  },
};

export const notificationService = {
  listNotifications: async (page = 1, pageSize = 20) => {
    const response = await api.get("reaction/notifications/", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getNotification: async (id) => {
    const response = await api.get(`reaction/notifications/${id}/`);
    return response.data;
  },

  updateNotification: async (id, data) => {
    const response = await api.patch(`reaction/notifications/${id}/`, data);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.post("reaction/notifications/mark-all-read/");
    return response.data;
  },

  getUnreadCount: async () => {
    const response = await api.get("reaction/notifications/unread-count/");
    return response.data;
  },
};

export const scoreService = {
  getMyScore: async () => {
    const response = await api.get("/score/me/");
    return response.data;
  },

  getMyRank: async () => {
    const response = await api.get("/score/rank/");
    return response.data;
  },

  getScoreHistory: async (params = {}) => {
    const response = await api.get("/score/history/", { params });
    return response.data;
  },

  getScoreHistoryDetail: async (id) => {
    const response = await api.get(`/score/history/${id}/`);
    return response.data;
  },

  getPublicScore: async (username) => {
    const response = await api.get(`/score/users/${username}/`);
    return response.data;
  },

  getLeaderboard: async (params = {}) => {
    const response = await api.get("/score/leaderboard/", { params });
    return response.data;
  },
};

export const auditService = {
  getReports: async (params = {}) => {
    const response = await api.get("/audit/reports/", { params });
    return response.data;
  },

  createReport: async (data) => {
    const response = await api.post("/audit/reports/create/", data);
    return response.data;
  },

  getReportDetail: async (id) => {
    const response = await api.get(`/audit/reports/${id}/`);
    return response.data;
  },

  updateReport: async (id, data) => {
    const response = await api.patch(`/audit/reports/${id}/`, data);
    return response.data;
  },

  getReportStats: async () => {
    const response = await api.get("/audit/reports/stats/");
    return response.data;
  },
};

export const feedbackService = {
  submitFeedback: async (data) => {
    const response = await api.post("/feedback/create/", data);
    return response.data;
  },

  getFeedbacks: async (params = {}) => {
    const response = await api.get("/feedback/", { params });
    return response.data;
  },

  getSingleFeedback: async (id) => {
    const response = await api.get(`/feedback/${id}/`);
    return response.data;
  },

  updateFeedback: async (id, data) => {
    const response = await api.patch(`/feedback/${id}/`, data);
    return response.data;
  },
};
