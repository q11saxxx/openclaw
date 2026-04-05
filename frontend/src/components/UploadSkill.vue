<template>
  <div>
    <el-form label-position="top">
      <el-form-item label="选择 Skill 文件">
        <input type="file" @change="onFileChange" />
        <div v-if="selectedFile" style="margin-top:8px;font-size:13px;color:#666">
          {{ selectedFile.name }} — {{ (selectedFile.size/1024).toFixed(1) }} KB
        </div>
      </el-form-item>

      <el-form-item label="运行语义审计（可选）">
        <el-switch v-model="runAudit" active-text="是" inactive-text="否" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="uploading" :disabled="!selectedFile" @click="handleUpload">上传 Skill</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadSkill } from '../api/skill'

const emit = defineEmits(['uploaded'])

const selectedFile = ref<File | null>(null)
const runAudit = ref(false)
const uploading = ref(false)

const onFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  selectedFile.value = input.files && input.files.length ? input.files[0] : null
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  
  // 验证文件大小（限制为50MB）
  const maxSize = 50 * 1024 * 1024
  if (selectedFile.value.size > maxSize) {
    ElMessage.error(`文件大小不能超过 50MB，当前文件：${(selectedFile.value.size / 1024 / 1024).toFixed(2)}MB`)
    return
  }
  
  uploading.value = true
  try {
    const res = await uploadSkill(selectedFile.value, runAudit.value)
    ElMessage.success('上传成功' + (runAudit.value ? '，正在后台执行审计...' : ''))
    emit('uploaded', res)
    // reset form
    selectedFile.value = null
    runAudit.value = false
  } catch (err: any) {
    const errorMsg = err?.response?.data?.detail || err?.message || '上传失败，请重试'
    ElMessage.error(errorMsg)
    console.error('Upload error:', err)
  } finally {
    uploading.value = false
  }
}
</script>
