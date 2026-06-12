export interface AudioStatus {
  volume: number
  muted: boolean
  current_source: string | null
  current_track: TrackInfo | null
  playback_status: PlaybackStatus
  shuffle?: string
  repeat?: string
}

export interface TrackInfo {
  title: string
  artist: string
  album: string
  duration: number
  position: number
  cover_art?: string
}

export type PlaybackStatus = 'playing' | 'paused' | 'stopped'

export interface BluetoothDevice {
  address: string
  name: string
  connected: boolean
  paired: boolean
}

export interface BluetoothStatus {
  connected: boolean
  device_name: string | null
  device_address: string | null
  battery_level: number | null
  available_devices: any[]
}

export interface WiFiNetwork {
  ssid: string
  bssid: string
  signal: number
  security: string
  connected: boolean
}

export interface WiFiStatus {
  connected: boolean
  ssid: string | null
  ip_address: string | null
  signal_strength: number
  available_networks: any[]
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