// components/providers/WalletProviders.tsx
'use client';

import '@rainbow-me/rainbowkit/styles.css';
import { RainbowKitProvider } from '@rainbow-me/rainbowkit';
import { WagmiConfig } from 'wagmi';
import { wagmiConfig } from '@/lib/walletConfig';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Create a TanStack Query client
const queryClient = new QueryClient();

export function WalletProviders({ children }: { children: React.ReactNode }) {
  return (
    <WagmiConfig config={wagmiConfig}>
      {/* Wagmi v2 requires a QueryClientProvider wrapper */}
      <QueryClientProvider client={queryClient}>
        {/* The 'chains' prop is no longer passed here */}
        <RainbowKitProvider modalSize="compact">{children}</RainbowKitProvider>
      </QueryClientProvider>
    </WagmiConfig>
  );
}