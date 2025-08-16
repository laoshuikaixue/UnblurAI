<template>
  <div class="home-container">
    <!-- 项目标题 -->
    <div class="project-header">
      <h1 class="project-title">UnblurAI</h1>
      <p class="project-subtitle">智能文字去模糊识别系统</p>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 提示词设置区域 -->
      <el-card class="prompt-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>🎯 提示词设置</span>
            <el-button 
              type="text" 
              @click="showPromptSettings = !showPromptSettings"
              class="toggle-btn"
            >
              {{ showPromptSettings ? '收起' : '展开' }}
            </el-button>
          </div>
        </template>
        
        <div v-show="showPromptSettings" class="prompt-content">
          <el-form :model="promptForm" label-width="100px">
            <el-form-item label="自定义提示词">
              <el-input
                v-model="promptForm.customPrompt"
                type="textarea"
                :rows="3"
                placeholder="输入自定义提示词来优化识别效果，例如：请识别图片中的中文文字内容"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>
            
            <el-form-item label="预设模板">
              <el-select 
                v-model="promptForm.template" 
                placeholder="选择预设模板"
                @change="onTemplateChange"
                style="width: 100%"
              >
                <el-option label="通用文字识别" value="general" />
                <el-option label="手写文字识别" value="handwritten" />
                <el-option label="印刷文字识别" value="printed" />
                <el-option label="英文文字识别" value="english" />
              </el-select>
            </el-form-item>
          </el-form>
          
          <div class="prompt-tips">
            <el-alert
              title="提示"
              type="info"
              :closable="false"
              show-icon
            >
              <template #default>
                <p>• 清晰描述图片中文字的特征（如手写、印刷、语言等）</p>
                <p>• 指定需要识别的文字类型或格式</p>
                <p>• 提供上下文信息有助于提高识别准确性</p>
              </template>
            </el-alert>
          </div>
        </div>
      </el-card>

      <!-- 文件上传区域 -->
      <el-card class="upload-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>📁 上传图片</span>
          </div>
        </template>
        
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :before-upload="beforeUpload"
          accept=".jpg,.jpeg,.png"
          :limit="1"
          :file-list="fileList"
        >
          <div class="upload-content">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p class="upload-title">点击或拖拽图片到此区域上传</p>
              <p class="upload-hint">支持 JPG、PNG、JPEG 格式，文件大小不超过 5MB</p>
            </div>
          </div>
        </el-upload>
        
        <!-- 上传按钮 -->
        <div class="upload-actions" v-if="fileList.length > 0">
          <el-button 
            type="primary" 
            size="large"
            @click="handleUpload"
            :loading="uploading"
            class="upload-btn"
          >
            {{ uploading ? '识别中...' : '开始识别' }}
          </el-button>
          <el-button 
            @click="clearFiles"
            size="large"
          >
            清除文件
          </el-button>
        </div>
      </el-card>



      <!-- 使用说明 -->
      <el-card class="guide-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>📖 使用说明</span>
          </div>
        </template>
        
        <div class="guide-content">
          <el-steps :active="0" direction="vertical">
            <el-step title="设置提示词" description="根据图片特征选择合适的提示词模板或自定义提示词" />
            <el-step title="上传图片" description="选择需要识别的模糊文字图片，支持拖拽上传" />
            <el-step title="开始识别" description="点击识别按钮，AI将分析图片并提取文字内容" />
            <el-step title="查看结果" description="在结果页面查看识别出的文字，支持进一步微调优化" />
          </el-steps>
        </div>
      </el-card>
    </div>
    
    <!-- Footer -->
    <footer class="footer">
      <p>Powered By LaoShui @ 2025</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { UploadFile, UploadFiles } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

// 响应式数据
const showPromptSettings = ref(false)
const uploading = ref(false)
const fileList = ref<UploadFiles>([])
const uploadRef = ref()

// 提示词表单
const promptForm = reactive({
  customPrompt: '',
  template: ''
})

