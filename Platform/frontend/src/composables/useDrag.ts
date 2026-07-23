import type { Ref } from 'vue'
import type { OverlayPos } from '@/stores/ui'

export function useDrag(pos: Ref<OverlayPos | null>) {
  let dragging = false
  let startMouse = { x: 0, y: 0 }

  /** Call from the drag handle's @pointerdown */
  function onGrab(e: PointerEvent) {
    if (e.button !== 0) return
    dragging = true
    startMouse = { x: e.clientX, y: e.clientY }
    // pos.value stays null until first actual move
    // Default CSS positioning remains in effect
    e.preventDefault()
  }

  function onMove(e: PointerEvent) {
    if (!dragging) return
    const dx = e.clientX - startMouse.x
    const dy = e.clientY - startMouse.y
    pos.value = { x: dx, y: dy }
  }

  /** Returns true if a drag was actually in progress */
  function onRelease(): boolean {
    const wasDragging = dragging
    dragging = false
    return wasDragging
  }

  return { onGrab, onMove, onRelease }
}
