// app/layout.tsx
import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { WalletProviders } from '@/components/providers/WalletProviders'; // Import the providers

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'DataShield - Protect Your Code from AI Training',
  description: 'Protect your GitHub repositories from unauthorized use in AI training datasets with blockchain-powered proof of authorship.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // Add `dark` className to enable your dark theme from globals.css
    // Add `suppressHydrationWarning` as recommended for wagmi/RainbowKit
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={inter.className}>
        {/* Wrap children with the WalletProviders component */}
        <WalletProviders>{children}</WalletProviders>
      </body>
    </html>
  );
}