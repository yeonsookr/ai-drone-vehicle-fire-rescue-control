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

  function moveMarker(marker: kakao.maps.Marker, lat: number, lng: number) {
    marker.setPosition(new window.kakao.maps.LatLng(lat, lng))
  }

  return { createMap, makeMarker, moveMarker }
}
