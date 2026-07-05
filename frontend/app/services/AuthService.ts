import { supabaseClient } from "../lib/supabase/client";
import { apiClient } from "../lib/api";
import type { User } from "../lib/types";

export const AuthService = {
  /** Check backend authentication status and return profile user */
  async getMe(): Promise<User> {
    return apiClient.get<User>("/auth/me");
  },

  /** Sign in user with email and password via Supabase */
  async signIn(email: string, password: string) {
    const { data, error } = await supabaseClient.auth.signInWithPassword({
      email,
      password,
    });
    if (error) throw new Error(error.message);
    return data;
  },

  /** Sign up user with email and password via Supabase */
  async signUp(email: string, password: string, fullName: string) {
    const { data, error } = await supabaseClient.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });
    if (error) throw new Error(error.message);
    return data;
  },

  /** Sign out from Supabase */
  async signOut() {
    const { error } = await supabaseClient.auth.signOut();
    if (error) throw new Error(error.message);
  },

  /** Initiate password recovery reset request */
  async forgotPassword(email: string, redirectTo: string) {
    const { data, error } = await supabaseClient.auth.resetPasswordForEmail(email, {
      redirectTo,
    });
    if (error) throw new Error(error.message);
    return data;
  },

  /** Update/reset password in recovery flow */
  async resetPassword(password: string) {
    const { data, error } = await supabaseClient.auth.updateUser({
      password,
    });
    if (error) throw new Error(error.message);
    return data;
  },

  /** Check current session status */
  async getSession() {
    const { data: { session }, error } = await supabaseClient.auth.getSession();
    if (error) throw new Error(error.message);
    return session;
  },
};
