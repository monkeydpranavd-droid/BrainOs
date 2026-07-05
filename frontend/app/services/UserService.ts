import { apiClient } from "../lib/api";
import type { User } from "../lib/types";

export const UserService = {
  async getMe(): Promise<User> {
    return apiClient.get<User>("/users/me");
  },

  async updateMe(payload: { full_name?: string; avatar_url?: string }): Promise<User> {
    return apiClient.patch<User>("/users/me", payload);
  },
};
