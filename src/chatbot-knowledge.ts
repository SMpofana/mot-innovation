// Knowledge base derived from social media research
// Sources: Reddit r/marketing, r/smallbusiness, r/Entrepreneur, r/digitalmarketing;
// G2 reviews of marketing tools; Quora; DuckDuckGo search snippets;
// Brandwatch blog on social listening tools; HubSpot content on dashboard tools.
// Research conducted August 2026.

export interface KnowledgeEntry {
  id: string;
  keywords: string[];
  question: string;
  answer: string;
  category: 'assets' | 'delivery' | 'tracking' | 'optimization' | 'pricing' | 'process' | 'general';
}

export const knowledgeBase: KnowledgeEntry[] = [
  {
    id: 'scattered-assets',
    keywords: ['scattered', 'disorganized', 'google drive', 'dropbox', 'dropbox', 'where are my', 'find assets', 'lost files', 'messy', 'chaos', 'scattered files', 'asset management', 'dam'],
    question: 'My marketing assets are scattered everywhere — Google Drive, Dropbox, individual laptops. How do you fix this?',
    answer: 'This is the #1 complaint we see. We set up a centralized Digital Asset Management (DAM) system with auto-tagging, consistent naming conventions, and cloud storage architecture. Your team gets one searchable hub for every logo, photo, video, and document — no more "who has the latest version?" Timeline: 2-3 weeks. Cost: included in the Intelligence Build ($2,500-$5,000).',
    category: 'assets',
  },
  {
    id: 'manual-posting',
    keywords: ['manual posting', 'manual', 'time consuming', 'time-consuming', 'too slow', 'posting takes', 'social media takes', 'scheduling', 'content calendar', 'repetitive'],
    question: 'Social media posting is manual and takes forever. Can you automate it?',
    answer: 'Yes — this is our Multi-Endpoint Delivery service. We build a pipeline where you create content once, and it\'s automatically formatted and scheduled for LinkedIn, Instagram, TikTok, X, Facebook, email, and your CMS. One source, every channel served. Most clients see 70-80% reduction in time-to-publish. Timeline: 1-2 weeks.',
    category: 'delivery',
  },
  {
    id: 'no-reporting',
    keywords: ['no reporting', 'reporting takes', 'manual reporting', 'spreadsheets', 'too long', 'reporting is a nightmare', 'data is scattered', 'no dashboard', 'no visibility', 'can\'t see', 'no idea what\'s working'],
    question: 'Reporting takes days and is always outdated. How do you solve this?',
    answer: 'We build unified performance dashboards that pull data from every platform into one real-time view. No more manual spreadsheet exports. Automated weekly and monthly reports go straight to your inbox. One e-commerce client cut reporting time from 2 days to 0. A SaaS client improved conversion rates 23% just by having visibility they didn\'t have before.',
    category: 'tracking',
  },
  {
    id: 'wasted-ad-spend',
    keywords: ['wasted', 'ad spend', 'wasting money', 'ads not working', 'roi', 'return on ad spend', 'roas', 'burning money', 'no results', 'campaigns not performing', 'optimize', 'a/b test'],
    question: 'I feel like I\'m wasting money on ads. Can you help optimize campaigns?',
    answer: 'This is our Campaign Optimization service. We set up A/B testing frameworks, analyze creative performance, reallocate budget to what\'s actually working, and build automated optimization rules. Your campaigns improve themselves over time. One client improved conversion rates 23% through systematic testing. This is included in our Intelligence Partner retainer ($1,000+/mo).',
    category: 'optimization',
  },
  {
    id: 'disconnected-tools',
    keywords: ['disconnected', 'too many tools', 'too many platforms', 'fragmented', 'silo', 'silos', 'integration', 'don\'t talk to each other', 'zapier', 'integration mess'],
    question: 'We have too many marketing tools that don\'t talk to each other. Can you integrate them?',
    answer: 'This is exactly what we do. We audit your current stack, map every tool and data flow, then build integrations so everything connects into one intelligent pipeline. Content flows from storage → channels → tracking → optimization automatically. We\'re channel-agnostic — we work with whatever platforms you already use. No vendor lock-in, no forced migrations.',
    category: 'process',
  },
  {
    id: 'pricing',
    keywords: ['price', 'cost', 'how much', 'pricing', 'expensive', 'affordable', 'budget', 'rate', 'fee', 'charge'],
    question: 'How much does this cost?',
    answer: 'We have three engagement models:\n\n1. Infrastructure Audit — $500 one-time: Full stack audit, infrastructure map, prioritized recommendations, 30-min walkthrough.\n\n2. Intelligence Build — $2,500-$5,000 project: Full infrastructure design and build (DAM, delivery pipeline, dashboards, team training, 30 days support).\n\n3. Intelligence Partner — $1,000+/mo retainer: Ongoing optimization, A/B testing, automated reporting, quarterly strategy reviews.\n\nAll engagements start with a free consultation. No accounts required.',
    category: 'pricing',
  },
  {
    id: 'timeline',
    keywords: ['timeline', 'how long', 'how fast', 'when', 'deadline', 'deliver', 'quick', 'rush'],
    question: 'How long does it take to build everything?',
    answer: 'It depends on scope:\n\n• Infrastructure Audit: 1 week\n• DAM setup & taxonomy: 2-3 weeks\n• Multi-channel delivery pipeline: 1-2 weeks\n• Performance dashboard: 1-2 weeks\n• Full Intelligence Build (end-to-end): 4-6 weeks\n• Ongoing optimization: continuous\n\nWe move fast because we build, not just advise. You\'ll see working systems within the first week.',
    category: 'process',
  },
  {
    id: 'no-account',
    keywords: ['account', 'sign up', 'login', 'register', 'create account', 'password'],
    question: 'Do I need to create an account to work with you?',
    answer: 'No. We don\'t believe in forcing you to create accounts just to talk to us. Book a free 30-minute consultation through the contact form, and we\'ll map your current infrastructure and show you exactly where the gaps are. We\'ll get back to you within 24 hours.',
    category: 'general',
  },
  {
    id: 'what-we-do',
    keywords: ['what do you do', 'services', 'offer', 'help with', 'what can you', 'who are you', 'about'],
    question: 'What exactly does M.O.T Innovation do?',
    answer: 'We design and build marketing intelligence infrastructure for businesses. Four pillars:\n\n1. Digital Marketing Infrastructure — DAM, content libraries, asset taxonomies\n2. Multi-Endpoint Delivery — push content to every channel from one source\n3. Performance Tracking & Reporting — unified dashboards, automated reports\n4. Campaign Optimization — A/B testing, budget reallocation, automated rules\n\nWe don\'t just consult — we build the actual systems and hand you the keys.',
    category: 'general',
  },
  {
    id: 'small-business',
    keywords: ['small business', 'small team', 'solo', 'solopreneur', 'startup', 'too big for us', 'enterprise', 'scale'],
    question: 'We\'re a small team — is this overkill for us?',
    answer: 'Not at all. Our systems are built to scale — from solopreneur to enterprise team. The Infrastructure Audit ($500) is a great starting point for small teams. You get a full map of what you have, what you\'re missing, and a prioritized action plan you can implement yourself or with us. Many small businesses start with the audit and upgrade to a build later.',
    category: 'pricing',
  },
  {
    id: 'vendor-lock-in',
    keywords: ['vendor lock', 'lock-in', 'locked in', 'proprietary', 'own the system', 'black box', 'transparent', 'ownership'],
    question: 'Will we be locked into your platform?',
    answer: 'No. You own everything we build. We use open standards and work with whatever platforms you already use — no vendor lock-in, no forced migrations, no black boxes. We hand you the keys and the documentation. If you want to take over maintenance yourself, you can. We\'re transparent about everything.',
    category: 'general',
  },
  {
    id: 'results',
    keywords: ['results', 'proof', 'case study', 'examples', 'portfolio', 'track record', 'success', 'roi proof'],
    question: 'Can you show me proof this works?',
    answer: 'Here are three recent results:\n\n• E-commerce Brand: 80% reduction in time-to-publish after DAM + delivery pipeline\n• SaaS Startup: Reporting time cut from 2 days to 0; conversion rate improved 23%\n• Content Creator Collective: 3x content output with same headcount; clear revenue attribution per creator\n\nAll through building systems, not just advice.',
    category: 'general',
  },
  {
    id: 'disconnected-tools',
    keywords: ['disconnected', 'too many tools', 'too many platforms', 'fragmented', 'silo', 'silos', 'integration', 'don\'t talk to each other', 'zapier', 'integration mess', '12 tools', 'tool overload', 'too many subscriptions'],
    question: 'My marketing tools don\'t talk to each other. Can you integrate them?',
    answer: 'This is the #1 pain point we see on Reddit and G2. The average marketing team uses 12+ tools and fewer than half of them talk to each other. We audit your current stack, recommend which to keep vs. replace, and build integration layers so everything connects. We\'re channel-agnostic — we work with whatever platforms you already use. No vendor lock-in, no forced migrations.',
    category: 'process',
  },
  {
    id: 'agency-vs-consultant',
    keywords: ['agency', 'consultant', 'slide deck', 'advise', 'advice', 'strategy', 'implementation', 'build not advise', 'retainer', 'agency vs', 'consultant vs', 'don\'t need another audit'],
    question: 'How are you different from a marketing agency?',
    answer: 'Agencies typically provide strategy and ongoing campaign management (often with monthly retainers). We build the systems your team or agency will use. If you\'ve ever felt like "agencies deliver slide decks but never build anything," you need an infrastructure consultant. We set up your DAM, configure your multi-channel delivery, build your dashboards, integrate your tools — then hand over a working system you own. More cost-effective than an ongoing retainer because you own the infrastructure once it\'s built.',
    category: 'general',
  },
  {
    id: 'social-listening-tools',
    keywords: ['social listening', 'brandwatch', 'meltwater', 'sprout social', 'mention', 'brand24', 'monitoring tool', 'listening tool', 'sentiment'],
    question: 'What social listening tools do you work with?',
    answer: 'We work with the top social listening tools on the market:\n\n1. Brandwatch — enterprise, ~$800+/month\n2. Meltwater — enterprise, ~$1,000+/month\n3. Sprout Social — $249-$499/seat/month\n4. Mention — $49-$149+/month\n5. Brand24 — $99-$399/month\n\nWe help you choose the right one for your budget and integrate it with your marketing dashboard so you get sentiment analysis and brand mentions alongside your performance data.',
    category: 'tracking',
  },
  {
    id: 'dashboarding-platforms',
    keywords: ['dashboard', 'dashboarding', 'power bi', 'dashthis', 'databox', 'hubspot', 'klipfolio', 'reporting tool', 'bi tool', 'analytics platform', 'which tool'],
    question: 'What dashboarding platforms do you use?',
    answer: 'We build dashboards using the top marketing analytics platforms:\n\n1. Microsoft Power BI — Free to $10-$20/user/month (Pro/Premium). Scalable, cross-tool data integration.\n2. HubSpot Marketing Hub — Free to $3,600/month (Enterprise). All-in-one with CRM.\n3. DashThis — $49-$299+/month. Automated marketing dashboards, multi-source, white-label.\n\nWe also work with Databox, Klipfolio, and Mixpanel. We choose based on your budget, team size, and existing tool stack.',
    category: 'tracking',
  },
];

// Quick reply suggestions shown when chat opens
export const quickReplies = [
  'My assets are scattered everywhere',
  'Social media posting takes too long',
  'My marketing tools don\'t integrate',
  'I\'m wasting money on ads',
  'How much does this cost?',
  'How are you different from an agency?',
];