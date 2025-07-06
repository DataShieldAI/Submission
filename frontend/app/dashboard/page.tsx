'use client';

import { useState, useEffect, useMemo } from 'react';
import { createPublicClient, createWalletClient, custom, http } from 'viem';
import { flowTestnet } from 'viem/chains';
import { Shield, Github, ExternalLink, Plus, Eye, FileText, CheckCircle, AlertCircle, Wallet, Search, LogOut, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import Link from 'next/link';
// Note: You will need to install this package to generate placeholder hashes
// npm install js-sha256 @types/js-sha256
import { sha256 } from 'js-sha256';

// --- TYPE DECLARATION FOR WINDOW.ETHEREUM ---
declare global {
  interface Window {
    ethereum?: any;
  }
}

// --- SMART CONTRACT CONFIGURATION ---
const CONTRACT_ADDRESS = '0x5fa19b4a48C20202055c8a6fdf16688633617D50';
const GITHUB_REPO_PROTECTION_ABI = [{"inputs":[{"internalType":"uint256","name":"repoId","type":"uint256"}],"name":"deactivateRepository","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"repoId","type":"uint256"}],"name":"getRepository","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"githubUrl","type":"string"},{"internalType":"string","name":"repoHash","type":"string"},{"internalType":"string","name":"codeFingerprint","type":"string"},{"internalType":"string[]","name":"keyFeatures","type":"string[]"},{"internalType":"string","name":"licenseType","type":"string"},{"internalType":"uint256","name":"registeredAt","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"string","name":"ipfsMetadata","type":"string"}],"internalType":"struct GitHubRepoProtection.Repository","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"repoHash","type":"string"}],"name":"getRepositoryByHash","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"githubUrl","type":"string"},{"internalType":"string","name":"repoHash","type":"string"},{"internalType":"string","name":"codeFingerprint","type":"string"},{"internalType":"string[]","name":"keyFeatures","type":"string[]"},{"internalType":"string","name":"licenseType","type":"string"},{"internalType":"uint256","name":"registeredAt","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"string","name":"ipfsMetadata","type":"string"}],"internalType":"struct GitHubRepoProtection.Repository","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"repoId","type":"uint256"}],"name":"getRepositoryViolations","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalRepositories","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getTotalViolations","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"user","type":"address"}],"name":"getUserRepositories","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"violationId","type":"uint256"}],"name":"getViolation","outputs":[{"components":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"originalRepoId","type":"uint256"},{"internalType":"address","name":"reporter","type":"address"},{"internalType":"string","name":"violatingUrl","type":"string"},{"internalType":"string","name":"evidenceHash","type":"string"},{"internalType":"uint256","name":"similarityScore","type":"uint256"},{"internalType":"enum GitHubRepoProtection.ViolationStatus","name":"status","type":"uint8"},{"internalType":"uint256","name":"reportedAt","type":"uint256"},{"internalType":"string","name":"dmcaReference","type":"string"}],"internalType":"struct GitHubRepoProtection.CodeViolation","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"githubUrl","type":"string"},{"internalType":"string","name":"repoHash","type":"string"},{"internalType":"string","name":"codeFingerprint","type":"string"},{"internalType":"string[]","name":"keyFeatures","type":"string[]"},{"internalType":"string","name":"licenseType","type":"string"},{"internalType":"string","name":"ipfsMetadata","type":"string"}],"name":"registerRepository","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"","type":"string"}],"name":"repoHashToId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"repoViolations","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"originalRepoId","type":"uint256"},{"internalType":"string","name":"violatingUrl","type":"string"},{"internalType":"string","name":"evidenceHash","type":"string"},{"internalType":"uint256","name":"similarityScore","type":"uint256"}],"name":"reportViolation","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"repositories","outputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"string","name":"githubUrl","type":"string"},{"internalType":"string","name":"repoHash","type":"string"},{"internalType":"string","name":"codeFingerprint","type":"string"},{"internalType":"string","name":"licenseType","type":"string"},{"internalType":"uint256","name":"registeredAt","type":"uint256"},{"internalType":"bool","name":"isActive","type":"bool"},{"internalType":"string","name":"ipfsMetadata","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"repoId","type":"uint256"},{"internalType":"string","name":"newLicense","type":"string"}],"name":"updateLicense","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"violationId","type":"uint256"},{"internalType":"enum GitHubRepoProtection.ViolationStatus","name":"newStatus","type":"uint8"},{"internalType":"string","name":"dmcaReference","type":"string"}],"name":"updateViolationStatus","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"userRepositories","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"violations","outputs":[{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"originalRepoId","type":"uint256"},{"internalType":"address","name":"reporter","type":"address"},{"internalType":"string","name":"violatingUrl","type":"string"},{"internalType":"string","name":"evidenceHash","type":"string"},{"internalType":"uint256","name":"similarityScore","type":"uint256"},{"internalType":"enum GitHubRepoProtection.ViolationStatus","name":"status","type":"uint8"},{"internalType":"uint256","name":"reportedAt","type":"uint256"},{"internalType":"string","name":"dmcaReference","type":"string"}],"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"repoId","type":"uint256"},{"indexed":false,"internalType":"string","name":"newLicense","type":"string"}],"name":"LicenseUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"repoId","type":"uint256"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"string","name":"githubUrl","type":"string"},{"indexed":false,"internalType":"string","name":"repoHash","type":"string"}],"name":"RepositoryRegistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"violationId","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"originalRepoId","type":"uint256"},{"indexed":true,"internalType":"address","name":"reporter","type":"address"},{"indexed":false,"internalType":"string","name":"violatingUrl","type":"string"},{"indexed":false,"internalType":"uint256","name":"similarityScore","type":"uint256"}],"name":"ViolationReported","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"violationId","type":"uint256"},{"indexed":false,"internalType":"enum GitHubRepoProtection.ViolationStatus","name":"newStatus","type":"uint8"},{"indexed":false,"internalType":"string","name":"dmcaReference","type":"string"}],"name":"ViolationStatusUpdated","type":"event"}];

