/**
 * 为每条 finding 提供可展示的安全建议：
 * - 优先使用后端下发的 recommendation / remediation 等字段
 * - 否则根据 agent、type、rule_id、文案关键词生成简短可执行的推断建议（前端兜底）
 */

import { normalizeDimensionKey } from './reportMultiDimScore'

export type FindingAdviceSource = 'report' | 'inferred'

export type FindingAdvice = {
  text: string
  source: FindingAdviceSource
}

const pickFirstString = (...vals: unknown[]): string => {
  for (const v of vals) {
    if (typeof v === 'string' && v.trim()) return v.trim()
  }
  return ''
}

/** 后端可能使用的其它建议字段名 */
const reportAdviceFields = (f: Record<string, unknown>): string =>
  pickFirstString(
    f.recommendation,
    f.remediation,
    f.fix_suggestion,
    f.suggestion,
    f.mitigation,
    f.action
  )

const matchesAny = (hay: string, patterns: RegExp[]) => patterns.some((re) => re.test(hay))

export function getFindingSecurityAdvice(f: any): FindingAdvice {
  if (!f || typeof f !== 'object') {
    return { text: '请结合证据与业务上下文人工复核该发现。', source: 'inferred' }
  }

  const fromReport = reportAdviceFields(f as Record<string, unknown>)
  if (fromReport) return { text: fromReport, source: 'report' }

  const agentKey = normalizeDimensionKey(f.agent)
  const blob = `${f.title || ''} ${f.reason || ''} ${f.description || ''} ${f.type || ''} ${f.rule_id || ''}`.toLowerCase()

  // —— 按规则 / 类型关键词 ——
  if (matchesAny(blob, [/prompt/, /inject/, /jailbreak/, /语义/, /instruction/])) {
    return {
      text: '审查相关提示词与系统指令边界：限制模型可执行工具与白名单、对用户可控输入做隔离与过滤；在沙箱中回归测试后再发布。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/curl\s*\|/, /wget.*\|.*sh/, /pip\s+install.*http/, /npm\s+install.*http/])) {
    return {
      text: '避免「下载后立即执行」链路：改为固定版本与哈希校验、使用私有制品库与 lockfile；在隔离环境构建产物后再分发。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/rm\s+-rf/, /chmod\s+777/, /mkfifo/, /\/dev\/tcp/])) {
    return {
      text: '收敛脚本权限与破坏性命令：改为显式路径与白名单参数、在 CI 中拦截高危命令；只在必要时以最小权限运行。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/shadow/, /\.ssh/, /credential/, /secret/, /token/, /api[_-]?key/, /password/])) {
    return {
      text: '清理敏感路径与密钥残留：轮换已暴露凭据、改用密钥管理服务；禁止将密钥写入仓库或 Skill 包，必要时用环境变量注入。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/file:\/\//])) {
    return {
      text: '限制 file:// 与本地路径依赖：改为容器内相对路径或受控存储；审计是否会读取用户磁盘或扩大暴露面。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/url_surface|外链|主机|network|http/])) {
    return {
      text: '梳理出站网络与白名单：记录域名用途、区分必需与可疑请求；对未知域名做拦截或二次审批后再接入生产。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/depend/, /cve/, /vuln/, /package/, /供应链/])) {
    return {
      text: '升级或替换有问题的依赖：锁定版本与 SBOM、启用漏洞扫描门禁；评估供应链来源与发布签名校验。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/license/, /许可证/, /anonymous|匿名/, /author/, /溯源|来源/])) {
    return {
      text: '补齐许可证与发布元数据：确认 SPDX 与版权声明；对匿名或来源不清的包提高审查级别并限制使用范围。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/diff/, /baseline/, /版本/, /变更/])) {
    return {
      text: '对照基线复核变更：重点检查新增脚本、依赖与权限变更；在合并前要求说明与额外评审。',
      source: 'inferred'
    }
  }
  if (matchesAny(blob, [/permission/, /chmod/, /private/, /敏感路径/])) {
    return {
      text: '收紧文件与路径权限：移除全局可读写的敏感文件访问；遵循最小权限并在文档中说明访问意图。',
      source: 'inferred'
    }
  }

  // —— 按 Agent 维度兜底 ——
  const byAgent: Record<string, string> = {
    static_security:
      '针对静态检出项：在隔离环境复现、确认是否为误报；若是真实风险则修改脚本/配置或移除危险模式，并在回归审计中验证。',
    semantic_audit:
      '针对语义风险：收紧 Skill 描述与指令、限制可被用户覆盖的系统提示；建议增加输出过滤与工具调用策略。',
    provenance:
      '针对来源与供应链：核实仓库与发布渠道可信度，启用签名或哈希校验；对高风险来源禁用自动更新。',
    dependency:
      '针对依赖风险：更新到安全补丁版本或替换组件；维护 lockfile 并在 CI 中阻断已知恶意包。',
    parser:
      '针对结构/Manifest 问题：修正 manifest 与目录约定，确保入口与资源声明一致，避免解析歧义。',
    other:
      '请结合证据做一次针对性评审：记录结论（误报/接受风险/需修复），必要时发起工单并在修复后复测。'
  }

  return {
    text: byAgent[agentKey] || byAgent.other,
    source: 'inferred'
  }
}

export function getFindingAdvicePlainText(f: any): string {
  return getFindingSecurityAdvice(f).text
}

export function findingAdviceAlertType(f: any): 'success' | 'warning' | 'info' | 'error' {
  const lvl = String(f.risk_level || f.level || f.severity || '').toLowerCase()
  if (lvl === 'critical' || lvl === 'high') return 'error'
  if (lvl === 'medium') return 'warning'
  if (lvl === 'low' || lvl === 'info') return 'info'
  return 'warning'
}
