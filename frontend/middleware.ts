import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { updateSession } from "./app/lib/supabase/middleware";

// Routes that require authentication
const PROTECTED_ROUTES = [
  "/",
  "/documents",
  "/organizations",
  "/workspaces",
  "/profile",
];

// Routes for guest users (should redirect to dashboard if already authenticated)
const AUTH_ROUTES = [
  "/login",
  "/signup",
  "/forgot-password",
  "/reset-password",
  "/verify-email",
];

export async function middleware(request: NextRequest) {
  const { response, user } = await updateSession(request);
  const { pathname } = request.nextUrl;

  const isProtectedRoute = PROTECTED_ROUTES.some((route) =>
    route === "/" ? pathname === "/" : pathname.startsWith(route)
  );
  const isAuthRoute = AUTH_ROUTES.some((route) =>
    pathname.startsWith(route)
  );

  // If attempting to access protected route without valid session
  if (isProtectedRoute && !user) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    // Preserve destination for redirect back after login
    url.searchParams.set("redirectTo", pathname);
    return NextResponse.redirect(url);
  }

  // If already authenticated and accessing login/signup paths
  if (isAuthRoute && user) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * Feel free to modify this pattern to include more paths.
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
