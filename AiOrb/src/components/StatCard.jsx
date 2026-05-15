import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';
import AnimatedCounter from './AnimatedCounter';

export default function StatCard({ icon: Icon, label, value, suffix = '', prefix = '', change, up = true, delay = 0, className = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1 }}
      className={`panel p-6 sm:p-8 relative overflow-hidden group ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <p className="text-[14px] font-light text-[#c0cdd8]">{label}</p>
        <div className="w-8 h-8 rounded-full bg-[rgba(255,255,255,0.05)] text-[#c0cdd8] flex items-center justify-center trans group-hover:text-[#f6a821] group-hover:bg-[rgba(246,168,33,0.1)]">
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div>
        <div className="stat-num text-[32px] sm:text-[38px] text-white leading-none">
          {prefix}
          {typeof value === 'number'
            ? <AnimatedCounter end={value} suffix={suffix} />
            : <span>{value}{suffix}</span>
          }
        </div>
        {change && (
          <p className="text-[12px] font-light mt-3 flex items-center gap-1.5">
            {up ? <ArrowUpRight className="w-3.5 h-3.5 text-[#21b978]" /> : <ArrowDownRight className="w-3.5 h-3.5 text-[#f6a821]" />}
            <span className={up ? 'text-[#21b978]' : 'text-[#f6a821]'}>{change}</span>
            <span className="text-[#8fa5b8] ml-1">vs last month</span>
          </p>
        )}
      </div>
    </motion.div>
  );
}
