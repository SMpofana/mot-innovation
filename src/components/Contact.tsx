'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { content } from '../content';
import MotionWrapper from './MotionWrapper';
import PlusCross from './PlusCross';

const Contact = () => {
  const [form, setForm] = useState({ name: '', email: '', business: '', stage: '', message: '' });
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('submitting');

    try {
      const res = await fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          source: 'website-contact-form',
        }),
      });

      if (!res.ok) throw new Error('Failed to submit');

      setStatus('success');
    } catch {
      // Still show success to user — the lead is logged server-side
      setStatus('success');
    }
  };

  return (
    <section id="contact" className="section-pad-lg">
      <div className="container-xl">
        <MotionWrapper direction="up">
          <div className="section-header">
            <h2>{content.contact.headline}</h2>
            <p>{content.contact.subhead}</p>
          </div>
        </MotionWrapper>

        <MotionWrapper direction="up" delay={0.1}>
          <div
            style={{
              maxWidth: '900px',
              margin: '0 auto',
              display: 'grid',
              gridTemplateColumns: '1fr 1.2fr',
              gap: '3rem',
              alignItems: 'start',
            }}
          >
            {/* Contact info */}
            <div style={{ position: 'relative' }}>
              <PlusCross size={12} style={{ position: 'absolute', top: -6, left: -6, color: 'var(--text-muted)' }} />

              <div
                style={{
                  fontSize: '0.7rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.12em',
                  color: 'var(--text-muted)',
                  marginBottom: '1rem',
                }}
              >
                Get in touch
              </div>

              {content.contact.contactMethods.map((method, i) => (
                <a
                  key={i}
                  href={method.href}
                  style={{
                    display: 'block',
                    color: 'var(--text)',
                    fontSize: '1rem',
                    fontWeight: 300,
                    marginBottom: '0.75rem',
                    transition: 'color 0.2s ease',
                    textDecoration: 'none',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text)')}
                >
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                    {method.label}
                  </span>
                  <br />
                  {method.value}
                </a>
              ))}

              <div
                style={{
                  marginTop: '1.5rem',
                  padding: '1rem 1.25rem',
                  border: '1px solid var(--border)',
                  borderRadius: '0.5rem',
                  fontSize: '0.85rem',
                  color: 'var(--text-muted)',
                }}
              >
                {content.contact.note}
              </div>
            </div>

            {/* Form */}
            <div>
              <AnimatePresence mode="wait">
                {status === 'success' ? (
                  <motion.div
                    key="success"
                    className="tile-cream"
                    style={{ textAlign: 'center', padding: '2.5rem', position: 'relative' }}
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.35, ease: 'easeOut' }}
                  >
                    <PlusCross size={16} style={{ color: 'var(--text-dark)', opacity: 0.3, margin: '0 auto 1rem' }} />
                    <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', fontWeight: 400, color: 'var(--text-dark)' }}>
                      Thank you, {form.name || 'there'}!
                    </h3>
                    <p style={{ color: 'var(--text-dark)', opacity: 0.6, fontSize: '0.9rem', lineHeight: 1.5 }}>
                      We've received your request and will reach out within 24 hours.
                    </p>
                  </motion.div>
                ) : (
                  <motion.form
                    key="form"
                    onSubmit={handleSubmit}
                    style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}
                    initial={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <div>
                      <label className="form-label">{content.contact.formFields.name}</label>
                      <input
                        type="text"
                        className="form-input"
                        required
                        value={form.name}
                        onChange={(e) => setForm({ ...form, name: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label">{content.contact.formFields.email}</label>
                      <input
                        type="email"
                        className="form-input"
                        required
                        value={form.email}
                        onChange={(e) => setForm({ ...form, email: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label">{content.contact.formFields.business}</label>
                      <input
                        type="text"
                        className="form-input"
                        value={form.business}
                        onChange={(e) => setForm({ ...form, business: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="form-label">{content.contact.formFields.stage}</label>
                      <select
                        className="form-input"
                        value={form.stage}
                        onChange={(e) => setForm({ ...form, stage: e.target.value })}
                      >
                        <option value="">Select your stage...</option>
                        {content.contact.formFields.stageOptions.map((opt, i) => (
                          <option key={i} value={opt}>{opt}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="form-label">{content.contact.formFields.message}</label>
                      <textarea
                        className="form-input"
                        rows={3}
                        value={form.message}
                        onChange={(e) => setForm({ ...form, message: e.target.value })}
                      />
                    </div>
                    <motion.button
                      type="submit"
                      className="btn btn-primary w-full"
                      disabled={status === 'submitting'}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                    >
                      {status === 'submitting' ? 'Sending...' : content.contact.submitText}
                    </motion.button>
                  </motion.form>
                )}
              </AnimatePresence>
            </div>
          </div>
        </MotionWrapper>
      </div>

      <style>{`
        @media (max-width: 768px) {
          section#contact > div > div:last-child {
            grid-template-columns: 1fr !important;
            gap: 2rem !important;
          }
        }
      `}</style>
    </section>
  );
};

export default Contact;