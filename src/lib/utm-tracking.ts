// UTM tracking parameters for content-driven leads
// Every link from YouTube, LinkedIn, and other content platforms
// should include these parameters so we can track which content drives leads.

export const UTM_PARAMS = {
  // Source: which platform the link was clicked from
  source: {
    youtube: 'youtube',
    linkedin: 'linkedin',
    tiktok: 'tiktok',
    twitter: 'twitter',
    email: 'email',
    direct: 'direct',
  },
  // Medium: what type of content
  medium: {
    short: 'short',        // YouTube Shorts
    longform: 'longform',  // YouTube long-form
    post: 'post',          // LinkedIn text post
    carousel: 'carousel',  // LinkedIn carousel
    newsletter: 'newsletter',
    bio: 'bio',            // Link in bio
  },
  // Campaign: which specific content piece
  // Format: pain_point_service (e.g., "scattered-assets-dam")
  campaign: {
    'disconnected-tools': 'disconnected-tools-integration',
    'manual-posting': 'manual-posting-delivery',
    'scattered-assets': 'scattered-assets-dam',
    'reporting-hours': 'reporting-hours-dashboards',
    'wasting-ads': 'wasting-ads-optimization',
    'agency-vs-builder': 'agency-vs-builder-general',
  },
};

// Generate a UTM-tracked URL for content
export function generateUTMUrl(
  base: string,
  source: string,
  medium: string,
  campaign: string
): string {
  const params = new URLSearchParams({
    utm_source: source,
    utm_medium: medium,
    utm_campaign: campaign,
    utm_content: `${source}-${medium}-${campaign}`,
  });
  return `${base}?${params.toString()}`;
}

// Example URLs for content:
// YouTube Short about scattered assets → /contact?utm_source=youtube&utm_medium=short&utm_campaign=scattered-assets-dam
// LinkedIn post about reporting → /services?utm_source=linkedin&utm_medium=post&utm_campaign=reporting-hours-dashboards

export const CONTENT_LINKS = {
  youtube: {
    contact: (campaign: string) =>
      generateUTMUrl('https://motinnovation.co.za/contact', 'youtube', 'short', campaign),
    services: (campaign: string) =>
      generateUTMUrl('https://motinnovation.co.za/services', 'youtube', 'longform', campaign),
  },
  linkedin: {
    contact: (campaign: string) =>
      generateUTMUrl('https://motinnovation.co.za/contact', 'linkedin', 'post', campaign),
    services: (campaign: string) =>
      generateUTMUrl('https://motinnovation.co.za/services', 'linkedin', 'carousel', campaign),
  },
};