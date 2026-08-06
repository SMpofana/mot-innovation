// Trionn-style decorative plus/cross motif
// Used at corners, intersections, and section boundaries

interface PlusCrossProps {
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}

export default function PlusCross({ size = 13, className, style }: PlusCrossProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 13 13"
      fill="none"
      className={className}
      style={{ flexShrink: 0, ...style }}
    >
      <line x1="6.5" y1="0" x2="6.5" y2="13" stroke="currentColor" strokeWidth="1" />
      <line x1="0" y1="6.5" x2="13" y2="6.5" stroke="currentColor" strokeWidth="1" />
    </svg>
  );
}