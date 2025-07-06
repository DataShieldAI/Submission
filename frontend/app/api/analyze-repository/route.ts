// In: app/api/analyze-repository/route.ts

import { NextResponse } from 'next/server';
import { sha256 } from 'js-sha256';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { github_url } = body;

    if (!github_url) {
      return NextResponse.json({ success: false, error: 'GitHub URL is required.' }, { status: 400 });
    }

    // --- 1. Parse URL to get owner and repo name ---
    let owner, repoName;
    try {
      const url = new URL(github_url);
      const pathParts = url.pathname.split('/').filter(p => p);
      if (pathParts.length < 2) throw new Error();
      owner = pathParts[0];
      repoName = pathParts[1].replace('.git', '');
    } catch {
      return NextResponse.json({ success: false, error: 'Invalid GitHub repository URL format.' }, { status: 400 });
    }

    // --- 2. Fetch repo data from GitHub to get the last update time ---
    // This makes the hash unique to the repo's current state.
    const repoResponse = await fetch(`https://api.github.com/repos/${owner}/${repoName}`);
    if (!repoResponse.ok) {
        return NextResponse.json({ success: false, error: 'Failed to fetch repository from GitHub. Check URL and repository permissions.' }, { status: 404 });
    }
    const repoData = await repoResponse.json();
    const lastPushedAt = repoData.pushed_at; // e.g., "2024-07-06T10:00:00Z"

    // --- 3. Generate data for the smart contract ---
    const repo_hash = '0x' + sha256(github_url + lastPushedAt);
    const fingerprint = `fingerprint_for_${repoName}_${lastPushedAt}`;
    const key_features = [`${repoName}-core`, 'data-module', 'user-interface'];
    const analysis = {
        checkedAt: new Date().toISOString(),
        hashSource: `SHA256 of URL and last push time (${lastPushedAt})`,
        repoStars: repoData.stargazers_count,
        language: repoData.language,
    };
    
    // --- 4. Return the structured data ---
    return NextResponse.json({
      success: true,
      repo_hash,
      fingerprint,
      key_features,
      analysis, // This will be stringified for the contract
    });

  } catch (error: any) {
    console.error('Analysis API Error:', error);
    return NextResponse.json({ success: false, error: 'An internal server error occurred.' }, { status: 500 });
  }
}