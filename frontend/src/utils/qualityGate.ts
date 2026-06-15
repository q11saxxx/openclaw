/**
 * 类 Sonar / CI 质量门禁：基于严重度与综合分给出通过/警告/阻断（默认策略可后续接配置）
 */

export type GateLevel = 'pass' | 'warn' | 'fail'

export type QualityGateResult = {
  level: GateLevel
  passed: boolean
  reasons: string[]
}

export function computeQualityGate(input: {
  safetyScore: number
  criticalCount: number
  highCount: number
}): QualityGateResult {
  const reasons: string[] = []

  if (input.criticalCount > 0) {
    reasons.push(`存在 ${input.criticalCount} 条严重（critical）发现 — 默认阻断发布。`)
    return { level: 'fail', passed: false, reasons }
  }

  if (input.safetyScore < 45) {
    reasons.push(`综合安全分为 ${input.safetyScore}，低于默认阈值 45 — 建议阻断直至修复或正式豁免。`)
    return { level: 'fail', passed: false, reasons }
  }

  let level: GateLevel = 'pass'

  if (input.highCount > 0) {
    reasons.push(`存在 ${input.highCount} 条高危发现 — 建议在合并/发布前完成修复或评审签字。`)
    level = 'warn'
  }

  if (input.safetyScore < 65) {
    reasons.push(`综合安全分为 ${input.safetyScore}，低于建议阈值 65 — 请安排安全评审。`)
    if (level === 'pass') level = 'warn'
  }

  if (reasons.length === 0) {
    reasons.push('未触发默认阻断条件；仍请结合业务与组织策略做最终放行。')
  }

  return { level, passed: level !== 'fail', reasons }
}

export function buildGateJsonPayload(input: {
  reportId: string
  safetyScore: number
  gate: QualityGateResult
  skillName?: string
}) {
  return {
    schema: 'openclaw-quality-gate/v1',
    report_id: input.reportId,
    skill_name: input.skillName ?? null,
    safety_score: input.safetyScore,
    gate_passed: input.gate.passed,
    gate_level: input.gate.level,
    reasons: input.gate.reasons,
    generated_at: new Date().toISOString()
  }
}
