'use client';

import { motion } from 'framer-motion';
import { content } from '../content';
import MotionWrapper from './MotionWrapper';
import PlusCross from './PlusCross';

const Pricing = () => {
  const scrollToContact = () => {
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section id="pricing" className="section-pad-lg" style={{ background: 'var(--bg-alt)' }}>
      <div className="container-xl">
        <MotionWrapper direction="up">
          <div className="section-header">
            <h2>{content.pricing.headline}</h2>
            <p>{content.pricing.subhead}</p>
          </div>
        </MotionWrapper>

        <div className="grid-cards" style={{ maxWidth: '1000px', margin: '0 auto' }}>
          {content.pricing.plans.map((plan, i) => (
            <motion.div
              key={i}
              className={plan.popular ? 'tile-cream' : 'tile-bordered'}
              style={{
                display: 'flex',
                flexDirection: 'column',
                padding: '2rem',
                position: 'relative',
                borderColor: plan.popular ? 'transparent' : 'var(--border)',
              }}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.4, delay: i * 0.1, ease: 'easeOut' }}
              whileHover={{ y: -4 }}
            >
              {/* Plus cross accent at top-right corner */}
              <PlusCross
                size={12}
                style={{
                  position: 'absolute',
                  top: 12,
                  right: 12,
                  color: plan.popular ? 'var(--text-dark)' : 'var(--text-muted)',
                  opacity: 0.4,
                }}
              />

              {/* Popular badge */}
              {plan.popular && (
                <div
                  style={{
                    fontSize: '0.7rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.12em',
                    color: 'var(--text-dark)',
                    opacity: 0.5,
                    marginBottom: '0.75rem',
                    fontWeight: 400,
                  }}
                >
                  Most Popular
                </div>
              )}

              <div style={{ marginBottom: '1rem' }}>
                <h3
                  style={{
                    fontSize: '1.15rem',
                    marginBottom: '0.5rem',
                    fontWeight: 400,
                    color: plan.popular ? 'var(--text-dark)' : 'var(--text)',
                  }}
                >
                  {plan.name}
                </h3>
                <p
                  style={{
                    fontSize: '0.85rem',
                    color: plan.popular ? 'var(--text-dark)' : 'var(--text-muted)',
                    opacity: plan.popular ? 0.6 : 1,
                    minHeight: '2.5rem',
                    lineHeight: 1.5,
                  }}
                >
                  {plan.description}
                </p>
              </div>

              <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
                <span
                  style={{
                    fontSize: '1.75rem',
                    fontWeight: 300,
                    fontVariantNumeric: 'tabular-nums',
                    letterSpacing: '-0.02em',
                    color: plan.popular ? 'var(--text-dark)' : 'var(--text)',
                  }}
                >
                  {plan.price}
                </span>
                <span
                  style={{
                    color: plan.popular ? 'var(--text-dark)' : 'var(--text-light)',
                    opacity: plan.popular ? 0.5 : 1,
                    fontSize: '0.8rem',
                  }}
                >
                  {plan.period}
                </span>
              </div>

              <ul style={{ listStyle: 'none', padding: 0, flex: 1, marginBottom: '1.5rem' }}>
                {plan.features.map((feature, j) => (
                  <motion.li
                    key={j}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.6rem',
                      padding: '0.5rem 0',
                      fontSize: '0.875rem',
                      color: plan.popular ? 'var(--text-dark)' : 'var(--text)',
                    }}
                    initial={{ opacity: 0, y: 6 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.15 + j * 0.04, duration: 0.25 }}
                  >
                    <PlusCross
                      size={9}
                      style={{
                        color: plan.popular ? 'var(--text-dark)' : 'var(--text-muted)',
                        opacity: 0.5,
                        marginTop: '4px',
                      }}
                    />
                    <span style={{ opacity: plan.popular ? 0.8 : 1 }}>{feature}</span>
                  </motion.li>
                ))}
              </ul>

              <motion.button
                onClick={scrollToContact}
                className={plan.popular ? 'btn btn-primary w-full' : 'btn btn-secondary w-full'}
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
              >
                {plan.cta}
              </motion.button>
            </motion.div>
          ))}
        </div>

        <MotionWrapper direction="fade" delay={0.3}>
          <p style={{ textAlign: 'center', color: 'var(--text-light)', fontSize: '0.8rem', marginTop: '2rem' }}>
            {content.pricing.note}
          </p>
        </MotionWrapper>
      </div>
    </section>
  );
};

export default Pricing;