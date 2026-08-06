'use client';

import Link from 'next/link';
import { content } from '../content';
import PlusCross from './PlusCross';

const Footer = () => {
  const navLinks = [
    { label: 'Services', href: '/services' },
    { label: 'Process', href: '/process' },
    { label: 'About', href: '/about' },
    { label: 'Contact', href: '/contact' },
  ];

  return (
    <footer
      style={{
        background: 'var(--bg-alt)',
        borderTop: '1px solid var(--border)',
        paddingTop: '3rem',
        paddingBottom: '2rem',
      }}
    >
      <div className="container-xl">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div
              style={{
                fontWeight: 400,
                fontSize: '1.1rem',
                marginBottom: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
              }}
            >
              <PlusCross size={14} style={{ color: 'var(--text-muted)' }} />
              <span style={{ color: 'var(--text)' }}>M.O.T Innovation</span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '300px', lineHeight: 1.6 }}>
              {content.footer.tagline}
            </p>
          </div>

          {/* Quick links */}
          <div>
            <span
              style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.12em',
                color: 'var(--text-muted)',
              }}
            >
              Navigate
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {navLinks.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  style={{
                    color: 'var(--text-muted)',
                    fontSize: '0.85rem',
                    textAlign: 'left',
                    textDecoration: 'none',
                    fontWeight: 300,
                    transition: 'color 0.2s ease',
                  }}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div>
            <span
              style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontSize: '0.7rem',
                textTransform: 'uppercase',
                letterSpacing: '0.12em',
                color: 'var(--text-muted)',
              }}
            >
              Get in Touch
            </span>
            {content.contact.contactMethods.map((method, i) => (
              <a
                key={i}
                href={method.href}
                style={{
                  display: 'block',
                  color: 'var(--text-muted)',
                  fontSize: '0.85rem',
                  marginBottom: '0.5rem',
                  transition: 'color 0.2s ease',
                  textDecoration: 'none',
                  fontWeight: 300,
                }}
              >
                {method.value}
              </a>
            ))}
          </div>
        </div>

        <div
          style={{
            paddingTop: '1.5rem',
            borderTop: '1px solid var(--border)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <p style={{ color: 'var(--text-light)', fontSize: '0.8rem', fontWeight: 300 }}>
            {content.footer.copyright}
          </p>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            {content.footer.links.map((link, i) => (
              <a
                key={i}
                href={link.href}
                style={{
                  color: 'var(--text-light)',
                  fontSize: '0.8rem',
                  transition: 'color 0.2s ease',
                  textDecoration: 'none',
                  fontWeight: 300,
                }}
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;