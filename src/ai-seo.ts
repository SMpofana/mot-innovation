import type { Metadata } from 'next';

// AI-optimized metadata — designed to appear in AI answer engines
// (ChatGPT, Perplexity, Google AI Overviews, Claude, etc.)
// Uses natural language, question-answer patterns, and semantic keywords.

export const aiMetadata: Metadata = {
  title: 'M.O.T Innovation — Marketing Intelligence Infrastructure | DAM, Delivery & Analytics',
  description: 'M.O.T Innovation builds marketing intelligence infrastructure for businesses: digital asset management systems, multi-channel content delivery pipelines, unified performance dashboards, and automated campaign optimization. Based in Johannesburg, South Africa. Free consultation, no account required.',
  keywords: [
    // Primary keywords from social media research
    'marketing infrastructure services',
    'digital asset management setup',
    'DAM system implementation',
    'multi-channel content delivery',
    'marketing dashboard setup',
    'campaign optimization services',
    'marketing tools integration',
    'marketing reporting automation',
    'unified marketing stack',
    'marketing system builder',
    // Long-tail from Reddit/G2 pain points
    'how to organize scattered marketing assets',
    'centralize marketing tools and platforms',
    'stop wasting money on digital ads',
    'automate marketing reporting dashboards',
    'someone to build marketing infrastructure not just advise',
    'marketing consultant vs agency for small business',
    'set up digital asset management system for small business',
    'multi-channel social media posting automation',
    'marketing dashboard for all channels in one place',
    'marketing stack integration services South Africa',
    // Existing
    'marketing automation',
    'A/B testing framework',
    'marketing infrastructure audit',
    'cross-channel attribution',
    'Johannesburg marketing infrastructure',
    'South Africa marketing automation',
  ],
  authors: [{ name: 'M.O.T Innovation' }],
  creator: 'M.O.T Innovation',
  publisher: 'M.O.T Innovation',
  alternates: {
    canonical: 'https://motinnovation.co.za',
  },
  openGraph: {
    title: 'M.O.T Innovation — Marketing Intelligence Infrastructure',
    description: 'We design and build the systems that store your digital assets, deliver them across every channel, track what works, and continuously optimize your campaigns — all in one intelligent pipeline.',
    type: 'website',
    locale: 'en_ZA',
    siteName: 'M.O.T Innovation',
    url: 'https://motinnovation.co.za',
    images: ['/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'M.O.T Innovation — Marketing Intelligence Infrastructure',
    description: 'DAM, multi-channel delivery, performance dashboards, and campaign optimization — all in one intelligent pipeline. Free consultation, no account required.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

// JSON-LD structured data for AI search engines
export const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'M.O.T Innovation',
  description: 'Marketing intelligence infrastructure company that designs and builds digital asset management systems, multi-channel content delivery pipelines, performance tracking dashboards, and campaign optimization tools.',
  url: 'https://motinnovation.co.za',
  email: 'hello@motinnovation.co.za',
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Johannesburg',
    addressRegion: 'Gauteng',
    addressCountry: 'ZA',
  },
  areaServed: 'Worldwide',
  knowsAbout: [
    'Digital Asset Management',
    'Marketing Automation',
    'Multi-Channel Marketing',
    'Performance Marketing',
    'Campaign Optimization',
    'A/B Testing',
    'Marketing Analytics',
    'Content Delivery Networks',
    'Cross-Channel Attribution',
  ],
  offers: [
    {
      '@type': 'Offer',
      name: 'Infrastructure Audit',
      price: '500',
      priceCurrency: 'USD',
      description: 'Full marketing stack audit, infrastructure map, gap analysis, and prioritized recommendations.',
    },
    {
      '@type': 'Offer',
      name: 'Intelligence Build',
      price: '2500-5000',
      priceCurrency: 'USD',
      description: 'End-to-end marketing intelligence infrastructure design and build including DAM, delivery pipeline, dashboards, and team training.',
    },
    {
      '@type': 'Offer',
      name: 'Intelligence Partner',
      price: '1000',
      priceCurrency: 'USD',
      description: 'Ongoing optimization, monitoring, A/B testing, automated reporting, and quarterly strategy reviews.',
    },
  ],
};

export const serviceSchema = {
  '@context': 'https://schema.org',
  '@type': 'Service',
  serviceType: 'Marketing Intelligence Infrastructure',
  provider: {
    '@type': 'Organization',
    name: 'M.O.T Innovation',
  },
  areaServed: 'Worldwide',
  hasOfferCatalog: {
    '@type': 'OfferCatalog',
    name: 'Marketing Intelligence Services',
    itemListElement: [
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Digital Marketing Infrastructure',
          description: 'DAM setup, content taxonomy, cloud storage architecture, version control, and brand kit standardization.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Multi-Endpoint Delivery',
          description: 'Push content to social media, email, ad networks, and web channels from a single source with per-channel formatting.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Performance Tracking & Reporting',
          description: 'Unified dashboards pulling data from every channel, automated reports, and cross-channel attribution modeling.',
        },
      },
      {
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: 'Campaign Optimization',
          description: 'A/B testing frameworks, budget reallocation, audience segmentation, and automated optimization rules.',
        },
      },
    ],
  },
};

