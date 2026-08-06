'use client';

import { motion } from 'framer-motion';

const channels = ['LinkedIn', 'Instagram', 'TikTok', 'X', 'Facebook', 'Google Ads', 'Meta Ads', 'LinkedIn Ads', 'Email', 'CMS'];

export default function Marquee() {
  return (
    <div className="py-10 overflow-hidden" style={{ background: 'var(--bg-alt)', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
      <div className="text-center mb-6">
        <p className="text-eyebrow">Channels We Connect</p>
      </div>
      <div className="relative">
        <div
          className="absolute left-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
          style={{ background: 'linear-gradient(90deg, var(--bg-alt), transparent)' }}
        />
        <div
          className="absolute right-0 top-0 bottom-0 w-24 z-10 pointer-events-none"
          style={{ background: 'linear-gradient(270deg, var(--bg-alt), transparent)' }}
        />

        <motion.div
          className="flex gap-16 whitespace-nowrap"
          animate={{ x: ['0%', '-50%'] }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
        >
          {[...channels, ...channels].map((item, i) => (
            <span
              key={i}
              style={{
                fontSize: '1rem',
                fontWeight: 400,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
              }}
            >
              {item}
            </span>
          ))}
        </motion.div>
      </div>
    </div>
  );
}