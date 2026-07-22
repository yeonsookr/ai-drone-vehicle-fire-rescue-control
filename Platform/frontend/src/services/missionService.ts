import { useMissionStore } from '@/stores/mission'

export function useMissionService() {
  const s = useMissionStore()

  return {
    get missions() { return s.missions },
    get selectedId() { return s.selectedId },
    get selected() { return s.selected },
    get selectedLogs() { return s.selectedLogs },
    get selectedCommands() { return s.selectedCommands },
    get loading() { return s.loading },
    get actionLoading() { return s.actionLoading },
    get error() { return s.error },

    fetch: () => s.fetch(),
    select: (id: string | null) => s.select(id),
    start: (id: string) => s.start(id),
    pause: (id: string) => s.pause(id),
    resume: (id: string) => s.resume(id),
    cancel: (id: string) => s.cancel(id),
  }
}
