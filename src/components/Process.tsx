'use client';

import { motion } from 'framer-motion';
import { content } from '../content';
import MotionWrapper from './MotionWrapper';

const Process = () => {
  return (
    <section id="process" className="section-pad">
      <div className="container-xl">
        <MotionWrapper direction="up">
          <div className="section-header">
            <h2>{content.process.headline}</h2>
            <p>{content.process.subhead}</p>
          </div>
        </MotionWrapper>

        {/* Desktop: horizontal stepper */}
        <div className="hidden md:grid grid-cols-4 gap-4 relative">
          {/* Thin connecting line */}
          <div
            className="absolute top-10 left-[12.5%] right-[12.5%]"
            style={{ height: '1px', background: 'var(--border)' }}
          />

          {content.process.steps.map((step, i) => (
            <MotionWrapper key={i} direction="up" delay={i * 0.12} className="text-center relative">
              <motion.div
                className="relative mx-auto mb-6 w-20 h-20 rounded-full flex items-center justify-center"
                style={{
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  color: 'var(--text)',
                  zIndex: 1,
                  fontVariantNumeric: 'tabular-nums',
                  fontSize: '1.25rem',
                  fontWeight: 300,
                  letterSpacing: '0.02em',
                }}
                whileHover={{ borderColor: 'var(--text-muted)' }}
              >
                {step.number}
              </motion.div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', fontWeight: 400 }}>{step.title}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.6 }}>
                {step.description}
              </p>
            </MotionWrapper>
          ))}
        </div>

        {/* Mobile: vertical timeline */}
        <div className="md:hidden" style={{ maxWidth: '850px', margin: '0 auto' }}>
          {content.process.steps.map((step, i) => (
            <motion.div
              key={i}
              className="process-line"
              style={{
                display: 'flex',
                gap: '2rem',
                paddingBottom: '2.5rem',
                paddingLeft: '1rem',
              }}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.4, delay: i * 0.12, ease: 'easeOut' }}
            >
              <motion.div
                style={{
                  flexShrink: 0,
                  width: '4.5rem',
                  height: '4.5rem',
                  borderRadius: '50%',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.25rem',
                  fontWeight: 300,
                  color: 'var(--text)',
                  position: 'relative',
                  zIndex: 1,
                  fontVariantNumeric: 'tabular-nums',
                }}
                whileHover={{ borderColor: 'var(--text-muted)' }}
              >
                {step.number}
              </motion.div>

              <div style={{ paddingTop: '0.5rem', paddingBottom: '1rem' }}>
                <h3 style={{ marginBottom: '0.5rem', fontWeight: 400, fontSize: '1.05rem' }}>{step.title}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                  {step.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Process;