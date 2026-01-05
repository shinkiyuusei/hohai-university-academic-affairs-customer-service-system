<template>
  <div class="disease-case-management">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon"><Document /></el-icon>
        植物病害案例管理
      </h1>
      <p class="page-subtitle">
        管理植物病害的具体案例，记录病害发生的详细信息和治疗措施
      </p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          添加案例
        </el-button>
      </div>
      <div class="right-actions">
        <el-select
          v-model="filterDiseaseId"
          placeholder="筛选病害"
          clearable
          style="width: 200px; margin-right: 12px"
          @change="loadCaseList"
        >
          <el-option
            v-for="option in diseaseOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索案例标题或地点"
          style="width: 300px"
          clearable
          @keyup.enter="loadCaseList"
        >
          <template #append>
            <el-button @click="loadCaseList">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 案例列表 -->
    <div class="case-list">
      <el-table
        v-loading="loading"
        :data="caseList"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="caseTitle" label="案例标题" min-width="200" />

        <el-table-column prop="diseaseName" label="关联病害" width="140">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.diseaseName }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="location" label="发生地点" width="140" />

        <el-table-column prop="plantType" label="植物种类" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.plantType || '-' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="severityLevel" label="严重程度" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severityLevel)">
              {{ row.severityLevel || '-' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="caseDate" label="发生时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.caseDate) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewCase(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="primary" @click="editCase(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteCase(row)">
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

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="dialogTitle"
      width="750px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="120px">
        <el-form-item label="关联病害" prop="diseaseId">
          <el-select
            v-model="form.diseaseId"
            placeholder="请选择关联的病害"
            style="width: 100%"
          >
            <el-option
              v-for="option in diseaseOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="案例标题" prop="caseTitle">
          <el-input v-model="form.caseTitle" placeholder="请输入案例标题" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发生地点" prop="location">
              <el-input v-model="form.location" placeholder="如：江苏省南京市" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发生时间" prop="caseDate">
              <el-date-picker
                v-model="form.caseDate"
                type="datetime"
                placeholder="选择日期时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="植物种类" prop="plantType">
              <el-select
                v-model="form.plantType"
                placeholder="请选择"
                style="width: 100%"
                filterable
                allow-create
              >
                <el-option label="水稻" value="水稻" />
                <el-option label="小麦" value="小麦" />
                <el-option label="玉米" value="玉米" />
                <el-option label="番茄" value="番茄" />
                <el-option label="马铃薯" value="马铃薯" />
                <el-option label="柑橘" value="柑橘" />
                <el-option label="苹果" value="苹果" />
                <el-option label="葡萄" value="葡萄" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="严重程度" prop="severityLevel">
              <el-select v-model="form.severityLevel" placeholder="请选择" style="width: 100%">
                <el-option label="轻度" value="轻度" />
                <el-option label="中度" value="中度" />
                <el-option label="重度" value="重度" />
                <el-option label="严重" value="严重" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="感染面积" prop="infectionArea">
          <el-input-number
            v-model="form.infectionArea"
            :min="0"
            :precision="2"
            placeholder="单位：亩"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="案例描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述病害案例"
          />
        </el-form-item>

        <el-form-item label="经济损失" prop="economicLoss">
          <el-input-number
            v-model="form.economicLoss"
            :min="0"
            :precision="2"
            placeholder="单位：万元"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="治疗方法" prop="treatmentMethod">
          <el-input
            v-model="form.treatmentMethod"
            type="textarea"
            :rows="3"
            placeholder="描述采取的治疗方法"
          />
        </el-form-item>

        <el-form-item label="治疗效果" prop="treatmentResult">
          <el-input
            v-model="form.treatmentResult"
            type="textarea"
            :rows="2"
            placeholder="描述治疗效果"
          />
        </el-form-item>

        <el-form-item label="数据来源" prop="dataSource">
          <el-input v-model="form.dataSource" placeholder="如：农业部门、调查报告等" />
        </el-form-item>

        <el-form-item label="案例图片" prop="images">
          <div class="images-upload-container">
            <el-upload
              v-model:file-list="imageList"
              :http-request="customUploadRequest"
              :on-change="handleFileChange"
              :on-remove="handleRemoveImage"
              :before-upload="(file) => {
                const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(file.name)
                if (!isImage) {
                  ElMessage.error('只能上传图片文件！')
                  return false
                }
                const isLt10M = file.size / 1024 / 1024 < 10
                if (!isLt10M) {
                  ElMessage.error('图片大小不能超过 10MB！')
                  return false
                }
                return true
              }"
              list-type="picture-card"
              :limit="9"
              multiple
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <div class="upload-tip">
              最多上传9张图片，支持 jpg/png/gif/bmp/webp 格式，单个文件不超过 10MB
            </div>
            <el-progress v-if="uploadingImages" :percentage="100" :indeterminate="true" />
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="案例详情"
      width="750px"
    >
      <div v-if="currentCase" class="case-detail">
        <el-descriptions
          :column="2"
          border
          :label-style="detailLabelStyle"
          :content-style="detailContentStyle"
        >
          <el-descriptions-item label="案例标题" :span="2">
            <span class="detail-value">{{ currentCase.caseTitle }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="关联病害" :span="2">
            <el-tag type="primary">
              {{ currentCase.diseaseCode }} - {{ currentCase.diseaseName }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发生时间">
            <span class="detail-value">{{ formatDate(currentCase.caseDate) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="发生地点">
            <span class="detail-value">{{ currentCase.location || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="植物种类">
            <el-tag>{{ currentCase.plantType || '-' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="getSeverityTag(currentCase.severityLevel)">
              {{ currentCase.severityLevel || '-' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="感染面积">
            <span class="detail-value">
              {{ currentCase.infectionArea !== null ? `${currentCase.infectionArea}亩` : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="经济损失">
            <span class="detail-value">
              {{ currentCase.economicLoss ? `${currentCase.economicLoss}万元` : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="案例描述" :span="2">
            <div class="detail-text">{{ currentCase.description || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="治疗方法" :span="2">
            <div class="detail-text">{{ currentCase.treatmentMethod || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="治疗效果" :span="2">
            <div class="detail-text">{{ currentCase.treatmentResult || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="数据来源" :span="2">
            <span class="detail-value">{{ currentCase.dataSource || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="案例图片" :span="2">
            <div
              v-if="currentCase.images && currentCase.images.length > 0"
              class="detail-images"
            >
              <el-image
                v-for="(img, index) in currentCase.images"
                :key="index"
                :src="resolveCaseImageUrl(img)"
                fit="cover"
                style="width: 150px; height: 150px; border-radius: 8px; margin-right: 12px; margin-bottom: 12px;"
                :preview-src-list="currentCase.images.map((i: any) => resolveCaseImageUrl(i)).filter(Boolean)"
                :initial-index="index"
                preview-teleported
              />
            </div>
            <span v-else class="detail-value">-</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, type CSSProperties } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadProps, type UploadFile, type UploadUserFile } from 'element-plus'
import {
  Document, Plus, Search, View, Edit, Delete, Upload, Picture, Delete as DeleteIcon
} from '@element-plus/icons-vue'
import { diseaseCaseApi, type CaseImage } from '@/api/disease_case'
import { plantDiseaseApi } from '@/api/plant_disease'
import { fileRequest } from '@/api/file_request'

// 列表相关
const loading = ref(false)
const caseList = ref<any[]>([])
const searchKeyword = ref('')
const filterDiseaseId = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 病害选项
const diseaseOptions = ref<any[]>([])

// 对话框相关
const showDialog = ref(false)
const showDetailDialog = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const currentCase = ref<any>(null)
const submitting = ref(false)
const detailLabelStyle: CSSProperties = {
  minWidth: '100px',
  whiteSpace: 'nowrap',
  paddingRight: '12px',
  fontWeight: '500',
  color: '#606266'
}
const detailContentStyle: CSSProperties = {
  wordBreak: 'break-word',
  paddingLeft: '12px'
}

type RawCaseImage = Partial<CaseImage> & {
  object_key?: string
  objectKey?: string
  objectkey?: string
  name?: string
  url?: string
}

const extractObjectKey = (img: RawCaseImage | null | undefined): string => {
  if (!img) return ''
  return (
    img.objectKey ||
    img.object_key ||
    img.objectkey ||
    img.name ||
    ''
  )
}

const resolveCaseImageUrl = (img: RawCaseImage | null | undefined): string => {
  if (!img) return ''
  if (img.url) return img.url
  const bucket = img.bucket
  const key = extractObjectKey(img)
  if (bucket && key) {
    return fileRequest.getFileUrl(bucket, key)
  }
  return ''
}

const normalizeCaseImages = (images?: RawCaseImage[]): CaseImage[] => {
  if (!images || !Array.isArray(images)) return []
  return images.map((img) => {
    const objectKey = extractObjectKey(img)
    const normalized = {
      ...(img as Record<string, any>),
      bucket: img.bucket || '',
      objectKey,
      object_key: objectKey
    }

    return {
      ...normalized,
      url: resolveCaseImageUrl(normalized)
    } as CaseImage & Record<string, any>
  })
}

// 表单相关
const formRef = ref<FormInstance>()
const form = ref({
  id: undefined as number | undefined,
  diseaseId: undefined as number | undefined,
  caseTitle: '',
  caseDate: undefined as string | undefined,
  location: undefined as string | undefined,
  plantType: undefined as string | undefined,
  severityLevel: undefined as string | undefined,
  infectionArea: undefined as number | undefined,
  description: undefined as string | undefined,
  economicLoss: undefined as number | undefined,
  treatmentMethod: undefined as string | undefined,
  treatmentResult: undefined as string | undefined,
  dataSource: undefined as string | undefined,
  images: [] as CaseImage[]
})

// 图片上传相关
const uploadingImages = ref(false)
const imageList = ref<UploadUserFile[]>([])
const caseImages = ref<CaseImage[]>([])
const processedFileUids = new Set<string | number>() // 记录已处理的文件UID

const formRules: FormRules = {
  diseaseId: [
    { required: true, message: '请选择关联的病害', trigger: 'change' }
  ],
  caseTitle: [
    { required: true, message: '请输入案例标题', trigger: 'blur' }
  ]
}

// 图片上传处理
const handleImagesUpload = async (files: File[]) => {
  if (files.length === 0) return

  uploadingImages.value = true
  try {
    const result = await diseaseCaseApi.uploadImages(files)

    // 先清除临时添加的文件项（status为'ready'的），并从Set中移除它们的UID
    imageList.value.forEach(item => {
      if (item.status === 'ready' && item.uid) {
        processedFileUids.delete(item.uid)
      }
    })
    imageList.value = imageList.value.filter(item => item.status !== 'ready')

    const normalized = normalizeCaseImages(result.images as RawCaseImage[])

    normalized.forEach((img) => {
      const newUid = Date.now() + Math.random()
      caseImages.value.push(img)
      imageList.value.push({
        name: extractObjectKey(img),
        url: img.url,
        uid: newUid,
        status: 'success'
      })
      processedFileUids.add(newUid)
    })

    form.value.images = [...caseImages.value]
    ElMessage.success(`成功上传 ${files.length} 张图片`)
  } catch (error: any) {
    // 上传失败时也要清除临时文件项，并从Set中移除它们的UID
    imageList.value.forEach(item => {
      if (item.status === 'ready' && item.uid) {
        processedFileUids.delete(item.uid)
      }
    })
    imageList.value = imageList.value.filter(item => item.status !== 'ready')
    ElMessage.error(error.message || '图片上传失败')
  } finally {
    uploadingImages.value = false
  }
}

// 删除图片
const handleRemoveImage = (file: UploadFile) => {
  const imageIndex = imageList.value.findIndex(item => item.uid === file.uid)
  if (imageIndex === -1) return

  imageList.value.splice(imageIndex, 1)
  caseImages.value.splice(imageIndex, 1)
  form.value.images = [...caseImages.value]

  if (file.uid) {
    processedFileUids.delete(file.uid)
  }
}

// 自定义上传请求
const customUploadRequest: UploadProps['httpRequest'] = (options) => {
  // 不立即上传，而是收集文件
  return {} as any
}

// 处理文件改变（批量上传）
const handleFileChange: UploadProps['onChange'] = async (file, fileList) => {
  // 过滤出新添加且未处理的文件
  const newFiles: File[] = []
  fileList.forEach(item => {
    if (item.raw && item.status === 'ready' && item.uid && !processedFileUids.has(item.uid)) {
      newFiles.push(item.raw)
      processedFileUids.add(item.uid) // 标记为已处理
    }
  })

  if (newFiles.length > 0) {
    await handleImagesUpload(newFiles)
  }
}

// 加载病害选项
const loadDiseaseOptions = async () => {
  try {
    const res = await plantDiseaseApi.getOptions()
    diseaseOptions.value = res
  } catch (error: any) {
    console.error('获取病害选项失败:', error)
  }
}

// 加载案例列表
const loadCaseList = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchKeyword.value
    }

    if (filterDiseaseId.value) {
      params.disease_id = filterDiseaseId.value
    }

    const res = await diseaseCaseApi.getList(params)
    caseList.value = res.list
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取案例列表失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '添加病害案例'
  form.value = {
    id: undefined,
    diseaseId: undefined,
    caseTitle: '',
    caseDate: undefined,
    location: undefined,
    plantType: undefined,
    severityLevel: undefined,
    infectionArea: undefined,
    description: undefined,
    economicLoss: undefined,
    treatmentMethod: undefined,
    treatmentResult: undefined,
    dataSource: undefined,
    images: []
  }
  imageList.value = []
  caseImages.value = []
  processedFileUids.clear() // 清空已处理文件记录
  showDialog.value = true
}

// 查看案例
const viewCase = async (row: any) => {
  try {
    const res = await diseaseCaseApi.getDetail(row.id)
    const normalizedImages = normalizeCaseImages(res.images as RawCaseImage[])
    const normalizedImageUrls = normalizeCaseImages(res.imageUrls as RawCaseImage[])

    currentCase.value = {
      ...res,
      images: normalizedImages.length > 0 ? normalizedImages : normalizedImageUrls,
      imageUrls: normalizedImageUrls
    }
    showDetailDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取案例详情失败')
  }
}

// 编辑案例
const editCase = async (row: any) => {
  try {
    const res = await diseaseCaseApi.getDetail(row.id)
    isEdit.value = true
    dialogTitle.value = '编辑病害案例'
    const normalizedImages = normalizeCaseImages(res.images as RawCaseImage[])
    const normalizedImageUrls = normalizeCaseImages(res.imageUrls as RawCaseImage[])
    const baseImages = normalizedImages.length > 0 ? normalizedImages : normalizedImageUrls

    form.value = {
      id: res.id,
      diseaseId: res.diseaseId,
      caseTitle: res.caseTitle,
      caseDate: res.caseDate,
      location: res.location,
      plantType: res.plantType,
      severityLevel: res.severityLevel,
      infectionArea: res.infectionArea,
      description: res.description,
      economicLoss: res.economicLoss,
      treatmentMethod: res.treatmentMethod,
      treatmentResult: res.treatmentResult,
      dataSource: res.dataSource,
      images: baseImages
    }

    // 加载已有图片 - 确保 caseImages 和 imageList 从同一数据源构建
    processedFileUids.clear() // 清空已处理文件记录
    caseImages.value = baseImages.map(img => ({ ...img }))
    form.value.images = [...caseImages.value]

    imageList.value = baseImages.map((img, index) => {
      const uid = Date.now() + index
      processedFileUids.add(uid)
      return {
        name: extractObjectKey(img),
        url: img.url,
        uid,
        status: 'success'
      }
    })

    showDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取案例详情失败')
  }
}

// 删除案例
const deleteCase = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除案例"${row.caseTitle}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await diseaseCaseApi.delete(row.id)
      ElMessage.success('删除成功')
      loadCaseList()
    } catch (error: any) {
      ElMessage.error(error.message || '删除失败')
    }
  }).catch(() => {})
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        await diseaseCaseApi.update(form.value.id!, form.value)
        ElMessage.success('更新成功')
      } else {
        await diseaseCaseApi.create(form.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
      loadCaseList()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 分页处理
const handleSizeChange = () => {
  currentPage.value = 1
  loadCaseList()
}

const handleCurrentChange = () => {
  loadCaseList()
}

const getSeverityTag = (level: string) => {
  const map: any = {
    '轻度': 'success',
    '中度': 'warning',
    '重度': 'danger',
    '严重': 'danger'
  }
  return map[level] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 初始化
onMounted(() => {
  loadDiseaseOptions()
  loadCaseList()
})
</script>

<style scoped>
.disease-case-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.title-icon {
  margin-right: 12px;
  font-size: 28px;
  color: #e6a23c;
}

.page-subtitle {
  color: #64748b;
  font-size: 14px;
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.right-actions {
  display: flex;
  align-items: center;
}

.case-list {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.case-detail {
  padding: 10px 0;
}

/* 强制设置描述列表标签宽度 */
.case-detail :deep(.el-descriptions__label) {
  min-width: 100px !important;
  width: 100px !important;
  max-width: 100px !important;
}

.detail-value {
  color: #303133;
  font-weight: 400;
}

.detail-text {
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 图片上传相关样式 */
.images-upload-container {
  width: 100%;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  line-height: 1.5;
}

.detail-images {
  display: flex;
  flex-wrap: wrap;
  padding: 8px 0;
  align-content: flex-start;
  max-height: 320px;
  overflow-y: auto;
}

:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
}

</style>
