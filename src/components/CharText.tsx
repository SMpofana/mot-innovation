'use client';

import { motion } from 'framer-motion';

interface CharTextProps {
  text: string;
  className?: string;
  delay?: number;
  stagger?: number;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span' | 'div';
}

// Trionn-style character-by-character text reveal
export default function CharText({
  text,
  className,
  delay = 0,
  stagger = 0.03,
  as: Tag = 'span',
}: CharTextProps) {
  const chars = text.split('');

  return (
    <Tag className={className} style={{ display: 'inline-block' }}>
      {chars.map((char, i) => (
        <motion.span
          key={i}
          className="char"
          initial={{ opacity: 0, y: '0.5em', filter: 'blur(8px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          transition={{
            duration: 0.5,
            delay: delay + i * stagger,
            ease: [0.25, 0.46, 0.45, 0.94],
          }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </Tag>
  );
}