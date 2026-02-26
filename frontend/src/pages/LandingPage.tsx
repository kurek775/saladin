import { useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { ShieldCheck, Bot, RotateCcw, Activity, ArrowRight, ChevronDown } from 'lucide-react'
import { useMousePosition } from '../hooks/useMousePosition'

// ---------- Matrix Rain (same technique as SplashScreen) ----------

const CHARS =
  'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF'

function useMatrixRain(canvasRef: React.RefObject<HTMLCanvasElement | null>) {
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animId: number
    const fontSize = 14
    const columns: number[] = []

    function resize() {
      canvas!.width = canvas!.offsetWidth
      canvas!.height = canvas!.offsetHeight
      const colCount = Math.floor(canvas!.width / fontSize)
      columns.length = 0
      for (let i = 0; i < colCount; i++) {
        columns.push(Math.random() * -canvas!.height / fontSize)
      }
    }

    resize()
    window.addEventListener('resize', resize)

    function draw() {
      ctx!.fillStyle = 'rgba(3, 7, 18, 0.05)'
      ctx!.fillRect(0, 0, canvas!.width, canvas!.height)
      ctx!.font = `${fontSize}px monospace`

      for (let i = 0; i < columns.length; i++) {
        const char = CHARS[Math.floor(Math.random() * CHARS.length)] ?? '0'
        const x = i * fontSize
        const colVal = columns[i] ?? 0
        const y = colVal * fontSize

        const brightness = Math.random()
        if (brightness > 0.9) {
          ctx!.fillStyle = '#ffffff'
        } else if (brightness > 0.6) {
          ctx!.fillStyle = '#22c55e'
        } else {
          ctx!.fillStyle = 'rgba(34, 197, 94, 0.4)'
        }

        ctx!.fillText(char, x, y)
        columns[i] = colVal + 1

        if (y > canvas!.height && Math.random() > 0.975) {
          columns[i] = 0
        }
      }

      animId = requestAnimationFrame(draw)
    }

    animId = requestAnimationFrame(draw)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [canvasRef])
}

// ---------- SVG Agent Network (hero) with data-flow particles ----------

const SVG_W = 440
const SVG_H = 260
const SUP_CX = SVG_W / 2
const SUP_CY = 55
const SUP_R = 34
const WORKER_R = 24
const WORKER_Y = 200
const WORKER_XS = [70, 170, 270, 370]

