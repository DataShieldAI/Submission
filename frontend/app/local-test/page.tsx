'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Terminal } from 'lucide-react';

// Define the endpoints we want to test
const TEST_ENDPOINTS = {
  analyze: {
    path: '/analyze-repository',
    method: 'POST',
    body: (url: string) => ({ github_url: url, license_type: "MIT", description: "" }),
  },
  audit: {
    path: '/security-audit',
    method: 'POST',
    body: (url: string) => ({ github_url: url }),
  },
  clean: {
    path: '/clean-urls',
    method: 'POST',
    body: (url: string) => ({ url_text: url }),
  }
};

type ActionKey = keyof typeof TEST_ENDPOINTS;

export default function LocalTestPage() {
  const [inputUrl, setInputUrl] = useState('https://github.com/DataShield-Security/datashield-example');
  const [selectedAction, setSelectedAction] = useState<ActionKey>('analyze');
  const [responseData, setResponseData] = useState<object | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Hardcode the local backend URL for this test page
  const agentApiUrl = 'http://localhost:8000';

  const handleTestSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setResponseData(null);

    const endpoint = TEST_ENDPOINTS[selectedAction];

    try {
      const response = await fetch(`${agentApiUrl}${endpoint.path}`, {
        method: endpoint.method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(endpoint.body(inputUrl)),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Backend Error ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      setResponseData(data);

    } catch (err: any) {
      console.error("Test API call failed:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        <Card className="bg-slate-950/50 border-purple-800/30">
          <CardHeader>
            <CardTitle className="text-2xl text-white">Backend Agent Test Console</CardTitle>
            <CardDescription className="text-slate-400">
              Directly interact with your local Python backend API for testing purposes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="input-url" className="text-slate-300">Input URL or Text</Label>
              <Input
                id="input-url"
                value={inputUrl}
                onChange={(e) => setInputUrl(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-400 focus:border-purple-500"
                placeholder="https://github.com/user/repo"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="action-select" className="text-slate-300">Action</Label>
              <Select value={selectedAction} onValueChange={(value) => setSelectedAction(value as ActionKey)}>
                <SelectTrigger id="action-select" className="bg-slate-800 border-slate-700 text-white">
                  <SelectValue placeholder="Select an action" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700 text-white">
                  <SelectItem value="analyze">Analyze Repository</SelectItem>
                  <SelectItem value="audit">Comprehensive Security Audit</SelectItem>
                  <SelectItem value="clean">Clean URLs from Text</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Button
                onClick={handleTestSubmit}
                disabled={isLoading || !inputUrl}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Terminal className="mr-2 h-4 w-4" />}
                Send Request to Backend
              </Button>
            </div>

            {(responseData || error) && (
              <div className="space-y-4 pt-4">
                <h3 className="text-lg font-semibold text-white">Response</h3>
                {error && (
                  <pre className="bg-red-900/20 text-red-300 p-4 rounded-md border border-red-500/30 text-sm overflow-x-auto">
                    {error}
                  </pre>
                )}
                {responseData && (
                  <pre className="bg-slate-800/50 p-4 rounded-md text-slate-300 text-sm overflow-x-auto">
                    {JSON.stringify(responseData, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}