// lib/walletConfig.ts
'use client';

import * as fcl from '@onflow/fcl';
import { connectorsForWallets } from '@rainbow-me/rainbowkit';
import {
  injectedWallet,
  metaMaskWallet,
  walletConnectWallet,
} from '@rainbow-me/rainbowkit/wallets';
import { flowWallet } from '@onflow/fcl-rainbowkit-adapter';
// Wagmi v2 imports
import { createConfig, http } from 'wagmi';
import { mainnet, polygon, optimism, arbitrum } from 'wagmi/chains';

// --- FCL Configuration ---
const walletConnectProjectId = '9b70cfa398b2355a5eb9b1cf99f4a981'; // Replace with your actual Project ID

fcl.config({
  'accessNode.api': 'https://rest-testnet.onflow.org',
  'discovery.wallet': 'https://fcl-discovery.onflow.org/testnet/authn',
  'app.detail.title': 'DataShield',
  'app.detail.icon': 'https://datashield-frontend.vercel.app/favicon.ico',
  'walletconnect.projectId': walletConnectProjectId,
});

// --- Wagmi and RainbowKit Configuration (for v2) ---

const chains = [mainnet, polygon, optimism, arbitrum] as const;

// Create connectors
const connectors = connectorsForWallets(
  [
    {
      groupName: 'Recommended',
      wallets: [
        flowWallet(), // This adapter is designed to be called directly.

        // FIX: Pass the function reference, NOT the result of calling the function.
        // RainbowKit will use the projectId from the appInfo object below.
        metaMaskWallet,
        walletConnectWallet,
        injectedWallet,
      ],
    },
  ],
  {
    appName: 'DataShield',
    projectId: walletConnectProjectId,
  }
);

// Create Wagmi config
export const wagmiConfig = createConfig({
  chains,
  connectors,
  transports: {
    [mainnet.id]: http(),
    [polygon.id]: http(),
    [optimism.id]: http(),
    [arbitrum.id]: http(),
  },
  ssr: true,
});