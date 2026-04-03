import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getDashboardRouteForRole, ROLE_OPTIONS } from '../utils/auth';
import api from '../services/api';

const STEPS = { FORM: 'form', OTP: 'otp', DONE: 'done' };

export default function SignupPage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  const [step, setStep] = useState(STEPS.FORM);
  const [role, setRole] = useState('patient');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [phone, setPhone] = useState('');
  const [otpChannel, setOtpChannel] = useState('whatsapp');
  const [lastDeliveredChannel, setLastDeliveredChannel] = useState('whatsapp');
  const [lastDeliveryMessage, setLastDeliveryMessage] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const stepLabel = useMemo(() => {
    if (step === STEPS.FORM) return 'Create Your Account';
    if (step === STEPS.OTP) return 'Verify Phone Number';
    return 'Account Created!';
  }, [step]);

  const stepNumber = step === STEPS.FORM ? 1 : step === STEPS.OTP ? 2 : 3;

  const channelLabel = otpChannel === 'whatsapp' ? 'WhatsApp' : 'SMS';

  useEffect(() => {
    if (!isAuthenticated || !user?.role) return;
    navigate(getDashboardRouteForRole(user.role), { replace: true });
  }, [isAuthenticated, navigate, user]);

  const handleChannelChange = (channel) => {
    setOtpChannel(channel);
    setError('');
    setInfo('');
  };

  const sendOtpForCurrentNumber = useCallback(async () => {
    const otpResult = await api.sendOtp(phone.trim(), otpChannel);
    const deliveredChannel = otpResult.channel || otpChannel;
    setLastDeliveredChannel(deliveredChannel);
    setLastDeliveryMessage(otpResult.message || '');

    if (otpResult.demo_mode) {
      setInfo(`Demo mode active: use OTP code 123456 via ${deliveredChannel === 'sms' ? 'SMS' : 'WhatsApp'}.`);
    } else {
      setInfo(`Verification code sent via ${deliveredChannel === 'sms' ? 'SMS' : 'WhatsApp'} to ${phone.trim()}.`);
    }

    return otpResult;
  }, [phone, otpChannel]);

  const handleSignup = useCallback(async (event) => {
    event.preventDefault();
    setError('');
    setInfo('');

    if (!name.trim() || !email.trim() || !password || !phone.trim()) {
      setError('All fields are required');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (!/^\+\d{10,15}$/.test(phone.trim())) {
      setError('Phone must be in E.164 format (e.g. +919876543210)');
      return;
    }

    setIsSubmitting(true);
    try {
      const signupResult = await api.signup({
        role,
        name: name.trim(),
        email: email.trim(),
        password,
        phone: phone.trim(),
      });

      setStep(STEPS.OTP);
      setInfo(signupResult?.message || 'Account created successfully. Sending OTP now.');

      try {
        await sendOtpForCurrentNumber();
      } catch (sendErr) {
        setError(sendErr.message || 'Account created, but OTP could not be sent yet. You can resend from this screen.');
        setInfo('');
      }
    } catch (err) {
      setError(err.message || 'Signup failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }, [role, name, email, password, phone, sendOtpForCurrentNumber]);

  const handleVerifyOtp = useCallback(async (event) => {
    event.preventDefault();
    setError('');
    setInfo('');

    if (!otp || otp.length < 4) {
      setError('Please enter the OTP code');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await api.verifyOtp(phone.trim(), otp);
      if (result.verified) {
        setStep(STEPS.DONE);
        setTimeout(() => navigate('/login'), 2500);
      } else {
        setError('Invalid OTP. Please try again.');
      }
    } catch (err) {
      setError(err.message || 'Verification failed');
    } finally {
      setIsSubmitting(false);
    }
  }, [otp, phone, navigate]);

  const handleResendOtp = useCallback(async () => {
    setError('');
    setInfo('');
    setIsSubmitting(true);
    try {
      await sendOtpForCurrentNumber();
    } catch (err) {
      setError(err.message || 'Failed to resend OTP');
    } finally {
      setIsSubmitting(false);
    }
  }, [sendOtpForCurrentNumber]);

  const signupHighlights = [
    {
      label: 'Role aware onboarding',
      value: 'Each account is tagged to a specific dashboard from the start.',
    },
    {
      label: 'OTP channels',
      value: 'Use WhatsApp or SMS depending on the delivery path that works best.',
    },
    {
      label: 'Verification status',
      value: 'Live delivery feedback tells you whether the OTP was actually sent.',
    },
  ];

  return (
    <div className="min-h-screen bg-[#06101d] text-white relative overflow-hidden px-4 py-8 sm:px-6 lg:px-8 flex items-center">
      <div className="absolute -top-28 -right-20 w-72 h-72 bg-teal-400/10 rounded-full blur-[100px]" />
      <div className="absolute -bottom-32 -left-20 w-80 h-80 bg-cyan-400/10 rounded-full blur-[120px]" />
      <div className="absolute inset-0 opacity-[0.08] bg-[radial-gradient(circle_at_top_left,white,transparent_28%),radial-gradient(circle_at_bottom_right,rgba(45,212,191,0.8),transparent_34%)]" />

      <div className="relative z-10 w-full max-w-6xl mx-auto grid gap-6 lg:grid-cols-[1.05fr_0.95fr] items-center">
        <section className="hidden lg:flex flex-col gap-6 pr-4 xl:pr-10">
          <div className="inline-flex w-fit items-center gap-2 rounded-full border border-teal-300/20 bg-teal-300/10 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-teal-100">
            Secure Signup
          </div>
          <div className="space-y-4">
            <h1 className="text-4xl xl:text-5xl font-headline font-black leading-tight">
              Create a verified account with a cleaner, more guided flow.
            </h1>
            <p className="max-w-xl text-base text-slate-300 leading-7">
              Register once, verify your phone number, and move into the correct SwasthaLink workspace. The screen keeps OTP delivery status visible so SMS and WhatsApp are easy to audit.
            </p>
          </div>

          <div className="grid gap-3">
            {signupHighlights.map((item) => (
              <div key={item.label} className="glass-card rounded-2xl border border-white/10 p-4">
                <p className="text-sm font-semibold text-white">{item.label}</p>
                <p className="mt-1 text-sm leading-6 text-slate-300">{item.value}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-card rounded-[32px] border border-white/10 p-6 sm:p-8 shadow-[0_24px_80px_rgba(2,8,23,0.45)]">
          <div className="mb-6">
            <p className="text-[11px] uppercase tracking-[0.24em] text-teal-200">Role-Based Access</p>
            <h2 className="text-3xl font-headline font-extrabold mt-2">SwasthaLink Signup</h2>
            <p className="text-sm text-slate-300 mt-2 leading-6">{stepLabel}</p>
          </div>

          <div className="flex items-center gap-0 mb-6">
            {[1, 2, 3].map((n) => (
              <div key={n} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-300 ${
                    n < stepNumber
                      ? 'bg-emerald-500/20 border-emerald-400/50 text-emerald-300'
                      : n === stepNumber
                        ? 'bg-gradient-to-r from-teal-300 to-cyan-400 border-teal-300/50 text-[#053438] shadow-[0_0_16px_rgba(45,212,191,0.4)]'
                        : 'bg-white/5 border-white/15 text-slate-500'
                  }`}
                >
                  {n < stepNumber ? '✓' : n}
                </div>
                {n < 3 && (
                  <div className={`w-10 h-0.5 ${n < stepNumber ? 'bg-emerald-400/40' : 'bg-white/10'}`} />
                )}
              </div>
            ))}
          </div>

          {error ? (
            <div className="rounded-2xl border border-rose-300/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100 mb-4">
              {error}
            </div>
          ) : null}

          {info ? (
            <div className="rounded-2xl border border-teal-300/30 bg-teal-500/10 px-4 py-3 text-sm text-teal-100 mb-4">
              {info}
            </div>
          ) : null}

          {step === STEPS.FORM && (
            <form onSubmit={handleSignup} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">Role</label>
                <select
                  value={role}
                  onChange={(event) => setRole(event.target.value)}
                  className="w-full rounded-2xl bg-[#0f2334] border border-white/15 px-4 py-3 text-sm text-white shadow-inner shadow-black/10 focus:outline-none focus:ring-2 focus:ring-teal-300/40"
                >
                  {ROLE_OPTIONS.map((item) => (
                    <option key={item.value} value={item.value} className="bg-[#0f2334] text-white">
                      {item.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">Full Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Enter your full name"
                  className="w-full rounded-2xl bg-[#0f2334] border border-white/15 px-4 py-3 text-sm text-white placeholder:text-slate-500 shadow-inner shadow-black/10 focus:outline-none focus:ring-2 focus:ring-teal-300/40"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">Email ID</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="name@hospital.com"
                  className="w-full rounded-2xl bg-[#0f2334] border border-white/15 px-4 py-3 text-sm text-white placeholder:text-slate-500 shadow-inner shadow-black/10 focus:outline-none focus:ring-2 focus:ring-teal-300/40"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    minLength={6}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Minimum 6 characters"
                    className="w-full rounded-2xl bg-[#0f2334] border border-white/15 px-4 py-3 pr-16 text-sm text-white placeholder:text-slate-500 shadow-inner shadow-black/10 focus:outline-none focus:ring-2 focus:ring-teal-300/40"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                    className="absolute inset-y-0 right-0 px-4 text-xs font-semibold uppercase tracking-[0.18em] text-teal-200 hover:text-teal-100 transition-colors"
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">WhatsApp Phone</label>
                <input
                  type="tel"
                  required
                  value={phone}
                  onChange={(event) => setPhone(event.target.value)}
                  placeholder="+919876543210"
                  className="w-full rounded-2xl bg-[#0f2334] border border-white/15 px-4 py-3 text-sm text-white placeholder:text-slate-500 shadow-inner shadow-black/10 focus:outline-none focus:ring-2 focus:ring-teal-300/40"
                />
                <p className="text-[11px] text-slate-500">
                  E.164 format with country code (example: +91 for India)
                </p>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">OTP Channel</label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'whatsapp', icon: 'Chat', label: 'WhatsApp' },
                    { value: 'sms', icon: 'SMS', label: 'SMS' },
                  ].map((channel) => (
                    <label
                      key={channel.value}
                      className={`flex items-center gap-3 px-4 py-3 rounded-2xl border cursor-pointer transition-all text-sm ${
                        otpChannel === channel.value
                          ? 'bg-teal-300/10 border-teal-300/40 text-teal-100'
                          : 'bg-white/[0.03] border-white/10 text-slate-300 hover:bg-white/[0.06]'
                      }`}
                    >
                      <input
                        type="radio"
                        value={channel.value}
                        checked={otpChannel === channel.value}
                        onChange={() => handleChannelChange(channel.value)}
                        className="hidden"
                      />
                      <span className="text-xs font-bold uppercase tracking-[0.2em] opacity-80">{channel.icon}</span>
                      <span>{channel.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300 text-[#053438] font-extrabold tracking-wide hover:shadow-[0_16px_30px_rgba(45,212,191,0.35)] transition-all disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Creating Account...' : 'Sign Up & Send OTP'}
              </button>
            </form>
          )}

          {step === STEPS.OTP && (
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-300 leading-6">
                We sent a verification code to <span className="text-white font-semibold">{phone}</span> via{' '}
                <span className="text-teal-200 font-semibold">{lastDeliveredChannel === 'sms' ? 'SMS' : 'WhatsApp'}</span>.
              </div>

              {lastDeliveryMessage ? (
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-xs leading-6 text-slate-400">
                  {lastDeliveryMessage}
                </div>
              ) : null}

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">Choose Delivery Channel</label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'whatsapp', label: 'WhatsApp' },
                    { value: 'sms', label: 'SMS' },
                  ].map((channel) => (
                    <button
                      key={channel.value}
                      type="button"
                      onClick={() => handleChannelChange(channel.value)}
                      className={`rounded-2xl border px-4 py-3 text-sm font-medium transition-all ${
                        otpChannel === channel.value
                          ? 'bg-teal-300/10 border-teal-300/40 text-teal-100'
                          : 'bg-white/[0.03] border-white/10 text-slate-300 hover:bg-white/[0.06]'
                      }`}
                    >
                      {channel.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300 uppercase tracking-[0.16em]">Enter OTP Code</label>
                <input
                  type="text"
                  value={otp}
                  onChange={(event) => {
                    setOtp(event.target.value.replace(/\D/g, '').slice(0, 6));
                    setError('');
                  }}
                  placeholder="• • • • • •"
                  maxLength={6}
                  autoFocus
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  className="w-full rounded-2xl bg-[#0f2334] border border-white/15 px-4 py-4 text-center text-2xl font-bold tracking-[12px] text-white placeholder:text-slate-500 shadow-inner shadow-black/10 focus:outline-none focus:ring-2 focus:ring-teal-300/40"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting || otp.length < 4}
                className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300 text-[#053438] font-extrabold tracking-wide hover:shadow-[0_16px_30px_rgba(45,212,191,0.35)] transition-all disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Verifying...' : 'Verify OTP'}
              </button>

              <button
                type="button"
                onClick={handleResendOtp}
                disabled={isSubmitting}
                className="w-full rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-center text-sm text-teal-200 hover:text-teal-100 hover:bg-white/[0.06] transition-all disabled:opacity-50"
              >
                Resend OTP via {channelLabel}
              </button>
            </form>
          )}

          {step === STEPS.DONE && (
            <div className="text-center py-8">
              <div className="text-5xl mb-4">Done</div>
              <h2 className="text-xl font-headline font-bold text-emerald-300 mb-2">Phone Verified</h2>
              <p className="text-sm text-slate-300 leading-6">
                Your account has been created and verified. Redirecting to login now.
              </p>
            </div>
          )}

          <div className="mt-6 text-center text-sm text-slate-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-teal-300 hover:text-teal-200 font-medium transition-colors"
            >
              Sign In
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}