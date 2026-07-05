import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Middleware is a passthrough — auth is handled client-side by AuthProvider.
// We don't do server-side session checks here to avoid complexity with
// Supabase SSR cookie management.
export function middleware(request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
