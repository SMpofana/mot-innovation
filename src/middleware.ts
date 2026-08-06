import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Capture UTM parameters on first visit and store in cookie
// so we can attribute leads to content even if they browse first
export function middleware(request: NextRequest) {
  const url = request.nextUrl;
  const utmParams = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
  const hasUtm = utmParams.some(p => url.searchParams.has(p));

  if (hasUtm) {
    const response = NextResponse.next();
    // Store UTM params in a cookie that lasts 30 days
    const utmData: Record<string, string> = {};
    utmParams.forEach(p => {
      const val = url.searchParams.get(p);
      if (val) utmData[p] = val;
    });
    response.cookies.set('mot_utm', JSON.stringify(utmData), {
      maxAge: 30 * 24 * 60 * 60, // 30 days
      httpOnly: true,
      sameSite: 'lax',
    });
    return response;
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon).*)'],
};