// M.O.T Innovation — Content configuration
// Single source of truth for all website text

export const content = {
  brand: {
    name: "M.O.T Innovation",
    shortName: "M.O.T",
    tagline: "Marketing Intelligence, Engineered.",
    description: "We help businesses set up their marketing intelligence infrastructure — from digital asset storage to multi-endpoint delivery, performance tracking, and campaign optimization.",
  },
  meta: {
    title: "M.O.T Innovation — Digital Marketing Intelligence",
    description: "Marketing intelligence infrastructure for businesses. Digital asset management, multi-channel delivery, performance tracking, and campaign optimization.",
    ogImage: "/og-image.png",
  },
  hero: {
    badge: "Marketing Intelligence Infrastructure",
    headline: "Your marketing stack doesn't talk to itself.",
    subhead: "12+ tools. Fewer than half connected. Assets scattered across drives, posting done by hand, reports built in spreadsheets, ad spend flying blind. We don't consult — we build the infrastructure that connects it all and makes it work.",
    primaryCTA: "Book a Free Consultation",
    secondaryCTA: "Explore Services",
    stats: [
      { value: "12+", label: "Tools Avg Teams Use" },
      { value: "10", label: "Channels Automated" },
      { value: "10+", label: "Hours Saved Weekly" },
      { value: "1248", label: "Hours Back to Your Team / 4 Yrs" },
    ],
  },
  services: {
    headline: "What We Build",
    subhead: "Four pillars of marketing intelligence that work together as one system.",
    items: [
      {
        id: "infrastructure",
        icon: "🗄️",
        title: "Digital Marketing Infrastructure",
        description: "How you store, organize, and retrieve digital assets. We set up DAM systems, content libraries, and asset taxonomies that scale with your team.",
        features: [
          "Digital Asset Management (DAM) setup",
          "Content taxonomy & tagging systems",
          "Cloud storage architecture",
          "Version control & approval workflows",
          "Brand kit & template standardization",
        ],
        deliverable: "A centralized asset hub your whole team can use",
        timeline: "2-3 weeks",
      },
      {
        id: "delivery",
        icon: "📡",
        title: "Multi-Endpoint Delivery",
        description: "Push content to every social media platform, email platform, ad network, and web channel from a single source — with formatting optimized per channel.",
        features: [
          "Social media pipeline (LinkedIn, Instagram, TikTok, X, Facebook)",
          "Email & newsletter integration",
          "Ad platform connectors (Google Ads, Meta Ads, LinkedIn Ads)",
          "CMS & website publishing workflows",
          "Cross-channel content scheduling",
        ],
        deliverable: "One content source, every channel served automatically",
        timeline: "1-2 weeks",
      },
      {
        id: "tracking",
        icon: "📊",
        title: "Performance Tracking & Reporting",
        description: "Unified dashboards that pull data from every channel into one view. Real-time KPIs, automated reports, and executive-ready insights.",
        features: [
          "Unified performance dashboards",
          "KPI framework design & implementation",
          "Automated weekly/monthly reports",
          "Cross-channel attribution modeling",
          "Executive summary generation",
        ],
        deliverable: "One dashboard that tells you exactly what's working",
        timeline: "1-2 weeks",
      },
      {
        id: "optimization",
        icon: "⚡",
        title: "Campaign Optimization",
        description: "Continuous improvement loops. We analyze what's performing, A/B test variations, reallocate budget, and tune your campaigns for maximum ROI.",
        features: [
          "A/B testing frameworks",
          "Budget reallocation strategies",
          "Audience segmentation & targeting refinement",
          "Creative performance analysis",
          "Automated optimization rules",
        ],
        deliverable: "Campaigns that improve themselves over time",
        timeline: "Ongoing",
      },
    ],
  },
  process: {
    headline: "How We Work",
    subhead: "A proven 4-step process to go from scattered marketing to intelligent infrastructure.",
    steps: [
      {
        number: "01",
        title: "Audit & Map",
        description: "We audit your current marketing stack — where assets live, what channels you use, what data you track, and where the gaps are. You get a full infrastructure map.",
      },
      {
        number: "02",
        title: "Design & Build",
        description: "We design your marketing intelligence architecture and build it out — DAM, delivery pipelines, tracking dashboards, and optimization rules.",
      },
      {
        number: "03",
        title: "Integrate & Automate",
        description: "We connect everything into one automated system. Content flows from storage to channels to tracking to optimization — with minimal manual intervention.",
      },
      {
        number: "04",
        title: "Monitor & Optimize",
        description: "We monitor performance, fine-tune campaigns, and continuously improve. Your marketing infrastructure gets smarter over time.",
      },
    ],
  },
  pricing: {
    headline: "Engagement Models",
    subhead: "Flexible options — from a single audit to full infrastructure partnership.",
    note: "All engagements start with a free consultation. No accounts required.",
    plans: [
      {
        name: "Infrastructure Audit",
        price: "$500",
        period: "one-time",
        description: "Get a complete map of your marketing infrastructure and a prioritized action plan.",
        features: [
          "Full stack audit",
          "Infrastructure map & gap analysis",
          "Prioritized recommendations",
          "30-min walkthrough call",
          "PDF report delivery",
        ],
        cta: "Book Audit",
        popular: false,
      },
      {
        name: "Intelligence Build",
        price: "$2,500-$5,000",
        period: "project-based",
        description: "We design and build your marketing intelligence infrastructure end-to-end.",
        features: [
          "Everything in the Audit",
          "DAM setup & taxonomy design",
          "Multi-channel delivery pipeline",
          "Unified performance dashboard",
          "Team training & handover",
          "30 days of support",
        ],
        cta: "Start Build",
        popular: true,
      },
      {
        name: "Intelligence Partner",
        price: "$1,000+/mo",
        period: "retainer",
        description: "Ongoing optimization, monitoring, and continuous improvement of your marketing infrastructure.",
        features: [
          "Everything in the Build",
          "Monthly optimization sprints",
          "Campaign A/B testing",
          "Automated reporting",
          "Quarterly strategy reviews",
          "Priority support",
        ],
        cta: "Become a Partner",
        popular: false,
      },
    ],
  },
  proof: {
    headline: "Why M.O.T Innovation",
    subhead: "We don't just consult — we build the systems that run your marketing.",
    benefits: [
      {
        title: "Engineers, Not Consultants",
        description: "We don't hand you a slide deck and leave. We build the actual infrastructure and hand you the keys.",
      },
      {
        title: "Channel-Agnostic",
        description: "We work with whatever platforms you use — no vendor lock-in, no forced migrations.",
      },
      {
        title: "Automated By Default",
        description: "Every system we build reduces manual work. Your team should think, not copy-paste.",
      },
      {
        title: "Built to Scale",
        description: "From solopreneur to enterprise team — the infrastructure grows with you, not against you.",
      },
    ],
    caseStudies: [
      {
        client: "E-commerce Brand",
        challenge: "Product photos scattered across Google Drive, Dropbox, and individual laptops. No consistent naming. Social media posting was manual and error-prone.",
        solution: "Centralized DAM with auto-tagging, built delivery pipeline to Instagram, Facebook, and email. Set up performance dashboard tracking conversions per channel.",
        result: "80% reduction in time-to-publish. Clear view of which channels actually drove sales.",
      },
      {
        client: "SaaS Startup",
        challenge: "Marketing data spread across 6 platforms with no unified view. Reporting took 2 days per month and was often outdated by the time it reached leadership.",
        solution: "Built unified dashboard pulling from all 6 sources. Automated weekly executive summaries. Set up A/B testing framework for landing pages.",
        result: "Reporting time cut from 2 days to 0. Conversion rate improved 23% through systematic testing.",
      },
      {
        client: "Content Creator Collective",
        challenge: "5 creators producing content with no shared system. Assets duplicated, channels inconsistent, no performance visibility.",
        solution: "Shared content library with role-based access. Cross-channel scheduling pipeline. Per-creator performance dashboards.",
        result: "3x content output with same headcount. Clear attribution of revenue to individual creators.",
      },
    ],
  },
  about: {
    headline: "About M.O.T Innovation",
    body: "M.O.T Innovation was founded on a simple principle: marketing should be intelligent by design, not by accident. We've seen too many businesses struggle with scattered assets, manual reporting, and campaigns that feel like guesswork. So we built a company that fixes it — not with advice, but with actual systems. We design, build, and maintain the marketing intelligence infrastructure that modern businesses need to compete. From how you store a digital asset to how you optimize a cross-channel campaign, we connect every piece into one intelligent pipeline.",
    values: [
      { title: "Build over Advise", description: "Deliver working systems, not recommendations." },
      { title: "Automate the Boring", description: "If a human does it twice, a system should do it forever." },
      { title: "Data-Driven Decisions", description: "Every recommendation backed by tracked performance data." },
      { title: "Transparent Infrastructure", description: "You own everything we build. No black boxes." },
    ],
  },
  contact: {
    headline: "Let's Build Your Marketing Intelligence",
    subhead: "Book a free 30-minute consultation. We'll map your current infrastructure and show you exactly where the gaps are.",
    formFields: {
      name: "Your Name",
      email: "Email Address",
      business: "Business Name",
      stage: "Where are you now?",
      stageOptions: [
        "Just starting — no infrastructure yet",
        "Have some systems but they're disconnected",
        "Established but need optimization",
        "Enterprise — need a full rebuild",
      ],
      message: "What's your biggest marketing infrastructure challenge?",
    },
    submitText: "Request Consultation",
    note: "No account needed. We'll get back to you within 24 hours.",
    contactMethods: [
      { label: "Email", value: "hello@motinnovation.co.za", href: "mailto:hello@motinnovation.co.za" },
      { label: "LinkedIn", value: "M.O.T Innovation", href: "#" },
    ],
  },
  // Calendly automatic booking (Path A — embed/popup, no OAuth/redirect URI).
  // Swap url for your real Calendly event link. Path B (API + OAuth) can be
  // layered on later via /api/lead without changing this config.
  booking: {
    url: "https://calendly.com/mpofanas/15-min-discovery-call",
    cta: "Book a Free Consultation",
  },
  footer: {
    copyright: "© 2026 M.O.T Innovation. All rights reserved.",
    tagline: "Marketing Intelligence, Engineered.",
    links: [
      { label: "Privacy", href: "/privacy" },
      { label: "Terms", href: "/terms" },
    ],
  },
};