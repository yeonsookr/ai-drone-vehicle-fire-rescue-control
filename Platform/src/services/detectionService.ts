import { useDetectionStore } from '@/stores/detection'
import type { OperatorJudgment } from '@/types'

export function fetchDetections() {
  return useDetectionStore().fetch()
}

export function judgeDetection(id: string, judgment: OperatorJudgment, reason?: string) {
  return useDetectionStore().judge(id, judgment, reason)
}

export function selectDetection(id: string | null) {
  useDetectionStore().select(id)
}