function HeroNetwork() {
  return (
    <svg
      viewBox={`0 0 ${SVG_W} ${SVG_H}`}
      className="w-[340px] sm:w-[440px] mx-auto"
      fill="none"
    >
      {/* Hidden path elements for animateMotion */}
      {WORKER_XS.map((wx, i) => (
        <path
          key={`path-down-${i}`}
          id={`conn-down-${i}`}
          d={`M${SUP_CX},${SUP_CY} L${wx},${WORKER_Y}`}
          fill="none"
          stroke="none"
        />
      ))}
      {WORKER_XS.map((wx, i) => (
        <path
          key={`path-up-${i}`}
          id={`conn-up-${i}`}
          d={`M${wx},${WORKER_Y} L${SUP_CX},${SUP_CY}`}
          fill="none"
          stroke="none"
        />
      ))}

      {/* Connection lines */}
      {WORKER_XS.map((wx, i) => {
        const length = Math.sqrt((wx - SUP_CX) ** 2 + (WORKER_Y - SUP_CY) ** 2)
        return (
          <motion.line
            key={`line-${i}`}
            x1={SUP_CX}
            y1={SUP_CY}
            x2={wx}
            y2={WORKER_Y}
            stroke="#22c55e"
            strokeWidth={1.5}
            strokeDasharray={length}
            strokeDashoffset={length}
            animate={{ strokeDashoffset: 0 }}
            transition={{ duration: 0.8, delay: 0.4 + i * 0.12, ease: 'easeOut' }}
            opacity={0.6}
          />
        )
      })}

      {/* Data flow particles — supervisor→worker (green, bright) */}
      {WORKER_XS.map((_, i) => (
        <circle key={`particle-down-${i}`} r="3" fill="#22c55e" opacity="0.8">
          <animateMotion
            dur={`${1.8 + i * 0.3}s`}
            repeatCount="indefinite"
            begin={`${1.2 + i * 0.4}s`}
          >
            <mpath href={`#conn-down-${i}`} />
          </animateMotion>
        </circle>
      ))}

      {/* Data flow particles — worker→supervisor (dimmer, slower) */}
      {WORKER_XS.map((_, i) => (
        <circle key={`particle-up-${i}`} r="2" fill="#22c55e" opacity="0.3">
          <animateMotion
            dur={`${2.4 + i * 0.35}s`}
            repeatCount="indefinite"
            begin={`${2.5 + i * 0.5}s`}
          >
            <mpath href={`#conn-up-${i}`} />
          </animateMotion>
        </circle>
      ))}

      {/* Supervisor node */}
      <motion.g
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <circle cx={SUP_CX} cy={SUP_CY} r={SUP_R + 8} fill="none" stroke="#22c55e" strokeWidth={1} opacity={0.2}>
          <animate attributeName="r" values={`${SUP_R + 6};${SUP_R + 12};${SUP_R + 6}`} dur="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.2;0.05;0.2" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx={SUP_CX} cy={SUP_CY} r={SUP_R} fill="#030712" stroke="#22c55e" strokeWidth={2} />
        <foreignObject x={SUP_CX - 12} y={SUP_CY - 12} width={24} height={24}>
          <ShieldCheck className="w-6 h-6 text-green-500" />
        </foreignObject>
      </motion.g>

      {/* Worker nodes */}
      {WORKER_XS.map((wx, i) => (
        <motion.g
          key={`worker-${i}`}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, delay: 0.6 + i * 0.15 }}
        >
          <circle cx={wx} cy={WORKER_Y} r={WORKER_R + 4} fill="none" stroke="#22c55e" strokeWidth={0.5} opacity={0.15}>
            <animate attributeName="opacity" values="0.15;0.05;0.15" dur={`${1.5 + i * 0.3}s`} repeatCount="indefinite" />
          </circle>
          <circle cx={wx} cy={WORKER_Y} r={WORKER_R} fill="#030712" stroke="#22c55e" strokeWidth={1.5} opacity={0.8} />
          <foreignObject x={wx - 10} y={WORKER_Y - 10} width={20} height={20}>
            <Bot className="w-5 h-5 text-green-500/80" />
          </foreignObject>
        </motion.g>
      ))}

      {/* Labels */}
      <motion.text
        x={SUP_CX}
        y={SUP_CY + SUP_R + 18}
        textAnchor="middle"
        className="text-[11px] fill-green-500/70 font-mono"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
      >
        Supervisor
      </motion.text>
    </svg>
  )
}

// ---------- Feature Cards with 3D tilt ----------

const features = [
  {
    icon: ShieldCheck,
    title: 'Unified Command',
    description:
      'One supervisor coordinates multiple workers — different LLM providers, unified output.',
  },
  {
    icon: RotateCcw,
    title: 'Iterative Refinement',
    description:
      'Built-in revision cycles. Workers execute, supervisors review, quality improves with each pass.',
  },
  {
    icon: Activity,
    title: 'Real-Time Monitoring',
    description:
      'Live WebSocket feeds, execution timelines, and system logs — full visibility into every orchestration.',
  },
]

function FeatureCard({
  icon: Icon,
  title,
  description,
  index,
}: (typeof features)[number] & { index: number }) {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = e.currentTarget
    const rect = el.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2
    el.style.transform = `perspective(600px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) scale(1.02)`
    const inner = el.querySelector<HTMLElement>('[data-tilt-icon]')
    if (inner) inner.style.transform = `translateZ(30px)`
    const text = el.querySelector<HTMLElement>('[data-tilt-text]')
    if (text) text.style.transform = `translateZ(15px)`
  }, [])

  const handleMouseLeave = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = e.currentTarget
    el.style.transform = ''
    const inner = el.querySelector<HTMLElement>('[data-tilt-icon]')
    if (inner) inner.style.transform = ''
    const text = el.querySelector<HTMLElement>('[data-tilt-text]')
    if (text) text.style.transform = ''
  }, [])

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.15 }}
      className="group rounded-xl border border-white/10 bg-white/5 p-6 transition-all duration-200 hover:border-green-500/40"
      style={{ transformStyle: 'preserve-3d' }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div
        data-tilt-icon=""
        className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10 transition-transform duration-200"
      >
        <Icon className="h-5 w-5 text-green-400" />
      </div>
      <div data-tilt-text="" className="transition-transform duration-200">
        <h3 className="mb-2 text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm leading-relaxed text-gray-400">{description}</p>
      </div>
    </motion.div>
  )
}

