<template>
  <div class="document-management">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon"><Document /></el-icon>
        文档管理
      </h1>
      <p class="page-subtitle">
        管理系统中的文档文件，支持上传、查看、编辑和删除
      </p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button type="primary" @click="showUploadDialog = true">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </div>
      <div class="right-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索文档标题或内容"
          style="width: 300px"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="document-list">
      <el-table
        v-loading="loading"
        :data="documentList"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="title" label="文档标题" min-width="200">
          <template #default="{ row }">
            <div class="document-title">
              <el-icon class="file-icon">
                <Document v-if="row.fileType === 'docx' || row.fileType === 'doc'" />
                <Document v-else-if="row.fileType === 'pdf'" />
                <Document v-else />
              </el-icon>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="filename" label="文件名" min-width="150" />
        
        <el-table-column prop="fileType" label="文件类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getFileTypeTag(row.fileType)">
              {{ row.fileType.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="fileSize" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.fileSize) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="userName" label="上传者" width="120" />

        <el-table-column prop="isGraphBuilt" label="图谱状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.isGraphBuilt === 1" type="success">
              <el-icon><Check /></el-icon>
              已构建
            </el-tag>
            <el-tag v-else type="info">未构建</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createTime) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDocument(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="success" @click="downloadDocument(row)">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button size="small" type="primary" @click="editDocument(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteDocument(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 上传文档对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="uploadFormRef" :model="uploadForm" :rules="uploadRules" label-width="80px">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="选择文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :before-upload="beforeUpload"
            accept=".txt,.docx,.doc,.pdf"
:limit="1"
            :file-list="fileList"
            :on-exceed="handleExceed"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 txt、docx、doc、pdf 格式，文件大小不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" :loading="uploading" @click="handleUpload">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 查看文档对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="文档详情"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentDocument" class="document-detail">
        <div class="detail-header">
          <h3>{{ currentDocument.title }}</h3>
          <div class="detail-meta">
            <span>文件名：{{ currentDocument.filename }}</span>
            <span>文件类型：{{ currentDocument.fileType.toUpperCase() }}</span>
            <span>文件大小：{{ formatFileSize(currentDocument.fileSize) }}</span>
            <span>上传者：{{ currentDocument.userName }}</span>
            <span>上传时间：{{ formatDate(currentDocument.createTime) }}</span>
          </div>
        </div>
        <div class="detail-content">
          <div class="content-section">
            <h4>文档摘要</h4>
            <p class="summary-text">{{ currentDocument.summary || '暂无摘要' }}</p>
          </div>
          <div class="content-section">
            <h4>文档内容</h4>
            <div class="content-text markdown-content">
              <div v-html="renderMarkdown(currentDocument.content || '暂无内容')"></div>
            </div>
          </div>
        </div>
        <div class="detail-actions">
          <el-button type="primary" @click="editFromView">
            <el-icon><Edit /></el-icon>
            编辑文档
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑文档对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑文档"
      width="1400px"
      :close-on-click-modal="false"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
        <el-form-item label="文档标题" prop="title">
          <el-input v-model="editForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="文档摘要" prop="summary">
          <div class="form-item-container">
            <el-input
              v-model="editForm.summary"
              type="textarea"
              :rows="3"
              placeholder="请输入文档摘要"
              maxlength="500"
              show-word-limit
            />
            <el-button 
              type="success" 
              size="small"
              :loading="generatingSummary"
              @click="handleGenerateSummary"
              class="ai-action-btn-corner"
            >
              <el-icon><MagicStick /></el-icon>
              AI生成摘要
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="文档内容" prop="content">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="20"
            placeholder="请输入文档内容"
            maxlength="10000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="图谱状态">
          <el-switch
            v-model="editForm.isGraphBuilt"
            :active-value="1"
            :inactive-value="0"
            active-text="已构建"
            inactive-text="未构建"
            active-color="#13ce66"
            inactive-color="#909399"
          />
          <el-alert
            title="提示：修改图谱状态可能导致增量构建逻辑不一致，请谨慎操作"
            type="warning"
            :closable="false"
            show-icon
            style="margin-top: 10px"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" :loading="editing" @click="handleEdit">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Upload, Search, View, Edit, Delete, Download, UploadFilled, MagicStick, Check } from '@element-plus/icons-vue'
import { documentApi } from '@/api/document'
import { fileRequest } from '@/api/file_request'
import { marked } from 'marked'

// 定义文档类型
interface DocumentItem {
  id: number
  title: string
  filename: string
  fileType: string
  fileSize: number
  content: string
  summary: string
  fileBucket: string
  fileObjectKey: string
  fileUrl?: string
  userId: number
  userName: string
  isGraphBuilt: number  // 是否已构建图谱：0-未构建，1-已构建
  status: number
  createTime: string
  updateTime: string
}

// 响应式数据
const loading = ref(false)
const documentList = ref<DocumentItem[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const fileList = ref<any[]>([])

// 对话框状态
const showUploadDialog = ref(false)
const showViewDialog = ref(false)
const showEditDialog = ref(false)
const uploading = ref(false)
const editing = ref(false)
const generatingSummary = ref(false)

// 表单数据
const uploadForm = reactive({
  title: '',
  file: null as File | null
})

const editForm = reactive({
  id: 0,
  title: '',
  summary: '',
  content: '',
  isGraphBuilt: 0
})

const currentDocument = ref<DocumentItem | null>(null)

// 表单验证规则
const uploadRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ],
  file: [
    { required: true, message: '请选择文件', trigger: 'change' }
  ]
}

const editRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ],
  summary: [
    { max: 500, message: '文档摘要不能超过500个字符', trigger: 'blur' }
  ],
  content: [
    { max: 10000, message: '文档内容不能超过10000个字符', trigger: 'blur' }
  ]
}

// 表单引用
const uploadFormRef = ref()
const editFormRef = ref()
const uploadRef = ref()

// 获取文档列表
const getDocumentList = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchKeyword.value || undefined
    }
    
    const response = await documentApi.getList(params)
    documentList.value = response.records
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取文档列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  getDocumentList()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
  getDocumentList()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  getDocumentList()
}

// 文件上传处理
const handleFileChange = (file: any, fileListParam: any[]) => {
  // 清空之前的文件列表，确保只保留最新上传的文件
  fileList.value = [file]
  uploadForm.file = file.raw
  
  // 自动回填文档标题（去掉文件后缀）
  if (file.name) {
    const fileName = file.name
    const lastDotIndex = fileName.lastIndexOf('.')
    if (lastDotIndex > 0) {
      uploadForm.title = fileName.substring(0, lastDotIndex)
    } else {
      uploadForm.title = fileName
    }
  }
}

// 文件移除处理
const handleFileRemove = () => {
  fileList.value = []
  uploadForm.file = null
  uploadForm.title = ''
}

// 处理文件数量超限
const handleExceed = (files: File[]) => {
  // 清空当前文件列表，只保留最新选择的文件
  uploadRef.value.clearFiles()
  const file = files[files.length - 1] // 取最后一个文件（最新选择的）
  uploadRef.value.handleStart(file)
  uploadRef.value.handleSuccess(file)
}



const beforeUpload = (file: File) => {
  const isValidType = ['.txt', '.docx', '.doc', '.pdf'].some(ext => 
    file.name.toLowerCase().endsWith(ext)
  )
  if (!isValidType) {
    ElMessage.error('只支持 txt、docx、doc、pdf 格式的文件')
    return false
  }
  
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  return false // 阻止自动上传
}

const handleUpload = async () => {
  if (!uploadForm.file) {
    ElMessage.error('请选择文件')
    return
  }
  
  try {
    await uploadFormRef.value.validate()
    uploading.value = true
    
    const formData = new FormData()
    formData.append('title', uploadForm.title)
    formData.append('file', uploadForm.file)
    
    await documentApi.upload(formData)
    ElMessage.success('文档上传成功')
    showUploadDialog.value = false
    resetUploadForm()
    getDocumentList()
  } catch (error) {
    ElMessage.error('文档上传失败')
  } finally {
    uploading.value = false
  }
}

const resetUploadForm = () => {
  uploadForm.title = ''
  uploadForm.file = null
  fileList.value = []
  uploadFormRef.value?.resetFields()
  uploadRef.value?.clearFiles()
}

// 查看文档
const viewDocument = async (document: DocumentItem) => {
  try {
    const response = await documentApi.getDetail(document.id)
    currentDocument.value = response
    showViewDialog.value = true
  } catch (error) {
    ElMessage.error('获取文档详情失败')
  }
}

// 编辑文档
const editDocument = (document: DocumentItem) => {
  editForm.id = document.id
  editForm.title = document.title
  editForm.summary = document.summary
  editForm.content = document.content
  editForm.isGraphBuilt = document.isGraphBuilt
  showEditDialog.value = true
}

// 从查看对话框跳转到编辑
const editFromView = () => {
  if (currentDocument.value) {
    editForm.id = currentDocument.value.id
    editForm.title = currentDocument.value.title
    editForm.summary = currentDocument.value.summary
    editForm.content = currentDocument.value.content
    editForm.isGraphBuilt = currentDocument.value.isGraphBuilt
    showViewDialog.value = false
    showEditDialog.value = true
  }
}

const handleEdit = async () => {
  try {
    await editFormRef.value.validate()
    editing.value = true

    await documentApi.update(editForm.id, {
      title: editForm.title,
      summary: editForm.summary,
      content: editForm.content,
      isGraphBuilt: editForm.isGraphBuilt
    })
    ElMessage.success('文档更新成功')
    showEditDialog.value = false
    getDocumentList()
  } catch (error) {
    ElMessage.error('文档更新失败')
  } finally {
    editing.value = false
  }
}

