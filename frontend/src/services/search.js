import api from "./api";

export const searchService = {
  searchAll: async (query) => {
    const [usersResponse, journeysResponse] = await Promise.all([
      api.get(`/accounts/users/search/?q=${encodeURIComponent(query)}`),
      api.get(`/journey/search/?q=${encodeURIComponent(query)}`),
    ]);

    return {
      users: usersResponse.data.data || [],
      journeys: journeysResponse.data.data || [],
    };
  },

  searchUsers: async (query) => {
    const response = await api.get(`/accounts/users/search/?q=${encodeURIComponent(query)}`);
    return response.data.data || [];
  },

  searchJourneys: async (query) => {
    const response = await api.get(`/journeys/search/?q=${encodeURIComponent(query)}`);
    return response.data.data || [];
  },
};
