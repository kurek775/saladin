import { useEffect, useRef, useState, type RefObject } from 'react'

interface MousePosition {
  x: number
  y: number
}

/**
 * Returns normalized mouse position (-1 to 1) relative to a ref element.
 * Throttled via requestAnimationFrame. Returns {0, 0} on mouse leave.
 * On touch devices: no effect (graceful degradation).
 */
export function useMousePosition(ref: RefObject<HTMLElement | null>): MousePosition {
  const [pos, setPos] = useState<MousePosition>({ x: 0, y: 0 })
  const rafId = useRef(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const onMove = (e: MouseEvent) => {
      cancelAnimationFrame(rafId.current)
      rafId.current = requestAnimationFrame(() => {
        const rect = el.getBoundingClientRect()
        const x = ((e.clientX - rect.left) / rect.width) * 2 - 1
        const y = ((e.clientY - rect.top) / rect.height) * 2 - 1
        setPos({ x, y })
      })
    }

    const onLeave = () => {
      cancelAnimationFrame(rafId.current)
      setPos({ x: 0, y: 0 })
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)

    return () => {
      cancelAnimationFrame(rafId.current)
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
    }
  }, [ref])

  return pos
}
