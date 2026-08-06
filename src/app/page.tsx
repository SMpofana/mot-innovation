import Link from 'next/link';
import type { Metadata } from 'next';
import { content } from '../content';
import Hero from '../components/Hero';
import Marquee from '../components/Marquee';
import BookingButton from '../components/BookingButton';
import { organizationSchema, faqSchema } from '../ai-seo';

export const metadata: Metadata = {
  alternates: { canonical: 'https://motinnovation.co.za' },
};

// Homepage answers 3 questions (marketing psychology: PAS — Problem, Agitate, Solution):
// 1. Why they came to us (pain points) — the frustration that brought them here
// 2. How we help (what we build) — the solution
// 3. What our help does for them (results) — proof & outcomes
// Plus a Work section with case studies (social proof + specificity bias)

export default function Home() {
  return (
    <>
      <Hero />
      <Marquee />

      {/* 1. Why they came to us — pain points (PAS: Problem + Agitate) */}
      <section className="section-pad" style={{ background: 'var(--bg)' }}>
        <div className="container-xl">
          <div className="section-header">
            <span className="text-eyebrow">The Problem</span>
            <h2 style={{ marginTop: '1rem' }}>Your marketing stack is broken — and it's costing you</h2>
            <p>The average marketing team uses 12+ tools. Fewer than half talk to each other. Every week, that disconnection drains time, money, and opportunity.</p>
          </div>

          {/* Loss aversion grid — each tile names the pain + what it costs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-px" style={{ background: 'var(--border)' }}>
            <PainPoint
              title="Assets scattered everywhere"
              description="Product photos on Google Drive, brand files on Dropbox, latest logos on someone's laptop. Nobody can find the right version — so your team recreates it from scratch."
              cost="Hours lost every week searching for files that should take seconds."
            />
            <PainPoint
              title="Posting takes forever"
              description="Manual posting to LinkedIn, Instagram, TikTok, email. Hours spent copy-pasting the same content in different formats, hoping nothing breaks."
              cost="10+ hours per week burned on work a pipeline should handle."
            />
            <PainPoint
              title="Reporting eats your week"
              description="Every month you spend days pulling data from 6 platforms into spreadsheets. By the time leadership sees it, it's already outdated."
              cost="2+ days per month building reports nobody trusts."
            />
            <PainPoint
              title="Ad spend feels like guessing"
              description="You're spending money on ads but can't tell which campaigns actually drive revenue. No A/B testing. No clear ROI. Just a budget that disappears."
              cost="Thousands in ad spend with no idea what's working."
            />
          </div>

          {/* Agitate — the cost of inaction */}
          <div style={{ textAlign: 'center', marginTop: '3rem', maxWidth: '600px', margin: '3rem auto 0' }}>
            <p style={{ fontSize: '1.05rem', color: 'var(--text)', lineHeight: 1.6 }}>
              Every week you stay disconnected, you lose time your team can't get back, money you can't account for, and campaigns you can't prove worked. <span style={{ color: 'var(--text-muted)' }}>The longer this goes on, the harder it gets to fix.</span>
            </p>
          </div>
        </div>
      </section>

      {/* 2. How we help — what we build (PAS: Solution) */}
      <section className="section-pad" style={{ background: 'var(--bg-alt)', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
        <div className="container-xl">
          <div className="section-header">
            <span className="text-eyebrow">How We Help</span>
            <h2 style={{ marginTop: '1rem' }}>We don't advise. We build.</h2>
            <p>Four pillars of marketing intelligence — designed, built, and connected into one system that runs itself.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-px" style={{ background: 'var(--border)' }}>
            <PillarTile
              number="01"
              title="Digital Asset Management"
              description="Centralized DAM with auto-tagging, taxonomy, and cloud storage. One searchable hub for every asset — findable in seconds, not hours."
              href="/services"
            />
            <PillarTile
              number="02"
              title="Multi-Channel Delivery"
              description="Create once, publish everywhere. Pipeline to 10 channels with per-channel formatting and scheduling. No more manual copy-paste."
              href="/services"
            />
            <PillarTile
              number="03"
              title="Performance Dashboards"
              description="Unified dashboards pulling real-time data from every platform. Automated reports. Zero manual spreadsheets. Always current."
              href="/services"
            />
            <PillarTile
              number="04"
              title="Campaign Optimization"
              description="A/B testing frameworks, budget reallocation, automated rules. Campaigns that improve themselves — so your ad spend stops guessing."
              href="/services"
            />
          </div>

          {/* Cognitive fluency — quick summary line */}
          <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              One source. Every channel. Zero manual busywork.
            </p>
          </div>
        </div>
      </section>

      {/* Work section — case studies (social proof + specificity bias) */}
      <section className="section-pad" style={{ background: 'var(--bg)' }}>
        <div className="container-xl">
          <div className="section-header">
            <span className="text-eyebrow">Selected Work</span>
            <h2 style={{ marginTop: '1rem' }}>Real systems. Real results.</h2>
            <p>Three businesses that stopped losing time and money to disconnected marketing. Here's what we built and what it delivered.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-px" style={{ background: 'var(--border)' }}>
            {content.proof.caseStudies.map((cs, i) => (
              <CaseStudyTile
                key={i}
                client={cs.client}
                challenge={cs.challenge}
                solution={cs.solution}
                result={cs.result}
              />
            ))}
          </div>

          <div style={{ textAlign: 'center', marginTop: '2.5rem' }}>
            <Link href="/services" className="btn btn-secondary">
              See How We Work
            </Link>
          </div>
        </div>
      </section>

      {/* 3. What our help does — results */}
      <section className="section-pad" style={{ background: 'var(--bg)' }}>
        <div className="container-xl">
          <div className="section-header">
            <span className="text-eyebrow">What It Does For You</span>
            <h2 style={{ marginTop: '1rem' }}>Working systems, measurable results</h2>
            <p>We don't hand you a slide deck. We hand you the keys to working infrastructure.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-px" style={{ background: 'var(--border)' }}>
            <ResultTile
              metric="80%"
              label="Reduction in time-to-publish"
              detail="E-commerce brand centralized DAM and automated delivery pipeline"
            />
            <ResultTile
              metric="1,248"
              label="Hours Back to Your Team / 4 Yrs"
              detail="Average hours a data analyst saves over 4 years with automated dashboards — time reallocated to strategy, not spreadsheets"
            />
            <ResultTile
              metric="23%"
              label="Conversion rate improvement"
              detail="SaaS startup through systematic A/B testing and optimization rules"
            />
          </div>

          {/* Social proof + specificity */}
          <div style={{ textAlign: 'center', marginTop: '3rem', maxWidth: '680px', margin: '3rem auto 0' }}>
            <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
              From solopreneurs to enterprise teams — the infrastructure grows with you, not against you. Every system we build is designed to run itself, so your team can think instead of copy-paste.
            </p>
          </div>

          <div style={{ textAlign: 'center', marginTop: '3rem' }}>
            <div className="flex flex-wrap gap-3 justify-center">
              <BookingButton />
              <Link href="/services" className="btn btn-secondary">
                Explore Services
              </Link>
              <Link href="/services" className="btn btn-secondary">
                See Services
              </Link>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function PainPoint({ title, description, cost }: { title: string; description: string; cost: string }) {
  return (
    <div className="tile" style={{ background: 'var(--bg)' }}>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 400, marginBottom: '0.75rem' }}>{title}</h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '0.75rem' }}>{description}</p>
      <p style={{ color: 'var(--text)', fontSize: '0.82rem', lineHeight: 1.5, fontWeight: 500 }}>
        {cost}
      </p>
    </div>
  );
}

