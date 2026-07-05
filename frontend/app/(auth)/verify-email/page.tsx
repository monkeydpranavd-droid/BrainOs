"use client";

import React, { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Mail, CheckCircle2, ArrowRight, Loader2 } from "lucide-react";

function VerifyEmailForm() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "your email";

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 relative overflow-hidden px-4">
      {/* Background gradients */}
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-violet-900/20 blur-[120px] pointer-events-none" />

      <div className="w-full max-w-md bg-slate-900/60 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl p-8 z-10 text-center">
        <div className="flex flex-col items-center mb-6">
          <div className="h-14 w-14 bg-indigo-950/60 border border-indigo-900/40 rounded-full flex items-center justify-center mb-4">
            <Mail className="h-6 w-6 text-indigo-400 animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Confirm your email
          </h1>
          <p className="text-slate-400 text-sm mt-2 max-w-sm">
            We have sent verification instructions to <strong className="text-slate-200">{email}</strong>.
          </p>
        </div>

        <div className="p-4 bg-indigo-950/20 border border-indigo-900/30 rounded-xl text-left mb-8">
          <div className="flex gap-3 mb-2.5">
            <CheckCircle2 className="h-5 w-5 text-indigo-400 shrink-0" />
            <p className="text-xs text-slate-350 leading-relaxed">
              Check spam or junk folders if you do not receive it within a few minutes.
            </p>
          </div>
          <div className="flex gap-3">
            <CheckCircle2 className="h-5 w-5 text-indigo-400 shrink-0" />
            <p className="text-xs text-slate-350 leading-relaxed">
              Click the link inside the email message to finalize activating your profile.
            </p>
          </div>
        </div>

        <Link
          href="/login"
          className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25 transition-all text-sm cursor-pointer"
        >
          Return to Log In
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
      </div>
    }>
      <VerifyEmailForm />
    </Suspense>
  );
}
