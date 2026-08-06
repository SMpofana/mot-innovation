'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

// Trionn-style belt preloader — horizontal strips that slide away
export default function Preloader() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(false), 2200);
    return () => clearTimeout(timer);
  }, []);

  const beltCount = 10;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="fixed inset-0 z-[100] flex items-center justify-center"
          style={{ background: 'var(--bg)' }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Belt strips */}
          <div className="absolute inset-0 flex flex-col">
            {Array.from({ length: beltCount }).map((_, i) => (
              <motion.div
                key={i}
                className="flex-1"
                style={{ background: 'var(--bg-card)', transformOrigin: 'top' }}
                initial={{ scaleY: 1 }}
                animate={{ scaleY: 0 }}
                transition={{
                  duration: 0.6,
                  delay: 1.2 + i * 0.05,
                  ease: [0.76, 0, 0.24, 1],
                }}
              />
            ))}
          </div>

          {/* Center content */}
          <motion.div
            className="relative z-10 flex flex-col items-center gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            {/* Logo box with plus corners */}
            <div style={{ position: 'relative', padding: '1.5rem 2rem' }}>
              {/* Corner plus marks */}
              <PlusCrossMark className="absolute -top-1 -left-1" />
              <PlusCrossMark className="absolute -top-1 -right-1" />
              <PlusCrossMark className="absolute -bottom-1 -left-1" />
              <PlusCrossMark className="absolute -bottom-1 -right-1" />

              <motion.div
                className="text-display"
                style={{ fontSize: '2rem', fontWeight: 500, letterSpacing: '-0.03em' }}
                initial={{ opacity: 0, filter: 'blur(10px)' }}
                animate={{ opacity: 1, filter: 'blur(0px)' }}
                transition={{ delay: 0.5, duration: 0.8 }}
              >
                M.O.T
              </motion.div>
            </div>

            {/* Tagline */}
            <motion.div
              style={{
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.2em',
                color: 'var(--text-muted)',
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.5 }}
            >
              Marketing Intelligence
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function PlusCrossMark({ className }: { className?: string }) {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 13 13"
      fill="none"
      className={className}
      style={{ color: 'var(--text-light)' }}
    >
      <line x1="6.5" y1="0" x2="6.5" y2="13" stroke="currentColor" strokeWidth="1" />
      <line x1="0" y1="6.5" x2="13" y2="6.5" stroke="currentColor" strokeWidth="1" />
    </svg>
  );
}