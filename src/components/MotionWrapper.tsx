'use client';

import { motion, useInView, useReducedMotion } from 'framer-motion';
import { useRef, ReactNode } from 'react';

type Direction = 'up' | 'down' | 'left' | 'right' | 'fade' | 'scale';

interface MotionWrapperProps {
  children: ReactNode;
  direction?: Direction;
  delay?: number;
  duration?: number;
  className?: string;
  style?: React.CSSProperties;
  once?: boolean;
  amount?: number;
}

const offsets: Record<Direction, { x: number; y: number; scale: number }> = {
  up: { x: 0, y: 40, scale: 1 },
  down: { x: 0, y: -40, scale: 1 },
  left: { x: 40, y: 0, scale: 1 },
  right: { x: -40, y: 0, scale: 1 },
  fade: { x: 0, y: 0, scale: 1 },
  scale: { x: 0, y: 0, scale: 0.92 },
};

export default function MotionWrapper({
  children,
  direction = 'up',
  delay = 0,
  duration = 0.6,
  className,
  style,
  once = true,
  amount = 0.2,
}: MotionWrapperProps) {
  const ref = useRef(null);
  const inView = useInView(ref, { once, amount });
  const reduceMotion = useReducedMotion();

  const offset = reduceMotion ? { x: 0, y: 0, scale: 1 } : offsets[direction];

  return (
    <motion.div
      ref={ref}
      className={className}
      style={style}
      initial={{ opacity: 0, x: offset.x, y: offset.y, scale: offset.scale }}
      animate={inView ? { opacity: 1, x: 0, y: 0, scale: 1 } : {}}
      transition={{ duration, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
    >
      {children}
    </motion.div>
  );
}