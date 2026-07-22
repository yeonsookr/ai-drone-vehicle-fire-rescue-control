const APP_KEY = import.meta.env.VITE_KAKAO_MAP_KEY

let loaded = false
let loading: Promise<void> | null = null

function loadSdk(): Promise<void> {
  if (loaded) return Promise.resolve()
  if (loading) return loading

  loading = new Promise<void>((resolve, reject) => {
    if (!APP_KEY) {
      reject(new Error('VITE_KAKAO_MAP_KEY 환경변수가 설정되지 않았습니다.'))
      return
    }
    const script = document.createElement('script')
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${APP_KEY}&autoload=false`
    script.onload = () => {
      window.kakao.maps.load(() => {
        loaded = true
        resolve()
      })
    }
    script.onerror = () => reject(new Error('Kakao Map SDK 로드 실패'))
    document.head.appendChild(script)
  })
  return loading
}

function deviceMarkerSvg(type: 'drone' | 'vehicle'): string {
  const droneColor = '#22d3ee'
  const vehicleColor = '#fbbf24'
  const color = type === 'drone' ? droneColor : vehicleColor
  const symbol = type === 'drone'
    ? '<text x="18" y="22" text-anchor="middle" font-size="14" font-family="sans-serif" fill="white" font-weight="bold">D</text>'
    : '<text x="18" y="22" text-anchor="middle" font-size="14" font-family="sans-serif" fill="white" font-weight="bold">V</text>'

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="36" height="42" viewBox="0 0 36 42">
    <path d="M18 0C8.06 0 0 8.06 0 18c0 13.5 18 24 18 24s18-10.5 18-24C36 8.06 27.94 0 18 0z" fill="${color}" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
    <circle cx="18" cy="16" r="10" fill="rgba(0,0,0,0.2)"/>
    ${symbol}
  </svg>`)}`
}

export function useKakaoMap() {
  async function createMap(
    container: HTMLElement,
    center?: { lat: number; lng: number },
    level = 8
  ) {
    await loadSdk()
    return new window.kakao.maps.Map(container, {
      center: new window.kakao.maps.LatLng(center?.lat ?? 37.5665, center?.lng ?? 126.978),
      level,
    })
  }

  function makeMarker(
    map: kakao.maps.Map,
    position: { lat: number; lng: number },
    title?: string
  ) {
    return new window.kakao.maps.Marker({
      map,
      position: new window.kakao.maps.LatLng(position.lat, position.lng),
      title,
    })
  }

  function makeDeviceMarker(
    map: kakao.maps.Map,
    position: { lat: number; lng: number },
    type: 'drone' | 'vehicle',
    title?: string
  ) {
    const image = new window.kakao.maps.MarkerImage(
      deviceMarkerSvg(type),
      new window.kakao.maps.Size(32, 38),
    )
    return new window.kakao.maps.Marker({
      map,
      position: new window.kakao.maps.LatLng(position.lat, position.lng),
      image,
      title,
    })
  }

  function moveMarker(marker: kakao.maps.Marker, lat: number, lng: number) {
    marker.setPosition(new window.kakao.maps.LatLng(lat, lng))
  }

  return { createMap, makeMarker, makeDeviceMarker, moveMarker }
}
