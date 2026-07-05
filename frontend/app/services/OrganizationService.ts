import { apiClient } from "../lib/api";
import type { Organization, OrganizationMember } from "../lib/types";

export const OrganizationService = {
  async list(): Promise<Organization[]> {
    return apiClient.get<Organization[]>("/organizations");
  },

  async create(payload: { name: string; slug?: string }): Promise<Organization> {
    return apiClient.post<Organization>("/organizations", payload);
  },

  async getById(orgId: string): Promise<Organization> {
    return apiClient.get<Organization>(`/organizations/${orgId}`);
  },

  async listMembers(orgId: string): Promise<OrganizationMember[]> {
    return apiClient.get<OrganizationMember[]>(`/organizations/${orgId}/members`);
  },

  async inviteMember(orgId: string, email: string, role: string): Promise<unknown> {
    return apiClient.post<unknown>(`/organizations/${orgId}/invite`, { email, role });
  },

  async acceptInvite(token: string): Promise<OrganizationMember> {
    return apiClient.post<OrganizationMember>("/organizations/accept-invite", { token });
  },
};
