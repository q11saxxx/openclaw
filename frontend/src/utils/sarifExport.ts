/**
 * 将 OpenClaw 报告导出为 SARIF 2.1.0（便于接入 GitHub Code Scanning、Azure Defender 等工具链）
 */

import { getRiskLevelFinding } from './reportMultiDimScore'

function sarifLevel(level: string): 'error' | 'warning' | 'note' | 'none' {
  if (level === 'critical' || level === 'high') return 'error'
  if (level === 'medium') return 'warning'
  return 'note'
}

function physicalLocation(f: any): { artifactLocation: { uri: string }; region?: { startLine: number } } | null {
  const ev = f.evidence
  if (ev && typeof ev === 'object' && !Array.isArray(ev)) {
    const uri = ev.file_path || ev.file || ev.path
    if (typeof uri === 'string' && uri.length > 0) {
      const line = ev.line_number ?? ev.line
      const base = { artifactLocation: { uri: uri.replace(/\\/g, '/') } }
      if (typeof line === 'number' && line > 0) {
        return { ...base, region: { startLine: line } }
      }
      return base
    }
  }
  if (typeof f.file_path === 'string' && f.file_path.length > 0) {
    const base = { artifactLocation: { uri: f.file_path.replace(/\\/g, '/') } }
    if (typeof f.line_number === 'number' && f.line_number > 0) {
      return { ...base, region: { startLine: f.line_number } }
    }
    return base
  }
  return null
}

export function buildSarifReport(report: any, reportId: string) {
  const findings = (report?.findings || []) as any[]
  const meta = report?.metadata || {}

  const ruleIdSet = new Set<string>()
  findings.forEach((f) => {
    ruleIdSet.add(String(f.type || f.rule_id || 'openclaw/unknown'))
  })

  const rules = [...ruleIdSet].map((id) => ({
    id,
    name: id,
    shortDescription: { text: id },
    helpUri: 'https://cwe.mitre.org/'
  }))

  const results = findings.map((f, index) => {
    const ruleId = String(f.type || f.rule_id || 'openclaw/unknown')
    const text = (f.reason || f.title || f.description || 'OpenClaw 安全审计发现项') as string
    const level = sarifLevel(getRiskLevelFinding(f))
    const phys = physicalLocation(f)
    const o: Record<string, unknown> = {
      ruleId,
      message: { text },
      level,
      properties: {
        openclawReportId: reportId,
        openclawIndex: index,
        agent: f.agent || null
      }
    }
    if (phys) {
      o.locations = [{ physicalLocation: phys }]
    }
    return o
  })

  return {
    $schema: 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json',
    version: '2.1.0',
    runs: [
      {
        tool: {
          driver: {
            name: 'OpenClaw',
            fullName: 'OpenClaw 技能包风险审计',
            version: '1.0.0',
            informationUri: 'https://github.com/',
            rules
          }
        },
        invocations: [{ executionSuccessful: true }],
        results,
        properties: {
          reportId,
          skillName: meta.skill_name || null,
          scanTime: meta.scan_time || null
        }
      }
    ]
  }
}

export function downloadSarifJson(report: any, reportId: string) {
  const doc = buildSarifReport(report, reportId)
  const blob = new Blob([JSON.stringify(doc, null, 2)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `openclaw_${reportId}.sarif.json`
  a.click()
  URL.revokeObjectURL(url)
}
