# UnblurAI - 文字去模糊识别系统

## 项目简介

UnblurAI 是一个基于 GLM-4.5V 视觉理解模型的智能文字去模糊识别系统。用户可以上传模糊的文字图片，系统会自动识别并还原出清晰的文字内容。该系统采用前后端分离架构，支持实时流式输出，为用户提供流畅的识别体验。

## 项目效果展示

| 阶段   | 图片展示                                                                                         | 说明                   |
|------|----------------------------------------------------------------------------------------------|----------------------|
| 原始图片 | ![原始清晰文字图片](https://github.com/user-attachments/assets/80774491-9451-465d-85a4-b22ad621894a) | 原始清晰文字图片             |
| 识别图片 | ![识别处理模糊图片](https://github.com/user-attachments/assets/558bf4be-c58f-4b27-972b-9f453c322e40) | 用户上传的模糊文字图片，文字内容难以辨认 |
| 识别结果 | ![清晰文字输出结果](https://github.com/user-attachments/assets/c33bd375-8578-47cb-8bd0-1a0c6e51e043) | 系统成功识别并输出的清晰的文字内容    |
| Diff | ![Diff](https://github.com/user-attachments/assets/487edeb9-d65f-4acb-a28a-ffb8be179547)     | 识别结果与原始字段的差异         |   

## 项目截图
<img width="3200" height="1904" alt="83b16f2f7ab4b57cfe8714b898261bf6" src="https://github.com/user-attachments/assets/2b254647-9df0-4e72-ac6b-470178642154" />

## 核心功能

- 🖼️ **智能图片识别**：支持 JPG、PNG、JPEG 格式图片上传（最大 5MB）
- 🤖 **GLM-4.5V 模型**：采用智谱AI最新的视觉理解模型进行文字识别
- 🎯 **提示词优化**：支持自定义提示词，提高识别准确性
- 📱 **响应式设计**：适配桌面端和移动端设备

## 技术栈

### 前端技术
- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - 基于 Vue 3 的组件库
- **Vite** - 现代化前端构建工具
- **Axios** - HTTP 客户端库
- **Pinia** - Vue 状态管理库
- **TypeScript** - 类型安全的 JavaScript 超集

### 后端技术
- **FastAPI** - 现代化 Python Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证和序列化
- **httpx** - 异步 HTTP 客户端
- **Pillow** - Python 图像处理库
- **ZhipuAI SDK** - 智谱AI官方SDK

### AI 模型
- **GLM-4.5V** - 智谱AI视觉理解模型
- **Thinking Mode** - 启用推理模式提升识别准确性

## 项目结构

```
UnblurAI/
├── frontend/                 # 前端项目
│   ├── src/
│   │   ├── components/       # Vue 组件
│   │   ├── views/           # 页面视图
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── utils/           # 工具函数
│   │   └── main.ts          # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # 后端项目
│   ├── api/                 # API 路由
│   ├── models/              # 数据模型
│   ├── services/            # 业务逻辑
│   ├── utils/               # 工具函数
│   ├── main.py              # 应用入口
│   └── requirements.txt     # Python 依赖
└── README.md
```

## 安装和运行


> [!NOTE] 
> 使用本项目需要有效的智谱AI API Key。请访问 [智谱AI开放平台](https://open.bigmodel.cn/) 获取API密钥。

### 环境要求

- Node.js 18+
- Python 3.8+
- 智谱AI API Key

### 1. 克隆项目

```bash
git clone <repository-url>
cd UnblurAI
```

### 2. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
echo "ZHIPUAI_API_KEY=your_api_key_here" > .env

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

## API 接口文档

### 上传并识别图片

**接口地址：** `POST /api/upload-stream`

**请求参数：**
- `file`: 图片文件（multipart/form-data）
- `prompt`: 自定义提示词（可选）

**响应格式：** Server-Sent Events (SSE)

进度事件
```json
{"type": "progress", "message": "正在处理图片...", "progress": 30}
```

成功事件
```json
{"type": "success", "recognized_text": "识别出的文字内容", "processing_time": 2.5}
```

错误事件
```json
{"type": "error", "message": "错误信息"}
```

### 提示词优化

**接口地址：** `POST /api/tune-prompt`

**请求参数：**
```json
{
  "original_prompt": "原始提示词",
  "user_requirements": "用户需求描述"
}
```

**响应格式：**
```json
{
  "optimized_prompt": "优化后的提示词",
  "optimization_suggestions": ["建议1", "建议2"]
}
```

## 使用说明

1. **上传图片**：点击上传区域或拖拽图片文件到指定区域
2. **自定义提示词**：可选择使用默认提示词或输入自定义提示词
3. **开始识别**：点击"开始识别"按钮，系统将实时显示识别进度
4. **查看结果**：识别完成后自动跳转到结果页面显示识别出的文字
5. **复制结果**：可一键复制识别结果到剪贴板

## 许可证

[GPL-3.0 License](LICENSE)
