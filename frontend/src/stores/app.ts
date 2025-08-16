import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface RecognitionResult {
  original_image: string
  recognized_text: string
  confidence: number
  processing_time?: number
  isProcessing?: boolean
}

export interface StreamingProgress {
  type: 'start' | 'progress' | 'success' | 'error'
  message?: string
  recognized_text?: string
  confidence?: number
  processing_time?: number
}

export const useAppStore = defineStore('app', () => {
  // 状态
  const prompt = ref('')
  const recognitionResult = ref<RecognitionResult | null>(null)
  const isLoading = ref(false)
  const streamingLogs = ref<string[]>([])
  const isStreaming = ref(false)

  // 动作
  const setPrompt = (newPrompt: string) => {
    prompt.value = newPrompt
  }

  const setRecognitionResult = (result: RecognitionResult) => {
    recognitionResult.value = result
  }

  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }

  const clearResult = () => {
    recognitionResult.value = null
    streamingLogs.value = []
    isStreaming.value = false
  }

  const updateStreamingProgress = (progress: StreamingProgress) => {
    switch (progress.type) {
      case 'start':
        isStreaming.value = true
        streamingLogs.value.push(progress.message || '开始识别...')
        break
        
      case 'progress':
        streamingLogs.value.push(progress.message || '处理中...')
        break
        
      case 'success':
        isStreaming.value = false
        streamingLogs.value.push('识别完成！')
        console.log('收到success事件:', progress)
        console.log('当前recognitionResult:', recognitionResult.value)
        if (recognitionResult.value) {
          recognitionResult.value.recognized_text = progress.recognized_text || ''
          recognitionResult.value.confidence = progress.confidence || 0.95
          recognitionResult.value.processing_time = progress.processing_time || 0
          recognitionResult.value.isProcessing = false
          console.log('更新后的recognitionResult:', recognitionResult.value)
        } else {
          console.error('recognitionResult为null，无法更新')
        }
        break
        
      case 'error':
        isStreaming.value = false
        streamingLogs.value.push(`错误: ${progress.message || '识别失败'}`)
        if (recognitionResult.value) {
          recognitionResult.value.isProcessing = false
        }
        break
    }
  }

  const addStreamingLog = (message: string) => {
    streamingLogs.value.push(message)
  }

  const reset = () => {
    prompt.value = ''
    recognitionResult.value = null
    isLoading.value = false
    streamingLogs.value = []
    isStreaming.value = false
  }

  return {
    // 状态
    prompt,
    recognitionResult,
    isLoading,
    streamingLogs,
    isStreaming,
    // 动作
    setPrompt,
    setRecognitionResult,
    setLoading,
    clearResult,
    updateStreamingProgress,
    addStreamingLog,
    reset
  }
})