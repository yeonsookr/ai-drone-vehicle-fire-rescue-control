import { useMissionStore } from '@/stores/mission'

export function useMissionService() {
  const s = useMissionStore()
  return {
    get missions() { return s.missions },
    get selectedId() { return s.selectedId },
    get selected() { return s.selected },
    get loading() { return s.loading },
    get error() { return s.error },
    fetch: () => s.fetch(),
    select: (id: string | null) => s.select(id),
  }
}
