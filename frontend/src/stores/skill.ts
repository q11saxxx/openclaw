import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listSkills } from '../api/skill'

export const useSkillStore = defineStore('skill', () => {
    const skills = ref<any[]>([])
    const total = ref(0)
    const loading = ref(false)

    async function fetchSkills(params: any = {}) {
        loading.value = true
        try {
            const res = await listSkills(params)
            if (res && res.items) {
                skills.value = res.items
                total.value = res.total || res.items.length
            } else {
                skills.value = Array.isArray(res) ? res : []
                total.value = skills.value.length
            }
        } finally {
            loading.value = false
        }
    }

    return { skills, total, loading, fetchSkills }
})
