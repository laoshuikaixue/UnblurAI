<template>
  <div class="result-container">
    <!-- 页面标题 -->
    <div class="header">
      <el-button 
        type="text" 
        @click="goBack"
        class="back-btn"
      >
        <el-icon><ArrowLeft /></el-icon>
        返回首页
      </el-button>
      <h1 class="title">识别结果</h1>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content" v-if="result">
      <!-- 识别结果展示 -->
      <div class="result-display">
        <!-- 原始图片 -->
        <el-card class="image-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📷 原始图片</span>
            </div>
          </template>
          <div 
            class="image-container interactive-image"
            ref="imageContainer"
            @wheel="handleWheel"
            @mousedown="handleMouseDown"
            @mousemove="handleMouseMove"
            @mouseup="handleMouseUp"
            @mouseleave="handleMouseUp"
          >
            <img 
              :src="result.original_image" 
              alt="原始图片" 
              class="original-image" 
              :style="imageStyle"
              draggable="false"
            />
            <div class="image-controls">
              <div class="zoom-info">
                <el-tag size="small">{{ Math.round(imageZoom * 100) }}%</el-tag>
              </div>
              <div class="control-buttons">
                <el-button size="small" @click="resetImageView" :icon="RefreshRight">重置</el-button>
                <el-button size="small" @click="showImageModal = true" :icon="ZoomIn">全屏</el-button>
              </div>
            </div>
            <div class="image-hint" v-if="imageZoom === 1 && !isDragging">
              <span>滚轮缩放 • 拖拽移动</span>
            </div>
          </div>
        </el-card>

        <!-- 识别文字 -->
        <el-card class="text-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>📝 识别文字</span>
            </div>
          </template>
          <div class="text-content">
            <!-- 流式输出日志 - 只在处理中显示 -->
            <div class="streaming-logs" v-if="appStore.streamingLogs.length > 0 && appStore.isStreaming">
              <h4>识别过程</h4>
              <div class="logs-container">
                <div 
                  v-for="(log, index) in appStore.streamingLogs" 
                  :key="index"
                  class="log-item"
                  :class="{ 'error-log': log.startsWith('错误:') }"
                >
                  <el-icon v-if="log.startsWith('错误:')" class="log-icon error"><CircleClose /></el-icon>
                  <el-icon v-else-if="log.includes('完成')" class="log-icon success"><CircleCheck /></el-icon>
                  <el-icon v-else class="log-icon info"><InfoFilled /></el-icon>
                  <span class="log-text">{{ log }}</span>
                  <span class="log-time">{{ new Date().toLocaleTimeString() }}</span>
                </div>
                <div v-if="appStore.isStreaming" class="log-item processing">
                  <el-icon class="log-icon processing"><Loading /></el-icon>
                  <span class="log-text">正在处理中...</span>
                </div>
              </div>
            </div>
            
            <!-- 识别结果 -->
            <div class="recognized-text" v-if="currentText && !appStore.isStreaming">
              {{ currentText }}
            </div>
            <div v-else-if="appStore.isStreaming || (result.isProcessing && !currentText)" class="processing-placeholder">
              <el-icon class="is-loading processing-icon"><Loading /></el-icon>
              <p>{{ appStore.streamingLogs.length > 0 ? appStore.streamingLogs[appStore.streamingLogs.length - 1] : '正在识别图片中的文字内容，请稍候...' }}</p>
            </div>
            
            <div class="text-actions" v-if="currentText">
              <el-button 
                type="primary" 
                @click="copyText"
                :icon="DocumentCopy"
              >
                复制文字
              </el-button>
              <el-button 
                @click="selectAllText"
                :icon="Select"
              >
                全选
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 自然语言微调 -->
      <el-card class="tuning-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>🔧 智能微调</span>
            <el-button 
              type="text" 
              @click="showTuning = !showTuning"
              class="toggle-btn"
            >
              {{ showTuning ? '收起' : '展开' }}
            </el-button>
          </div>
        </template>
        
        <div v-show="showTuning" class="tuning-content">
          <div class="tuning-description">
            <el-alert
              title="使用说明"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>通过自然语言描述来优化识别结果，例如：</p>
                <ul>
                  <li>"请修正错别字"</li>
                  <li>"添加标点符号"</li>
                  <li>"调整段落格式"</li>
                  <li>"翻译成英文"</li>
                </ul>
              </template>
            </el-alert>
          </div>
          
          <el-form :model="tuningForm" class="tuning-form">
            <el-form-item label="优化指令">
              <el-input
                v-model="tuningForm.instruction"
                type="textarea"
                :rows="3"
                placeholder="请描述您希望如何优化识别结果..."
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary"
                @click="handleTuning"
                :loading="tuningLoading"
                :disabled="!tuningForm.instruction.trim()"
              >
                {{ tuningLoading ? '优化中...' : '开始优化' }}
              </el-button>
              <el-button @click="resetText">
                恢复原文
              </el-button>
            </el-form-item>
          </el-form>
          
          <!-- 优化历史 -->
          <div v-if="tuningHistory.length > 0" class="tuning-history">
            <h4>优化历史</h4>
            <div class="history-list">
              <div 
                v-for="(item, index) in tuningHistory" 
                :key="index"
                class="history-item"
              >
                <div class="history-instruction">
                  <el-tag size="small" type="info">{{ item.instruction }}</el-tag>
                </div>
                <div class="history-actions">
                  <el-button 
                    type="text" 
                    size="small"
                    @click="applyHistoryResult(item.result)"
                  >
                    应用此结果
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button 
          type="primary" 
          size="large"
          @click="copyText"
          :icon="DocumentCopy"
        >
          复制最终结果
        </el-button>
        <el-button 
          size="large"
          @click="downloadText"
          :icon="Download"
        >
          下载为文本
        </el-button>
        <el-button 
          size="large"
          @click="recognizeAgain"
          :icon="Refresh"
        >
          重新识别
        </el-button>
      </div>
    </div>

    <!-- 无结果状态 -->
    <div v-else class="no-result">
      <el-empty description="暂无识别结果">
        <el-button type="primary" @click="goBack">返回首页</el-button>
      </el-empty>
    </div>
    
    <!-- Footer -->
    <footer class="footer">
      <p>Powered By LaoShui @ 2025</p>
    </footer>
    
    <!-- 图片放大模态框 -->
    <el-dialog
      v-model="showImageModal"
      title="原始图片预览"
      width="90%"
      :show-close="true"
      center
      class="image-modal"
    >
      <div class="modal-image-container">
        <img 
          :src="result?.original_image" 
          alt="原始图片" 
          class="modal-image"
        />
      </div>
      <template #footer>
        <el-button @click="showImageModal = false" type="primary">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  DocumentCopy,
  Select,
  Download, 
  Refresh,
  ZoomIn,
  Close,
  Loading,
  CircleClose,
  CircleCheck,
  InfoFilled
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

