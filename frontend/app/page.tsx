'use client';

import { useState, useEffect } from 'react';
import { Shield, Github, Lock, FileText, Globe, Zap, Users, Code2, Database, Wallet, Fingerprint, Bot, Scan, Twitter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import Image from 'next/image';
import * as fcl from '@onflow/fcl';

// FCL config should ideally be in a central file like _app.tsx or flow/config.ts
fcl.config()
  .put("accessNode.api", "https://rest-testnet.onflow.org")
  .put("discovery.wallet", "https://fcl-discovery.onflow.org/testnet/authn")
  .put("app.detail.title", "DataShield")
  .put("app.detail.icon", "https://datashield-frontend.vercel.app/favicon.ico"); // Replace with your deployed icon URL

// Define a type for the user object
interface FlowUser {
  loggedIn: boolean;
  addr?: string;
}

export default function HomePage() {
  const [user, setUser] = useState<FlowUser>({ loggedIn: false });

  // Subscribe to FCL's currentUser
  useEffect(() => {
    fcl.currentUser.subscribe(setUser);
  }, []);

  const handleConnectWallet = () => {
    fcl.authenticate();
  };

  const handleDisconnectWallet = () => {
    fcl.unauthenticate();
  };
  
  // Utility to truncate wallet address
  const truncateAddress = (address: string | undefined) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Animated background pattern */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-purple-500/10 animate-pulse"></div>
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-bounce"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-pink-500/5 rounded-full blur-3xl animate-bounce" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-purple-800/20 bg-slate-950/80 backdrop-blur-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-purple-400" />
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                DataShield
              </span>
            </div>
            <div className="flex items-center space-x-4">
              {user.loggedIn ? (
                <div className="flex items-center space-x-3">
                  <Badge variant="outline" className="border-green-500/50 text-green-400 font-mono">
                    {truncateAddress(user.addr)}
                  </Badge>
                  <Link href="/dashboard">
                    <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                      Dashboard
                    </Button>
                  </Link>
                   <Button onClick={handleDisconnectWallet} variant="destructive" size="sm">
                    Disconnect
                  </Button>
                </div>
              ) : (
                <Button 
                  onClick={handleConnectWallet}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                >
                  <Wallet className="mr-2 h-4 w-4" />
                  Connect Flow Wallet
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 py-32 lg:py-48">
        <div className="container mx-auto px-6 text-center">
          <Badge className="mb-6 bg-purple-900/50 border-purple-700/50 text-purple-300">
            Protect Your GitHub Data
          </Badge>
          <h1 className="text-4xl lg:text-7xl font-bold mb-6 leading-tight" style={{ color: '#d946ef' }}>
            DataShield
          </h1>
          <p className="text-xl lg:text-2xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            Protect your GitHub code from unauthorized AI training
          </p>
          <div className="flex justify-center">
            {user.loggedIn ? (
              <Link href="/dashboard">
                <Button 
                  size="lg" 
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-3 text-lg"
                >
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <Button 
                size="lg" 
                onClick={handleConnectWallet}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-3 text-lg"
              >
                <Wallet className="mr-2 h-5 w-5" />
                Connect Flow Wallet to Start
              </Button>
            )}
          </div>
        </div>
      </section>

       {/* What's Happening to Your Code */}
       <section className="relative z-10 py-20 bg-slate-950/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4 text-white">What's Happening to Your Code</h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Your GitHub repositories are being scraped and used to train AI models without your consent
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <Card className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm">
              <CardHeader>
                <Database className="h-12 w-12 text-purple-400 mb-2" />
                <CardTitle className="text-white">The Stack</CardTitle>
                <CardDescription className="text-slate-300">
                  6TB of permissively licensed code from GitHub
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm">
              <CardHeader>
                <FileText className="h-12 w-12 text-pink-400 mb-2" />
                <CardTitle className="text-white">The Pile</CardTitle>
                <CardDescription className="text-slate-300">
                  800GB of diverse text data including code repositories
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="bg-slate-900/50 border-purple-800/30 backdrop-blur-sm">
              <CardHeader>
                <Code2 className="h-12 w-12 text-purple-400 mb-2" />
                <CardTitle className="text-white">CodeParrot</CardTitle>
                <CardDescription className="text-slate-300">
                  Code datasets used to train AI coding assistants
                </CardDescription>
              </CardHeader>
            </Card>
          </div>

          <div className="text-center">
            <div className="bg-gradient-to-r from-red-900/20 to-orange-900/20 border border-red-800/30 rounded-lg p-6 max-w-2xl mx-auto">
              <Lock className="h-8 w-8 text-red-400 mx-auto mb-2" />
              <p className="text-red-200 font-medium">
                Developers deserve the right to opt out or control how their code is used
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4 text-white">How It Works</h2>
            <p className="text-xl text-slate-300">Automated protection with decentralized proof of authorship</p>
          </div>
          
          <div className="grid md:grid-cols-5 gap-6">
            {[
              { 
                icon: Wallet, 
                title: "Connect", 
                desc: "Link your Flow wallet and GitHub account"
              },
              { 
                icon: Github, 
                title: "Register Repo", 
                desc: "Submit your GitHub repo URL"
              },
              { 
                icon: Fingerprint, 
                title: "Mint Proof", 
                desc: "Generate a Flow NFT proving authorship"
              },
              { 
                icon: Bot, 
                title: "AI Monitoring", 
                desc: "Automated scanning of public datasets"
              },
              { 
                icon: FileText, 
                title: "Submit Claim", 
                desc: "File opt-out or license assertion"
              }
            ].map((step, index) => (
              <div key={index} className="text-center">
                <div className="relative mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <step.icon className="h-8 w-8 text-white" />
                  </div>
                  {index < 4 && (
                    <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-purple-600 to-pink-600"></div>
                  )}
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-slate-300">{step.desc}</p>
              </div>
            ))}
          </div>

          {/* Privacy & Decentralization Highlights */}
          <div className="mt-16 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="text-center p-6 bg-slate-900/30 rounded-lg border border-purple-800/20">
              <Shield className="h-8 w-8 text-green-400 mx-auto mb-3" />
              <h4 className="text-white font-semibold mb-2">Privacy First</h4>
              <p className="text-sm text-slate-400">Only hashed fingerprints are stored — your source code never leaves your control</p>
            </div>
            <div className="text-center p-6 bg-slate-900/30 rounded-lg border border-purple-800/20">
              <Zap className="h-8 w-8 text-purple-400 mx-auto mb-3" />
              <h4 className="text-white font-semibold mb-2">Automated</h4>
              <p className="text-sm text-slate-400">AI agents do the monitoring work so you don't have to manually check datasets</p>
            </div>
            <div className="text-center p-6 bg-slate-900/30 rounded-lg border border-purple-800/20">
              <Database className="h-8 w-8 text-pink-400 mx-auto mb-3" />
              <h4 className="text-white font-semibold mb-2">Tamper-Proof</h4>
              <p className="text-sm text-slate-400">Flow provides authorship identity, IPFS ensures decentralized claim storage</p>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="relative z-10 py-20 bg-slate-950/50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4 text-white">Technology Stack</h2>
            <p className="text-xl text-slate-300">Built on cutting-edge blockchain and decentralized storage</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <Card className="bg-slate-900/70 border-purple-600/40 backdrop-blur-sm hover:border-purple-500/60 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 mb-4 flex items-center justify-center">
                  <Image 
                    src="/flow_logo-removebg-preview.png" 
                    alt="Flow Logo" 
                    width={48} 
                    height={48}
                    className="object-contain"
                  />
                </div>
                <CardTitle className="text-2xl text-white">Flow Blockchain</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-slate-200">
                  <li>• Secure identity management</li>
                  <li>• Smart contract automation</li>
                  <li>• NFT proof of authorship</li>
                  <li>• Low transaction costs</li>
                </ul>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-900/70 border-pink-600/40 backdrop-blur-sm hover:border-pink-500/60 transition-colors">
              <CardHeader>
                <div className="w-12 h-12 mb-4 flex items-center justify-center">
                  <Image 
                    src="/ipfs-logo-icon-b.png" 
                    alt="IPFS Logo" 
                    width={48} 
                    height={48}
                    className="object-contain"
                  />
                </div>
                <CardTitle className="text-2xl text-white">IPFS Storage</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-slate-200">
                  <li>• Tamper-proof claim storage</li>
                  <li>• Decentralized data hosting</li>
                  <li>• Permanent record keeping</li>
                  <li>• Global accessibility</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="relative z-10 py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4 text-white">Community Impact</h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                12,847
              </div>
              <p className="text-lg text-slate-300">Protected Repositories</p>
            </div>
            
            <div className="text-center">
              <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                3,429
              </div>
              <p className="text-lg text-slate-300">Claims Submitted</p>
            </div>
            
            <div className="text-center">
              <div className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                8,756
              </div>
              <p className="text-lg text-slate-300">NFTs Minted</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-purple-800/20 bg-slate-950/80 backdrop-blur-md py-12">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Shield className="h-6 w-6 text-purple-400" />
              <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                DataShield
              </span>
            </div>
            
            <div className="flex items-center space-x-6">
              <a 
                href="#" 
                className="text-slate-400 hover:text-purple-400 transition-colors"
                aria-label="Follow us on Twitter"
              >
                <Twitter className="h-6 w-6" />
              </a>
              <a 
                href="#" 
                className="text-slate-400 hover:text-purple-400 transition-colors"
                aria-label="View our GitHub repository"
              >
                <Github className="h-6 w-6" />
              </a>
            </div>
          </div>
          
          <div className="border-t border-purple-800/20 mt-8 pt-8 text-center text-slate-400">
            <p>&copy; 2025 DataShield. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}