// --- TYPE DEFINITIONS ---
interface Match {
  dataset: string;
  date: string;
  file: string;
  similarity: number;
  violationId: bigint;
}

interface Repository {
  id: bigint;
  name: string;
  fullName: string;
  status: 'protected' | 'match_found';
  dateRegistered: string;
  nftId?: string;
  matchesFound?: number;
  matches?: Match[];
  onChainData?: any;
}

// --- GITHUB OAUTH HOOK (UNCHANGED AS REQUESTED) ---
function useGitHubConnection() {
  const [isConnected, setIsConnected] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || "";
  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  const redirectUri = `${baseUrl}/api/github/callback`;
  const scope = "read:user repo";

  useEffect(() => {
    const storedUsername = localStorage.getItem("github_username");
    if (storedUsername) {
      setIsConnected(true);
      setUsername(storedUsername);
    }
  }, []);

  const connect = async () => {
    if (!clientId) {
      setError("GitHub Client ID is not configured. Please set NEXT_PUBLIC_GITHUB_CLIENT_ID in your .env file.");
      return;
    }
    setIsLoading(true);
    setError(null);
    const authUrl = new URL("https://github.com/login/oauth/authorize");
    authUrl.search = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      scope: scope,
      state: Math.random().toString(36).substring(7),
    }).toString();
    
    window.location.href = authUrl.toString();
  };

  const disconnect = () => {
    localStorage.removeItem("github_username");
    setIsConnected(false);
    setUsername(null);
    setError(null);
  };

  return { isConnected, username, connect, disconnect, isLoading, error };
}

