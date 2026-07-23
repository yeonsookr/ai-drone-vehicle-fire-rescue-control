/**
 * Video stream URL management.
 * Encapsulates MJPEG/RTSP/WebSocket stream source configuration.
 *
 * Currently configured for the USB webcam MJPEG server at:
 *   http://70.12.247.78:5000/video
 *
 * When each device has its own stream endpoint, extend this to
 * resolve per-device URLs (e.g. /video/DRONE-001).
 */

const STREAM_BASE = import.meta.env.VITE_STREAM_BASE_URL ?? 'http://70.12.247.78:5000'

export function useVideoStream() {
  /** Returns the MJPEG feed URL for a given device, or the default feed. */
  function getUrl(_deviceId?: string): string {
    // Future: resolve per-device endpoint, e.g. `${STREAM_BASE}/video/${deviceId}`
    return `${STREAM_BASE}/video`
  }

  /** MJPEG streams use <img src="…"> natively (multipart/x-mixed-replace). */
  function isMjpg(url: string): boolean {
    return url.includes('/video')
  }

  return { getUrl, isMjpg }
}
