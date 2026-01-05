<!-- MD5: auto-generated -->
<!--
版权声明 2025｜羊羊小栈 (GJQ)
识别码：KGZ-B9E773 · Author＝Y_Y·小栈 · Date：2025-10-28
原创作品——严禁二销；配套视频/文档亦不得二次发布。
违者须立即停止侵权，并按《羊羊小栈系统版权声明及保护条款》承担赔偿。
-->

<template>
  <div class="plant-disease-management">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon class="title-icon"><Grape /></el-icon>
        植物病害管理
      </h1>
      <p class="page-subtitle">
        管理植物病害的基本信息，包括病原体类型、症状、防治方法等档案数据
      </p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon>
          添加病害
        </el-button>
      </div>
      <div class="right-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索病害名称或编号"
          style="width: 300px"
          clearable
          @keyup.enter="loadDiseaseList"
        >
          <template #append>
            <el-button @click="loadDiseaseList">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 病害列表 -->
    <div class="disease-list">
      <el-table
        v-loading="loading"
        :data="diseaseList"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="diseaseCode" label="病害编号" width="150" />

        <el-table-column prop="diseaseName" label="病害名称" width="150">
          <template #default="{ row }">
            <strong>{{ row.diseaseName }}</strong>
          </template>
        </el-table-column>

        <el-table-column prop="diseaseNameEn" label="英文名称" width="180" />

        <el-table-column prop="pathogenType" label="病原体类型" width="120">
          <template #default="{ row }">
            <el-tag type="primary" size="small">
              {{ row.pathogenType || '-' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="severityLevel" label="严重程度" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severityLevel)">
              {{ row.severityLevel || '-' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="occurrenceSeason" label="发生季节" width="120">
          <template #default="{ row }">
            {{ row.occurrenceSeason || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="economicLoss" label="经济损失" width="140">
          <template #default="{ row }">
            {{ row.economicLoss ? `${row.economicLoss}万元` : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createTime) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDisease(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button size="small" type="primary" @click="editDisease(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteDisease(row)">
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="病害编号" prop="diseaseCode">
              <el-input v-model="form.diseaseCode" placeholder="如：PD2024001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="病害名称" prop="diseaseName">
              <el-input v-model="form.diseaseName" placeholder="如：稻瘟病" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="英文名称" prop="diseaseNameEn">
              <el-input v-model="form.diseaseNameEn" placeholder="如：Rice Blast" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="病原体类型" prop="pathogenType">
              <el-select v-model="form.pathogenType" placeholder="请选择" style="width: 100%">
                <el-option label="真菌" value="真菌" />
                <el-option label="细菌" value="细菌" />
                <el-option label="病毒" value="病毒" />
                <el-option label="类菌原体" value="类菌原体" />
                <el-option label="线虫" value="线虫" />
                <el-option label="卵菌" value="卵菌" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
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
          <el-col :span="12">
            <el-form-item label="发生季节" prop="occurrenceSeason">
              <el-input v-model="form.occurrenceSeason" placeholder="如：春季、夏季" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="受害植物" prop="affectedPlants">
          <el-select
            v-model="form.affectedPlants"
            multiple
            filterable
            allow-create
            default-first-option
            :reserve-keyword="false"
            placeholder="输入植物名称后回车添加"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="分布区域" prop="distributionArea">
          <el-select
            v-model="form.distributionArea"
            multiple
            filterable
            allow-create
            default-first-option
            :reserve-keyword="false"
            placeholder="输入地区名称后回车添加"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="症状描述" prop="symptoms">
          <el-input
            v-model="form.symptoms"
            type="textarea"
            :rows="3"
            placeholder="描述病害的主要症状特征"
          />
        </el-form-item>

        <el-form-item label="防治方法" prop="preventionMethods">
          <el-input
            v-model="form.preventionMethods"
            type="textarea"
            :rows="3"
            placeholder="描述预防和治疗方法"
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

        <el-form-item label="病害图片" prop="image">
          <div class="image-upload-container">
            <el-upload
              v-if="!imageUrl"
              class="image-uploader"
              :auto-upload="true"
              :show-file-list="false"
              :http-request="handleImageUpload"
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
            >
              <div class="upload-area">
                <el-icon class="upload-icon"><Upload /></el-icon>
                <div class="upload-text">点击上传图片</div>
                <div class="upload-tip">支持 jpg/png/gif/bmp/webp 格式，文件大小不超过 10MB</div>
              </div>
            </el-upload>
            <div v-else class="image-preview">
              <div class="image-wrapper">
                <el-image
                  :src="imageUrl"
                  fit="cover"
                  style="width: 200px; height: 200px; border-radius: 8px;"
                  :preview-src-list="[imageUrl]"
                  preview-teleported
                />
              </div>
              <el-button
                type="danger"
                size="small"
                :icon="DeleteIcon"
                class="delete-image-btn"
                @click="handleRemoveImage"
              >
                删除图片
              </el-button>
            </div>
            <el-progress v-if="uploadingImage" :percentage="100" :indeterminate="true" />
          </div>
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述病害相关信息"
          />
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
      title="病害详情"
      width="750px"
    >
      <div v-if="currentDisease" class="disease-detail">
        <el-descriptions
          :column="2"
          border
          :label-style="detailLabelStyle"
          :content-style="detailContentStyle"
        >
          <el-descriptions-item label="病害编号">
            <span class="detail-value">{{ currentDisease.diseaseCode }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="病害名称">
            <span class="detail-value">{{ currentDisease.diseaseName }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="英文名称">
            <span class="detail-value">{{ currentDisease.diseaseNameEn || '-' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="病原体类型">
            <el-tag type="primary" size="small">
              {{ currentDisease.pathogenType || '-' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="严重程度">
            <el-tag :type="getSeverityTag(currentDisease.severityLevel)">
              {{ currentDisease.severityLevel || '-' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发生季节">
            <span class="detail-value">
              {{ currentDisease.occurrenceSeason || '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="经济损失">
            <span class="detail-value">
              {{ currentDisease.economicLoss ? `${currentDisease.economicLoss}万元` : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            <span class="detail-value">
              {{ currentDisease.createTime ? formatDate(currentDisease.createTime) : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="受害植物" :span="2">
            <div class="detail-tags">
              <el-tag
                v-for="(plant, index) in (currentDisease.affectedPlants || [])"
                :key="index"
                class="tag-item"
              >
                {{ plant }}
              </el-tag>
              <span v-if="!(currentDisease.affectedPlants && currentDisease.affectedPlants.length)" class="detail-value">-</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="分布区域" :span="2">
            <div class="detail-tags">
              <el-tag
                v-for="(area, index) in (currentDisease.distributionArea || [])"
                :key="index"
                class="tag-item"
                type="info"
              >
                {{ area }}
              </el-tag>
              <span v-if="!(currentDisease.distributionArea && currentDisease.distributionArea.length)" class="detail-value">-</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="症状描述" :span="2">
            <div class="detail-text">{{ currentDisease.symptoms || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="防治方法" :span="2">
            <div class="detail-text">{{ currentDisease.preventionMethods || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="详细描述" :span="2">
            <div class="detail-text">{{ currentDisease.description || '-' }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="病害图片" :span="2">
            <div v-if="currentDisease.imageBucket && currentDisease.imageObjectKey" class="detail-image">
              <el-image
                :src="getImageUrl(currentDisease.imageBucket, currentDisease.imageObjectKey)"
                fit="cover"
                style="width: 300px; height: 300px; border-radius: 8px;"
                :preview-src-list="[getImageUrl(currentDisease.imageBucket, currentDisease.imageObjectKey)]"
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
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadProps, type UploadFile } from 'element-plus'
import {
  Grape, Plus, Search, View, Edit, Delete, Upload, Picture, Delete as DeleteIcon
} from '@element-plus/icons-vue'
import { plantDiseaseApi } from '@/api/plant_disease'
import { fileRequest } from '@/api/file_request'

// 列表相关
const loading = ref(false)
const diseaseList = ref<any[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 对话框相关
const showDialog = ref(false)
const showDetailDialog = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const currentDisease = ref<any>(null)
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

// 表单相关
const formRef = ref<FormInstance>()
// Copyright anchor · 羊羊小栈原创模块 (请勿删除) 🔐
const form = ref({
  id: undefined as number | undefined,
  diseaseCode: '',
  diseaseName: '',
  diseaseNameEn: undefined as string | undefined,
  pathogenType: undefined as string | undefined,
  severityLevel: undefined as string | undefined,
  affectedPlants: [] as string[],
  distributionArea: [] as string[],
  occurrenceSeason: undefined as string | undefined,
  symptoms: undefined as string | undefined,
  preventionMethods: undefined as string | undefined,
  economicLoss: undefined as number | undefined,
  description: undefined as string | undefined,
  imageBucket: undefined as string | undefined,
  imageObjectKey: undefined as string | undefined
})

// 图片上传相关
const uploadingImage = ref(false)
const imageUrl = ref<string | undefined>(undefined)

const formRules: FormRules = {
  diseaseCode: [
    { required: true, message: '请输入病害编号', trigger: 'blur' }
  ],
  diseaseName: [
    { required: true, message: '请输入病害名称', trigger: 'blur' }
  ]
}

// 內嵌提示：y.a.n.g x.i.a.o z.h.a.n版權所有，請勿於未授權情況下重發。

// 图片上传处理
const handleImageUpload: UploadProps['httpRequest'] = async (options) => {
  const { file, onSuccess, onError } = options
  uploadingImage.value = true

  try {
    const result = await plantDiseaseApi.uploadImage(file as File)
    form.value.imageBucket = result.bucket
    form.value.imageObjectKey = result.objectKey
    imageUrl.value = getImageUrl(result.bucket, result.objectKey)
    ElMessage.success('图片上传成功')
    onSuccess?.(result as any)
  } catch (error: any) {
    ElMessage.error(error.message || '图片上传失败')
    onError?.(error as any)
  } finally {
    uploadingImage.value = false
  }
}

// 删除图片
const handleRemoveImage = () => {
  form.value.imageBucket = undefined
  form.value.imageObjectKey = undefined
  imageUrl.value = undefined
}

// 加载病害列表
const loadDiseaseList = async () => {
  loading.value = true
  try {
    const res = await plantDiseaseApi.getList({
      page: currentPage.value,
      size: pageSize.value,
      keyword: searchKeyword.value
    })

    diseaseList.value = res.list
    total.value = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取病害列表失败')
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  dialogTitle.value = '添加病害'
  form.value = {
    id: undefined,
    diseaseCode: '',
    diseaseName: '',
    diseaseNameEn: undefined,
    pathogenType: undefined,
    severityLevel: undefined,
    affectedPlants: [],
    distributionArea: [],
    occurrenceSeason: undefined,
    symptoms: undefined,
    preventionMethods: undefined,
    economicLoss: undefined,
    description: undefined,
    imageBucket: undefined,
    imageObjectKey: undefined
  }
  imageUrl.value = undefined
  showDialog.value = true
}

// 查看病害
const viewDisease = async (row: any) => {
  try {
    const res = await plantDiseaseApi.getDetail(row.id)
    currentDisease.value = res
    showDetailDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取病害详情失败')
  }
}

// 编辑病害
const editDisease = async (row: any) => {
  try {
    const res = await plantDiseaseApi.getDetail(row.id)
    isEdit.value = true
    dialogTitle.value = '编辑病害'
    form.value = {
      id: res.id,
      diseaseCode: res.diseaseCode,
      diseaseName: res.diseaseName,
      diseaseNameEn: res.diseaseNameEn,
      pathogenType: res.pathogenType,
      severityLevel: res.severityLevel,
      affectedPlants: res.affectedPlants || [],
      distributionArea: res.distributionArea || [],
      occurrenceSeason: res.occurrenceSeason,
      symptoms: res.symptoms,
      preventionMethods: res.preventionMethods,
      economicLoss: res.economicLoss,
      description: res.description,
      imageBucket: res.imageBucket,
      imageObjectKey: res.imageObjectKey
    }
    imageUrl.value = getImageUrl(res.imageBucket, res.imageObjectKey)
    showDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取病害详情失败')
  }
}

// 删除病害
const deleteDisease = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除病害"${row.diseaseName}"吗？删除后关联的病害案例也会被删除！`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await plantDiseaseApi.delete(row.id)
      ElMessage.success('删除成功')
      loadDiseaseList()
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
        await plantDiseaseApi.update(form.value.id!, form.value)
        ElMessage.success('更新成功')
      } else {
        await plantDiseaseApi.create(form.value)
        ElMessage.success('创建成功')
      }
      showDialog.value = false
      loadDiseaseList()
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
  loadDiseaseList()
}

const handleCurrentChange = () => {
  loadDiseaseList()
}

// 工具函数
const getImageUrl = (imageBucket?: string, imageObjectKey?: string) => {
  if (!imageBucket || !imageObjectKey) return ''
  return fileRequest.getFileUrl(imageBucket, imageObjectKey)
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
  loadDiseaseList()
})
</script>

<style scoped>
.plant-disease-management {
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
  color: #67c23a;
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

.disease-list {
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

.disease-detail {
  padding: 10px 0;
}

/* 强制设置描述列表标签宽度 */
.disease-detail :deep(.el-descriptions__label) {
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

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tag-item {
  margin: 0;
}

/* 图片上传相关样式 */
.image-upload-container {
  width: 100%;
}

.image-uploader {
  width: 100%;
}

.image-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 100%;
}

.image-uploader :deep(.el-upload:hover) {
  border-color: var(--primary-color);
}

.upload-area {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 16px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.image-preview {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.image-wrapper {
  display: inline-block;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 4px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.image-wrapper:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.delete-image-btn {
  flex-shrink: 0;
}

.detail-image {
  padding: 8px 0;
}

</style>
