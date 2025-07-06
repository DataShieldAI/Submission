// app/api/github/callback/route.ts

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');

  if (!code) {
    return NextResponse.redirect(new URL('/dashboard?error=github_auth_failed', request.url));
  }

  try {
    // Step 1: Exchange the code for an access token
    const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        client_id: process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID,
        client_secret: process.env.GITHUB_CLIENT_SECRET,
        code: code,
      }),
    });

    const tokenData = await tokenResponse.json();

    if (tokenData.error || !tokenData.access_token) {
      console.error('GitHub token exchange error:', tokenData.error_description);
      return NextResponse.redirect(new URL('/dashboard?error=github_token_failed', request.url));
    }

    const accessToken = tokenData.access_token;

    // Step 2: Use the access token to get user information
    const userResponse = await fetch('https://api.github.com/user', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: 'application/vnd.github.v3+json',
      },
    });

    const userData = await userResponse.json();

    if (!userResponse.ok) {
        console.error('GitHub user fetch error:', userData.message);
        return NextResponse.redirect(new URL('/dashboard?error=github_user_fetch_failed', request.url));
    }
    
    const username = userData.login;

    // Step 3: Redirect to a dedicated callback page to set localStorage
    const callbackUrl = new URL('/github-callback', request.url);
    callbackUrl.searchParams.set('username', username);
    
    return NextResponse.redirect(callbackUrl);

  } catch (error) {
    console.error('An unexpected error occurred during GitHub auth:', error);
    return NextResponse.redirect(new URL('/dashboard?error=internal_server_error', request.url));
  }
}