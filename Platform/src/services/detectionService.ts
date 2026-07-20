import { useDetectionStore } from '@/stores/detection'
import type { OperatorJudgment } from '@/types'

export function useDetectionService() {
  const s = useDetectionStore()
  return {
    get events() { return s.events },
    get selected() { return s.selected },
    get alertCount() { return s.alertCount },
    fetch: () => s.fetch(),
    select: (id: string | null) => s.select(id),
    judge: (id: string, judgment: OperatorJudgment, reason?: string) => s.judge(id, judgment, reason),
  }
}