// ---------- Architecture Diagram ----------

function ArchitectureDiagram() {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })

  const nodeDelay = (i: number) => 0.15 * i
  const lineDelay = (i: number) => 0.6 + 0.1 * i

  const workers = ['GPT-4', 'Claude', 'Gemini', 'Llama']
  const workerSpacing = 100
  const startX = 200 - ((workers.length - 1) * workerSpacing) / 2

  return (
    <div ref={ref}>
      <svg viewBox="0 0 400 320" className="mx-auto w-full max-w-lg" fill="none">
        {/* Supervisor → Worker lines */}
        {workers.map((_, i) => {
          const wx = startX + i * workerSpacing
          const length = Math.sqrt((wx - 200) ** 2 + 100 ** 2)
          return (
            <motion.line
              key={`sw-${i}`}
              x1={200} y1={50} x2={wx} y2={150}
              stroke="#22c55e" strokeWidth={1.2} opacity={0.5}
              strokeDasharray={length}
              strokeDashoffset={length}
              animate={inView ? { strokeDashoffset: 0 } : {}}
              transition={{ duration: 0.6, delay: lineDelay(i) }}
            />
          )
        })}

        {/* Worker → Output lines */}
        {workers.map((_, i) => {
          const wx = startX + i * workerSpacing
          return (
            <motion.line
              key={`wo-${i}`}
              x1={wx} y1={150} x2={wx} y2={220}
              stroke="#22c55e" strokeWidth={1} opacity={0.35}
              strokeDasharray={70}
              strokeDashoffset={70}
              animate={inView ? { strokeDashoffset: 0 } : {}}
              transition={{ duration: 0.4, delay: lineDelay(i) + 0.3 }}
            />
          )
        })}

        {/* Supervisor node */}
        <motion.g
          initial={{ opacity: 0, scale: 0 }}
          animate={inView ? { opacity: 1, scale: 1 } : {}}
          transition={{ duration: 0.4, delay: nodeDelay(0) }}
        >
          <circle cx={200} cy={50} r={28} fill="#030712" stroke="#22c55e" strokeWidth={1.5} />
          <text x={200} y={54} textAnchor="middle" className="text-[11px] fill-green-400 font-mono">
            Supervisor
          </text>
        </motion.g>

        {/* Worker nodes */}
        {workers.map((label, i) => {
          const wx = startX + i * workerSpacing
          return (
            <motion.g
              key={`wn-${i}`}
              initial={{ opacity: 0, scale: 0 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.4, delay: nodeDelay(i + 1) }}
            >
              <circle cx={wx} cy={150} r={22} fill="#030712" stroke="#22c55e" strokeWidth={1.2} opacity={0.8} />
              <text x={wx} y={154} textAnchor="middle" className="text-[10px] fill-green-400/80 font-mono">
                {label}
              </text>
            </motion.g>
          )
        })}

        {/* Output row */}
        {workers.map((_, i) => {
          const wx = startX + i * workerSpacing
          return (
            <motion.g
              key={`out-${i}`}
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: lineDelay(i) + 0.5 }}
            >
              <rect x={wx - 16} y={220} width={32} height={16} rx={3} fill="none" stroke="#22c55e" strokeWidth={0.8} opacity={0.5} />
              <text x={wx} y={231} textAnchor="middle" className="text-[8px] fill-green-500/60 font-mono">
                out
              </text>
            </motion.g>
          )
        })}

        {/* Review → Revision loop arrow */}
        <motion.path
          d="M120 250 H280"
          stroke="#22c55e" strokeWidth={1} opacity={0.4}
          strokeDasharray={160} strokeDashoffset={160}
          animate={inView ? { strokeDashoffset: 0 } : {}}
          transition={{ duration: 0.6, delay: 1.4 }}
        />
        <motion.text
          x={200} y={268}
          textAnchor="middle"
          className="text-[10px] fill-green-500/60 font-mono"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.6 }}
        >
          Review → Revise → Final
        </motion.text>

        {/* Loop arrow */}
        <motion.path
          d="M280 250 C 300 250, 300 130, 200 100"
          stroke="#22c55e" strokeWidth={1} opacity={0.3}
          fill="none"
          strokeDasharray={200} strokeDashoffset={200}
          animate={inView ? { strokeDashoffset: 0 } : {}}
          transition={{ duration: 0.8, delay: 1.6 }}
          markerEnd="url(#arrowhead)"
        />

        <defs>
          <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <path d="M0,0 L8,3 L0,6" fill="#22c55e" opacity={0.4} />
          </marker>
        </defs>
      </svg>
    </div>
  )
}

