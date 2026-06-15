/**
 * 发现项处置状态（对标 Sonar/CodeQL 等：确认 / 误报 / 接受风险 / 已修复）
 * 仅存浏览器本地，便于评审流程；若需审计留痕可再接后端。
 */

import { findingBookmarkKey } from './findingBookmarks'

export type TriageStatus = 'open' | 'confirmed' | 'false_positive' | 'accepted_risk' | 'fixed'

export const TRIAGE_LABEL: Record<TriageStatus, string> = {
  open: '待处理',
  confirmed: '已确认',
  false_positive: '误报',
  accepted_risk: '接受风险',
  fixed: '已修复'
}

const LS_KEY = 'openclaw:finding-triage:v1'

type TriageStore = Record<string, Record<string, { status: TriageStatus; note: string }>>

function load(): TriageStore {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (!raw) return {}
    const o = JSON.parse(raw)
    return o && typeof o === 'object' ? o : {}
  } catch {
    return {}
  }
}

function save(store: TriageStore) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(store))
  } catch {
    /* ignore */
  }
}

export function getTriageRecord(reportId: string, findingKey: string): { status: TriageStatus; note: string } {
  const r = load()[reportId]?.[findingKey]
  return r ? { ...r } : { status: 'open', note: '' }
}

export function setTriageRecord(
  reportId: string,
  findingKey: string,
  patch: Partial<{ status: TriageStatus; note: string }>
) {
  const store = load()
  if (!store[reportId]) store[reportId] = {}
  const cur = getTriageRecord(reportId, findingKey)
  store[reportId][findingKey] = {
    status: patch.status ?? cur.status,
    note: patch.note !== undefined ? patch.note : cur.note
  }
  save(store)
}

export function triageKeyForFinding(f: any, index: number): string {
  return findingBookmarkKey(f, index)
}

export function isActiveTriageStatus(status: TriageStatus): boolean {
  return status !== 'false_positive' && status !== 'fixed'
}
