import axios, { type AxiosInstance, type AxiosError } from 'axios'
import type {
  AudioStatus,
  BluetoothStatus,
  WiFiStatus,
  BluetoothDevice,
  WiFiNetwork,
  ApiResponse,
} from '@/types'

const getApiUrl = (): string => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.host}`
  }
  return 'http://localhost:8000'
}

export const API_BASE_URL = getApiUrl()

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('[API Error]', error.message)
        return Promise.reject(error)
      }
    )
  }

  async getAudioStatus(): Promise<AudioStatus> {
    const response = await this.client.get<AudioStatus>('/api/audio/status')
    return response.data
  }

  async setVolume(level: number): Promise<ApiResponse<{ volume: number }>> {
    const response = await this.client.post<ApiResponse<{ volume: number }>>(
      `/api/audio/volume?level=${level}`
    )
    return response.data
  }

  async setMuted(muted: boolean): Promise<ApiResponse<{ muted: boolean }>> {
    const response = await this.client.post<ApiResponse<{ muted: boolean }>>(
      `/api/audio/mute?muted=${muted}`
    )
    return response.data
  }

  async getBluetoothStatus(): Promise<BluetoothStatus> {
    const response = await this.client.get<BluetoothStatus>('/api/bluetooth/status')
    return response.data
  }

  async getBluetoothDevices(): Promise<BluetoothDevice[]> {
    const response = await this.client.get<BluetoothDevice[]>('/api/bluetooth/devices')
    return response.data
  }

  async connectBluetooth(address: string): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>(
      `/api/bluetooth/connect?address=${address}`
    )
    return response.data
  }

  async disconnectBluetooth(): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>('/api/bluetooth/disconnect')
    return response.data
  }

  async unpairBluetooth(address: string): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>(
      `/api/bluetooth/unpair?address=${address}`
    )
    return response.data
  }

  async getWiFiStatus(): Promise<WiFiStatus> {
    const response = await this.client.get<WiFiStatus>('/api/wifi/status')
    return response.data
  }

  async getWiFiNetworks(): Promise<WiFiNetwork[]> {
    const response = await this.client.get<WiFiNetwork[]>('/api/wifi/networks')
    return response.data
  }

  async connectWiFi(ssid: string, password?: string): Promise<ApiResponse<void>> {
    const params = new URLSearchParams({ ssid })
    if (password) {
      params.append('password', password)
    }
    const response = await this.client.post<ApiResponse<void>>(
      `/api/wifi/connect?${params.toString()}`
    )
    return response.data
  }

  async disconnectWiFi(): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>('/api/wifi/disconnect')
    return response.data
  }

  async forgetWiFi(ssid: string): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>(`/api/wifi/forget?ssid=${ssid}`)
    return response.data
  }

  async playBluetooth(): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>('/api/bluetooth/player/play')
    return response.data
  }

  async pauseBluetooth(): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>('/api/bluetooth/player/pause')
    return response.data
  }

  async nextBluetooth(): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>('/api/bluetooth/player/next')
    return response.data
  }

  async previousBluetooth(): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>('/api/bluetooth/player/previous')
    return response.data
  }

  async setBluetoothShuffle(mode: string): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>(
      `/api/bluetooth/player/shuffle?mode=${mode}`
    )
    return response.data
  }

  async setBluetoothRepeat(mode: string): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>(
      `/api/bluetooth/player/repeat?mode=${mode}`
    )
    return response.data
  }

  async setDiscoverable(enabled: boolean): Promise<ApiResponse<void>> {
    const response = await this.client.post<ApiResponse<void>>(
      `/api/bluetooth/discoverable?enabled=${enabled}`
    )
    return response.data
  }
}

export const api = new ApiClient()
export default api