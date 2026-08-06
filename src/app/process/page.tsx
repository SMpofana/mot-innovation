import type { Metadata } from 'next';
import Link from 'next/link';
import Breadcrumbs from '../../components/Breadcrumbs';
import Process from '../../components/Process';
import { content } from '../../content';

export const metadata: Metadata = {
  title: 'Process — M.O.T Innovation',
  description:
    'A proven 4-step process to build marketing intelligence infrastructure: audit and map your current stack, design and build the architecture, integrate and automate, then monitor and optimize continuously.',
  alternates: { canonical: 'https://motinnovation.co.za/process' },
  openGraph: {
    title: 'Process — M.O.T Innovation',
    description:
      'From scattered marketing to intelligent infrastructure in four steps: Audit & Map, Design & Build, Integrate & Automate, Monitor & Optimize.',
    url: 'https://motinnovation.co.za/process',
    type: 'website',
  },
  keywords: [
    'marketing infrastructure process',
    'marketing audit',
    'marketing systems design',
    'marketing automation setup',
    'campaign optimization process',
    'how to build marketing infrastructure',
  ],
};

export default function ProcessPage() {
  return (
    <article>
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Process', href: '/process' },
        ]}
      />

      <section className="section-pad" style={{ paddingTop: '2rem' }}>
        <div className="container-xl">
          {/* Page header */}
          <div className="section-header" style={{ marginBottom: '3rem' }}>
            <span className="text-eyebrow">How We Work</span>
            <h1 style={{ marginTop: '1rem' }}>Process</h1>
            <p style={{ marginTop: '1rem' }}>
              A proven 4-step process to go from scattered marketing to intelligent infrastructure.
            </p>
          </div>

          {/* Detailed timeline */}
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {content.process.steps.map((step, i) => (
              <section key={i} className="tile" style={{ position: 'relative' }}>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'auto 1fr',
                    gap: '2rem',
                    alignItems: 'start',
                  }}
                >
                  {/* Step number */}
                  <div
                    style={{
                      width: '4rem',
                      height: '4rem',
                      borderRadius: '50%',
                      border: '1px solid var(--border)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '1.25rem',
                      fontWeight: 300,
                      fontVariantNumeric: 'tabular-nums',
                      color: 'var(--text)',
                      flexShrink: 0,
                    }}
                  >
                    {step.number}
                  </div>

                  {/* Step content */}
                  <div>
                    <h2 style={{ fontSize: '1.35rem', fontWeight: 400, marginBottom: '0.75rem' }}>
                      {step.title}
                    </h2>
                    <p
                      style={{
                        color: 'var(--text-muted)',
                        fontSize: '0.95rem',
                        lineHeight: 1.7,
                      }}
                    >
                      {step.description}
                    </p>
                  </div>
                </div>
              </section>
            ))}
          </div>

          {/* Interactive process component */}
          <div style={{ marginTop: '3rem' }}>
            <Process />
          </div>
        </div>
      </section>

      {/* Internal links */}
      <section className="section-pad-sm" style={{ background: 'var(--bg-alt)' }}>
        <div className="container-xl" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '1.5rem' }}>
            See how it translates to results.
          </h2>
          <div style={{ display: 'inline-flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link href="/services" className="btn btn-secondary">
              Explore Services
            </Link>
            <Link href="/services" className="btn btn-secondary">
              View Pricing
            </Link>
            <Link href="/contact" className="btn btn-primary">
              Start Your Audit
            </Link>
          </div>
        </div>
      </section>
    </article>
  );
}