// 响应式数据
const showTuning = ref(false)
const tuningLoading = ref(false)
const currentText = ref('')
const tuningHistory = ref<Array<{instruction: string, result: string}>>([])
const showImageModal = ref(false)

// 图片交互相关数据
const imageContainer = ref<HTMLElement>()
const imageZoom = ref(1)
const imagePosition = reactive({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = reactive({ x: 0, y: 0 })
const lastPosition = reactive({ x: 0, y: 0 })

// 表单数据
const tuningForm = reactive({
  instruction: ''
})

// 计算属性
const result = computed(() => appStore.recognitionResult)

// 图片样式计算属性
const imageStyle = computed(() => ({
  transform: `scale(${imageZoom.value}) translate(${imagePosition.x}px, ${imagePosition.y}px)`,
  transformOrigin: 'center center',
  transition: isDragging.value ? 'none' : 'transform 0.2s ease',
  cursor: isDragging.value ? 'grabbing' : (imageZoom.value > 1 ? 'grab' : 'default')
}))

// 生命周期
onMounted(() => {
  if (result.value) {
    currentText.value = result.value.recognized_text
  } else {
    // 如果没有结果，返回首页
    router.push('/')
  }
})

// 监听识别结果变化
watch(
  () => appStore.recognitionResult?.recognized_text,
  (newText) => {
    if (newText) {
      currentText.value = newText
      console.log('识别结果更新:', newText)
    }
  },
  { immediate: true }
)

// 方法
const goBack = () => {
  router.push('/')
}



const copyText = async () => {
  try {
    await navigator.clipboard.writeText(currentText.value)
    ElMessage.success('文字已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择复制')
  }
}

const selectAllText = () => {
  const textElement = document.querySelector('.recognized-text')
  if (textElement) {
    const range = document.createRange()
    range.selectNodeContents(textElement)
    const selection = window.getSelection()
    selection?.removeAllRanges()
    selection?.addRange(range)
  }
}

const handleTuning = async () => {
  if (!tuningForm.instruction.trim()) {
    ElMessage.warning('请输入优化指令')
    return
  }

  tuningLoading.value = true
  
  try {
    // 调用后端API进行文字微调
    const formData = new FormData()
    formData.append('text', currentText.value)
    formData.append('instruction', tuningForm.instruction)
    
    const response = await fetch('http://localhost:8000/api/tune', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    const optimizedText = result.tuned_text
    
    // 保存到历史记录
    tuningHistory.value.push({
      instruction: tuningForm.instruction,
      result: optimizedText
    })
    
    // 更新当前文字
    currentText.value = optimizedText
    
    ElMessage.success('优化完成！')
    
    // 清空输入框
    tuningForm.instruction = ''
    
  } catch (error) {
    console.error('优化失败:', error)
    ElMessage.error('优化失败，请重试')
  } finally {
    tuningLoading.value = false
  }
}

const resetText = () => {
  if (result.value) {
    currentText.value = result.value.recognized_text
    ElMessage.success('已恢复原始识别结果')
  }
}

const applyHistoryResult = (historyResult: string) => {
  currentText.value = historyResult
  ElMessage.success('已应用历史优化结果')
}

const downloadText = () => {
  const blob = new Blob([currentText.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `识别结果_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('文件下载成功')
}

const recognizeAgain = async () => {
  try {
    await ElMessageBox.confirm(
      '重新识别将清除当前结果和优化历史，是否继续？',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // 清除结果并返回首页
    appStore.clearResult()
    router.push('/')
    
  } catch {
    // 用户取消操作
  }
}

// 图片交互方法
const handleWheel = (event: WheelEvent) => {
  event.preventDefault()
  
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  const newZoom = Math.max(0.5, Math.min(3, imageZoom.value + delta))
  
  imageZoom.value = newZoom
  
  // 如果缩放到1，重置位置
  if (newZoom === 1) {
    imagePosition.x = 0
    imagePosition.y = 0
  }
}

const handleMouseDown = (event: MouseEvent) => {
  if (imageZoom.value <= 1) return
  
  isDragging.value = true
  dragStart.x = event.clientX
  dragStart.y = event.clientY
  lastPosition.x = imagePosition.x
  lastPosition.y = imagePosition.y
  
  event.preventDefault()
}

const handleMouseMove = (event: MouseEvent) => {
  if (!isDragging.value || imageZoom.value <= 1) return
  
  const deltaX = event.clientX - dragStart.x
  const deltaY = event.clientY - dragStart.y
  
  imagePosition.x = lastPosition.x + deltaX / imageZoom.value
  imagePosition.y = lastPosition.y + deltaY / imageZoom.value
  
  event.preventDefault()
}

const handleMouseUp = () => {
  isDragging.value = false
}

const resetImageView = () => {
  imageZoom.value = 1
  imagePosition.x = 0
  imagePosition.y = 0
}
</script>

<style scoped>
.result-container {
  min-height: 100vh;
  background: #f8fafc;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  color: #1e293b;
}

.back-btn {
  color: #64748b;
  font-size: 16px;
  margin-right: 20px;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: white;
  border: 1px solid #e2e8f0;
}

.back-btn:hover {
  background-color: #f1f5f9;
  color: #1e293b;
  border-color: #cbd5e1;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: #0f172a;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.footer {
  text-align: center;
  padding: 40px 20px 20px;
  color: #94a3b8;
  font-size: 14px;
  border-top: 1px solid #e2e8f0;
  margin-top: 40px;
}

.footer p {
  margin: 0;
  font-weight: 500;
}

/* 图片模态框样式 */
.image-modal .el-dialog__body {
  padding: 0;
}

.modal-image-container {
  text-align: center;
  background: #f5f7fa;
  padding: 20px;
}

.modal-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.image-modal .el-dialog__footer {
  text-align: center;
  padding: 20px;
}

.result-display {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.confidence-badge {
  margin-left: 12px;
}

.image-container {
  position: relative;
  text-align: center;
  background: #f8fafc;
  border-radius: 8px;
  overflow: hidden;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.interactive-image {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.original-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  user-select: none;
  -webkit-user-drag: none;
}

.image-controls {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 10;
}

.zoom-info {
  display: flex;
  justify-content: flex-end;
}

.control-buttons {
  display: flex;
  gap: 6px;
}

.image-hint {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  opacity: 0.8;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.image-container:hover .image-hint {
  opacity: 1;
}

.text-content {
  padding: 20px;
}

.recognized-text {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  min-height: 200px;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin-bottom: 16px;
  user-select: text;
  max-height: 300px;
  overflow-y: auto;
}

.text-actions {
  display: flex;
  gap: 12px;
}

.streaming-logs {
  margin-bottom: 20px;
}

.streaming-logs h4 {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.logs-container {
  height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
  padding: 8px;
}

.log-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  margin-bottom: 4px;
  border-radius: 4px;
  background: white;
  font-size: 13px;
  transition: all 0.2s;
}

.log-item:last-child {
  margin-bottom: 0;
}

.log-item.error-log {
  background: #fef0f0;
  border-left: 3px solid #f56c6c;
}

.log-item.processing {
  background: #f0f9ff;
  border-left: 3px solid #409eff;
}

.log-icon {
  margin-right: 8px;
  font-size: 14px;
}

.log-icon.error {
  color: #f56c6c;
}

.log-icon.success {
  color: #67c23a;
}

.log-icon.info {
  color: #909399;
}

.log-icon.processing {
  color: #409eff;
}

.log-text {
  flex: 1;
  color: #606266;
}

.log-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-left: 8px;
}

.processing-placeholder {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.processing-placeholder .processing-icon {
  font-size: 32px;
  margin-bottom: 12px;
  color: #409eff;
}

.processing-placeholder p {
  margin: 0;
  font-size: 14px;
}

.processing-badge .el-tag .el-icon {
  margin-right: 4px;
}

.toggle-btn {
  color: #2563eb;
  font-weight: 500;
}

.tuning-content {
  margin-top: 16px;
}

.tuning-description {
  margin-bottom: 20px;
}

.tuning-form {
  margin-bottom: 20px;
}

.tuning-history {
  border-top: 1px solid #e9ecef;
  padding-top: 20px;
}

.tuning-history h4 {
  margin: 0 0 16px 0;
  color: #64748b;
  font-size: 14px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.no-result {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-container {
    padding: 16px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .result-display {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .el-button {
    width: 100%;
    max-width: 200px;
  }
}
</style>