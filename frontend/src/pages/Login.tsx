import { useState } from 'react';
import { Shield, Mail, Lock, User, AlertCircle, ArrowRight, CheckCircle } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../lib/api';

type Step = 'login' | 'signup' | 'otp';

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [step, setStep] = useState<Step>('login');

  // Shared form fields
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [toastOTP, setToastOTP] = useState('');

  const from = (location.state as any)?.from?.pathname || '/dashboard';

  /* ─── Helpers ─────────────────────────────────────────────────── */
  const clearMessages = () => { setError(''); setSuccessMsg(''); };

  /* ─── Login: step 1 ─── */
  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      if (res.data.requires_otp) {
        // Extract OTP from the message (dev-mode)
        const match = (res.data.message as string).match(/OTP:\s*(\d{6})/);
        if (match) setToastOTP(match[1]);
        setStep('otp');
      } else {
        sessionStorage.setItem('astra_token', res.data.access_token);
        navigate(from, { replace: true });
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  /* ─── Login: OTP step ─── */
  const handleOTPSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);
    try {
      const res = await api.post('/auth/verify-otp', { username, otp });
      sessionStorage.setItem('astra_token', res.data.access_token);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid or expired OTP.');
    } finally {
      setLoading(false);
    }
  };

  /* ─── Sign Up ─── */
  const handleSignupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);
    try {
      await api.post('/auth/register', {
        username,
        email,
        password,
        role: 'officer',
      });
      // Keep username + password in state so they can log straight in
      setSuccessMsg('Account created! Click "Login" to continue.');
      setStep('login');
      setEmail('');          // email not needed for login form
      // username and password already set - user just hits Login
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Try a different username or email.');
    } finally {
      setLoading(false);
    }
  };

  /* ─── Shared input classes ─── */
  const inputBase =
    'block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-shadow';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center p-4">

      {/* OTP Toast */}
      {toastOTP && (
        <div className="fixed top-4 right-4 z-50 bg-white border border-indigo-100 rounded-xl shadow-2xl p-4 max-w-xs flex items-start gap-3 animate-pulse">
          <Mail className="h-6 w-6 text-indigo-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-slate-900">Email Received</p>
            <p className="text-sm text-slate-500 mt-0.5">
              Your verification code is:{' '}
              <span className="font-bold tracking-widest text-indigo-600">{toastOTP}</span>
            </p>
            <p className="text-xs text-slate-400 mt-1 italic">Development mode — no actual email sent</p>
          </div>
          <button onClick={() => setToastOTP('')} className="text-slate-300 hover:text-slate-500 ml-auto">✕</button>
        </div>
      )}

      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-indigo-600 shadow-lg mb-4">
            <Shield className="h-9 w-9 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">ASTRA</h1>
          <p className="text-indigo-300 mt-1 text-sm">Advanced System for Traffic &amp; Resource Analytics</p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">

          {/* ── OTP STEP ─────────────────────────────────── */}
          {step === 'otp' && (
            <div className="p-8 space-y-6">
              <div className="text-center">
                <div className="mx-auto h-12 w-12 rounded-full bg-indigo-50 flex items-center justify-center mb-3">
                  <Mail className="h-6 w-6 text-indigo-600" />
                </div>
                <h2 className="text-xl font-bold text-slate-900">Verify Your Identity</h2>
                <p className="text-sm text-slate-500 mt-1">
                  Enter the 6-digit code shown in the notification.
                </p>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-100 text-red-600 text-sm p-3 rounded-lg flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 flex-shrink-0" /> {error}
                </div>
              )}

              <form onSubmit={handleOTPSubmit} className="space-y-4">
                <input
                  type="text"
                  required
                  maxLength={6}
                  inputMode="numeric"
                  value={otp}
                  onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
                  className="block w-full px-4 py-4 text-center text-3xl font-bold tracking-[0.6em] border-2 border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"
                  placeholder="------"
                />
                <button
                  type="submit"
                  disabled={loading || otp.length !== 6}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {loading ? 'Verifying…' : 'Verify & Enter Dashboard'}
                  {!loading && <ArrowRight className="h-4 w-4" />}
                </button>
                <button type="button" onClick={() => { setStep('login'); clearMessages(); }} className="w-full text-sm text-slate-500 hover:text-slate-700 text-center">
                  ← Back to Login
                </button>
              </form>
            </div>
          )}

          {/* ── LOGIN / SIGN-UP STEP ─────────────────────── */}
          {step !== 'otp' && (
            <>
              {/* Tab bar */}
              <div className="flex border-b border-slate-200">
                {(['login', 'signup'] as Step[]).map(tab => (
                  <button
                    key={tab}
                    onClick={() => { setStep(tab); clearMessages(); }}
                    className={`flex-1 py-4 text-sm font-semibold capitalize transition-colors ${
                      step === tab
                        ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white'
                        : 'text-slate-500 hover:text-slate-700 bg-slate-50'
                    }`}
                  >
                    {tab === 'login' ? 'Login' : 'New User?'}
                  </button>
                ))}
              </div>

              <div className="p-8 space-y-5">
                {error && (
                  <div className="bg-red-50 border border-red-100 text-red-600 text-sm p-3 rounded-lg flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" /> {error}
                  </div>
                )}
                {successMsg && (
                  <div className="bg-green-50 border border-green-100 text-green-700 text-sm p-3 rounded-lg flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 flex-shrink-0" /> {successMsg}
                  </div>
                )}

                <form onSubmit={step === 'login' ? handleLoginSubmit : handleSignupSubmit} className="space-y-4">
                  {/* Username */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">Username</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <input
                        id="username"
                        type="text"
                        required
                        autoComplete="username"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                        className={inputBase}
                        placeholder="Enter your username"
                      />
                    </div>
                  </div>

                  {/* Email — only on Sign Up */}
                  {step === 'signup' && (
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">Email Address</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <input
                          id="email"
                          type="email"
                          required
                          autoComplete="email"
                          value={email}
                          onChange={e => setEmail(e.target.value)}
                          className={inputBase}
                          placeholder="john@police.gov.in"
                        />
                      </div>
                    </div>
                  )}

                  {/* Password */}
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <input
                        id="password"
                        type="password"
                        required
                        minLength={8}
                        autoComplete={step === 'login' ? 'current-password' : 'new-password'}
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        className={inputBase}
                        placeholder="••••••••"
                      />
                    </div>
                    {step === 'signup' && (
                      <p className="mt-1 text-xs text-slate-400">Minimum 8 characters</p>
                    )}
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 transition-colors shadow-md"
                  >
                    {loading
                      ? 'Processing…'
                      : step === 'login' ? 'Login' : 'Create Account'}
                    {!loading && <ArrowRight className="h-4 w-4" />}
                  </button>
                </form>
              </div>
            </>
          )}
        </div>

        <p className="text-center text-xs text-indigo-400 mt-6">
          ASTRA · Bengaluru Traffic Command System
        </p>
      </div>
    </div>
  );
}
