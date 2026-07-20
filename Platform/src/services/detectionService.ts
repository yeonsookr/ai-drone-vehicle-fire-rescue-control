import { useDetectionStore } from '@/stores/detection'
import type { OperatorJudgment } from '@/types'

let _store: ReturnType<typeof useDetectionStore> | null = null
function store() {
  if (!_store) _store = useDetectionStore()
  return _store
}

export function useDetectionService() {
  const s = store()
  return {
    events: s.events,
    selected: s.selected,
    selectedId: s.selectedId,
    alertCount: s.alertCount,
    fetch: () => s.fetch(),
    select: (id: string | null) => s.select(id),
    judge: (id: string, judgment: OperatorJudgment, reason?: string) => s.judge(id, judgment, reason),
  }
}
