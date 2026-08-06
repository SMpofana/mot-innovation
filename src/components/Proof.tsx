'use client';

import { motion } from 'framer-motion';
import { content } from '../content';
import MotionWrapper from './MotionWrapper';
import PlusCross from './PlusCross';

const Proof = () => {
  return (
    <section id="proof" className="section-pad">
      <div className="container-xl">
        <MotionWrapper direction="up">
          <div className="section-header">
            <h2>{content.proof.headline}</h2>
            <p>{content.proof.subhead}</p>
          </div>
        </MotionWrapper>

        {/* Bento grid — large feature card + smaller cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-16">
          {/* Large card — spans 2 columns and 2 rows */}
          <motion.div
            className="tile md:col-span-2 md:row-span-2"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', position: 'relative' }}
          >
            <PlusCross size={12} style={{ position: 'absolute', top: 12, right: 12, color: 'var(--text-muted)', opacity: 0.4 }} />
            <div>
              <span
                style={{
                  display: 'block',
                  marginBottom: '0.75rem',
                  fontSize: '0.7rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  color: 'var(--text-muted)',
                }}
              >
                Our Philosophy
              </span>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '0.75rem', fontWeight: 400 }}>{content.proof.benefits[0].title}</h3>
              <p style={{ color: 'var(--text-muted)', lineHeight: 1.6, fontSize: '0.95rem' }}>{content.proof.benefits[0].description}</p>
            </div>
            <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {['DAM', 'Delivery', 'Tracking', 'Optimize'].map((tag) => (
                <span
                  key={tag}
                  style={{
                    fontSize: '0.7rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    padding: '0.35rem 0.75rem',
                    border: '1px solid var(--border)',
                    borderRadius: '0.375rem',
                    color: 'var(--text-muted)',
                    fontWeight: 400,
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>

          {/* Smaller cards */}
          {content.proof.benefits.slice(1).map((benefit, i) => (
            <motion.div
              key={i}
              className="tile"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.3 }}
              transition={{ duration: 0.4, delay: (i + 1) * 0.1, ease: 'easeOut' }}
              style={{ position: 'relative' }}
            >
              <PlusCross size={12} style={{ position: 'absolute', top: 12, right: 12, color: 'var(--text-muted)', opacity: 0.4 }} />
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', fontWeight: 400 }}>
                {benefit.title}
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                {benefit.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Case studies with cream result highlight */}
        <MotionWrapper direction="up" delay={0.2}>
          <div style={{ maxWidth: '850px', margin: '0 auto' }}>
            <h3 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '1.25rem', fontWeight: 400 }}>
              Case Studies
            </h3>
            {content.proof.caseStudies.map((cs, i) => (
              <motion.div
                key={i}
                className="tile"
                style={{ marginBottom: '1.5rem', padding: '0', overflow: 'hidden' }}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.4, delay: i * 0.12 }}
              >
                {/* Client header bar */}
                <div
                  style={{
                    padding: '0.75rem 1.5rem',
                    background: 'var(--bg-alt)',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span
                    style={{
                      fontWeight: 400,
                      fontSize: '0.8rem',
                      color: 'var(--text)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                    }}
                  >
                    {cs.client}
                  </span>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.12em',
                      color: 'var(--text-muted)',
                    }}
                  >
                    Case Study
                  </span>
                </div>

                <div style={{ padding: '1.5rem', display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
                  <div className="md:grid-cols-2" style={{ display: 'grid', gap: '1rem' }}>
                    <div>
                      <span
                        style={{
                          display: 'block',
                          marginBottom: '0.25rem',
                          fontSize: '0.7rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.12em',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Challenge
                      </span>
                      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{cs.challenge}</p>
                    </div>
                    <div>
                      <span
                        style={{
                          display: 'block',
                          marginBottom: '0.25rem',
                          fontSize: '0.7rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.12em',
                          color: 'var(--text-muted)',
                        }}
                      >
                        Solution
                      </span>
                      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{cs.solution}</p>
                    </div>
                  </div>

                  {/* Result — cream highlight box */}
                  <div
                    className="tile-cream"
                    style={{
                      borderRadius: '0.5rem',
                      padding: '1rem 1.25rem',
                    }}
                  >
                    <span
                      style={{
                        display: 'block',
                        marginBottom: '0.5rem',
                        fontSize: '0.7rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.12em',
                        color: 'var(--text-dark)',
                        opacity: 0.5,
                      }}
                    >
                      Result
                    </span>
                    <p style={{ fontSize: '0.9rem', fontWeight: 400, color: 'var(--text-dark)', lineHeight: 1.5 }}>
                      {cs.result}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </MotionWrapper>
      </div>

      <style>{`
        @media (min-width: 768px) {
          section#proof .tile > div:last-child > div.md\\\\:grid-cols-2 {
            grid-template-columns: 1fr 1fr;
          }
        }
      `}</style>
    </section>
  );
};

export default Proof;