// ---------- CTA Button ----------

function CTAButton({ children }: { children: React.ReactNode }) {
  return (
    <Link
      to="/dashboard"
      className="group inline-flex items-center gap-2 rounded-lg border border-green-500/50 px-6 py-3 font-mono text-sm font-semibold text-green-400 transition-all hover:bg-green-500/10 hover:shadow-[0_0_20px_rgba(34,197,94,0.15)]"
    >
      {children}
      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
    </Link>
  )
}

// ---------- Scroll Indicator ----------

function ScrollIndicator() {
  return (
    <motion.div
      className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 2.5, duration: 0.5 }}
    >
      <span className="text-[10px] font-mono uppercase tracking-widest text-green-500/50">Scroll</span>
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
      >
        <ChevronDown className="h-5 w-5 text-green-500/40" />
      </motion.div>
    </motion.div>
  )
}

// ---------- Landing Page ----------

export function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const heroRef = useRef<HTMLElement>(null)
  useMatrixRain(canvasRef)
  const mouse = useMousePosition(heroRef)

  return (
    <div className="relative min-h-screen overflow-x-hidden" style={{ backgroundColor: '#030712', color: '#fff' }}>
      {/* Matrix rain background — covers entire page */}
      <canvas ref={canvasRef} className="pointer-events-none fixed inset-0 h-full w-full" />

      {/* Semi-transparent overlay so text remains readable */}
      <div className="pointer-events-none fixed inset-0 bg-[#030712]/70" />

      {/* ===== Section 1: Hero ===== */}
      <section
        ref={heroRef}
        className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 text-center"
      >
        {/* Hero parallax: SVG network follows mouse */}
        <motion.div
          animate={{ x: mouse.x * 20, y: mouse.y * 15 }}
          transition={{ type: 'spring', stiffness: 150, damping: 20, mass: 0.5 }}
        >
          <HeroNetwork />
        </motion.div>

        {/* Title moves opposite for depth illusion */}
        <motion.h1
          className="mt-8 font-mono text-4xl font-bold tracking-[0.3em] text-green-400 sm:text-5xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0, x: mouse.x * -8 }}
          transition={{ delay: 1.2, duration: 0.6 }}
        >
          SALADIN
        </motion.h1>

        <motion.p
          className="mt-3 font-mono text-sm tracking-widest text-green-500/60"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, x: mouse.x * -5, y: mouse.y * -3 }}
          transition={{ delay: 1.6, duration: 0.5 }}
        >
          Multi-Agent Orchestration
        </motion.p>

        <motion.p
          className="mt-4 max-w-md text-sm leading-relaxed text-gray-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.9, duration: 0.5 }}
        >
          Coordinate diverse AI agents under unified command
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.2, duration: 0.5 }}
          className="mt-8"
        >
          <CTAButton>Enter Command Center</CTAButton>
        </motion.div>

        <ScrollIndicator />
      </section>

      {/* ===== Section 2: Feature Cards ===== */}
      <section className="relative z-10 mx-auto max-w-5xl px-6 py-24">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <FeatureCard key={f.title} {...f} index={i} />
          ))}
        </div>
      </section>

      {/* ===== Section 3: Architecture Visual ===== */}
      <section className="relative z-10 mx-auto max-w-3xl px-6 py-24">
        <motion.h2
          className="mb-12 text-center font-mono text-lg tracking-wider text-green-400/80"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          Orchestration Flow
        </motion.h2>
        <ArchitectureDiagram />
      </section>

      {/* ===== Section 4: Footer CTA ===== */}
      <section className="relative z-10 flex flex-col items-center gap-4 px-6 pb-20 pt-12 text-center">
        <CTAButton>Begin Orchestration</CTAButton>
        <p className="mt-2 text-xs text-gray-500">Built for multi-agent coordination</p>
      </section>
    </div>
  )
}
