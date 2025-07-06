'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import * as fcl from "@onflow/fcl";

// FCL config at app init — ideally move to `_app.tsx` or a `flowConfig.ts`
fcl.config()
  .put("accessNode.api", "https://rest-testnet.onflow.org") // testnet endpoint
  .put("discovery.wallet", "https://fcl-discovery.onflow.org/testnet/authn") // testnet wallet discovery

// Define a type for the FCL user object to avoid implicit 'any'
interface FlowUser {
  addr?: string;
  loggedIn?: boolean;
}

export default function ReportPage() {
  const { register, handleSubmit, reset } = useForm();

  const [account, setAccount] = useState<FlowUser | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Apply the FlowUser type to the user parameter
    fcl.currentUser().subscribe((user: FlowUser) => {
      if (user?.addr) {
        setAccount({ addr: user.addr });
      } else {
        setAccount(null);
      }
    });
  }, []);

  const connectWallet = () => {
    fcl.authenticate();
  };

  const disconnectWallet = () => {
    fcl.unauthenticate();
  };

  const onSubmit = async (data: any) => {
    if (!account) {
      toast.error("Please connect your Flow wallet first");
      return;
    }

    setIsLoading(true);
    try {
      // send to backend
      const res = await fetch("http://0.0.0.0:8000/register-link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: data.url,
          suggested_dmca: data.dmca,
        }),
      });
      if (!res.ok) throw new Error("Backend error");

      toast.success("Submitted to backend");

      // TODO: send transaction on-chain here via FCL
      const txId = await fcl.mutate({
        cadence: `
          transaction(url: String, licenseCID: String, dmcaCID: String) {
            prepare(acct: AuthAccount) {
              log("Transaction prepared for:")
              log(acct.address)
              log("URL: " + url)
              log("License CID: " + licenseCID)
              log("DMCA CID: " + dmcaCID)
            }
          }
        `,
        args: (arg, t) => [
          arg(data.url, t.String),
          arg(data.licenseCid, t.String),
          arg(data.dmca, t.String),
        ],
        proposer: fcl.authz,
        payer: fcl.authz,
        authorizations: [fcl.authz],
        limit: 999,
      });

      toast.info("Transaction submitted: " + txId);
      await fcl.tx(txId).onceSealed();
      toast.success("Transaction sealed!");

      reset();
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Failed to submit transaction.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    // This parent div ensures the page has a dark background consistent with the theme
    <div className="min-h-screen w-full bg-slate-950 text-slate-100">
      <div className="container mx-auto max-w-2xl px-4 py-12 md:py-24">
        <h1 className="text-3xl lg:text-4xl font-bold mb-8 text-center bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Report Infringement
        </h1>

        <div className="w-full mx-auto space-y-6">
           {/* Wallet Connection Status */}
          {!account ? (
             <div className="text-center">
                <Button onClick={connectWallet} className="mb-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                  Connect Flow Wallet to Proceed
                </Button>
             </div>
          ) : (
            <div className="mb-4 p-4 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <p className="text-sm text-slate-300">
                Connected as: <span className="font-mono text-green-400">{account.addr}</span>
              </p>
              <Button
                onClick={disconnectWallet}
                variant="destructive"
                size="sm"
              >
                Disconnect
              </Button>
            </div>
          )}

          {/* Form */}
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-6 bg-slate-900/80 p-6 md:p-8 rounded-lg border border-purple-800/30 backdrop-blur-sm"
          >
            <div>
              <Label htmlFor='url' className="text-slate-300">Repository URL</Label>
              <Input
                id='url'
                {...register("url", { required: true })}
                placeholder="https://github.com/user/repo"
                className="bg-slate-800 border-slate-700 mt-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <Label htmlFor='licenseCid' className="text-slate-300">License CID (IPFS)</Label>
              <Input
                id='licenseCid'
                {...register("licenseCid", { required: true })}
                placeholder="Qm..."
                className="bg-slate-800 border-slate-700 mt-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <Label htmlFor='dmca' className="text-slate-300">Suggested DMCA CID (IPFS)</Label>
              <Input
                id='dmca'
                {...register("dmca", { required: true })}
                placeholder="Qm..."
                className="bg-slate-800 border-slate-700 mt-2 focus:ring-purple-500"
              />
            </div>

            <Button
              type="submit"
              className="w-full !mt-8 text-lg py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
              disabled={!account || isLoading}
            >
              {isLoading ? "Submitting..." : "Submit Infringement"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}