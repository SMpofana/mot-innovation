import type { Metadata } from 'next';
import Breadcrumbs from '../../components/Breadcrumbs';

export const metadata: Metadata = {
  title: 'Terms of Service',
  description: 'The terms and conditions for using M.O.T Innovation services and website. No account required, transparent pricing, you own everything we build.',
  alternates: { canonical: 'https://motinnovation.co.za/terms' },
};

export default function TermsPage() {
  return (
    <article className="section-pad" style={{ background: 'var(--bg)' }}>
      <div className="container-xl" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Breadcrumbs items={[
          { label: 'Home', href: '/' },
          { label: 'Terms of Service', href: '/terms' },
        ]} />

        <div style={{ paddingTop: '2rem' }}>
          <span className="text-eyebrow">Legal</span>
          <h1 style={{ marginTop: '1rem', marginBottom: '2rem' }}>Terms of Service</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '3rem' }}>
            Last updated: August 2026
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>1. Services</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                M.O.T Innovation provides marketing intelligence infrastructure services including:
                digital asset management (DAM) system setup, multi-channel content delivery pipeline
                configuration, performance tracking dashboard implementation, and campaign optimization
                framework installation. We build systems — we do not provide ongoing campaign management
                or advertising services.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>2. No Account Required</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                You do not need to create an account to browse our website, read our content, or request
                a consultation. All engagements start with a free 30-minute consultation. No registration,
                no password, no login required.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>3. Pricing</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                Our pricing is transparent: Infrastructure Audit ($500 one-time), Intelligence Build
                ($2,500–$5,000 project-based), and Intelligence Partner ($1,000+/month retainer).
                All prices are in USD. We reserve the right to change pricing with 30 days notice.
                Existing engagements are not affected by price changes.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>4. You Own Everything We Build</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                All infrastructure, systems, dashboards, and configurations we build for you are your
                property. We use open standards and work with whatever platforms you already use.
                There is no vendor lock-in, no proprietary platform requirement, and no black box.
                You receive full documentation and training for everything we build.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>5. Payment Terms</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                For the Infrastructure Audit, payment is due before the audit begins. For the
                Intelligence Build, 50% is due at project start and 50% at completion. For the
                Intelligence Partner retainer, payment is due monthly in advance. All payments
                are processed through Stripe.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>6. Refund Policy</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                The Infrastructure Audit is non-refundable once the audit has begun. The Intelligence
                Build includes a 30-day support period — if you are not satisfied with the delivered
                infrastructure within 30 days of completion, we will fix any issues at no additional
                cost. The Intelligence Partner retainer can be cancelled with 30 days notice.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>7. Confidentiality</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                We treat all client information as confidential. We will not share your business data,
                marketing strategies, or infrastructure details with any third party without your
                explicit consent. We may use anonymized case study data (e.g., "E-commerce Brand:
                80% reduction in time-to-publish") without identifying you specifically.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>8. Limitation of Liability</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                M.O.T Innovation is not liable for any indirect, incidental, or consequential damages
                arising from the use of the systems we build. Our total liability is limited to the
                amount paid for the specific engagement that gave rise to the claim. We are not
                responsible for third-party platform outages, API changes, or service disruptions.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>9. Contact</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                For questions about these terms, contact us at hello@motinnovation.co.za.
              </p>
            </section>
          </div>
        </div>
      </div>
    </article>
  );
}