// 优化的预设模板（简体中文）
const promptTemplates = {
  general: `请仔细识别这张图片中的所有文字内容，特别注意以下要求：
1. 识别所有可见的文字，包括模糊、不清晰或部分遮挡的文字
2. 尽可能准确地还原文字的原始内容和含义
3. 保持原有的文本格式、段落结构和排版布局
4. 对于模糊或不确定的文字，请根据上下文进行合理推测
5. 使用简体中文输出结果
6. 如果图片中包含英文或其他语言，请保持原语言不变
7. 按照从上到下、从左到右的顺序输出文字内容

请直接输出识别到的文字内容，不需要添加额外的说明或解释。`,
  handwritten: `请仔细识别这张图片中的手写文字内容，特别注意以下要求：
1. 重点识别手写字体，包括潦草、模糊或不规范的手写文字
2. 根据笔画特征和上下文推测不清晰的手写字符
3. 保持手写文本的原有格式和段落结构
4. 对于连笔字或草书，请尽量还原其准确含义
5. 使用简体中文输出结果
6. 按照书写顺序输出文字内容

请直接输出识别到的手写文字内容。`,
  printed: `请仔细识别这张图片中的印刷体文字内容，特别注意以下要求：
1. 识别所有印刷体文字，包括不同字体和字号的文本
2. 准确还原印刷文本的格式、段落和排版布局
3. 保持原有的标题、正文、标点符号等结构
4. 识别表格、列表等特殊格式的文本内容
5. 使用简体中文输出结果
6. 按照版面布局顺序输出文字内容

请直接输出识别到的印刷体文字内容。`,
  english: `Please carefully recognize all English text content in this image, with special attention to:
1. Identify all visible English text, including blurred or partially obscured words
2. Accurately restore the original content and meaning of the text
3. Maintain the original text format, paragraph structure and layout
4. For unclear words, make reasonable inferences based on context
5. Output results in English
6. Follow reading order from top to bottom, left to right

Please directly output the recognized English text content without additional explanations.`
}

// 模板选择处理
const onTemplateChange = (value: string) => {
  if (value && promptTemplates[value as keyof typeof promptTemplates]) {
    promptForm.customPrompt = promptTemplates[value as keyof typeof promptTemplates]
  }
}

// 文件变化处理
const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  fileList.value = files
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isValidType = ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 5

  if (!isValidType) {
    ElMessage.error('只支持 JPG、PNG、JPEG 格式的图片！')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('图片大小不能超过 5MB！')
    return false
  }
  return true
}

// 处理上传
const handleUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的图片')
    return
  }

  const file = fileList.value[0].raw
  if (!file) {
    ElMessage.error('文件读取失败')
    return
  }

  uploading.value = true
  
  try {
    // 保存提示词到store
    appStore.setPrompt(promptForm.customPrompt)
    
    // 保存文件信息到store，准备在结果页面使用
    const initialResult = {
      original_image: URL.createObjectURL(file),
      recognized_text: '',
      confidence: 0,
      processing_time: 0,
      isProcessing: true
    }
    
    appStore.setRecognitionResult(initialResult)
    
    // 立即跳转到结果页面
    router.push('/result')
    
    // 在后台开始流式识别
    const formData = new FormData()
    formData.append('file', file)
    if (promptForm.customPrompt) {
      formData.append('custom_prompt', promptForm.customPrompt)
    }
    
    // 使用流式上传API
    const response = await fetch('http://localhost:8000/api/upload-stream', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // 处理流式响应
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    if (!reader) {
      throw new Error('无法读取响应流')
    }
    
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            // 通过store更新结果页面的状态
            appStore.updateStreamingProgress(data)
            
          } catch (parseError) {
            console.error('解析SSE数据失败:', parseError)
          }
        }
      }
    }
    
  } catch (error) {
    console.error('上传失败:', error)
    // 通过store通知结果页面发生错误
    appStore.updateStreamingProgress({
      type: 'error',
      message: '识别失败，请重试'
    })
  } finally {
    uploading.value = false
  }
}

// 清除文件
const clearFiles = () => {
  fileList.value = []
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f8fafc;
  padding: 20px;
}

.project-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 20px 0;
}

.project-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 10px 0;
  color: #0f172a;
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.project-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin: 0;
  font-weight: 400;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  color: #1e293b;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #0f172a;
}

.subtitle {
  font-size: 1.2rem;
  color: #64748b;
  margin: 0;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.toggle-btn {
  color: #3b82f6;
  font-weight: 500;
}

.prompt-content {
  margin-top: 16px;
}

.prompt-tips {
  margin-top: 16px;
}

.upload-demo {
  width: 100%;
}

.upload-content {
  padding: 40px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-title {
  font-size: 16px;
  color: #606266;
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.upload-btn {
  min-width: 120px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.feature-item {
  text-align: center;
  padding: 24px;
  border-radius: 12px;
  background: white;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #cbd5e1;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 12px;
  color: #3b82f6;
}

.feature-item h3 {
  font-size: 16px;
  color: #1e293b;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.feature-item p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.guide-content {
  margin-top: 16px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container {
    padding: 16px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .upload-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .upload-btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>