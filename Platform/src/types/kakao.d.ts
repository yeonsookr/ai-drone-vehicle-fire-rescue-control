declare namespace kakao.maps {
  class Map {
    constructor(container: HTMLElement, options: MapOptions)
    setCenter(latlng: LatLng): void
    setLevel(level: number): void
    setMapTypeId(mapTypeId: number): void
    getCenter(): LatLng
    getLevel(): number
  }

  interface MapOptions {
    center: LatLng
    level?: number
    mapTypeId?: number
    draggable?: boolean
    scrollwheel?: boolean
  }

  class LatLng {
    constructor(lat: number, lng: number)
    getLat(): number
    getLng(): number
  }

  class Marker {
    constructor(options: MarkerOptions)
    setMap(map: Map | null): void
    setPosition(position: LatLng): void
    getPosition(): LatLng
  }

  interface MarkerOptions {
    map?: Map
    position: LatLng
    title?: string
    clickable?: boolean
    image?: MarkerImage
  }

  class MarkerImage {
    constructor(src: string, size: Size, options?: MarkerImageOptions)
  }

  class Size {
    constructor(width: number, height: number)
  }

  interface MarkerImageOptions {
    offset?: Point
  }

  class Point {
    constructor(x: number, y: number)
  }

  function load(callback: () => void): void
}

interface Window {
  kakao: typeof kakao
}
