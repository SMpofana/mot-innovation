'use client';

import { motion } from 'framer-motion';
import { content } from '../content';

/**
 * BookingButton — opens Calendly's popup widget for automatic booking.
 *
 * Path A of the Calendly integration: no OAuth, no backend, no redirect URI.
 * The booking event URL is centralized in content.booking.url so you can swap
 * it without touching components. The widget script is injected lazily on
 * first click so it never slows initial page load.
 *
 * (Path B — Calendly API + OAuth — can be layered on later without changing
 *  this component: swap the handler to redirect to Calendly's authorize URL
 *  instead of opening the widget. See /api/lead for the integration seam.)
 */
export default function BookingButton({
  label = content.booking.cta,
  className = 'btn btn-primary',
}: {
  label?: string;
  className?: string;
}) {
  const url = content.booking.url;

  const openCalendly = () => {
    if ((window as any).Calendly) {
      (window as any).Calendly.initPopupWidget({ url });
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    script.onload = () => (window as any).Calendly.initPopupWidget({ url });
    document.body.appendChild(script);
  };

  return (
    <motion.button
      type="button"
      onClick={openCalendly}
      className={className}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {label}
    </motion.button>
  );
}
