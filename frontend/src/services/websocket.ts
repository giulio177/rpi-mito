import { useAudioStore } from '@/stores/audio'
import { useBluetoothStore } from '@/stores/bluetooth'
import { useWiFiStore } from '@/stores/wifi'
import type { WebSocketMessage, AudioStatus, BluetoothStatus, WiFiStatus } from '@/types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

type ConnectionCallback = () => void

class WebSocketManager {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private isConnecting = false
  private onConnectCallbacks: ConnectionCallback[] = []
  private onDisconnectCallbacks: ConnectionCallback[] = []

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return
    }

    this.isConnecting = true

    try {
      this.ws = new WebSocket(WS_URL)

      this.ws.onopen = () => {
        console.log('[WS] Connected')
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.onConnectCallbacks.forEach((cb) => cb())
        this.requestStatusUpdate()
      }

      this.ws.onclose = () => {
        console.log('[WS] Disconnected')
        this.isConnecting = false
        this.onDisconnectCallbacks.forEach((cb) => cb())
        this.scheduleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('[WS] Error:', error)
        this.isConnecting = false
      }

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data)
      }
    } catch (error) {
      console.error('[WS] Failed to connect:', error)
      this.isConnecting = false
      this.scheduleReconnect()
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  requestStatusUpdate(): void {
    this.send({ type: 'get_status', data: {} })
  }

  onConnect(callback: ConnectionCallback): void {
    this.onConnectCallbacks.push(callback)
  }

  onDisconnect(callback: ConnectionCallback): void {
    this.onDisconnectCallbacks.push(callback)
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WS] Max reconnect attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(
      `[WS] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`
    )

    setTimeout(() => {
      this.connect()
    }, this.reconnectDelay)
  }

  private handleMessage(data: string): void {
    try {
      const message: { type: string; data: Record<string, unknown> } = JSON.parse(data)

      switch (message.type) {
        case 'status_update':
          this.handleStatusUpdate(message.data)
          break
        case 'audio_update':
          this.handleAudioUpdate(message.data as Partial<AudioStatus>)
          break
        case 'bluetooth_update':
          this.handleBluetoothUpdate(message.data as unknown as BluetoothStatus)
          break
        case 'wifi_update':
          this.handleWiFiUpdate(message.data as unknown as WiFiStatus)
          break
        default:
          console.log('[WS] Unknown message type:', message.type)
      }
    } catch (error) {
      console.error('[WS] Failed to parse message:', error)
    }
  }

  private handleStatusUpdate(data: Record<string, unknown>): void {
    const audioStore = useAudioStore()
    const bluetoothStore = useBluetoothStore()
    const wifiStore = useWiFiStore()

    if (data.audio) {
      audioStore.updateFromWs(data.audio as AudioStatus)
    }
    if (data.bluetooth) {
      bluetoothStore.updateFromWs(data.bluetooth as BluetoothStatus)
    }
    if (data.wifi) {
      wifiStore.updateFromWs(data.wifi as WiFiStatus)
    }
  }

  private handleAudioUpdate(data: Partial<AudioStatus>): void {
    const audioStore = useAudioStore()
    audioStore.updateFromWs(data)
  }

  private handleBluetoothUpdate(data: BluetoothStatus): void {
    const bluetoothStore = useBluetoothStore()
    bluetoothStore.updateFromWs(data)
  }

  private handleWiFiUpdate(data: WiFiStatus): void {
    const wifiStore = useWiFiStore()
    wifiStore.updateFromWs(data)
  }
}

export const wsManager = new WebSocketManager()
export default wsManager