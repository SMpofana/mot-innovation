import type { Metadata } from 'next';
import Link from 'next/link';
import Breadcrumbs from '../../components/Breadcrumbs';
import ContactForm from '../../components/ContactForm';
import BookingButton from '../../components/BookingButton';
import PlusCross from '../../components/PlusCross';
import { content } from '../../content';

export const metadata: Metadata = {
  title: 'Contact — M.O.T Innovation',
  description:
    'Book a free 30-minute consultation with M.O.T Innovation. We\'ll map your current marketing infrastructure and show you exactly where the gaps are. No account needed — we respond within 24 hours.',
  alternates: { canonical: 'https://motinnovation.co.za/contact' },
  openGraph: {
    title: 'Contact M.O.T Innovation',
    description:
      'Book a free consultation. We\'ll map your marketing infrastructure and identify gaps. Response within 24 hours, no account required.',
    url: 'https://motinnovation.co.za/contact',
    type: 'website',
  },
  keywords: [
    'contact M.O.T Innovation',
    'marketing infrastructure consultation',
    'free marketing audit',
    'book marketing consultation',
    'Johannesburg marketing contact',
    'marketing infrastructure quote',
  ],
};

export default function ContactPage() {
  return (
    <article>
      <Breadcrumbs
        items={[
          { label: 'Home', href: '/' },
          { label: 'Contact', href: '/contact' },
        ]}
      />

      <section className="section-pad" style={{ paddingTop: '2rem' }}>
        <div className="container-xl">
          {/* Page header */}
          <div className="section-header" style={{ marginBottom: '3rem' }}>
            <span className="text-eyebrow">Get in Touch</span>
            <h1 style={{ marginTop: '1rem' }}>Contact</h1>
            <p style={{ marginTop: '1rem' }}>
              {content.contact.subhead}
            </p>
            <div style={{ marginTop: '1.5rem' }}>
              <BookingButton label="Book a Free Consultation Now" />
            </div>
          </div>

          {/* Contact grid */}
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
            <div className="tile-bordered" style={{ position: 'relative' }}>
              <PlusCross size={12} style={{ position: 'absolute', top: 12, right: 12, color: 'var(--text-muted)', opacity: 0.4 }} />

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
                    textDecoration: 'none',
                  }}
                >
                  <span
                    style={{
                      color: 'var(--text-muted)',
                      fontSize: '0.8rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                    }}
                  >
                    {method.label}
                  </span>
                  <br />
                  {method.value}
                </a>
              ))}

              <div
                style={{
                  marginTop: '1.5rem',
                  fontSize: '0.85rem',
                  color: 'var(--text-muted)',
                }}
              >
                {content.contact.note}
              </div>
            </div>

            {/* Form */}
            <div>
              <ContactForm />
            </div>
          </div>
        </div>
      </section>

      {/* Internal links */}
      <section className="section-pad-sm" style={{ background: 'var(--bg-alt)' }}>
        <div className="container-xl" style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 400, marginBottom: '1.5rem' }}>
            Explore before you reach out.
          </h2>
          <div style={{ display: 'inline-flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link href="/services" className="btn btn-secondary">
              Services
            </Link>
            <Link href="/services" className="btn btn-secondary">
              Pricing
            </Link>
            <Link href="/process" className="btn btn-secondary">
              Our Process
            </Link>
          </div>
        </div>
      </section>

      <style>{`
        @media (max-width: 768px) {
          article section section + div[style*="grid-template-columns: 1fr 1.2fr"],
          article > section > div > div[style*="grid-template-columns: 1fr 1.2fr"] {
            grid-template-columns: 1fr !important;
            gap: 2rem !important;
          }
        }
      `}</style>
    </article>
  );
}