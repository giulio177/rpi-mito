import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AudioStatus, TrackInfo, PlaybackStatus } from '@/types'
import api from '@/services/api'

export const useAudioStore = defineStore('audio', () => {
  const volume = ref(50)
  const muted = ref(false)
  const currentSource = ref<string | null>(null)
  const currentTrack = ref<TrackInfo | null>(null)
  const playbackStatus = ref<PlaybackStatus>('stopped')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const effectiveVolume = computed(() => (muted.value ? 0 : volume.value))

  async function fetchStatus(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const status = await api.getAudioStatus()
      volume.value = status.volume
      muted.value = status.muted
      currentSource.value = status.current_source
      currentTrack.value = status.current_track
      playbackStatus.value = status.playback_status
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch audio status'
    } finally {
      isLoading.value = false
    }
  }

  async function setVolume(level: number): Promise<void> {
    const clampedLevel = Math.max(0, Math.min(100, level))
    error.value = null
    try {
      const result = await api.setVolume(clampedLevel)
      if (result.success && result.data) {
        volume.value = result.data.volume
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to set volume'
    }
  }

  async function setMuted(mute: boolean): Promise<void> {
    error.value = null
    try {
      const result = await api.setMuted(mute)
      if (result.success && result.data) {
        muted.value = result.data.muted
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to set mute'
    }
  }

  async function toggleMute(): Promise<void> {
    await setMuted(!muted.value)
  }

  function updateFromWs(data: Partial<AudioStatus>): void {
    if (data.volume !== undefined) {
      volume.value = data.volume
    }
    if (data.muted !== undefined) {
      muted.value = data.muted
    }
    if (data.current_source !== undefined) {
      currentSource.value = data.current_source
    }
    if (data.current_track !== undefined) {
      currentTrack.value = data.current_track
    }
    if (data.playback_status !== undefined) {
      playbackStatus.value = data.playback_status
    }
  }

  return {
    volume,
    muted,
    currentSource,
    currentTrack,
    playbackStatus,
    isLoading,
    error,
    effectiveVolume,
    fetchStatus,
    setVolume,
    setMuted,
    toggleMute,
    updateFromWs,
  }
})