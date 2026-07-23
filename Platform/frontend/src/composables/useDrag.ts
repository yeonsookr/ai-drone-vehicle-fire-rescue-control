import type { Ref } from 'vue'
import type { OverlayPos } from '@/stores/ui'

export function useDrag(pos: Ref<OverlayPos | null>) {
  let dragging = false
  let startMouse = { x: 0, y: 0 }
  let startPos = { x: 0, y: 0 }

  function onGrab(e: PointerEvent) {
    dragging = true
    startMouse = { x: e.clientX, y: e.clientY }
    if (pos.value) {
      startPos = { ...pos.value }
    } else {
      // First drag: convert viewport coords to containing-block coords
      const el = e.currentTarget as HTMLElement
      const r = el.getBoundingClientRect()
      const parent = el.offsetParent as HTMLElement
      const pr = parent.getBoundingClientRect()
      startPos = { x: r.left - pr.left, y: r.top - pr.top }
      pos.value = { x: r.left - pr.left, y: r.top - pr.top }
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
