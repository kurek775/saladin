import { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, ShieldCheck } from 'lucide-react'

const SESSION_KEY = 'saladin-splash-seen'
const TOTAL_DURATION = 3000
const EXIT_DURATION = 0.6

const CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF'

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
      canvas!.width = window.innerWidth
      canvas!.height = window.innerHeight
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
        const char = CHARS[Math.floor(Math.random() * CHARS.length)]
        const x = i * fontSize
        const y = columns[i] * fontSize

        const brightness = Math.random()
        if (brightness > 0.9) {
          ctx!.fillStyle = '#ffffff'
        } else if (brightness > 0.6) {
          ctx!.fillStyle = '#22c55e'
        } else {
          ctx!.fillStyle = 'rgba(34, 197, 94, 0.4)'
        }

        ctx!.fillText(char, x, y)
        columns[i]++

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

// SVG layout constants
const SVG_W = 400
const SVG_H = 240
const SUP_CX = SVG_W / 2
const SUP_CY = 50
const SUP_R = 30
const WORKER_R = 22
const WORKER_Y = 190
const WORKER_XS = [80, 160, 240, 320]

function AgentNetwork() {
  return (
    <svg
      viewBox={`0 0 ${SVG_W} ${SVG_H}`}
      className="w-[320px] sm:w-[400px] mx-auto"
      fill="none"
    >
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
            transition={{ duration: 0.8, delay: 0.6 + i * 0.12, ease: 'easeOut' }}
            opacity={0.6}
          />
        )
      })}

      {/* Supervisor node */}
      <motion.g
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        {/* Glow */}
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
          transition={{ duration: 0.4, delay: 0.8 + i * 0.15 }}
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
    </svg>
  )
}

function TypewriterText({ text, delay, className }: { text: string; delay: number; className?: string }) {
  const [displayed, setDisplayed] = useState('')

  useEffect(() => {
    const timeout = setTimeout(() => {
      let i = 0
      const interval = setInterval(() => {
        i++
        setDisplayed(text.slice(0, i))
        if (i >= text.length) clearInterval(interval)
      }, 70)
      return () => clearInterval(interval)
    }, delay)
    return () => clearTimeout(timeout)
  }, [text, delay])

  return (
    <span className={className}>
      {displayed}
      {displayed.length < text.length && (
        <span className="inline-block w-[2px] h-[1em] bg-green-500 ml-0.5 animate-pulse align-middle" />
      )}
    </span>
  )
}

export function SplashScreen() {
  const [visible, setVisible] = useState(() => {
    if (sessionStorage.getItem(SESSION_KEY)) return false
    sessionStorage.setItem(SESSION_KEY, '1')
    return true
  })
  const [exiting, setExiting] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useMatrixRain(canvasRef)

  const handleExit = useCallback(() => {
    setExiting(true)
  }, [])

  useEffect(() => {
    if (!visible) return
    const timer = setTimeout(handleExit, TOTAL_DURATION)
    return () => clearTimeout(timer)
  }, [visible, handleExit])

  if (!visible && !exiting) return null

  return (
    <AnimatePresence onExitComplete={() => setVisible(false)}>
      {!exiting && (
        <motion.div
          key="splash"
          className="fixed inset-0 z-50 flex flex-col items-center justify-center"
          style={{ backgroundColor: '#030712' }}
          exit={{ opacity: 0 }}
          transition={{ duration: EXIT_DURATION, ease: 'easeInOut' }}
        >
          {/* Matrix rain canvas */}
          <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" />

          {/* Content layer */}
          <div className="relative z-10 flex flex-col items-center gap-6">
            <AgentNetwork />

            <div className="flex flex-col items-center gap-2 mt-2">
              <TypewriterText
                text="SALADIN"
                delay={1400}
                className="font-mono text-3xl sm:text-4xl font-bold tracking-[0.3em] text-green-400"
              />

              <motion.span
                className="font-mono text-sm tracking-widest text-green-500/60"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2.2, duration: 0.5 }}
              >
                Multi-Agent Orchestration
              </motion.span>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
