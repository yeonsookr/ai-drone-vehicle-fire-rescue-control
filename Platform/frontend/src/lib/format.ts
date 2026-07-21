export function fmtCoord(lat: number, lng: number, precision = 4): string {
  return `${lat.toFixed(precision)}, ${lng.toFixed(precision)}`
}

export function fmtTime(iso: string): string {
  if (!iso || iso === '-') return '-'
  return iso.slice(0, 19).replace('T', ' ')
}

export function fmtBattery(v: number): string {
  return `${v.toFixed(0)}%`
}

export function fmtAltitude(m: number): string {
  return `${m.toFixed(0)}m`
}

export function fmtSpeed(mps: number): string {
  return `${mps.toFixed(1)} m/s`
}

export function fmtHeading(deg: number): string {
  return `${deg.toFixed(0)}°`
}

export function fmtConfidence(v: number): string {
  return `${(v * 100).toFixed(0)}%`
}

export function isErrorBattery(battery: number): boolean {
  return battery <= 10
}

export function isWarnBattery(battery: number): boolean {
  return battery <= 30 && battery > 10
}
