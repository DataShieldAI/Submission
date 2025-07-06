// app/github-callback/page.tsx

'use client';

import { useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Loader2, Github } from 'lucide-react';

export default function GitHubCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const username = searchParams.get('username');
    
    if (username) {
      // Set the item in localStorage for the main app to pick up
      localStorage.setItem('github_username', username);
      // Redirect to the dashboard
      router.replace('/dashboard');
    } else {
      // Handle error case, maybe redirect with an error message
      router.replace('/dashboard?error=authentication_failed');
    }
    
  }, [searchParams, router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-900 text-white">
      <Github className="h-16 w-16 text-purple-400 mb-6" />
      <div className="flex items-center text-xl font-semibold">
        <Loader2 className="mr-3 h-6 w-6 animate-spin" />
        <p>Finalizing GitHub connection...</p>
      </div>
      <p className="mt-2 text-slate-400">Please wait, you will be redirected shortly.</p>
    </div>
  );
}