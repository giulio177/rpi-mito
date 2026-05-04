import { ref } from 'vue'

const isOpen = ref(false)
const inputValue = ref('')
const keyboardTitle = ref('')
let resolvePromise: ((value: string | null) => void) | null = null

export function useKeyboard() {
  const openKeyboard = (initialValue = '', title = 'Inserisci testo') => {
    inputValue.value = initialValue
    keyboardTitle.value = title
    isOpen.value = true
    
    return new Promise<string | null>((resolve) => {
      resolvePromise = resolve
    })
  }

  const close = (save: boolean) => {
    isOpen.value = false
    if (resolvePromise) {
      resolvePromise(save ? inputValue.value : null)
      resolvePromise = null
    }
  }

  const appendChar = (char: string) => { inputValue.value += char }
  const backspace = () => { inputValue.value = inputValue.value.slice(0, -1) }

  return { isOpen, inputValue, keyboardTitle, openKeyboard, close, appendChar, backspace }
}
