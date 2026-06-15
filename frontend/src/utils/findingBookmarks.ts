/** 报告内风险项「关注」书签（仅浏览器本地，不上传服务器） */

const LS_KEY = 'openclaw:finding-bookmarks:v1'

type BookmarkStore = Record<string, string[]>

function loadStore(): BookmarkStore {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (!raw) return {}
    const o = JSON.parse(raw)
    return o && typeof o === 'object' ? o : {}
  } catch {
    return {}
  }
}

function saveStore(store: BookmarkStore) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(store))
  } catch {
    /* quota or private mode */
  }
}

/** 稳定键：用于在折叠列表中识别同一条发现（含序号避免完全重复标题冲突） */
export function findingBookmarkKey(f: any, index: number): string {
  const title = (f.title || f.reason || '').slice(0, 240)
  const agent = f.agent || ''
  const cat = f.category || ''
  return `${index}::${agent}::${cat}::${title}`
}

export function listBookmarkKeys(reportId: string): string[] {
  const s = loadStore()
  return [...(s[reportId] || [])]
}

export function isFindingBookmarked(reportId: string, key: string): boolean {
  const arr = loadStore()[reportId]
  return Array.isArray(arr) && arr.includes(key)
}

/** 切换关注状态，返回切换后是否已关注 */
export function toggleFindingBookmark(reportId: string, key: string): boolean {
  const store = loadStore()
  const set = new Set(store[reportId] || [])
  if (set.has(key)) {
    set.delete(key)
  } else {
    set.add(key)
  }
  store[reportId] = [...set]
  saveStore(store)
  return set.has(key)
}
