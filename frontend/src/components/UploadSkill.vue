<template>
  <div>
    <el-button type="primary" @click="dialogVisible = true">
      <el-icon><Upload /></el-icon>
      上传技能包
    </el-button>
    
    <el-dialog 
      v-model="dialogVisible" 
      title="上传技能包" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form label-position="top">
        <el-form-item label="选择技能包文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".zip,.tar.gz,.tgz,.json"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 .zip, .tar.gz, .json 格式，文件大小不超过 50MB
              </div>
            </template>
          </el-upload>
          
          <div v-if="selectedFile" style="margin-top:12px;padding:12px;background:#f5f7fa;border-radius:6px">
            <div style="display:flex;align-items:center;gap:8px">
              <el-icon :size="20"><Document /></el-icon>
              <div style="flex:1">
                <div style="font-weight:500">{{ selectedFile.name }}</div>
                <div style="font-size:12px;color:#909399">
                  {{ formatFileSize(selectedFile.size) }}
                </div>
              </div>
              <el-button link type="danger" @click="clearFile">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="运行审计（可选）">
          <el-switch 
            v-model="runAudit" 
            active-text="上传后立即执行审计" 
            inactive-text="仅上传" 
          />
        </el-form-item>
        
        <el-alert
          v-if="runAudit"
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom:16px"
        >
          <p style="margin:0;font-size:13px">
            审计将在后台异步执行，您可以在"审计任务"页面查看进度。
          </p>
        </el-alert>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="uploading" 
          :disabled="!selectedFile" 
          @click="handleUpload"
        >
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, UploadFilled, Document, Close } from '@element-plus/icons-vue'
import { uploadSkill } from '../api/skill'

const emit = defineEmits(['uploaded'])

const dialogVisible = ref(false)
const selectedFile = ref<File | null>(null)
const runAudit = ref(false)
const uploading = ref(false)
const uploadRef = ref()

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

const clearFile = () => {
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  
  // 验证文件大小（限制为50MB）
  const maxSize = 50 * 1024 * 1024
  if (selectedFile.value.size > maxSize) {
    ElMessage.error(`文件大小不能超过 50MB，当前文件：${formatFileSize(selectedFile.value.size)}`)
    return
  }
  
  uploading.value = true
  try {
    const res = await uploadSkill(selectedFile.value, runAudit.value)
    ElMessage.success({
      message: '上传成功' + (runAudit.value ? '，正在后台执行审计...' : ''),
      duration: 3000
    })
    emit('uploaded', res)
    
    // 关闭对话框并重置
    dialogVisible.value = false
    clearFile()
    runAudit.value = false
  } catch (err: any) {
    const errorMsg = err?.response?.data?.detail || err?.message || '上传失败，请重试'
    ElMessage.error(errorMsg)
    console.error('Upload error:', err)
  } finally {
    uploading.value = false
  }
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}
</script>

<style scoped>
.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}
</style>