// 生成文档摘要
const handleGenerateSummary = async () => {
  try {
    // 检查文本长度限制
    if (!editForm.content || editForm.content.trim().length === 0) {
      ElMessage.warning('请先输入文档内容')
      return
    }
    
    if (editForm.content.length > 10000) {
      ElMessage.warning('文档内容不能超过10000字，请精简内容后重试')
      return
    }
    
    generatingSummary.value = true
    
    // 使用编辑表单中的内容生成摘要
    const response = await documentApi.generateSummary(editForm.content)
    ElMessage.success('摘要生成成功')
    
    // 直接更新编辑表单中的摘要
    editForm.summary = response.summary
  } catch (error) {
    ElMessage.error('摘要生成失败')
  } finally {
    generatingSummary.value = false
  }
}



// 下载文档
const downloadDocument = async (doc: DocumentItem) => {
  try {
    if (!doc.fileBucket || !doc.fileObjectKey) {
      ElMessage.error('文档文件信息缺失，无法下载')
      return
    }

    ElMessage.info('正在准备下载...')
    
    // 使用fileRequest获取文件blob
    const blob = await fileRequest.get(doc.fileBucket, doc.fileObjectKey)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = doc.filename || `${doc.title}.${doc.fileType}`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 删除文档
const deleteDocument = async (document: DocumentItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文档"${document.title}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await documentApi.delete(document.id)
    ElMessage.success('文档删除成功')
    getDocumentList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('文档删除失败')
    }
  }
}

// 工具函数
const getFileTypeTag = (fileType: string) => {
  const typeMap: Record<string, 'primary' | 'success' | 'warning' | 'info' | 'danger'> = {
    'txt': 'info',
    'docx': 'primary',
    'doc': 'warning',
    'pdf': 'danger'
  }
  return typeMap[fileType] || 'info'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// Markdown渲染函数
const renderMarkdown = (content: string) => {
  if (!content || content === '暂无内容') {
    return content
  }
  try {
    return marked(content)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return content
  }
}

// 生命周期
onMounted(() => {
  getDocumentList()
})
</script>

<style scoped>
.document-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.title-icon {
  margin-right: 8px;
  color: #409eff;
}

.page-subtitle {
  color: #666;
  margin: 0;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.document-list {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.document-title {
  display: flex;
  align-items: center;
}

.file-icon {
  margin-right: 8px;
  color: #409eff;
}

.pagination-wrapper {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.document-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.detail-header h3 {
  margin: 0 0 12px 0;
  color: #333;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 14px;
  color: #666;
}

.detail-meta span {
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
}

.detail-content h4 {
  margin: 16px 0 8px 0;
  color: #333;
}

.content-text {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  max-height: 300px;
  overflow-y: auto;
}

.content-text pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.content-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px dashed #eee;
}

.content-section:last-child {
  border-bottom: none;
}

.summary-text {
  color: #666;
  font-style: italic;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.detail-actions {
  margin-top: 20px;
  text-align: right;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.form-item-container {
  position: relative;
  width: 100%;
}

.form-item-container .el-input {
  width: 100%;
}

.form-item-container .el-textarea {
  width: 100%;
}

.form-item-container .el-textarea__inner {
  width: 100%;
  min-height: 300px;
  resize: vertical;
}


.ai-action-btn-corner {
  position: absolute;
  bottom: 8px;
  right: 8px;
  z-index: 10;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-action-tip {
  position: absolute;
  bottom: 8px;
  right: 120px;
  z-index: 10;
}

.ai-action-tip small {
  color: #909399;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #e4e7ed;
}

/* 确保文本域在布局中正确显示 */
.el-form-item__content {
  width: 100%;
}

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.6;
  color: #333;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  color: #2c3e50;
}

.markdown-content h1 { font-size: 24px; }
.markdown-content h2 { font-size: 20px; }
.markdown-content h3 { font-size: 18px; }
.markdown-content h4 { font-size: 16px; }
.markdown-content h5 { font-size: 14px; }
.markdown-content h6 { font-size: 12px; }

.markdown-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content li {
  margin: 4px 0;
  line-height: 1.6;
}

.markdown-content blockquote {
  margin: 12px 0;
  padding: 8px 16px;
  border-left: 4px solid #409eff;
  background-color: #f8f9fa;
  color: #666;
}

.markdown-content code {
  background-color: #f1f3f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content pre {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 12px 0;
}

.markdown-content pre code {
  background-color: transparent;
  padding: 0;
}

.markdown-content strong {
  font-weight: 600;
  color: #2c3e50;
}

.markdown-content em {
  font-style: italic;
  color: #666;
}

.markdown-content a {
  color: #409eff;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.markdown-content hr {
  border: none;
  border-top: 1px solid #eee;
  margin: 16px 0;
}
</style>