function PillarTile({ number, title, description, href }: { number: string; title: string; description: string; href: string }) {
  return (
    <Link href={href} className="tile" style={{ background: 'var(--bg)', display: 'block', textDecoration: 'none', color: 'inherit' }}>
      <div style={{ fontSize: '0.7rem', fontWeight: 500, color: 'var(--text-light)', marginBottom: '1rem', fontVariantNumeric: 'tabular-nums' }}>{number}</div>
      <h3 style={{ fontSize: '1.05rem', fontWeight: 400, marginBottom: '0.5rem' }}>{title}</h3>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.6 }}>{description}</p>
    </Link>
  );
}

function CaseStudyTile({ client, challenge, solution, result }: { client: string; challenge: string; solution: string; result: string }) {
  // Extract the key metric from the result string (e.g., "80%", "23%", "3x")
  const metricMatch = result.match(/(\d+%|\d+x|\d,\d+)/);
  const metric = metricMatch ? metricMatch[0] : null;

  return (
    <div className="tile" style={{ background: 'var(--bg)', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Client type */}
      <div>
        <span className="text-eyebrow" style={{ fontSize: '0.65rem', display: 'block', marginBottom: '0.25rem' }}>Client</span>
        <h3 style={{ fontSize: '1rem', fontWeight: 500, marginBottom: 0 }}>{client}</h3>
      </div>

      {/* Challenge */}
      <div>
        <span className="text-eyebrow" style={{ fontSize: '0.65rem', display: 'block', marginBottom: '0.25rem' }}>Challenge</span>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', lineHeight: 1.5 }}>{challenge}</p>
      </div>

      {/* Solution */}
      <div>
        <span className="text-eyebrow" style={{ fontSize: '0.65rem', display: 'block', marginBottom: '0.25rem' }}>Solution</span>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', lineHeight: 1.5 }}>{solution}</p>
      </div>

      {/* Result — cream highlight for the metric */}
      <div className="tile-cream" style={{ marginTop: 'auto', padding: '1.25rem', borderRadius: '0.5rem' }}>
        {metric && (
          <div style={{
            fontSize: '2.5rem',
            fontWeight: 400,
            fontFamily: 'var(--font-playfair-display), Georgia, serif',
            letterSpacing: '-0.03em',
            lineHeight: 1,
            marginBottom: '0.5rem',
            color: 'var(--text-dark)',
            fontVariantNumeric: 'tabular-nums',
          }}>
            {metric}
          </div>
        )}
        <span style={{
          display: 'block',
          fontSize: '0.65rem',
          textTransform: 'uppercase',
          letterSpacing: '0.12em',
          color: 'var(--text-dark-muted)',
          marginBottom: '0.5rem',
        }}>
          Result
        </span>
        <p style={{ fontSize: '0.82rem', fontWeight: 400, color: 'var(--text-dark)', lineHeight: 1.5, margin: 0 }}>
          {result}
        </p>
      </div>
    </div>
  );
}

function ResultTile({ metric, label, detail }: { metric: string; label: string; detail: string }) {
  return (
    <div className="tile" style={{ background: 'var(--bg)' }}>
      <div style={{ fontSize: '2.5rem', fontWeight: 400, fontFamily: 'var(--font-playfair-display), Georgia, serif', letterSpacing: '-0.03em', marginBottom: '0.5rem', fontVariantNumeric: 'tabular-nums' }}>
        {metric}
      </div>
      <div className="text-eyebrow" style={{ marginBottom: '0.75rem', fontSize: '0.65rem' }}>{label}</div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5 }}>{detail}</p>
    </div>
  );
}