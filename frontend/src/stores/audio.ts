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

  // --- Local Audio Playback (HTML5) ---
  const htmlAudio = ref<HTMLAudioElement | null>(null)
  const localCurrentSong = ref<any>(null)
  const isLocalPlaying = ref(false)
  const localProgress = ref(0)
  const localPlaylist = ref<any[]>([])
  const shuffleEnabled = ref(false)
  const repeatEnabled = ref(false)
  const shuffleRemaining = ref<any[]>([])

  const playNext = () => {
    if (localPlaylist.value.length === 0) return
    
    if (shuffleEnabled.value) {
      if (shuffleRemaining.value.length === 0) {
        if (repeatEnabled.value) {
          shuffleRemaining.value = [...localPlaylist.value]
          if (localCurrentSong.value) {
             shuffleRemaining.value = shuffleRemaining.value.filter(s => s.id !== localCurrentSong.value.id)
          }
        } else {
          isLocalPlaying.value = false
          return // Stop playing
        }
      }
      if (shuffleRemaining.value.length === 0) return
      
      const randomIndex = Math.floor(Math.random() * shuffleRemaining.value.length)
      const nextSong = shuffleRemaining.value[randomIndex]
      shuffleRemaining.value.splice(randomIndex, 1)
      playLocalSong(nextSong, localPlaylist.value, true)
    } else {
      let nextIndex = 0
      if (localCurrentSong.value) {
        const currentIndex = localPlaylist.value.findIndex(s => s.id === localCurrentSong.value.id)
        nextIndex = currentIndex + 1
      }
      
      if (nextIndex >= localPlaylist.value.length) {
        if (repeatEnabled.value) {
          nextIndex = 0
        } else {
          isLocalPlaying.value = false
          return // Stop playing
        }
      }
      playLocalSong(localPlaylist.value[nextIndex], localPlaylist.value, true)
    }
  }

  const playPrevious = () => {
    if (localPlaylist.value.length === 0) return
    
    if (htmlAudio.value && htmlAudio.value.currentTime > 3) {
      htmlAudio.value.currentTime = 0
      return
    }

    if (shuffleEnabled.value) {
       playNext() // On shuffle, just pick another random song
    } else {
      let prevIndex = localPlaylist.value.length - 1
      if (localCurrentSong.value) {
        const currentIndex = localPlaylist.value.findIndex(s => s.id === localCurrentSong.value.id)
        prevIndex = currentIndex - 1
      }
      
      if (prevIndex < 0) {
        prevIndex = localPlaylist.value.length - 1
      }
      playLocalSong(localPlaylist.value[prevIndex], localPlaylist.value, true)
    }
  }

  if (typeof window !== 'undefined') {
    htmlAudio.value = new window.Audio()
    htmlAudio.value.addEventListener('timeupdate', () => {
      if (htmlAudio.value && htmlAudio.value.duration) {
        localProgress.value = (htmlAudio.value.currentTime / htmlAudio.value.duration) * 100
      }
    })
    htmlAudio.value.addEventListener('ended', () => {
      playNext()
    })
  }

  const playLocalSong = (song: any, playlist?: any[], forcePlay = false) => {
    if (!htmlAudio.value) return
    
    if (playlist) {
      localPlaylist.value = playlist
    }
    
    if (localCurrentSong.value?.id === song.id && !forcePlay) {
      // Toggle play/pause if same song
      if (isLocalPlaying.value) {
        htmlAudio.value.pause()
        isLocalPlaying.value = false
      } else {
        htmlAudio.value.play()
        isLocalPlaying.value = true
      }
      return
    }
    
    // Play new song
    localCurrentSong.value = song
    htmlAudio.value.src = `http://localhost:8000/library/${song.filename}`
    htmlAudio.value.play()
    isLocalPlaying.value = true
  }

  const toggleShuffle = () => {
    shuffleEnabled.value = !shuffleEnabled.value
    if (shuffleEnabled.value) {
      shuffleRemaining.value = [...localPlaylist.value]
      if (localCurrentSong.value) {
         shuffleRemaining.value = shuffleRemaining.value.filter(s => s.id !== localCurrentSong.value.id)
      }
    }
  }

  const toggleRepeat = () => {
    repeatEnabled.value = !repeatEnabled.value
  }

  const toggleLocalPlay = () => {
    if (!htmlAudio.value || !localCurrentSong.value) return
    if (isLocalPlaying.value) {
      htmlAudio.value.pause()
      isLocalPlaying.value = false
    } else {
      htmlAudio.value.play()
      isLocalPlaying.value = true
    }
  }

  const seekLocal = (percent: number) => {
    if (!htmlAudio.value || !htmlAudio.value.duration) return
    htmlAudio.value.currentTime = (percent / 100) * htmlAudio.value.duration
    localProgress.value = percent
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
    // Local playback
    htmlAudio,
    localCurrentSong,
    isLocalPlaying,
    localProgress,
    localPlaylist,
    shuffleEnabled,
    repeatEnabled,
    playLocalSong,
    toggleLocalPlay,
    seekLocal,
    playNext,
    playPrevious,
    toggleShuffle,
    toggleRepeat
  }
})