'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { content } from '../content';
import MotionWrapper from './MotionWrapper';
import PlusCross from './PlusCross';

const Services = () => {
  const [activeId, setActiveId] = useState(content.services.items[0].id);
  const activeService = content.services.items.find((s) => s.id === activeId)!;

  return (
    <section id="services" className="section-pad-lg" style={{ background: 'var(--bg-alt)' }}>
      <div className="container-xl">
        <MotionWrapper direction="up">
          <div className="section-header">
            <h2>{content.services.headline}</h2>
            <p>{content.services.subhead}</p>
          </div>
        </MotionWrapper>

        {/* Minimal tab buttons with underline indicator */}
        <MotionWrapper direction="up" delay={0.1}>
          <div
            className="flex flex-wrap justify-center gap-0"
            style={{ marginBottom: '3rem', borderBottom: '1px solid var(--border)', maxWidth: '900px', margin: '0 auto 3rem' }}
          >
            {content.services.items.map((service) => {
              const isActive = activeId === service.id;
              return (
                <button
                  key={service.id}
                  onClick={() => setActiveId(service.id)}
                  className="relative"
                  style={{
                    padding: '1rem 1.5rem',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: isActive ? 'var(--text)' : 'var(--text-muted)',
                    fontSize: '0.8rem',
                    fontWeight: 400,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em',
                    borderBottom: isActive ? '2px solid var(--accent)' : '2px solid transparent',
                    transition: 'color 0.2s ease, border-color 0.2s ease',
                  }}
                >
                  {service.title}
                </button>
              );
            })}
          </div>
        </MotionWrapper>

        {/* Active service detail — cream card with plus cross corners */}
        <div style={{ maxWidth: '900px', margin: '0 auto', position: 'relative' }}>
          {/* Plus cross at corners */}
          <PlusCross size={13} style={{ position: 'absolute', top: -6, left: -6, color: 'var(--text-muted)' }} />
          <PlusCross size={13} style={{ position: 'absolute', top: -6, right: -6, color: 'var(--text-muted)' }} />
          <PlusCross size={13} style={{ position: 'absolute', bottom: -6, left: -6, color: 'var(--text-muted)' }} />
          <PlusCross size={13} style={{ position: 'absolute', bottom: -6, right: -6, color: 'var(--text-muted)' }} />

          <div
            className="tile-cream"
            style={{
              padding: '0',
              overflow: 'hidden',
            }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activeId}
                style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              >
                {/* Left: description */}
                <div style={{ padding: '2.5rem' }}>
                  <div
                    style={{
                      fontSize: '2rem',
                      marginBottom: '1rem',
                      lineHeight: 1,
                    }}
                  >
                    {activeService.icon}
                  </div>
                  <h3 style={{ marginBottom: '1rem', fontWeight: 400, color: 'var(--text-dark)' }}>{activeService.title}</h3>
                  <p style={{ color: 'var(--text-dark)', opacity: 0.7, fontSize: '1rem', marginBottom: '1.5rem', lineHeight: 1.6 }}>
                    {activeService.description}
                  </p>
                  <div
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.5rem 1rem',
                      background: 'transparent',
                      borderRadius: '0.5rem',
                      fontSize: '0.8rem',
                      color: 'var(--text-dark)',
                      fontWeight: 400,
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                      marginBottom: '0.5rem',
                      border: '1px solid rgba(26,26,26,0.15)',
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <path d="M20 6L9 17l-5-5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    {activeService.deliverable}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dark)', opacity: 0.5, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                    Timeline — {activeService.timeline}
                  </div>
                </div>

                {/* Right: features list */}
                <div
                  style={{
                    padding: '2.5rem',
                    background: 'rgba(26,26,26,0.04)',
                    borderLeft: '1px solid rgba(26,26,26,0.1)',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.75rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.12em',
                      marginBottom: '1.5rem',
                      color: 'var(--text-dark)',
                      opacity: 0.5,
                    }}
                  >
                    What's Included
                  </div>
                  <ul style={{ listStyle: 'none', padding: 0 }}>
                    {activeService.features.map((feature, i) => (
                      <motion.li
                        key={i}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '0.75rem',
                          padding: '0.6rem 0',
                          borderBottom: i < activeService.features.length - 1 ? '1px solid rgba(26,26,26,0.08)' : 'none',
                        }}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 + i * 0.05, duration: 0.3 }}
                      >
                        <PlusCross size={10} style={{ color: 'var(--text-dark)', opacity: 0.4, marginTop: '4px' }} />
                        <span style={{ fontSize: '0.9rem', color: 'var(--text-dark)', fontWeight: 400 }}>{feature}</span>
                      </motion.li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Responsive: stack on mobile */}
      <style>{`
        @media (max-width: 768px) {
          section#services .tile-cream > div { grid-template-columns: 1fr !important; }
          section#services .tile-cream > div > div:last-child {
            border-left: none !important;
            border-top: 1px solid rgba(26,26,26,0.1);
          }
        }
      `}</style>
    </section>
  );
};

export default Services;