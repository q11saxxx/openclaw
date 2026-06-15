/**
 * 报告多维度安全分模型（与报告详情页一致，供对比、导出等复用）
 */

export const getRiskLevelFinding = (finding: any) => {
  const level = finding.risk_level || finding.level || finding.severity || ''
  return String(level).toLowerCase()
}

export const LEVEL_DEDUCT: Record<string, number> = {
  critical: 30,
  high: 20,
  medium: 10,
  low: 5,
  info: 2
}

export const DIMENSION_SCHEMA = [
  { key: 'static_security', name: '静态安全检测', weight: 0.26 },
  { key: 'semantic_audit', name: '语义审计', weight: 0.22 },
  { key: 'provenance', name: '来源与供应链', weight: 0.22 },
  { key: 'dependency', name: '依赖分析', weight: 0.16 },
  { key: 'parser', name: '结构解析', weight: 0.08 },
  { key: 'other', name: '其他检测', weight: 0.06 }
] as const

export type DimKey = (typeof DIMENSION_SCHEMA)[number]['key']

export type DimensionRow = {
  key: DimKey
  name: string
  weight: number
  weightPercent: number
  score: number
  findingCount: number
  contribution: number
  color: string
  suggestion: string
  statusTag: 'danger' | 'warning' | 'info' | 'success'
  statusLabel: string
}

export const normalizeDimensionKey = (agent: string): DimKey => {
  const a = String(agent || '').toLowerCase()
  if (a === 'static_security' || a.includes('static')) return 'static_security'
  if (a === 'semantic_audit' || a.includes('semantic')) return 'semantic_audit'
  if (a === 'provenance' || a.includes('provenance')) return 'provenance'
  if (a === 'dependency' || a.includes('depend')) return 'dependency'
  if (a === 'parser' || a.includes('parse')) return 'parser'
  return 'other'
}

export function buildDimensionRows(findings: any[]): DimensionRow[] {
  const levelsByDim: Record<DimKey, string[]> = {
    static_security: [],
    semantic_audit: [],
    provenance: [],
    dependency: [],
    parser: [],
    other: []
  }
  for (const f of findings) {
    const k = normalizeDimensionKey(f.agent)
    levelsByDim[k].push(getRiskLevelFinding(f))
  }

  return DIMENSION_SCHEMA.map((meta) => {
    const levels = levelsByDim[meta.key]
    const deduction = levels.reduce((sum, lvl) => sum + (LEVEL_DEDUCT[lvl] || 0), 0)
    const score = Math.max(0, Math.min(100, 100 - deduction))
    const contribution = score * meta.weight
    const findingCount = levels.length
    const color =
      score >= 81 ? '#67c23a' : score >= 61 ? '#409eff' : score >= 41 ? '#e6a23c' : '#f56c6c'

    let suggestion = ''
    let statusTag: DimensionRow['statusTag'] = 'success'
    let statusLabel = ''

    if (findingCount === 0) {
      suggestion =
        '本维度未发现风险项。若本次任务未启用该检测链路，该维度按满分参与加权。'
      statusLabel = '未检出'
    } else if (score >= 81) {
      suggestion =
        '本维度以低危或信息类问题为主，可在常规迭代中消化，发布前抽查确认即可。'
      statusLabel = '良好'
    } else if (score >= 61) {
      suggestion =
        '仍存在一定扣分项，建议在排期内逐项处理中低危发现，避免与后续变更叠加成高危。'
      statusTag = 'info'
      statusLabel = '建议优化'
    } else if (score >= 41) {
      suggestion =
        '中高危问题偏多，上线前建议完成修复或制定可验证的缓解措施，并做好留痕。'
      statusTag = 'warning'
      statusLabel = '需优先处理'
    } else {
      suggestion =
        '该维度风险突出或含严重项，建议视为阻断条件：先收敛问题再复测，勿带病发布。'
      statusTag = 'danger'
      statusLabel = '高风险'
    }

    return {
      key: meta.key,
      name: meta.name,
      weight: meta.weight,
      weightPercent: Math.round(meta.weight * 1000) / 10,
      score,
      findingCount,
      contribution,
      color,
      suggestion,
      statusTag,
      statusLabel
    }
  })
}

export function compositeScoreFromRows(rows: DimensionRow[]): number {
  return Math.round(rows.reduce((sum, row) => sum + row.contribution, 0))
}

export function compositeScoreFromFindings(findings: any[]): number {
  return compositeScoreFromRows(buildDimensionRows(findings || []))
}
