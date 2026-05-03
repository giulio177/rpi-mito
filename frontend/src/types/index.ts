export interface AudioStatus {
  volume: number
  muted: boolean
  current_source: string | null
  current_track: TrackInfo | null
  playback_status: PlaybackStatus
}

export interface TrackInfo {
  title: string
  artist: string
  album: string
  duration: number
  position: number
}

export type PlaybackStatus = 'playing' | 'paused' | 'stopped'

export interface BluetoothDevice {
  address: string
  name: string
  connected: boolean
  paired: boolean
}

export interface BluetoothStatus {
  enabled: boolean
  discovering: boolean
  connected_device: BluetoothDevice | null
  devices: BluetoothDevice[]
}

export interface WiFiNetwork {
  ssid: string
  bssid: string
  signal: number
  security: string
  connected: boolean
}

export interface WiFiStatus {
  enabled: boolean
  connected: boolean
  current_ssid: string | null
  ip_address: string | null
  networks: WiFiNetwork[]
}

export type WebSocketMessageType =
  | 'status_update'
  | 'get_status'
  | 'audio_update'
  | 'bluetooth_update'
  | 'wifi_update'
  | 'obd_update'

export interface WebSocketMessage {
  type: WebSocketMessageType
  data: Record<string, unknown>
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}