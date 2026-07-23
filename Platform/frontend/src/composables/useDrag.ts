import type { Ref } from 'vue'
import type { OverlayPos } from '@/stores/ui'

export function useDrag(pos: Ref<OverlayPos | null>) {
  let dragging = false
  let startMouse = { x: 0, y: 0 }
  let startPos = { x: 0, y: 0 }

  function onGrab(e: PointerEvent) {
    if (e.button !== 0) return
    dragging = true
    startMouse = { x: e.clientX, y: e.clientY }
    startPos = { x: pos.value?.x ?? 0, y: pos.value?.y ?? 0 }
    e.preventDefault()
  }

  function onMove(e: PointerEvent) {
    if (!dragging) return
    const dx = e.clientX - startMouse.x
    const dy = e.clientY - startMouse.y
    pos.value = { x: startPos.x + dx, y: startPos.y + dy }
  }

  /** Returns true if a drag was actually in progress */
  function onRelease(): boolean {
    const wasDragging = dragging
    dragging = false
    return wasDragging
  }

  return { onGrab, onMove, onRelease }
}
