<template>
  <div>
    <div style="display:flex;justify-content:space-between;margin-bottom:12px;">
      <el-input 
        v-model="q" 
        placeholder="按名称/路径搜索" 
        style="width:320px"
        @keyup.enter="refresh"
        clearable
      >
        <template #append>
          <el-button @click="refresh">搜索</el-button>
        </template>
      </el-input>
      <upload-skill @uploaded="refresh" />
    </div>

    <el-table :data="skills" style="width:100%" v-loading="store.loading">
      <el-table-column prop="name" label="Skill 名称" />
      <el-table-column prop="version" label="版本" />
      <el-table-column prop="author" label="开发者" />
      <el-table-column prop="last_audit" label="最后审计时间" />
      <el-table-column label="风险等级">
        <template #default="{ row }">
          <risk-badge :level="row.risk_level" />
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="goDetail(row.id)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top:12px;text-align:right">
      <el-pagination 
        :total="total" 
        :page-size="pageSize" 
        v-model:current-page="page" 
        @current-change="onPageChange" 
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useSkillStore } from '../../stores/skill'
import UploadSkill from '../../components/UploadSkill.vue'
import RiskBadge from '../../components/RiskBadge.vue'
import { useRouter } from 'vue-router'

const store = useSkillStore()
const q = ref('')
const page = ref(1)
const pageSize = 10
const router = useRouter()

const skills = computed(() => store.skills)
const total = computed(() => store.total)

let searchTimer: any = null

// 添加搜索防抖
watch(q, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    refresh()
  }, 500)
})

const refresh = async () => {
  await store.fetchSkills({ page: page.value, size: pageSize, q: q.value })
}

const onPageChange = (p:number) => { page.value = p; refresh() }
const goDetail = (id:string) => router.push(`/skills/${id}`)

onMounted(() => { refresh() })
</script>
