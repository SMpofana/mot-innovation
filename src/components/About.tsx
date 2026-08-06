'use client';

import { motion } from 'framer-motion';
import { content } from '../content';
import MotionWrapper from './MotionWrapper';
import PlusCross from './PlusCross';

const About = () => {
  return (
    <section id="about" className="section-pad-sm" style={{ background: 'var(--bg-alt)' }}>
      <div className="container-xl">
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <MotionWrapper direction="up">
            <div className="section-header">
              <h2>{content.about.headline}</h2>
            </div>
          </MotionWrapper>

          <MotionWrapper direction="up" delay={0.1}>
            <p
              style={{
                fontSize: '1.05rem',
                color: 'var(--text-muted)',
                lineHeight: 1.8,
                marginBottom: '3rem',
                fontWeight: 300,
              }}
            >
              {content.about.body}
            </p>
          </MotionWrapper>

          <div className="grid-2">
            {content.about.values.map((value, i) => (
              <motion.div
                key={i}
                style={{
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start',
                  padding: '1.25rem',
                  borderTop: '1px solid var(--border)',
                }}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.3 }}
                transition={{ duration: 0.35, delay: i * 0.08 }}
              >
                <PlusCross
                  size={14}
                  style={{
                    color: 'var(--text-muted)',
                    flexShrink: 0,
                    marginTop: '2px',
                  }}
                />
                <div>
                  <h3 style={{ fontSize: '1rem', marginBottom: '0.35rem', fontWeight: 400 }}>
                    {value.title}
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                    {value.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;