import { createClient } from "@supabase/supabase-js";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export async function updateSession(request: NextRequest) {
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  });

  const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: false,
      detectSessionInUrl: false,
      storage: {
        getItem(key) {
          const cookie = request.cookies.get(key);
          return cookie ? cookie.value : null;
        },
        setItem(key, value) {
          request.cookies.set(key, value);
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          });
          response.cookies.set(key, value, { path: "/" });
        },
        removeItem(key) {
          request.cookies.delete(key);
          response = NextResponse.next({
            request: {
              headers: request.headers,
            },
          });
          response.cookies.set(key, "", { maxAge: -1, path: "/" });
        },
      },
    },
  });

  // Retrieves user and refreshes session if required
  const { data: { user } } = await supabase.auth.getUser();

  return { response, user };
}
