import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export async function createSupabaseServer() {
  const cookieStore = await cookies();

  return createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: false,
      detectSessionInUrl: false,
      storage: {
        getItem(key) {
          const cookie = cookieStore.get(key);
          return cookie ? cookie.value : null;
        },
        setItem(key, value) {
          try {
            cookieStore.set(key, value, { path: "/" });
          } catch (err) {
            // Safe fallback when executed in read-only Server Components
          }
        },
        removeItem(key) {
          try {
            cookieStore.set(key, "", { maxAge: -1, path: "/" });
          } catch (err) {
            // Safe fallback
          }
        },
      },
    },
  });
}
