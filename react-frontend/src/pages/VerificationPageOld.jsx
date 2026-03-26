import React, { useState, useEffect, useRef } from 'react';
import './LoginPage.css';

const VerificationPage = ({ onNavigate = () => {} }) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isLoading, setIsLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(120);
  const inputRefs = useRef([]);

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  const handleOtpChange = (e, index) => {
    const value = e.target.value;
    if (/^\d*$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);

      if (value && index < 5) {
        inputRefs.current[index + 1]?.focus();
      }
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = (e) => {
    e.preventDefault();
    const fullOtp = otp.join('');
    if (fullOtp.length === 6) {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        onNavigate('chatbot');
      }, 1500);
    }
  };

  const handleResend = () => {
    setTimeLeft(120);
    setOtp(['', '', '', '', '', '']);
  };

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="bg-mesh font-body text-on-surface min-h-screen flex flex-col">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 bg-white/70 backdrop-blur-md shadow-sm border-b border-white/20 flex items-center justify-between px-6 py-4 font-headline antialiased">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-emerald-600 text-2xl">fingerprint</span>
          <span className="text-xl font-bold text-emerald-600 tracking-tight">PersonaAI</span>
        </div>
        <div className="hidden md:flex gap-8 items-center text-slate-500">
          <a className="text-emerald-600 hover:opacity-80 transition-opacity active:scale-95 duration-200" href="#">
            Secure
          </a>
          <a className="hover:opacity-80 transition-opacity active:scale-95 duration-200" href="#">
            Verify
          </a>
          <a className="hover:opacity-80 transition-opacity active:scale-95 duration-200" href="#">
            Support
          </a>
        </div>
        <div className="flex items-center gap-4">
          <button className="w-10 h-10 rounded-full bg-surface-container-highest flex items-center justify-center text-on-surface hover:opacity-80 transition-opacity active:scale-95 duration-200">
            <span className="material-symbols-outlined">help_outline</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex items-center justify-center px-4 pt-24 pb-32">
        <div className="max-w-md w-full">
          {/* Verification Card */}
          <div className="glass-card rounded-xl p-8 shadow-2xl relative overflow-hidden">
            {/* Decorative Elements */}
            <div className="absolute -top-12 -right-12 w-32 h-32 bg-primary-container/20 rounded-full blur-3xl"></div>
            <div className="absolute -bottom-12 -left-12 w-32 h-32 bg-secondary-container/20 rounded-full blur-3xl"></div>

            <div className="relative z-10 text-center mb-10">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-fixed rounded-full mb-6 shadow-lg shadow-primary/20">
                <span className="material-symbols-outlined text-primary text-4xl">lock_person</span>
              </div>
              <h1 className="font-headline text-3xl font-extrabold text-on-surface tracking-tight mb-2">
                Security Verification
              </h1>
              <p className="text-on-surface-variant font-body px-4">
                Enter the 6-digit code sent to your registered device to continue access.
              </p>
            </div>

            {/* OTP Input Form */}
            <form className="space-y-8" onSubmit={handleVerify}>
              <div className="flex justify-between gap-2 sm:gap-4">
                {otp.map((digit, index) => (
                  <input
                    key={index}
                    ref={(el) => (inputRefs.current[index] = el)}
                    type="text"
                    maxLength="1"
                    value={digit}
                    onChange={(e) => handleOtpChange(e, index)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    placeholder={index === 0 ? '4' : '·'}
                    className="w-12 h-16 sm:w-14 sm:h-20 text-center text-2xl font-bold rounded-lg border-2 border-outline-variant bg-white/50 focus:border-secondary-container focus:ring-4 focus:ring-secondary-container/20 transition-all outline-none"
                  />
                ))}
              </div>

              <div className="space-y-4">
                <button
                  type="submit"
                  disabled={isLoading || otp.join('').length !== 6}
                  className="w-full bg-primary-container text-on-primary-container font-headline font-bold py-4 rounded-full shadow-lg shadow-primary/20 hover:shadow-primary/30 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  <span>{isLoading ? 'Verifying...' : 'Verify Identity'}</span>
                  <span className="material-symbols-outlined">
                    {isLoading ? 'hourglass_empty' : 'arrow_forward'}
                  </span>
                </button>

                <div className="flex items-center justify-between px-2 text-sm font-label">
                  <button
                    type="button"
                    onClick={handleResend}
                    disabled={timeLeft > 0}
                    className="text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1 disabled:opacity-50"
                  >
                    <span className="material-symbols-outlined text-sm">refresh</span>
                    {timeLeft > 0 ? `Resend (${minutes}:${seconds.toString().padStart(2, '0')})` : 'Resend Code'}
                  </button>
                  <a
                    href="#"
                    className="text-tertiary font-semibold hover:opacity-80 transition-opacity"
                  >
                    Forgot Password?
                  </a>
                </div>
              </div>
            </form>

            {/* Status Banner */}
            <div className="mt-10 p-4 bg-secondary-container/10 rounded-lg flex items-start gap-3 border border-secondary-container/20">
              <span className="material-symbols-outlined text-secondary">shield_lock</span>
              <div className="text-xs">
                <p className="font-bold text-on-secondary-container">End-to-End Encrypted</p>
                <p className="text-on-secondary-container/70">
                  Your verification process is secured with high-grade biometric matching and RSA-4096 encryption.
                </p>
              </div>
            </div>
          </div>

          {/* Footer Links */}
          <p className="mt-8 text-center text-on-surface-variant text-sm font-label">
            Need help?{' '}
            <a href="#" className="text-secondary font-bold hover:underline">
              Contact Persona Support
            </a>
          </p>
        </div>
      </main>

      {/* Bottom Navigation (Mobile Only) */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full flex justify-around items-center px-4 pb-6 pt-3 bg-white/70 backdrop-blur-lg shadow-[0_-4px_12px_rgba(0,0,0,0.05)] border-t border-white/20 z-50 rounded-t-3xl">
        <button className="flex flex-col items-center justify-center text-slate-400 font-label text-[11px] font-medium hover:text-emerald-500 transition-colors active:scale-90">
          <span className="material-symbols-outlined mb-1">shield</span>
          Secure
        </button>
        <button className="flex flex-col items-center justify-center bg-emerald-500/10 text-emerald-600 font-label text-[11px] font-medium rounded-full px-4 py-1 active:scale-90">
          <span className="material-symbols-outlined mb-1">lock_open</span>
          Verify
        </button>
        <button className="flex flex-col items-center justify-center text-slate-400 font-label text-[11px] font-medium hover:text-emerald-500 transition-colors active:scale-90">
          <span className="material-symbols-outlined mb-1">help_outline</span>
          Support
        </button>
      </nav>

      {/* Decorative Background Elements */}
      <div className="fixed top-20 left-10 w-64 h-64 bg-secondary-container/5 rounded-full blur-[100px] -z-10"></div>
      <div className="fixed bottom-20 right-10 w-96 h-96 bg-tertiary-container/5 rounded-full blur-[100px] -z-10"></div>
    </div>
  );
};

export default VerificationPage;
