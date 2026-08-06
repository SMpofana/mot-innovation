'use client';

import { useState, useEffect, useMemo } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';

const Header = () => {
  const pathname = usePathname();
  const [lightMode, setLightMode] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  const navItems = useMemo(() => [
    { href: '/', label: 'Home' },
    { href: '/services', label: 'Services' },
    { href: '/process', label: 'Process' },
    { href: '/about', label: 'About' },
    { href: '/contact', label: 'Contact' },
  ], []);

  const isHome = pathname === '/';

  useEffect(() => {
    const savedMode = localStorage.getItem('mot-light-mode');
    const isLight = savedMode === 'true';
    setLightMode(isLight);
    if (isLight) document.documentElement.classList.add('light');
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close drawer on route change
  useEffect(() => {
    setDrawerOpen(false);
  }, [pathname]);

  const toggleTheme = () => {
    const newMode = !lightMode;
    setLightMode(newMode);
    localStorage.setItem('mot-light-mode', newMode.toString());
    if (newMode) document.documentElement.classList.add('light');
    else document.documentElement.classList.remove('light');
  };

  const isActive = (href: string) => {
    if (href === '/') return isHome;
    return pathname === href;
  };

  return (
    <>
      <header
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-500"
        style={{
          background: scrolled ? 'var(--bg)' : 'transparent',
          borderBottom: scrolled ? '1px solid var(--border)' : '1px solid transparent',
          backdropFilter: scrolled ? 'blur(20px)' : 'none',
        }}
      >
        <div className="container-xl flex items-center justify-between" style={{ padding: '1.25rem 1.5rem' }}>
          {/* Logo — minimal text + plus cross */}
          <Link
            href="/"
            className="flex items-center gap-2"
            style={{ color: 'var(--text)' }}
          >
            <span style={{ fontWeight: 500, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>M.O.T</span>
            <svg width="11" height="11" viewBox="0 0 13 13" fill="none" style={{ color: 'var(--text-light)' }}>
              <line x1="6.5" y1="0" x2="6.5" y2="13" stroke="currentColor" strokeWidth="1" />
              <line x1="0" y1="6.5" x2="13" y2="6.5" stroke="currentColor" strokeWidth="1" />
            </svg>
          </Link>

          {/* Desktop Nav — uppercase, minimal */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="relative px-3 py-2 text-xs font-medium uppercase transition-colors duration-300"
                style={{
                  color: isActive(item.href) ? 'var(--text)' : 'var(--text-muted)',
                  letterSpacing: '0.1em',
                }}
              >
                {item.label}
                {isActive(item.href) && (
                  <motion.div
                    layoutId="nav-underline"
                    className="absolute -bottom-1 left-3 right-3 h-px"
                    style={{ background: 'var(--text)' }}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
              </Link>
            ))}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 transition-colors"
              style={{ color: 'var(--text-muted)' }}
              aria-label="Toggle theme"
            >
              {lightMode ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <circle cx="12" cy="12" r="4" />
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" strokeLinecap="round" />
                </svg>
              )}
            </button>
            <Link
              href="/contact"
              className="btn btn-primary hidden sm:inline-flex"
              style={{ padding: '0.6rem 1.25rem', fontSize: '0.7rem' }}
            >
              Consultation
            </Link>
            {/* Mobile toggle */}
            <button
              onClick={() => setDrawerOpen(!drawerOpen)}
              className="md:hidden p-2"
              style={{ color: 'var(--text)' }}
              aria-label="Toggle menu"
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                {drawerOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" strokeLinecap="round" strokeLinejoin="round" />
                ) : (
                  <path d="M3 12h18M3 6h18M3 18h18" strokeLinecap="round" strokeLinejoin="round" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-40 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setDrawerOpen(false)}
              style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)' }}
            />
            <motion.aside
              className="fixed top-0 right-0 bottom-0 z-50 md:hidden"
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              style={{
                width: '300px',
                background: 'var(--bg)',
                borderLeft: '1px solid var(--border)',
                paddingTop: '5rem',
                paddingLeft: '1.5rem',
                paddingRight: '1.5rem',
                paddingBottom: '2rem',
              }}
            >
              <nav className="flex flex-col gap-1">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="px-4 py-3 text-left text-sm font-medium uppercase transition-colors"
                    style={{
                      color: isActive(item.href) ? 'var(--text)' : 'var(--text-muted)',
                      letterSpacing: '0.1em',
                    }}
                  >
                    {item.label}
                  </Link>
                ))}
                <Link
                  href="/contact"
                  className="btn btn-primary mt-4 w-full"
                  style={{ fontSize: '0.75rem' }}
                >
                  Free Consultation
                </Link>
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default Header;