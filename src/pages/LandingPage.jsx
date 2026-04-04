import { useState } from 'react';
import { Link } from 'react-router-dom';
import Logo from '../components/Logo';

const coreFeatures = [
  {
    icon: 'smart_toy',
    title: 'AI-Powered Simplification',
    description: 'Gemini 2.5 Flash instantly transforms complex medical jargon into everyday language patients understand.',
    benefit: 'Reduces comprehension barriers by 85%',
  },
  {
    icon: 'translate',
    title: 'Bilingual Output',
    description: 'Automatic translation to Bengali and English keeps both languages conversational and practical.',
    benefit: 'Serves diverse patient populations',
  },
  {
    icon: 'chat_bubble',
    title: 'WhatsApp Delivery',
    description: 'Send simplified summaries, medication schedules, and follow-ups directly to patient phones.',
    benefit: 'Increases adherence rates',
  },
  {
    icon: 'quiz',
    title: 'Comprehension Checks',
    description: '3-question dynamic quizzes verify understanding with adaptive retry for low scores.',
    benefit: 'Ensures patient readiness',
  },
  {
    icon: 'volume_up',
    title: 'Read-Aloud Support',
    description: 'Text-to-speech in Bengali for patients with literacy barriers or visual challenges.',
    benefit: 'Accessibility for all users',
  },
  {
    icon: 'bar_chart',
    title: 'Analytics Dashboard',
    description: 'Track readmission risk, comprehension scores, and medication adherence in real time.',
    benefit: 'Data-driven care decisions',
  },
];

const roles = [
  {
    role: 'Patient',
    icon: 'patient_list',
    description: 'View clear discharge summaries, medication schedules, follow-up dates, and emergency symptoms.',
    features: [
      '📋 Simplified summaries in plain language',
      '💊 Visual medication guide with plain names',
      '📅 Follow-up appointment reminders',
      '🚨 Emergency symptom alerts',
    ],
    color: 'emerald',
  },
  {
    role: 'Caregiver',
    icon: 'groups',
    description: 'Support patient recovery with clear guidance, monitoring links, and family-focused summaries.',
    features: [
      '👥 Family-aware care instructions',
      '🔔 Real-time alerts and updates',
      '📞 Emergency contact shortcuts',
      '📊 Patient progress tracking',
    ],
    color: 'cyan',
  },
  {
    role: 'Doctor',
    icon: 'stethoscope',
    description: 'Approve prescriptions, review patient comprehension, and monitor adherence outcomes.',
    features: [
      '✅ Prescription approval workflows',
      '📈 Comprehension analytics',
      '🏥 Patient insight summaries',
      '⚙️ Role-based admin controls',
    ],
    color: 'teal',
  },
];

const workflow = [
  { num: '1', title: 'Upload', desc: 'Doctor uploads hospital discharge summary or handwritten prescription.' },
  { num: '2', title: 'Simplify', desc: 'AI translates clinical text into patient-ready language.' },
  { num: '3', title: 'Translate', desc: 'Bilingual output in English and Bengali.' },
  { num: '4', title: 'Deliver', desc: 'Send via WhatsApp, email, or in-app dashboard.' },
  { num: '5', title: 'Verify', desc: 'Patient completes comprehension quiz.' },
  { num: '6', title: 'Monitor', desc: 'Track adherence and readmission risk factors.' },
];

const impact = [
  { metric: '40-80%', label: 'Patients who struggle to understand discharge instructions' },
  { metric: '25%', label: 'Preventable readmissions from poor understanding' },
  { metric: '12hr', label: 'Time to symptom onset after discharge' },
];

