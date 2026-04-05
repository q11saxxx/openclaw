<template>
  <div>
    <h3>审计进度</h3>
    <progress-steps :stage="stage" :logs="logs" />
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import ProgressSteps from '../../components/ProgressSteps.vue'
import { useRoute } from 'vue-router'
import { getAuditStatus } from '../../api/audit'

const route = useRoute()
const id = route.params.id as string
const stage = ref(0)
const logs = ref('')

let timer: any = null

const poll = async () => {
  try {
    const res = await getAuditStatus(id)
    stage.value = res.progress || 0
    logs.value = (res.logs || []).join('\n')
    if (!res.completed) {
      timer = setTimeout(poll, 2000)
    }
  } catch (e) {
    // ignore
  }
}

onMounted(() => { poll() })
</script>
