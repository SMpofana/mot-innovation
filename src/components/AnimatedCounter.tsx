'use client';

import { motion, useInView, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface AnimatedCounterProps {
  value: string;
  label: string;
  delay?: number;
}

// Extracts the numeric portion and any suffix (like "+") from the value string
function parseValue(value: string) {
  const match = value.match(/^(\d[\d,]*)(.*)$/);
  if (!match) return { isNumeric: false, display: value, target: 0, suffix: '' };
  const numStr = match[1].replace(/,/g, '');
  const target = parseInt(numStr, 10);
  const suffix = match[2];
  return { isNumeric: true, display: value, target, suffix };
}

// Count-up animation with easeOut when scrolled into view.
// Formats numbers with commas (e.g., 1248 -> "1,248").
export default function AnimatedCounter({ value, label, delay = 0 }: AnimatedCounterProps) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, amount: 0.4 });
  const count = useMotionValue(0);

  const { isNumeric, target, suffix } = parseValue(value);

  // Transform raw number to comma-formatted string
  const rounded = useTransform(count, (latest) => {
    return Math.round(latest).toLocaleString('en-US');
  });

  useEffect(() => {
    if (inView && isNumeric) {
      const controls = animate(count, target, {
        duration: 1.8,
        delay,
        ease: [0.25, 0.46, 0.45, 0.94], // easeOut quart
      });
      return controls.stop;
    }
  }, [inView, isNumeric, target, count, delay]);

  return (
    <div
      ref={ref}
      style={{
        background: 'var(--bg)',
        padding: '2rem 1rem',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontSize: '2.5rem',
          fontWeight: 300,
          letterSpacing: '-0.03em',
          marginBottom: '0.25rem',
          fontVariantNumeric: 'tabular-nums',
          color: 'var(--text)',
        }}
      >
        {isNumeric ? (
          <motion.span>{rounded}</motion.span>
        ) : (
          <span>{value}</span>
        )}
        {isNumeric && suffix && (
          <span style={{ fontSize: '1.25rem', marginLeft: '0.15rem', color: 'var(--text-muted)' }}>
            {suffix}
          </span>
        )}
      </div>
      <div className="text-eyebrow" style={{ fontSize: '0.65rem' }}>
        {label}
      </div>
    </div>
  );
}