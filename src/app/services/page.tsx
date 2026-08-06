import type { Metadata } from 'next';
import Link from 'next/link';
import Breadcrumbs from '../../components/Breadcrumbs';
import Services from '../../components/Services';
import PlusCross from '../../components/PlusCross';
import BookingButton from '../../components/BookingButton';
import { content } from '../../content';

export const metadata: Metadata = {
  title: 'Services — M.O.T Innovation',
  description:
    'Marketing intelligence infrastructure services: digital asset management (DAM), multi-endpoint content delivery, unified performance tracking dashboards, and automated campaign optimization.',
  alternates: { canonical: 'https://motinnovation.co.za/services' },
  openGraph: {
    title: 'Services — M.O.T Innovation',
    description:
      'Four pillars of marketing intelligence: DAM systems, multi-channel delivery, performance dashboards, and campaign optimization — built as one connected system.',
    url: 'https://motinnovation.co.za/services',
    type: 'website',
  },
  keywords: [
    'marketing infrastructure services',
    'digital asset management setup',
    'multi-channel content delivery',
    'performance tracking dashboard',
    'campaign optimization services',
    'DAM system',
    'marketing automation',
  ],
};

export default function ServicesPage() {
  return (
    <article>
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Services', href: '/services' },
        ]}
      />

      <section className="section-pad" style={{ paddingTop: '2rem' }}>
        <div className="container-xl">
          {/* Page header */}
          <div className="section-header" style={{ marginBottom: '3rem' }}>
            <span className="text-eyebrow">What We Build</span>
            <h1 style={{ marginTop: '1rem' }}>Services</h1>
            <p style={{ marginTop: '1rem' }}>
              Four pillars of marketing intelligence that work together as one system.
            </p>
          </div>

          {/* Detailed service tiles */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '900px', margin: '0 auto' }}>
            {content.services.items.map((service, i) => (
              <section key={service.id} className="tile" style={{ position: 'relative' }}>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'auto 1fr',
                    gap: '1.5rem',
                    alignItems: 'start',
                  }}
                >
                  <div
                    style={{
                      fontSize: '2rem',
                      lineHeight: 1,
                      marginTop: '0.25rem',
                    }}
                  >
                    {service.icon}
                  </div>
                  <div>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        marginBottom: '0.5rem',
                      }}
                    >
                      <h2 style={{ fontSize: '1.35rem', fontWeight: 400, margin: 0 }}>
                        {service.title}
                      </h2>
                      <span
                        style={{
                          fontSize: '0.7rem',
                          textTransform: 'uppercase',
                          letterSpacing: '0.12em',
                          color: 'var(--text-muted)',
                          border: '1px solid var(--border)',
                          borderRadius: '0.25rem',
                          padding: '0.2rem 0.6rem',
                        }}
                      >
                        {service.timeline}
                      </span>
                    </div>
                    <p
                      style={{
                        color: 'var(--text-muted)',
                        fontSize: '0.95rem',
                        lineHeight: 1.6,
                        marginBottom: '1.25rem',
                      }}
                    >
                      {service.description}
                    </p>

                    <div
                      style={{
                        fontSize: '0.7rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.12em',
                        color: 'var(--text-muted)',
                        marginBottom: '0.75rem',
                      }}
                    >
                      What&apos;s Included
                    </div>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                      {service.features.map((feature, j) => (
                        <li
                          key={j}
                          style={{
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: '0.6rem',
                            fontSize: '0.85rem',
                            color: 'var(--text)',
                          }}
                        >
                          <PlusCross
                            size={9}
                            style={{ color: 'var(--text-muted)', opacity: 0.5, marginTop: '4px', flexShrink: 0 }}
                          />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>

                    <div
                      style={{
                        marginTop: '1.25rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        border: '1px solid var(--border)',
                        borderRadius: '0.375rem',
                        fontSize: '0.8rem',
                        color: 'var(--text-muted)',
                        fontWeight: 400,
                      }}
                    >
                      <PlusCross size={10} style={{ color: 'var(--text-muted)', opacity: 0.6 }} />
                      {service.deliverable}
                    </div>
                  </div>
                </div>
              </section>
            ))}
          </div>

          {/* Interactive tabs section (existing component) */}
          <div style={{ marginTop: '4rem' }}>
            <Services />
          </div>
        </div>
      </section>

      {/* Pricing section */}
      <section className="section-pad" style={{ background: 'var(--bg-alt)', borderTop: '1px solid var(--border)' }}>
        <div className="container-xl">
          <div className="section-header" style={{ marginBottom: '3rem' }}>
            <span className="text-eyebrow">Engagement Models</span>
            <h2 style={{ marginTop: '1rem' }}>Pricing</h2>
            <p style={{ marginTop: '1rem' }}>
              Flexible options — from a single audit to full infrastructure partnership.
            </p>
          </div>

          <div className="grid-cards" style={{ maxWidth: '1000px', margin: '0 auto' }}>
            {content.pricing.plans.map((plan, i) => (
              <section
                key={i}
                className={plan.popular ? 'tile-cream' : 'tile-bordered'}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                }}
              >
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

                <div
                  style={{
                    marginBottom: '1.5rem',
                    display: 'flex',
                    alignItems: 'baseline',
                    gap: '0.5rem',
                  }}
                >
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
                    <li
                      key={j}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.6rem',
                        padding: '0.5rem 0',
                        fontSize: '0.875rem',
                        color: plan.popular ? 'var(--text-dark)' : 'var(--text)',
                      }}
                    >
                      <PlusCross
                        size={9}
                        style={{
                          color: plan.popular ? 'var(--text-dark)' : 'var(--text-muted)',
                          opacity: 0.5,
                          marginTop: '4px',
                          flexShrink: 0,
                        }}
                      />
                      <span style={{ opacity: plan.popular ? 0.8 : 1 }}>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/contact"
                  className={plan.popular ? 'btn btn-cream' : 'btn btn-secondary'}
                  style={{ width: '100%' }}
                >
                  {plan.cta}
                </Link>
              </section>
            ))}
          </div>

          <p
            style={{
              textAlign: 'center',
              color: 'var(--text-light)',
              fontSize: '0.8rem',
              marginTop: '2rem',
            }}
          >
            {content.pricing.note}
          </p>
        </div>
      </section>

      {/* Internal links */}
      <section className="section-pad-sm" style={{ background: 'var(--bg)' }}>
        <div className="container-xl" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '1.5rem' }}>
            Ready to get started?
          </h2>
          <div style={{ display: 'inline-flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link href="/process" className="btn btn-secondary">
              Our Process
            </Link>
            <BookingButton label="Get a Consultation" />
          </div>
        </div>
      </section>

      <style>{`
        @media (max-width: 768px) {
          article ul[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </article>
  );
}