function LandingPage() {
  const [activeRole, setActiveRole] = useState(0);

  return (
    <div className="relative overflow-hidden bg-[#041125] text-white">
      <style>{`
        .pulse-grid {
          background-image:
            linear-gradient(to right, rgba(255,255,255,0.06) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(255,255,255,0.06) 1px, transparent 1px);
          background-size: 56px 56px;
          mask-image: radial-gradient(circle at 50% 30%, black 30%, transparent 70%);
        }

        .rise-up {
          opacity: 0;
          transform: translateY(24px);
          animation: rise-up 0.9s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        }

        .rise-up.delay-1 { animation-delay: 0.08s; }
        .rise-up.delay-2 { animation-delay: 0.16s; }
        .rise-up.delay-3 { animation-delay: 0.24s; }
        .rise-up.delay-4 { animation-delay: 0.32s; }
        .rise-up.delay-5 { animation-delay: 0.4s; }

        .float-slow {
          animation: float-slow 8s ease-in-out infinite;
        }

        .float-slower {
          animation: float-slow 12s ease-in-out infinite reverse;
        }

        .orb-glow {
          animation: orb-glow 4.8s ease-in-out infinite;
        }

        .pulse-ring {
          animation: pulse-ring 2.4s ease-out infinite;
        }

        .scale-in {
          animation: scale-in 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
          opacity: 0;
        }

        .scale-in.delay-1 { animation-delay: 0.1s; }
        .scale-in.delay-2 { animation-delay: 0.2s; }
        .scale-in.delay-3 { animation-delay: 0.3s; }

        @keyframes rise-up {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes float-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-16px); }
        }

        @keyframes orb-glow {
          0%, 100% { filter: blur(88px) saturate(95%); opacity: 0.5; }
          50% { filter: blur(120px) saturate(140%); opacity: 0.8; }
        }

        @keyframes pulse-ring {
          0% {
            box-shadow: 0 0 0 0 rgba(45, 212, 191, 0.7);
          }
          70% {
            box-shadow: 0 0 0 20px rgba(45, 212, 191, 0);
          }
          100% {
            box-shadow: 0 0 0 0 rgba(45, 212, 191, 0);
          }
        }

        @keyframes scale-in {
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        .tab-active {
          background: linear-gradient(135deg, rgba(45, 212, 191, 0.2), rgba(34, 211, 238, 0.1));
          border-color: rgba(45, 212, 191, 0.6);
        }
      `}</style>

      <div className="absolute inset-0 pulse-grid opacity-50" />
      <div className="pointer-events-none absolute -top-32 -left-32 h-96 w-96 rounded-full bg-[#2dd4bf]/25 orb-glow" />
      <div className="pointer-events-none absolute top-1/4 -right-40 h-[32rem] w-[32rem] rounded-full bg-[#22d3ee]/20 orb-glow" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-[#f59e0b]/15 orb-glow" />

      <div className="absolute inset-0 pulse-grid opacity-70" />
      <div className="pointer-events-none absolute -top-20 -left-20 h-80 w-80 rounded-full bg-[#2dd4bf]/35 orb-glow" />
      <div className="pointer-events-none absolute top-1/3 -right-28 h-[26rem] w-[26rem] rounded-full bg-[#22d3ee]/25 orb-glow" />
      <div className="pointer-events-none absolute bottom-[-6rem] left-1/3 h-80 w-80 rounded-full bg-[#f59e0b]/20 orb-glow" />

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ HEADER ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <header className="relative z-20 mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
        <Link to="/" className="rise-up no-underline hover:opacity-90 transition-opacity">
          <Logo size="md" showText={true} />
        </Link>

        <nav className="rise-up delay-1 flex items-center gap-3">
          <Link
            to="/login"
            className="rounded-xl border border-white/20 bg-white/8 px-5 py-2.5 text-sm font-semibold text-slate-100 transition-all hover:bg-white/15 hover:border-white/40"
          >
            Login
          </Link>
          <Link
            to="/signup"
            className="rounded-xl bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300 px-5 py-2.5 text-sm font-black text-[#04262b] shadow-[0_8px_20px_rgba(45,212,191,0.35)] transition-all hover:scale-[1.04] active:scale-[0.98]"
          >
            Get Started
          </Link>
        </nav>
      </header>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ HERO ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-12 lg:px-10 lg:py-20">
        <div className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-8">
            <div className="rise-up inline-flex items-center gap-2 rounded-full border border-teal-100/20 bg-teal-200/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-teal-100">
              <span className="h-2 w-2 rounded-full bg-teal-200 animate-pulse" />
              Healthcare Reimagined
            </div>

            <h1 className="rise-up delay-1 text-5xl font-black leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
              Transform Medical Complexity into Patient Clarity.
            </h1>

            <p className="rise-up delay-2 max-w-2xl text-lg leading-8 text-slate-200/90">
              SwasthaLink bridges the 40-80% comprehension gap in hospital discharge instructions. AI-powered simplification, bilingual delivery, and WhatsApp integration keep patients informed, adherent, and safe at home.
            </p>

            <div className="rise-up delay-3 flex flex-wrap items-center gap-4">
              <Link
                to="/signup"
                className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300 px-7 py-4 text-base font-black uppercase tracking-[0.16em] text-[#04262b] shadow-[0_16px_40px_rgba(45,212,191,0.4)] transition-all hover:scale-[1.05] active:scale-[0.95]"
              >
                <span className="material-symbols-outlined">rocket_launch</span>
                Launch Free Access
              </Link>

              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-2xl border border-white/25 bg-white/8 px-7 py-4 text-base font-bold uppercase tracking-[0.16em] text-slate-100 transition-all hover:bg-white/15 hover:border-white/40"
              >
                <span className="material-symbols-outlined">login</span>
                Sign In
              </Link>
            </div>

            <div className="rise-up delay-4 grid pt-4 grid-cols-3 gap-4">
              {impact.map((item, idx) => (
                <div key={idx} className="rounded-2xl border border-white/10 bg-white/[0.05] p-4 backdrop-blur">
                  <p className="text-2xl font-black text-teal-200">{item.metric}</p>
                  <p className="mt-1 text-xs font-semibold text-slate-300 leading-tight">{item.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rise-up delay-2 relative">
            <div className="relative overflow-hidden rounded-[2.5rem] border border-white/15 bg-[#071b34]/70 p-8 shadow-[0_32px_80px_rgba(2,10,25,0.6)] backdrop-blur-2xl">
              <div className="absolute inset-0 bg-gradient-to-br from-teal-200/5 via-transparent to-cyan-200/5" />
              <div className="relative space-y-6">
                <div className="flex items-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-300/30 via-teal-300/20 to-cyan-300/10">
                    <span className="material-symbols-outlined text-3xl text-emerald-200">healing</span>
                  </div>
                  <div>
                    <p className="text-sm uppercase tracking-[0.2em] text-slate-300 font-semibold">Patient Dashboard</p>
                    <p className="text-xl font-black text-white">Smart Care Portal</p>
                  </div>
                </div>

                <div className="space-y-3 pt-4">
                  {['Clear discharge summaries', 'Medication schedules', 'Follow-up reminders', 'Smart health tips'].map((item, i) => (
                    <div key={i} className="flex items-center gap-3 rounded-xl border border-white/8 bg-white/[0.05] px-4 py-3">
                      <span className="text-lg text-emerald-300">✓</span>
                      <span className="text-sm font-semibold text-slate-100">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ THE PROBLEM ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-16 lg:px-10">
        <div className="space-y-12">
          <div className="rise-up text-center space-y-4 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-rose-100/20 bg-rose-200/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-rose-100">
              <span className="material-symbols-outlined text-base">warning</span>
              The Challenge
            </div>
            <h2 className="text-4xl lg:text-5xl font-black text-white tracking-tight">
              Patients Don't Understand Discharge Instructions
            </h2>
            <p className="text-lg text-slate-300">Medical jargon, dense paragraphs, and rushed handoffs create dangerous knowledge gaps.</p>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            {[
              { num: '40-80%', title: 'Comprehension Failure', desc: 'Patients misunderstand critical care instructions' },
              { num: '25%', title: 'Preventable Readmissions', desc: 'Caused by poor understanding and non-adherence' },
              { num: '12 hrs', title: 'Critical Window', desc: 'Average time to symptom onset after discharge' },
            ].map((item, idx) => (
              <div key={idx} className={`rise-up delay-${idx + 1} rounded-2xl border border-white/10 bg-white/[0.05] p-8 backdrop-blur`}>
                <p className="text-4xl font-black text-rose-300">{item.num}</p>
                <h3 className="mt-3 text-xl font-bold text-white">{item.title}</h3>
                <p className="mt-2 text-sm text-slate-300">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ HOW IT WORKS ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-16 lg:px-10">
        <div className="space-y-12">
          <div className="rise-up text-center space-y-4 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-teal-100/20 bg-teal-200/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-teal-100">
              <span className="material-symbols-outlined text-base">workflow</span>
              The Solution
            </div>
            <h2 className="text-4xl lg:text-5xl font-black text-white tracking-tight">
              From Complex to Crystal Clear
            </h2>
            <p className="text-lg text-slate-300">6-step AI-powered workflow that puts control back in patients' hands.</p>
          </div>

          <div className="grid gap-6 lg:grid-cols-6">
            {workflow.map((step, idx) => (
              <div key={idx} className={`rise-up delay-${Math.min(idx, 3)} relative group`}>
                <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.04] p-6 h-full backdrop-blur hover:border-teal-300/60 hover:bg-teal-300/5 transition-all">
                  <div className="absolute -top-4 -left-4 h-12 w-12 rounded-full bg-gradient-to-br from-teal-300 via-cyan-300 to-emerald-300 flex items-center justify-center text-lg font-black text-[#04262b] shadow-[0_0_20px_rgba(45,212,191,0.4)]">
                    {step.num}
                  </div>
                  <h3 className="mt-4 text-lg font-bold text-white">{step.title}</h3>
                  <p className="mt-2 text-sm text-slate-300">{step.desc}</p>
                </div>
                {idx < 5 && (
                  <div className="hidden lg:flex absolute top-12 -right-3 w-6 h-[2px] bg-gradient-to-r from-teal-300/60 to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ CORE FEATURES ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-16 lg:px-10">
        <div className="space-y-12">
          <div className="rise-up text-center space-y-4 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-100/20 bg-cyan-200/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-cyan-100">
              <span className="material-symbols-outlined text-base">star</span>
              Core Features
            </div>
            <h2 className="text-4xl lg:text-5xl font-black text-white tracking-tight">
              Powered by Advanced AI & Clinical Insight
            </h2>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            {coreFeatures.map((feat, idx) => (
              <div
                key={idx}
                className={`rise-up delay-${Math.min(idx % 3, 2)} rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] via-white/[0.04] to-transparent p-8 backdrop-blur hover:border-teal-300/60 hover:shadow-[0_20px_40px_rgba(45,212,191,0.1)] transition-all`}
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br from-teal-300/30 via-cyan-300/20 to-emerald-300/10">
                  <span className="material-symbols-outlined text-2xl text-teal-100">{feat.icon}</span>
                </div>
                <h3 className="mt-4 text-xl font-bold text-white">{feat.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-300">{feat.description}</p>
                <div className="mt-5 rounded-lg border border-teal-200/20 bg-teal-200/10 px-3 py-2">
                  <p className="text-xs font-semibold text-teal-100">→ {feat.benefit}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ ROLE-BASED ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-16 lg:px-10">
        <div className="space-y-12">
          <div className="rise-up text-center space-y-4 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-100/20 bg-emerald-200/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-emerald-100">
              <span className="material-symbols-outlined text-base">groups</span>
              Built for Everyone
            </div>
            <h2 className="text-4xl lg:text-5xl font-black text-white tracking-tight">
              Role-Based Workspaces
            </h2>
            <p className="text-lg text-slate-300">Each user gets what they need—from simple care guidance to powerful analytics.</p>
          </div>

          <div className="flex gap-3 flex-wrap justify-center mb-12">
            {roles.map((r, idx) => (
              <button
                key={idx}
                onClick={() => setActiveRole(idx)}
                className={`scale-in delay-${idx} flex items-center gap-2 rounded-xl px-5 py-3 font-semibold transition-all ${
                  activeRole === idx
                    ? 'tab-active'
                    : 'border border-white/15 bg-white/[0.05] hover:border-white/25 hover:bg-white/10'
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">{roles[idx].icon}</span>
                {r.role}
              </button>
            ))}
          </div>

          <div className="grid gap-8 lg:grid-cols-2 items-center">
            <div className={`${activeRole === 0 ? 'animate-fadeIn' : ''} space-y-6`}>
              <div>
                <p className="text-sm font-bold uppercase tracking-[0.2em] text-emerald-200 mb-2">Dashboard for {roles[activeRole].role}s</p>
                <h3 className="text-3xl font-black text-white mb-3">{roles[activeRole].description}</h3>
              </div>
              <div className="space-y-3">
                {roles[activeRole].features.map((feat, i) => (
                  <div key={i} className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/[0.05] p-4">
                    <span className="text-xl flex-shrink-0 mt-1">{feat.split(' ')[0]}</span>
                    <span className="text-sm text-slate-200 font-medium">{feat.split(' ').slice(1).join(' ')}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="float-slower relative overflow-hidden rounded-2xl border border-white/15 bg-[#071b34]/60 p-8 backdrop-blur">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-200/5 via-transparent to-cyan-200/5" />
              <div className="relative">
                <div className={`h-80 rounded-xl border border-white/10 bg-gradient-to-br from-white/[0.1] to-white/[0.05] flex items-center justify-center`}>
                  <div className="text-center">
                    <span className={`material-symbols-outlined text-7xl`} style={{color: activeRole === 0 ? '#10b981' : activeRole === 1 ? '#06b6d4' : '#14b8a6'}}>
                      {roles[activeRole].icon}
                    </span>
                    <p className="mt-4 text-sm font-bold text-slate-300 uppercase tracking-[0.2em]">{roles[activeRole].role} Portal</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ TECH STACK ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-16 lg:px-10">
        <div className="space-y-12">
          <div className="rise-up text-center space-y-4 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 rounded-full border border-amber-100/20 bg-amber-200/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.22em] text-amber-100">
              <span className="material-symbols-outlined text-base">memory</span>
              Technology Stack
            </div>
            <h2 className="text-4xl lg:text-5xl font-black text-white tracking-tight">
              Enterprise-Grade Infrastructure
            </h2>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rise-up delay-1 rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.04] p-8 backdrop-blur">
              <h3 className="text-xl font-bold text-amber-200 mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined">cloud</span>
                Backend
              </h3>
              <div className="space-y-2 text-slate-300 text-sm">
                <p>• <span className="font-semibold">FastAPI</span> — Async Python framework</p>
                <p>• <span className="font-semibold">Gemini 2.5 Flash</span> — AI-powered summarization</p>
                <p>• <span className="font-semibold">Twilio</span> — WhatsApp & SMS delivery</p>
                <p>• <span className="font-semibold">Supabase</span> — PostgreSQL database</p>
                <p>• <span className="font-semibold">AWS S3</span> — Secure file storage</p>
              </div>
            </div>

            <div className="rise-up delay-2 rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.04] p-8 backdrop-blur">
              <h3 className="text-xl font-bold text-cyan-200 mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined">laptop</span>
                Frontend
              </h3>
              <div className="space-y-2 text-slate-300 text-sm">
                <p>• <span className="font-semibold">React 18</span> — UI framework</p>
                <p>• <span className="font-semibold">Vite</span> — Fast build tooling</p>
                <p>• <span className="font-semibold">Tailwind CSS v4</span> — Styling</p>
                <p>• <span className="font-semibold">Three.js</span> — 3D animations</p>
                <p>• <span className="font-semibold">Chart.js</span> — Data visualization</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ CTA FOOTER ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <section className="relative z-10 mx-auto w-full max-w-7xl px-6 py-20 lg:px-10">
        <div className="rise-up relative overflow-hidden rounded-3xl border border-white/15 bg-gradient-to-br from-teal-200/10 via-white/5 to-cyan-200/10 p-12 lg:p-20 backdrop-blur-xl shadow-[0_20px_60px_rgba(45,212,191,0.15)]">
          <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:30px_30px] pointer-events-none" />
          <div className="relative z-10 text-center space-y-8">
            <h2 className="text-4xl lg:text-5xl font-black text-white">
              Ready to Transform Patient Care?
            </h2>
            <p className="text-lg text-slate-300 max-w-2xl mx-auto">
              Join hospitals and healthcare providers across India using SwasthaLink to improve discharge comprehension and reduce preventable readmissions.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/signup"
                className="inline-flex items-center gap-2 rounded-2xl bg-gradient-to-r from-teal-300 via-cyan-300 to-emerald-300 px-8 py-4 text-base font-black uppercase tracking-[0.16em] text-[#04262b] shadow-[0_16px_40px_rgba(45,212,191,0.4)] transition-all hover:scale-[1.05] active:scale-[0.95]"
              >
                <span className="material-symbols-outlined">start</span>
                Start Your Free Access
              </Link>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-2xl border border-white/30 bg-white/10 px-8 py-4 text-base font-bold uppercase tracking-[0.16em] text-slate-100 transition-all hover:bg-white/20 hover:border-white/50"
              >
                <span className="material-symbols-outlined">login</span>
                Sign In
              </Link>
            </div>

            <p className="text-sm text-slate-400">No credit card required • Start simplifying today</p>
          </div>
        </div>
      </section>

      {/* ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ FOOTER ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ */}
      <footer className="relative z-10 border-t border-white/10 bg-[#02080f]/80 px-6 py-12 lg:px-10">
        <div className="mx-auto max-w-7xl text-center">
          <p className="text-sm text-slate-400">
            © 2026 SwasthaLink. Transforming healthcare communication, one patient at a time.
          </p>
          <p className="mt-3 text-xs text-slate-500">
            Built with <span className="text-rose-400">❤</span> for patients, doctors, and families across India.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
