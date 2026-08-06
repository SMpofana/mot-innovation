import type { Metadata } from 'next';
import Breadcrumbs from '../../components/Breadcrumbs';

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'How M.O.T Innovation collects, uses, and protects your personal data. We do not require accounts, do not sell your data, and only use your information to provide our services.',
  alternates: { canonical: 'https://motinnovation.co.za/privacy' },
};

export default function PrivacyPage() {
  return (
    <article className="section-pad" style={{ background: 'var(--bg)' }}>
      <div className="container-xl" style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Breadcrumbs items={[
          { label: 'Home', href: '/' },
          { label: 'Privacy Policy', href: '/privacy' },
        ]} />

        <div style={{ paddingTop: '2rem' }}>
          <span className="text-eyebrow">Legal</span>
          <h1 style={{ marginTop: '1rem', marginBottom: '2rem' }}>Privacy Policy</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '3rem' }}>
            Last updated: August 2026
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>1. Information We Collect</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                When you contact us through our website form, we collect the information you provide:
                your name, email address, business name, business stage, and your message. We also
                collect technical data automatically, including your IP address, browser type, and
                the pages you visit. If you arrive via a link from YouTube, LinkedIn, or other content,
                we capture UTM parameters to understand which content brought you here.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>2. How We Use Your Information</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                We use your information to: respond to your consultation request, send you our lead
                nurturing email sequence (if you request a consultation), improve our content and
                services, and track which marketing content drives leads so we can optimize our content.
                We do not use your data for advertising or sell it to third parties.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>3. No Account Required</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                We do not require you to create an account to use our website or request a consultation.
                You can contact us once and we will respond within 24 hours. You will not be added to
                any ongoing mailing list unless you explicitly request a consultation.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>4. Cookies</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                We use a single first-party cookie to remember UTM parameters (which content source
                brought you to our site) for up to 30 days. This cookie is httpOnly, does not track
                you across other websites, and is not used for advertising. We do not use third-party
                tracking cookies, Google Analytics, or Facebook Pixel.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>5. Data Storage</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                Lead data is stored securely in our content management system. We do not store
                credit card information on our servers — all payments are processed through
                third-party payment processors (Stripe) that are PCI-DSS compliant.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>6. Your Rights</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                You have the right to: request a copy of your data, request deletion of your data,
                opt out of our email sequence at any time, and request that we stop processing your
                data. To exercise any of these rights, email hello@motinnovation.co.za.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>7. Third-Party Services</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                We may use the following third-party services to provide our services: Sanity CMS
                (content storage), YouTube Data API (video publishing), LinkedIn API (content
                publishing), Google Gemini API (content generation), and Stripe (payment processing).
                Each of these services has their own privacy policy governing how they handle data.
              </p>
            </section>

            <section>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>8. Contact</h2>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.7 }}>
                For privacy questions or requests, contact us at hello@motinnovation.co.za.
                M.O.T Innovation is based in Johannesburg, South Africa.
              </p>
            </section>
          </div>
        </div>
      </div>
    </article>
  );
}