// --- MAIN DASHBOARD COMPONENT ---
export default function DashboardPage() {
  const [account, setAccount] = useState<`0x${string}` | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false); // Use a separate state for submission
  const [error, setError] = useState<string | null>(null);
  const { isConnected: isGitHubConnected, username: githubUsername, connect: connectGitHub, disconnect: disconnectGitHub, isLoading: isGitHubLoading } = useGitHubConnection();

  const [showProtectModal, setShowProtectModal] = useState(false);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [showNFTModal, setShowNFTModal] = useState(false);
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [newRepoUrl, setNewRepoUrl] = useState('');
  const [newRepoLicense, setNewRepoLicense] = useState('MIT');
  const [claimReason, setClaimReason] = useState('');
  const [claimType, setClaimType] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Setup viem clients
  const publicClient = useMemo(() => createPublicClient({ chain: flowTestnet, transport: http() }), []);
  const walletClient = useMemo(() => typeof window !== "undefined" && window.ethereum ? createWalletClient({ chain: flowTestnet, transport: custom(window.ethereum) }) : null, [account]);

  // --- DATA FETCHING & WEB3 INTERACTIONS ---
  const connectWallet = async () => {
    if (!walletClient) {
      setError("Wallet not found. Please install a wallet extension like MetaMask.");
      return;
    }
    try {
      const [address] = await walletClient.requestAddresses();
      setAccount(address);
    } catch (err: any) {
      setError("Failed to connect wallet: " + (err.shortMessage || err.message));
    }
  };

  const fetchRepositories = async (userAddress: `0x${string}`) => {
    if (!publicClient) return;
    setIsLoading(true);
    try {
      const repoIds = (await publicClient.readContract({
        address: CONTRACT_ADDRESS,
        abi: GITHUB_REPO_PROTECTION_ABI,
        functionName: 'getUserRepositories',
        args: [userAddress],
      })) as bigint[];

      const repoPromises = repoIds.map(async (id) => {
        const repoData = (await publicClient.readContract({
          address: CONTRACT_ADDRESS,
          abi: GITHUB_REPO_PROTECTION_ABI,
          functionName: 'getRepository',
          args: [id],
        })) as any;

        const violationIds = (await publicClient.readContract({
          address: CONTRACT_ADDRESS,
          abi: GITHUB_REPO_PROTECTION_ABI,
          functionName: 'getRepositoryViolations',
          args: [id],
        })) as bigint[];

        const matches: Match[] = [];
        if (violationIds.length > 0) {
           const violationPromises = violationIds.map(vid => publicClient.readContract({
             address: CONTRACT_ADDRESS,
             abi: GITHUB_REPO_PROTECTION_ABI,
             functionName: 'getViolation',
             args: [vid]
           }));
           const violations = await Promise.all(violationPromises) as any[];
           violations.forEach(v => {
             matches.push({
               dataset: v.violatingUrl,
               date: new Date(Number(v.reportedAt) * 1000).toISOString(),
               file: "N/A",
               similarity: Number(v.similarityScore) / 100,
               violationId: v.id
             });
           });
        }
        
        const fullName = new URL(repoData.githubUrl).pathname.slice(1);
        
        const newRepo: Repository = {
          id: repoData.id,
          name: fullName.split('/')[1],
          fullName: fullName,
          status: matches.length > 0 ? 'match_found' : 'protected',
          dateRegistered: new Date(Number(repoData.registeredAt) * 1000).toISOString(),
          nftId: `REPO-${repoData.id.toString()}`,
          matchesFound: matches.length,
          matches: matches,
          onChainData: repoData
        };
        return newRepo;
      });

      const userRepos = await Promise.all(repoPromises);
      setRepositories(userRepos.filter(r => r.onChainData.isActive).sort((a, b) => new Date(b.dateRegistered).getTime() - new Date(a.dateRegistered).getTime()));
      setError(null);
    } catch (err: any) {
      console.error("Failed to fetch repositories:", err);
      setError("Could not fetch repositories from the blockchain. " + (err.shortMessage || err.message));
    } finally {
      setIsLoading(false);
    }
  };
  
  useEffect(() => {
    if (walletClient && !account) {
      connectWallet();
    }
  }, [walletClient]);

  useEffect(() => {
    if (account && publicClient) {
      fetchRepositories(account);
    }
  }, [account, publicClient]);

  useEffect(() => {
    if (!publicClient || !account) return;

    const unwatchRepoRegistered = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESS,
      abi: GITHUB_REPO_PROTECTION_ABI,
      eventName: 'RepositoryRegistered',
      onLogs: (logs) => {
        const isMyEvent = logs.some(log => (log as any).args.owner?.toLowerCase() === account.toLowerCase());
        if (isMyEvent) {
          console.log("New repository registered! Refreshing list...");
          fetchRepositories(account);
        }
      }
    });

    const unwatchViolationReported = publicClient.watchContractEvent({
      address: CONTRACT_ADDRESS,
      abi: GITHUB_REPO_PROTECTION_ABI,
      eventName: 'ViolationReported',
      onLogs: (logs) => {
         console.log("New violation reported! Refreshing list...");
         fetchRepositories(account);
      }
    });

    return () => {
      unwatchRepoRegistered();
      unwatchViolationReported();
    };
  }, [publicClient, account]);


  // --- UPDATED REGISTRATION FUNCTION ---
  const handleProtectRepo = async () => {
    if (!walletClient || !account) {
      setError("Please connect your wallet first.");
      return;
    }
    if (!isGitHubConnected || !githubUsername) {
      setError("Please connect your GitHub account first.");
      return;
    }
    
    setIsSubmitting(true);
    setError(null);

    try {
      // 1. Call your new backend API route to get analysis data
      const response = await fetch('/api/analyze-repository', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_url: newRepoUrl }),
      });

      const analysis = await response.json();

      if (!response.ok || !analysis.success) {
        throw new Error(analysis.error || "Failed to analyze repository.");
      }

      // 2. Verify the repo owner matches the connected GitHub user
      const url = new URL(newRepoUrl);
      const ownerFromUrl = url.pathname.split('/')[1];
      if (ownerFromUrl.toLowerCase() !== githubUsername.toLowerCase()) {
        throw new Error(`Repository owner (${ownerFromUrl}) does not match your connected account (${githubUsername}).`);
      }
      
      // 3. Use the analysis data from your API to call the smart contract
      const { request } = await publicClient.simulateContract({
          account,
          address: CONTRACT_ADDRESS,
          abi: GITHUB_REPO_PROTECTION_ABI,
          functionName: 'registerRepository',
          args: [
              newRepoUrl,
              analysis.repo_hash,
              analysis.fingerprint,
              analysis.key_features,
              newRepoLicense,
              JSON.stringify(analysis.analysis), // The 'ipfsMetadata' field
          ]
      });

      const hash = await walletClient.writeContract(request);
      await publicClient.waitForTransactionReceipt({ hash });
      
      setShowProtectModal(false);
      setNewRepoUrl('');
      setNewRepoLicense('MIT');
      await fetchRepositories(account); // Refresh list
      
    } catch (err: any) {
       console.error("Submission Error:", err);
       setError("Failed to register: " + (err.shortMessage || err.message));
    } finally {
       setIsSubmitting(false);
    }
  };

  const handleSubmitClaim = async () => {
    if (!selectedRepo) return;
    try {
      const response = await fetch('/api/submit-claim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repoId: selectedRepo.id.toString(),
          reason: claimReason,
          type: claimType,
          matches: selectedRepo.matches
        })
      });
      if(!response.ok) throw new Error("Failed to submit claim.");
    } catch (err: any) {
       setError("Failed to submit claim: " + err.message);
    } finally {
      setShowClaimModal(false);
      setClaimReason('');
      setClaimType('');
      setSelectedRepo(null);
    }
  };

  // --- UI HELPER FUNCTIONS & RENDER LOGIC ---
  const filteredRepositories = repositories.filter(repo =>
    repo.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    repo.fullName.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'protected': return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'match_found': return <AlertCircle className="h-4 w-4 text-red-400" />;
      default: return <CheckCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'protected': return 'Protected';
      case 'match_found': return 'Match Found';
      default: return 'Unknown';
    }
  };

  const truncatedAddress = useMemo(() => account ? `${account.slice(0, 6)}...${account.slice(-4)}` : 'Connect Wallet', [account]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 via-pink-500/5 to-purple-500/5"></div>
      </div>

      <header className="relative z-10 border-b border-purple-800/20 bg-slate-950/80 backdrop-blur-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-purple-400" />
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                DataShield
              </span>
            </Link>
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={connectWallet} disabled={!!account} className="border-green-500/50 text-green-400">
                <Wallet className="mr-2 h-4 w-4" />
                {truncatedAddress}
              </Button>
              {isGitHubConnected ? (
                 <Badge variant="outline" className="border-blue-500/50 text-blue-400">
                  <Github className="mr-2 h-4 w-4" />
                  {githubUsername}
                  <LogOut className="ml-2 h-3 w-3 cursor-pointer hover:text-red-400" onClick={disconnectGitHub}/>
                </Badge>
              ) : (
                <Button variant="outline" onClick={connectGitHub} disabled={isGitHubLoading} className="border-blue-600/50 text-blue-400 hover:bg-blue-900/50">
                  {isGitHubLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin"/> : <Github className="mr-2 h-4 w-4" />}
                  Connect GitHub
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="relative z-10 container mx-auto px-6 py-8">
        <div className="mb-8">
           <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">My Repositories</h1>
              {error && <p className="text-red-400 text-sm p-3 bg-red-900/20 rounded-md border border-red-500/30">{error}</p>}
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  placeholder="Search repositories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 w-64 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-400 focus:border-purple-500"
                />
              </div>

              <Dialog open={showProtectModal} onOpenChange={(isOpen) => {
                setShowProtectModal(isOpen);
                if (!isOpen) {
                  setNewRepoUrl('');
                  setNewRepoLicense('MIT');
                  setError(null);
                }
              }}>
                <DialogTrigger asChild>
                  <Button disabled={!account || !isGitHubConnected} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50">
                    <Plus className="mr-2 h-4 w-4" />
                    Protect Repository
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-900 border-purple-800/30">
                  <DialogHeader>
                    <DialogTitle className="text-white">Protect a Repository</DialogTitle>
                    <DialogDescription className="text-slate-300">
                      Enter your GitHub repository URL and select its license to register on-chain.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div>
                      <Label htmlFor="repo-url" className="text-slate-300">Repository URL</Label>
                      <Input
                        id="repo-url"
                        placeholder="https://github.com/username/repository"
                        value={newRepoUrl}
                        onChange={(e) => setNewRepoUrl(e.target.value)}
                        className="bg-slate-800 border-slate-700 text-white"
                      />
                    </div>
                    
                    <div>
                        <Label htmlFor="license-type" className="text-slate-300">License Type</Label>
                        <Select value={newRepoLicense} onValueChange={setNewRepoLicense}>
                            <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                                <SelectValue placeholder="Select a license" />
                            </SelectTrigger>
                            <SelectContent className="bg-slate-800 border-slate-700 text-white">
                                <SelectItem value="MIT" className="text-white hover:bg-slate-700">MIT</SelectItem>
                                <SelectItem value="Apache-2.0" className="text-white hover:bg-slate-700">Apache-2.0</SelectItem>
                                <SelectItem value="GPL-3.0" className="text-white hover:bg-slate-700">GPL-3.0</SelectItem>
                                <SelectItem value="BSD-3-Clause" className="text-white hover:bg-slate-700">BSD-3-Clause</SelectItem>
                                <SelectItem value="AGPL-3.0" className="text-white hover:bg-slate-700">AGPL-3.0</SelectItem>
                                <SelectItem value="Custom-AI" className="text-white hover:bg-slate-700">Custom-AI</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="flex justify-end space-x-2">
                      <Button variant="outline" onClick={() => setShowProtectModal(false)}>Cancel</Button>
                      <Button onClick={handleProtectRepo} disabled={isSubmitting || !newRepoUrl} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                        {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Verify & Register
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Total Repositories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{repositories.length}</div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-green-800/30 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Protected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                {repositories.filter(r => r.status === 'protected').length}
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900/50 border-red-800/30 backdrop-blur-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-300">Matches Found</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-400">
                {repositories.filter(r => r.status === 'match_found').length}
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="space-y-6">
             {isLoading && !repositories.length ? (
                <div className="text-center text-slate-400 py-12">
                    <Loader2 className="h-12 w-12 mx-auto animate-spin text-purple-400 mb-4"/>
                    <p>Loading repositories from the blockchain...</p>
                </div>
             ) : !account ? (
                <Card className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm">
                    <CardContent className="text-center py-12">
                        <Wallet className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-white mb-2">Connect Your Wallet</h3>
                        <p className="text-slate-400 mb-6">Connect your wallet to manage your protected repositories.</p>
                        <Button onClick={connectWallet} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                           <Wallet className="mr-2 h-4 w-4" /> Connect Wallet
                        </Button>
                    </CardContent>
                </Card>
            ) : filteredRepositories.length === 0 ? (
                <Card className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm">
                    <CardContent className="text-center py-12">
                        <Shield className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                         {searchQuery ? (
                            <>
                                <h3 className="text-lg font-medium text-white mb-2">No repositories found</h3>
                                <p className="text-slate-400 mb-6">No repositories match your search: "{searchQuery}".</p>
                                <Button onClick={() => setSearchQuery('')} variant="outline" className="border-purple-600/50 text-purple-400 hover:bg-purple-900/50">Clear Search</Button>
                            </>
                         ) : (
                            <>
                                <h3 className="text-lg font-medium text-white mb-2">No Repositories Protected</h3>
                                <p className="text-slate-400 mb-6">Start by protecting your first repository.</p>
                                <Button onClick={() => setShowProtectModal(true)} disabled={!isGitHubConnected} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50">
                                    <Plus className="mr-2 h-4 w-4" /> Protect First Repository
                                </Button>
                                {!isGitHubConnected && <p className="text-sm text-slate-500 mt-4">Connect your GitHub account to begin.</p>}
                            </>
                         )}
                    </CardContent>
                </Card>
            ) : (
              <div className="grid gap-6">
                {filteredRepositories.map((repo) => (
                  <Card key={String(repo.id)} className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm hover:border-purple-700/50 transition-colors">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <a 
                            href={`https://github.com/${repo.fullName}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-blue-400 transition-colors"
                          >
                            <Github className="h-5 w-5 text-slate-400 hover:text-blue-400" />
                          </a>
                          <div>
                            <CardTitle className="text-white">{repo.fullName}</CardTitle>
                            <CardDescription className="text-slate-400">
                              Registered on {new Date(repo.dateRegistered).toLocaleDateString()}
                            </CardDescription>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(repo.status)}
                          <Badge 
                            variant="outline" 
                            className={
                              repo.status === 'protected' ? 'border-green-500/50 text-green-400' :
                              'border-red-500/50 text-red-400'
                            }
                          >
                            {getStatusText(repo.status)}
                          </Badge>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <div className="grid md:grid-cols-2 gap-4 mb-4">
                        <div className="space-y-2">
                          {repo.nftId && (
                            <div className="flex items-center space-x-2 text-sm text-slate-400">
                              <Shield className="h-4 w-4" />
                              <span>Registration ID: {repo.nftId}</span>
                            </div>
                          )}
                        </div>
                        
                        {repo.matchesFound && repo.matchesFound > 0 && (
                          <div className="space-y-2">
                            <div className="text-sm text-red-400">
                              {repo.matchesFound} {repo.matchesFound === 1 ? 'match' : 'matches'} found in public datasets
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <Separator className="mb-4 bg-slate-700" />
                      
                      <div className="flex flex-wrap gap-2">
                        <Dialog open={showNFTModal && selectedRepo?.id === repo.id} onOpenChange={(open) => {
                          setShowNFTModal(open);
                          if (!open) setSelectedRepo(null);
                        }}>
                          <DialogTrigger asChild>
                            <Button variant="outline" size="sm" className="border-purple-600/50 text-purple-400 hover:bg-purple-900/50" onClick={() => setSelectedRepo(repo)}>
                              <Eye className="mr-1 h-3 w-3" /> View Details
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="bg-slate-900 border-purple-800/30">
                            <DialogHeader>
                              <DialogTitle className="text-white">Registration Details</DialogTitle>
                              <DialogDescription className="text-slate-300">
                                On-chain proof of registration for {repo.fullName}
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4 py-4">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="text-slate-400">Registration ID:</span>
                                  <div className="text-white font-mono">{repo.nftId}</div>
                                </div>
                                <div>
                                  <span className="text-slate-400">Repository Hash:</span>
                                  <div className="text-white font-mono break-all" title={repo.onChainData?.repoHash}>{repo.onChainData?.repoHash.slice(0, 12)}...</div>
                                </div>
                                <div>
                                  <span className="text-slate-400">Timestamp:</span>
                                  <div className="text-white">{new Date(repo.dateRegistered).toLocaleString()}</div>
                                </div>
                                <div>
                                  <span className="text-slate-400">License:</span>
                                  <div className="text-white font-mono">{repo.onChainData?.licenseType}</div>
                                </div>
                              </div>
                              <div className="flex space-x-2">
                                <Button asChild variant="outline" size="sm" className="border-purple-600/50 text-purple-400">
                                  <a href={`https://testnet.flowscan.org/contract/${CONTRACT_ADDRESS}`} target="_blank" rel="noopener noreferrer">
                                    <ExternalLink className="mr-1 h-3 w-3" /> Flowscan
                                  </a>
                                </Button>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                        
                        {repo.status === 'match_found' && (
                          <Dialog open={showMatchModal && selectedRepo?.id === repo.id} onOpenChange={(open) => {
                            setShowMatchModal(open);
                            if (!open) setSelectedRepo(null);
                          }}>
                            <DialogTrigger asChild>
                              <Button variant="outline" size="sm" className="border-red-600/50 text-red-400 hover:bg-red-900/50" onClick={() => setSelectedRepo(repo)}>
                                <Search className="mr-1 h-3 w-3" /> View Matches
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="bg-slate-900 border-purple-800/30 max-w-2xl">
                              <DialogHeader>
                                <DialogTitle className="text-white">Match Details for {repo.fullName}</DialogTitle>
                                <DialogDescription className="text-slate-300">
                                  Detected matches in public AI training datasets or other repositories.
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-4 py-4">
                                {repo.matches?.map((match, index) => (
                                  <div key={index} className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                                      <div>
                                        <span className="text-slate-400">Violating URL:</span>
                                        <a href={match.dataset} target="_blank" rel="noopener noreferrer" className="text-white font-medium break-all hover:text-purple-400">{match.dataset}</a>
                                      </div>
                                      <div>
                                        <span className="text-slate-400">Detected On:</span>
                                        <div className="text-white">{new Date(match.date).toLocaleString()}</div>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </DialogContent>
                          </Dialog>
                        )}
                        
                        {repo.status === 'match_found' && (
                          <Dialog open={showClaimModal && selectedRepo?.id === repo.id} onOpenChange={(open) => {
                            setShowClaimModal(open);
                            if (!open) setSelectedRepo(null);
                          }}>
                            <DialogTrigger asChild>
                              <Button size="sm" className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700" onClick={() => setSelectedRepo(repo)}>
                                <FileText className="mr-1 h-3 w-3" /> Submit Claim
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="bg-slate-900 border-purple-800/30">
                              <DialogHeader>
                                <DialogTitle className="text-white">Submit Claim</DialogTitle>
                                <DialogDescription className="text-slate-300">
                                  Submit a claim for unauthorized use of {repo.fullName}.
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4 py-4">
                                <div>
                                  <Label htmlFor="claim-type" className="text-slate-300">Claim Type</Label>
                                  <Select value={claimType} onValueChange={setClaimType}>
                                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white"><SelectValue placeholder="Select claim type" /></SelectTrigger>
                                    <SelectContent className="bg-slate-800 border-slate-700">
                                      <SelectItem value="opt-out" className="text-white">Opt-out Request</SelectItem>
                                      <SelectItem value="license" className="text-white">License Assertion</SelectItem>
                                      <SelectItem value="takedown" className="text-white">Takedown Notice (DMCA)</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div>
                                  <Label htmlFor="claim-reason" className="text-slate-300">Reason for Claim</Label>
                                  <Textarea id="claim-reason" placeholder="Describe the nature of the violation..." value={claimReason} onChange={(e) => setClaimReason(e.target.value)} className="bg-slate-800 border-slate-700 text-white" rows={4}/>
                                </div>
                                <div className="flex justify-end space-x-2">
                                  <Button variant="outline" onClick={() => setShowClaimModal(false)}>Cancel</Button>
                                  <Button onClick={handleSubmitClaim} className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700" disabled={!claimType || !claimReason.trim()}>
                                    Submit Claim
                                  </Button>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
        </div>
      </main>
    </div>
  );
}