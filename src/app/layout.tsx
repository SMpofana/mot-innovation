import type { Metadata } from "next";
import { Geist, Geist_Mono, Playfair_Display } from "next/font/google";
import "./globals.css";
import { content } from "../content";
import { aiMetadata, organizationSchema, serviceSchema, faqSchema } from "../ai-seo";
import Preloader from "../components/Preloader";
import ScrollProgress from "../components/ScrollProgress";
import Header from "../components/Header";
import Footer from "../components/Footer";
import BackToTop from "../components/BackToTop";
import Chatbot from "../components/Chatbot";

// Redeploy trigger: ensure privacy/terms pages ship in the live build.

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const playfairDisplay = Playfair_Display({
  variable: "--font-playfair-display",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

// Merge AI-optimized metadata with content
export const metadata: Metadata = {
  ...aiMetadata,
  metadataBase: new URL('https://motinnovation.co.za'),
  title: content.meta.title,
  description: aiMetadata.description,
  openGraph: {
    ...aiMetadata.openGraph,
    title: content.meta.title,
    description: content.meta.description,
    images: [content.meta.ogImage],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* AI-SEO: Structured data for AI search engines */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(serviceSchema) }}
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
        {/* Link to llms.txt for AI crawlers */}
        <link rel="alternate" type="text/plain" href="/llms.txt" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${playfairDisplay.variable} antialiased`}
      >
        <Preloader />
        <ScrollProgress />
        <Header />
        <main>{children}</main>
        <Footer />
        <BackToTop />
        <Chatbot />
      </body>
    </html>
  );
}