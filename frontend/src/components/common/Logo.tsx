interface LogoProps {
  size?: number
  className?: string
}

export function Logo({ size = 32, className }: LogoProps): React.JSX.Element {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      fill="none"
      width={size}
      height={size}
      className={className}
    >
      {/* Shield body */}
      <path
        d="M32 4 L56 16 V34 C56 48 44 58 32 62 C20 58 8 48 8 34 V16 Z"
        fill="currentColor"
        className="text-background"
        stroke="currentColor"
        strokeWidth="2.5"
        style={{ stroke: 'hsl(var(--primary))' }}
      />
      {/* Inner glow line */}
      <path
        d="M32 8 L52 18 V34 C52 46 42 54 32 58 C22 54 12 46 12 34 V18 Z"
        fill="none"
        stroke="currentColor"
        strokeWidth="0.5"
        opacity="0.3"
        style={{ stroke: 'hsl(var(--primary))' }}
      />
      {/* Central supervisor node */}
      <circle cx="32" cy="24" r="6" fill="currentColor" className="text-background" stroke="currentColor" strokeWidth="1.5" style={{ stroke: 'hsl(var(--primary))' }} />
      <circle cx="32" cy="24" r="3" fill="currentColor" opacity="0.8" style={{ fill: 'hsl(var(--primary))' }} />
      {/* Worker nodes */}
      <circle cx="20" cy="40" r="4" fill="currentColor" className="text-background" stroke="currentColor" strokeWidth="1.2" style={{ stroke: 'hsl(var(--primary))' }} />
      <circle cx="20" cy="40" r="2" fill="currentColor" opacity="0.5" style={{ fill: 'hsl(var(--primary))' }} />
      <circle cx="32" cy="44" r="4" fill="currentColor" className="text-background" stroke="currentColor" strokeWidth="1.2" style={{ stroke: 'hsl(var(--primary))' }} />
      <circle cx="32" cy="44" r="2" fill="currentColor" opacity="0.5" style={{ fill: 'hsl(var(--primary))' }} />
      <circle cx="44" cy="40" r="4" fill="currentColor" className="text-background" stroke="currentColor" strokeWidth="1.2" style={{ stroke: 'hsl(var(--primary))' }} />
      <circle cx="44" cy="40" r="2" fill="currentColor" opacity="0.5" style={{ fill: 'hsl(var(--primary))' }} />
      {/* Connection lines supervisor → workers */}
      <line x1="32" y1="30" x2="20" y2="36" stroke="currentColor" strokeWidth="1" opacity="0.5" style={{ stroke: 'hsl(var(--primary))' }} />
      <line x1="32" y1="30" x2="32" y2="40" stroke="currentColor" strokeWidth="1" opacity="0.5" style={{ stroke: 'hsl(var(--primary))' }} />
      <line x1="32" y1="30" x2="44" y2="36" stroke="currentColor" strokeWidth="1" opacity="0.5" style={{ stroke: 'hsl(var(--primary))' }} />
    </svg>
  )
}
