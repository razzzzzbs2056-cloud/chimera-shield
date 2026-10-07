import { NextResponse, type NextRequest } from "next/server";

// Cheap edge gate: no session cookie → login. Sessions are validated against
// the database in server components and route handlers.
export function middleware(req: NextRequest) {
  const has = req.cookies.has("aec_session");
  const { pathname } = req.nextUrl;
  const isAuthPage = pathname === "/login" || pathname === "/register";
  if (!has && !isAuthPage && !pathname.startsWith("/api/auth") && !pathname.startsWith("/api/v1/")) {
    if (pathname.startsWith("/api/")) return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = { matcher: ["/((?!_next/static|_next/image|favicon.ico|icon.svg).*)"] };
