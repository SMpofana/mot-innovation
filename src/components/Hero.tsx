'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import BookingButton from './BookingButton';
import { content } from '../content';
import CharText from './CharText';
import PlusCross from './PlusCross';
import AnimatedCounter from './AnimatedCounter';

const Hero = () => {
  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center justify-center overflow-hidden"
      style={{ background: 'var(--bg)' }}
    >
      {/* Grid overlay */}
      <div className="grid-overlay" />

      {/* Corner plus marks */}
      <div style={{ position: 'absolute', top: '5rem', left: '1.5rem', color: 'var(--text-light)' }}>
        <PlusCross />
      </div>
      <div style={{ position: 'absolute', top: '5rem', right: '1.5rem', color: 'var(--text-light)' }}>
        <PlusCross />
      </div>
      <div style={{ position: 'absolute', bottom: '2rem', left: '1.5rem', color: 'var(--text-light)' }}>
        <PlusCross />
      </div>
      <div style={{ position: 'absolute', bottom: '2rem', right: '1.5rem', color: 'var(--text-light)' }}>
        <PlusCross />
      </div>

      <div className="container-xl relative z-10" style={{ paddingTop: '8rem', paddingBottom: '6rem' }}>
        <div className="text-center" style={{ maxWidth: '900px', margin: '0 auto' }}>
          {/* Eyebrow */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            style={{ marginBottom: '2rem' }}
          >
            <span className="text-eyebrow">{content.hero.badge}</span>
          </motion.div>

          {/* Headline — char-by-char reveal (PAS: Problem) */}
          <h1 className="text-display" style={{ marginBottom: '1.5rem' }}>
            <CharText
              text="Your marketing"
              as="span"
              delay={0.2}
            />
            <br />
            <CharText
              text="stack doesn't"
              as="span"
              delay={0.6}
            />
            <br />
            <span style={{ color: 'var(--text-muted)', fontWeight: 300 }}>
              <CharText
                text="talk to itself."
                as="span"
                delay={1.1}
              />
            </span>
          </h1>

          {/* Subhead */}
          <motion.p
            style={{
              fontSize: '1.05rem',
              color: 'var(--text-muted)',
              maxWidth: '600px',
              margin: '0 auto 3rem',
              lineHeight: 1.7,
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.6 }}
          >
            {content.hero.subhead}
          </motion.p>

          {/* CTAs */}
          <motion.div
            className="flex flex-wrap gap-3 justify-center"
            style={{ marginBottom: '5rem' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.8 }}
          >
            <BookingButton label={content.hero.primaryCTA} />
            <Link href="/services" className="btn btn-secondary">
              {content.hero.secondaryCTA}
            </Link>
          </motion.div>

          {/* Stats — count-up on scroll into view with easeOut */}
          <motion.div
            className="grid grid-cols-2 md:grid-cols-4 gap-px"
            style={{
              maxWidth: '800px',
              margin: '0 auto',
              background: 'var(--border)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 2 }}
          >
            {content.hero.stats.map((stat, i) => (
              <AnimatedCounter
                key={i}
                value={stat.value}
                label={stat.label}
                delay={i * 0.2}
              />
            ))}
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 -translate-x-1/2 pointer-events-none"
        style={{ color: 'var(--text-light)' }}
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
          <path d="M12 5v14M19 12l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </motion.div>
    </section>
  );
};

export default Hero;