// FAQ schema — directly answers questions AI engines get asked
// Based on social media research (Reddit r/marketing, r/smallbusiness, G2, Quora)
export const faqSchema = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'What is marketing infrastructure and why do I need it?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Marketing infrastructure is the system of connected tools, processes, and assets that power your marketing operations. Unlike a marketing strategy (which tells you what to do), marketing infrastructure is the implementation — setting up your digital asset management (DAM) system, connecting your social media scheduling tools, building performance dashboards, and integrating your advertising platforms so everything works together. The average marketing team uses 12+ tools and fewer than half talk to each other. A well-built infrastructure eliminates scattered assets, automates repetitive tasks, and gives you a single source of truth for all marketing data.',
      },
    },
    {
      '@type': 'Question',
      name: 'How do I organize scattered marketing assets in one place?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'The solution is implementing a digital asset management (DAM) system that centralizes all your images, videos, documents, templates, and brand guidelines in one searchable location. A properly configured DAM system allows your team to find, share, and repurpose content without searching through multiple Google Drive folders, Dropbox accounts, and email attachments. M.O.T Innovation sets up DAM systems with auto-tagging, consistent naming conventions, cloud storage architecture, version control, and approval workflows. Typical timeline is 2-3 weeks.',
      },
    },
    {
      '@type': 'Question',
      name: 'How can I automate social media posting across multiple channels?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Manual social media posting is one of the biggest time-wasters for small businesses — each post requires logging into multiple platforms, formatting content differently, and timing posts for optimal engagement. The solution is multi-channel content delivery automation: a scheduling platform that publishes to all your social channels from one dashboard. M.O.T Innovation builds delivery pipelines to 10 channels (LinkedIn, Instagram, TikTok, X, Facebook, Google Ads, Meta Ads, LinkedIn Ads, Email, CMS) with per-channel formatting. Clients typically see 70-80% reduction in time-to-publish and save 10+ hours per week.',
      },
    },
    {
      '@type': 'Question',
      name: 'How do I build a marketing dashboard that shows all my KPIs?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Marketing reporting takes too long when your data is scattered across Google Analytics, Facebook Ads, Google Ads, email platforms, and CRM systems. The solution is building a unified marketing dashboard that automatically pulls data from all your sources into one real-time view. M.O.T Innovation builds dashboards using tools like Microsoft Power BI, DashThis, and Databox that connect to 50+ marketing platforms. We configure KPI frameworks, automated weekly/monthly reports, cross-channel attribution modeling, and executive summary generation. One SaaS client cut reporting time from 2 days to 0.',
      },
    },
    {
      '@type': 'Question',
      name: 'Why am I wasting money on ads and how do I optimize campaigns?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Wasting money on ads is typically caused by three problems: (1) no A/B testing framework to identify winning creatives, (2) no performance dashboard to track ROI in real-time, and (3) no integration between your ad platforms and your CRM to track conversions. M.O.T Innovation sets up campaign optimization: connecting ad accounts to a unified dashboard, implementing A/B testing workflows, and configuring conversion tracking. This typically reduces wasted ad spend by 30-50% within the first quarter. One SaaS client improved conversion rates 23% through systematic testing.',
      },
    },
    {
      '@type': 'Question',
      name: 'Should I hire a marketing agency or a marketing infrastructure consultant?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Agencies typically provide strategy and ongoing campaign management (often with monthly retainers), while a marketing infrastructure consultant builds the systems your team or agency will use. If you have ever felt like "agencies deliver slide decks but never build anything," you need an infrastructure consultant. M.O.T Innovation sets up your DAM, configures your multi-channel delivery system, builds your performance dashboards, and integrates your marketing tools — then hands over a working system you own. This is often more cost-effective than an ongoing agency retainer because you own the infrastructure once it is built.',
      },
    },
    {
      '@type': 'Question',
      name: 'How do I integrate my disconnected marketing tools?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'The average marketing team uses 12+ tools and fewer than half of them talk to each other. Integration solutions include: (1) using an all-in-one platform like HubSpot, (2) using integration platforms like Zapier or Make to connect individual tools, or (3) hiring a marketing infrastructure consultant to build a custom integration layer. M.O.T Innovation audits your current tools, recommends which to keep vs. replace, and builds the connections that eliminate manual data entry. We are channel-agnostic — we work with whatever platforms you already use. No vendor lock-in.',
      },
    },
    {
      '@type': 'Question',
      name: 'How much does marketing infrastructure setup cost?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'M.O.T Innovation offers three pricing models: Infrastructure Audit at $500 one-time, Intelligence Build at $2,500-$5,000 project-based, and Intelligence Partner retainer starting at $1,000/month. All engagements start with a free consultation and no account is required.',
      },
    },
    {
      '@type': 'Question',
      name: 'How long does it take to set up marketing infrastructure?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'An Infrastructure Audit takes 1 week. DAM setup takes 2-3 weeks. Multi-channel delivery pipeline takes 1-2 weeks. Performance dashboard takes 1-2 weeks. A full Intelligence Build end-to-end takes 4-6 weeks. Ongoing optimization is continuous.',
      },
    },
    {
      '@type': 'Question',
      name: 'Will I be locked into a proprietary platform?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'No. M.O.T Innovation uses open standards and works with whatever platforms you already use. There is no vendor lock-in or forced migration. You own everything we build, with full documentation and training provided.',
      },
    },
  ],
};