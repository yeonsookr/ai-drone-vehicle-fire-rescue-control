import type { Ref } from 'vue'
import type { OverlayPos } from '@/stores/ui'

export function useDrag(pos: Ref<OverlayPos | null>) {
  let dragging = false
  let startMouse = { x: 0, y: 0 }
  let startPos = { x: 0, y: 0 }

  /** Call from the drag handle's @pointerdown */
  function onGrab(e: PointerEvent) {
    // Only respond to primary button (left click)
    if (e.button !== 0) return
    dragging = true
    startMouse = { x: e.clientX, y: e.clientY }
    if (pos.value) {
      startPos = { ...pos.value }
    } else {
      const el = e.currentTarget as HTMLElement
      const container = (el.offsetParent ?? el.parentElement) as HTMLElement
      const cr = container.getBoundingClientRect()
      const er = el.getBoundingClientRect()
      // Position the overlay so the handle stays under the cursor
      startPos = { x: er.left - cr.left, y: er.top - cr.top }
    }
    e.preventDefault()
  }

  function onMove(e: PointerEvent) {
    if (!dragging) return
    const dx = e.clientX - startMouse.x
    const dy = e.clientY - startMouse.y
    pos.value = { x: startPos.x + dx, y: startPos.y + dy }
  }

  function onRelease() {
    dragging = false
  }

  return { onGrab, onMove, onRelease }
}
