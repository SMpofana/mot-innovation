import type { Metadata } from 'next';
import Link from 'next/link';
import Breadcrumbs from '../../components/Breadcrumbs';
import About from '../../components/About';
import PlusCross from '../../components/PlusCross';
import { content } from '../../content';

export const metadata: Metadata = {
  title: 'About — M.O.T Innovation',
  description:
    'M.O.T Innovation builds marketing intelligence infrastructure — not advice, but actual systems. We design, build, and maintain DAM, delivery pipelines, tracking dashboards, and optimization tools that modern businesses need to compete.',
  alternates: { canonical: 'https://motinnovation.co.za/about' },
  openGraph: {
    title: 'About M.O.T Innovation',
    description:
      'Marketing should be intelligent by design, not by accident. We build the systems — not recommendations — that connect your marketing infrastructure into one intelligent pipeline.',
    url: 'https://motinnovation.co.za/about',
    type: 'website',
  },
  keywords: [
    'about M.O.T Innovation',
    'marketing intelligence company',
    'marketing infrastructure builder',
    'Johannesburg marketing',
    'South Africa marketing automation',
    'marketing systems integrator',
  ],
};

export default function AboutPage() {
  return (
    <article>
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'About', href: '/about' },
        ]}
      />

      <section className="section-pad" style={{ paddingTop: '2rem' }}>
        <div className="container-xl" style={{ maxWidth: '800px', margin: '0 auto' }}>
          {/* Page header */}
          <div className="section-header" style={{ marginBottom: '2.5rem' }}>
            <span className="text-eyebrow">Our Story</span>
            <h1 style={{ marginTop: '1rem' }}>About M.O.T Innovation</h1>
          </div>

          {/* Body */}
          <p
            style={{
              fontSize: '1.1rem',
              color: 'var(--text-muted)',
              lineHeight: 1.8,
              marginBottom: '3rem',
              fontWeight: 300,
            }}
          >
            {content.about.body}
          </p>

          {/* Values */}
          <section>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '2rem' }}>
              What We Value
            </h2>
            <div className="grid-2">
              {content.about.values.map((value, i) => (
                <div
                  key={i}
                  className="tile"
                  style={{
                    display: 'flex',
                    gap: '1rem',
                    alignItems: 'flex-start',
                  }}
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
                </div>
              ))}
            </div>
          </section>

          {/* Why choose us section */}
          <section style={{ marginTop: '3rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '2rem' }}>
              Why M.O.T Innovation
            </h2>
            <div className="grid-2">
              {content.proof.benefits.map((benefit, i) => (
                <div key={i} className="tile" style={{ position: 'relative' }}>
                  <PlusCross
                    size={12}
                    style={{
                      position: 'absolute',
                      top: 12,
                      right: 12,
                      color: 'var(--text-muted)',
                      opacity: 0.4,
                    }}
                  />
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', fontWeight: 400 }}>
                    {benefit.title}
                  </h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                    {benefit.description}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>

      {/* Internal links */}
      <section className="section-pad-sm" style={{ background: 'var(--bg-alt)' }}>
        <div className="container-xl" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '1.5rem' }}>
            Let&apos;s build your marketing intelligence.
          </h2>
          <div style={{ display: 'inline-flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link href="/services" className="btn btn-secondary">
              Explore Services
            </Link>
            <Link href="/services" className="btn btn-secondary">
              View Pricing
            </Link>
            <Link href="/contact" className="btn btn-primary">
              Get in Touch
            </Link>
          </div>
        </div>
      </section>
    </article>
  );
}