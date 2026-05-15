import { motion } from 'framer-motion';

export default function Card({ children, className = '', accent = false, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: delay * 0.08, ease: [0.4, 0, 0.2, 1] }}
      className={`
        card-hover-accent trans
        ${accent ? 'panel-accent' : 'panel'}
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}
