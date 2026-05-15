import { useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight, ShieldCheck } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // No auth logic per user request, direct to dashboard
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-6 bg-[#253342]">
      
      {/* Top Header Logo */}
      <div className="absolute top-8 left-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded bg-[#314256] flex items-center justify-center">
           <ShieldCheck className="w-6 h-6 text-[#f6a821]" />
        </div>
        <span className="text-xl font-medium text-white tracking-wide">AiOrb</span>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1] }}
        className="w-full max-w-[520px]"
      >
        <div className="panel p-10 sm:p-16 shadow-[0_10px_40px_rgba(0,0,0,0.3)]">
          
          <div className="mb-10 text-center">
            <h1 className="text-[32px] font-medium text-white mb-3">Login to Dashboard</h1>
            <p className="text-[16px] text-[#8fa5b8] font-light">Enter your credentials to access the secure intelligence hub.</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-7">
            <div className="space-y-3">
              <label className="text-[14px] font-medium text-[#c9d5e0]">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-[#8fa5b8]" />
                </div>
                <input
                  type="email"
                  required
                  placeholder="admin@aiorb.com"
                  className="w-full pl-12 pr-4 py-3.5 bg-[#202b38] border border-[#3f5063] rounded text-[16px] text-white placeholder-[#5c7080] focus:outline-none focus:border-[#f6a821] focus:ring-1 focus:ring-[#f6a821] trans"
                />
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-[14px] font-medium text-[#c9d5e0]">Password</label>
                <a href="#" className="text-[14px] font-medium text-[#f6a821] hover:text-[#ffc04a] trans">Forgot password?</a>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-[#8fa5b8]" />
                </div>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full pl-12 pr-4 py-3.5 bg-[#202b38] border border-[#3f5063] rounded text-[16px] text-white placeholder-[#5c7080] focus:outline-none focus:border-[#f6a821] focus:ring-1 focus:ring-[#f6a821] trans"
                />
              </div>
            </div>

            <div className="flex items-center mt-2">
               <input type="checkbox" id="remember" className="w-4 h-4 rounded border-[#3f5063] bg-[#202b38] text-[#f6a821] focus:ring-[#f6a821]" />
               <label htmlFor="remember" className="ml-2 text-[14px] text-[#c9d5e0]">Remember me for 30 days</label>
            </div>

            <button
              type="submit"
              className="w-full py-4 mt-8 bg-[#f6a821] hover:bg-[#ffb53a] text-[#1e2835] rounded font-semibold text-[16px] flex items-center justify-center gap-2 shadow-lg trans"
            >
              Sign In
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>
          
          <div className="mt-10 pt-8 border-t border-[#3f5063] text-center">
            <p className="text-[15px] font-light text-[#8fa5b8]">
              Need access? <a href="#" className="text-white hover:text-[#f6a821] font-medium trans">Contact System Administrator</a>
            </p>
          </div>

        </div>
      </motion.div>
    </div>
  );
}
