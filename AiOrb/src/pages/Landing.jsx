import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, ShieldCheck, Zap, Brain, Globe } from 'lucide-react';
import AnimatedCounter from '../components/AnimatedCounter';
const landingStats = [
  { label: 'Users Protected',     value: 284750 },
  { label: 'Seamless Journeys',   value: 2100000 },
  { label: 'Assist Sessions',     value: 128400  },
  { label: 'Languages Supported', value: 12      },
];

const features = [
  { title: 'Seamless Flows', description: 'Ensure smooth, frictionless journeys across essential apps and services.', color: 'green' },
  { title: 'Struggle Detection', description: 'Behavioral AI that catches hesitation patterns and rage taps to offer help proactively.', color: 'orange' },
  { title: 'Accessibility Engine', description: 'Multilingual voice assistance and simplified UI modes powered by adaptive AI.', color: 'green' },
  { title: 'Zero Friction', description: 'Real-time analysis to remove barriers before users drop off.', color: 'red' },
];

const featureIcons = { red: ShieldCheck, orange: Brain, green: Globe };
const featureColors = {
  red:    { dot: 'bg-[#e03c3c]', text: 'text-[#e03c3c]' },
  orange: { dot: 'bg-[#f97316]', text: 'text-[#f97316]' },
  green:  { dot: 'bg-[#34d399]', text: 'text-[#34d399]' },
};

const stagger = { container: { animate: { transition: { staggerChildren: 0.08 } } }, item: { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.4,0,0.2,1] } } } };

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Subtle dot background */}
      <div className="fixed inset-0 dot-bg opacity-100 pointer-events-none" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 sm:px-16 h-[64px] border-b border-[#161616]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-[#e03c3c] flex items-center justify-center">
            <Zap className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="text-[15px] font-semibold tracking-tight">AiOrb</span>
        </div>
        <div className="flex items-center gap-2">
          <Link to="/login" className="px-4 py-2 text-sm text-[#666] hover:text-white trans rounded-lg hover:bg-[#141414]">
            Login
          </Link>
          <Link to="/dashboard" className="px-4 py-2 text-sm font-medium bg-[#e03c3c] hover:bg-[#cc3333] text-white rounded-lg trans">
            Dashboard
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 max-w-5xl mx-auto px-8 sm:px-16 pt-24 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Badge */}
          <div className="inline-flex items-center gap-2 mb-8 px-3 py-1.5 rounded-full bg-[#111] border border-[#222] text-[12px] text-[#888]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#e03c3c] pulse-dot" />
            AI-Powered Digital Protection Platform
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
            Protecting the<br />
            <span className="text-[#e03c3c]">Silent Majority.</span>
          </h1>

          <p className="text-[17px] text-[#555] max-w-xl leading-relaxed mb-10">
            Fraud detection, accessibility intelligence, and behavioral analytics
            for the billions who struggle with technology — silently.
          </p>

          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="group inline-flex items-center gap-2 px-5 py-3 bg-[#e03c3c] hover:bg-[#cc3333] text-white text-sm font-medium rounded-lg trans"
            >
              Open Dashboard
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 trans" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-5 py-3 bg-[#111] border border-[#222] text-[#888] hover:text-white hover:border-[#333] text-sm font-medium rounded-lg trans"
            >
              Sign In
            </Link>
          </div>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.25 }}
          className="grid grid-cols-2 sm:grid-cols-4 gap-px mt-20 bg-[#161616] rounded-2xl overflow-hidden border border-[#161616]"
        >
          {landingStats.map((stat, i) => (
            <div key={i} className="bg-[#0d0d0d] px-6 py-6">
              <p className="stat-num text-3xl text-white mb-1">
                <AnimatedCounter end={stat.value} />
              </p>
              <p className="text-[12px] text-[#444] font-medium">{stat.label}</p>
            </div>
          ))}
        </motion.div>
      </section>

      {/* Features */}
      <section className="relative z-10 max-w-5xl mx-auto px-8 sm:px-16 py-20 border-t border-[#111]">
        <div className="mb-12">
          <p className="text-[12px] font-medium text-[#e03c3c] uppercase tracking-widest mb-3">Platform</p>
          <h2 className="text-3xl font-bold tracking-tight">Four modules. One protection layer.</h2>
        </div>

        <motion.div
          variants={stagger.container}
          initial="initial"
          whileInView="animate"
          viewport={{ once: true }}
          className="grid sm:grid-cols-2 gap-4"
        >
          {features.map((f, i) => {
            const colors = featureColors[f.color] || featureColors.red;
            return (
              <motion.div key={i} variants={stagger.item} className="panel card-hover-accent p-6 trans">
                <div className="flex items-center gap-2.5 mb-4">
                  <span className={`w-2 h-2 rounded-full ${colors.dot}`} />
                  <h3 className="text-[14px] font-semibold text-white">{f.title}</h3>
                </div>
                <p className="text-[13px] text-[#555] leading-relaxed">{f.description}</p>
              </motion.div>
            );
          })}
        </motion.div>
      </section>

      {/* Mission */}
      <section className="relative z-10 max-w-5xl mx-auto px-8 sm:px-16 py-20 border-t border-[#111]">
        <div className="panel-accent p-8 sm:p-12">
          <p className="text-[12px] font-medium text-[#e03c3c] uppercase tracking-widest mb-4">Mission</p>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-4 text-white max-w-2xl">
            Designing systems for the people technology leaves behind.
          </h2>
          <p className="text-[15px] text-[#555] leading-relaxed max-w-2xl">
            Over <span className="text-white">3 billion people</span> face digital exclusion daily —
            scammed, confused, and abandoned by systems never built for them.
            AiOrb uses AI to detect fraud, guide users through confusion, and make every app more human.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-[#111] px-8 sm:px-16 py-8">
        <div className="max-w-5xl mx-auto flex items-center justify-between text-[12px] text-[#333]">
          <span>© 2026 AiOrb</span>
          <span>Designing Systems for the Silent Majority</span>
        </div>
      </footer>
    </div>
  );
}
