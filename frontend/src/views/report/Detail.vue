<template>
  <div class="report-detail fade-in">
    <div class="page-header">
      <el-page-header @back="$router.back()">
        <template #content>
          <div class="header-content">
            <span class="header-title">审计报告详情</span>
            <span class="header-subtitle" v-if="metadata?.skill_name">{{ metadata.skill_name }}</span>
          </div>
        </template>
        <template #extra>
          <el-button size="small" @click="copyReportLink">
            <el-icon><Link /></el-icon>
            <span>复制报告链接</span>
          </el-button>
        </template>
      </el-page-header>
    </div>

    <div v-if="summary" v-loading="loading">
      <!-- 风险概览 -->
      <el-row :gutter="20" class="overview-cards">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon risk-level">
                <el-icon :size="26"><Aim /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-label">风险等级</div>
                <risk-badge :level="riskLevel" class="overview-value" />
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon confidence">
                <el-icon :size="26"><Compass /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-label">置信度</div>
                <div class="overview-value text-primary">
                  {{ confidencePercent }}%
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon findings">
                <el-icon :size="26"><Histogram /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-label">发现数量</div>
                <div class="overview-value text-success">
                  {{ findings.length }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="overview-card" shadow="hover">
            <div class="overview-item">
              <div class="overview-icon actions">
                <el-icon :size="26"><FolderOpened /></el-icon>
              </div>
              <div class="overview-content">
                <div class="overview-label">导出报告</div>
                <div class="action-buttons">
                  <el-button size="small" @click="download('md')">
                    <el-icon><Document /></el-icon>
                    <span>Markdown</span>
                  </el-button>
                  <el-button size="small" @click="download('json')">
                    <el-icon><Files /></el-icon>
                    <span>JSON 数据</span>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 专业审计能力：质量门禁 + 问题热点 -->
      <el-row :gutter="20" class="pro-audit-row">
        <el-col :xs="24" :lg="12">
          <el-card shadow="hover" class="gate-card">
            <template #header>
              <div class="gate-card-header">
                <span class="gate-title">质量门禁（类持续集成 / Sonar 质量门禁）</span>
                <el-button size="small" text type="primary" @click="exportGateJson">导出门禁 JSON</el-button>
              </div>
            </template>
            <div class="gate-body">
              <el-tag
                :type="qualityGateResult.level === 'fail' ? 'danger' : qualityGateResult.level === 'warn' ? 'warning' : 'success'"
                size="large"
                effect="dark"
                class="gate-tag"
              >
                {{ qualityGateResult.passed ? '放行（默认策略）' : '阻断' }}
              </el-tag>
              <ul class="gate-reasons">
                <li v-for="(r, gi) in qualityGateResult.reasons" :key="gi">{{ r }}</li>
              </ul>
              <p class="gate-hint">策略与常见 SAST 门禁一致：存在严重项或综合分过低时判定为失败；存在高危项或综合分偏低时给出警告。后续可接入组织自定义策略。</p>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="12">
          <el-card shadow="hover" class="hotspot-card">
            <template #header>
              <span class="hotspot-title">问题热点（按规则类型聚合）</span>
            </template>
            <el-table v-if="hotspotRows.length" :data="hotspotRows" size="small" stripe border max-height="220">
              <el-table-column prop="rule" label="规则 / 类型" min-width="160" show-overflow-tooltip />
              <el-table-column prop="count" label="次数" width="72" align="center" />
            </el-table>
            <el-empty v-else description="暂无类型字段可聚合" :image-size="80" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 技能包信息 -->
      <el-card class="skill-info-card" shadow="hover">
        <template #header>
          <span class="card-title-with-icon">
            <el-icon class="card-head-icon"><Box /></el-icon>
            技能包信息
          </span>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="技能包名称">
            {{ metadata?.skill_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="版本">
            {{ metadata?.version || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开发者">
            {{ metadata?.author || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 扫描可复现与供应链合规信号（对齐企业 SAST / 供应链审计常见元数据） -->
      <el-card class="scan-provenance-card" shadow="hover">
        <template #header>
          <div class="scan-provenance-header">
            <span class="scan-provenance-title">扫描与供应链元数据</span>
            <el-button size="small" text type="primary" @click="copyCiSummaryLink">
              <el-icon><Link /></el-icon>
              复制 CI 摘要接口 URL
            </el-button>
          </div>
        </template>
        <p class="scan-pro-hint">
          便于流水线门禁与事后追溯：耗时、选项快照、许可证类文件名、引擎版本；完整结构仍见 JSON 导出。
        </p>
        <el-descriptions :column="2" border class="scan-desc">
          <el-descriptions-item label="审计引擎">
            {{ metadata?.engine_version || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="扫描时间">
            {{ metadata?.scan_time || '-' }}
          </el-descriptions-item>
          <template v-if="hasScanProvenanceBlock">
            <el-descriptions-item label="开始时间">
              {{ scanProvenance.started_at || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ scanProvenance.finished_at || '—' }}
            </el-descriptions-item>
            <el-descriptions-item v-if="scanProvenance.duration_ms != null" label="扫描耗时">
              {{ formatScanDuration(scanProvenance.duration_ms) }}
            </el-descriptions-item>
            <el-descriptions-item label="基线对比">
              {{ scanProvenance.baseline_used ? '已使用基线包' : '未使用' }}
            </el-descriptions-item>
            <el-descriptions-item label="请求选项快照" :span="2">
              {{ optionsAppliedText }}
            </el-descriptions-item>
            <el-descriptions-item label="Agent 异常" :span="2">
              {{ agentErrorsText }}
            </el-descriptions-item>
          </template>
          <el-descriptions-item v-else label="扩展扫描块" :span="2">
            <span class="text-muted">此报告为升级前生成，无 scan 扩展字段。</span>
          </el-descriptions-item>
          <el-descriptions-item label="Manifest 许可证字段">
            {{ supplyChainMeta.manifest_license_field || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="Manifest 作者字段">
            {{ supplyChainMeta.manifest_author_field || '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="仓库内许可证类文件" :span="2">
            <template v-if="licenseLikeFiles.length">
              <el-tag
                v-for="(f, i) in licenseLikeFiles"
                :key="i"
                size="small"
                effect="plain"
                class="license-tag"
              >{{ f }}</el-tag>
            </template>
            <span v-else class="text-muted">未探测到常见许可证文件名（不影响其它检测结论）</span>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- OpenClaw：技能包专用创新视角（声明—实现—执行面） -->
      <el-card v-if="innovationBundle" class="innovation-card" shadow="hover">
        <template #header>
          <div class="scan-provenance-header">
            <span class="scan-provenance-title">OpenClaw 创新洞察</span>
            <el-button size="small" text type="primary" @click="copyInnovationFingerprint">
              <el-icon><CopyDocument /></el-icon>
              复制完整意图指纹
            </el-button>
          </div>
        </template>
        <p class="scan-pro-hint">{{ innovationBundle.about }}</p>
        <el-descriptions :column="2" border class="scan-desc">
          <el-descriptions-item label="意图指纹（短）">
            <code class="mono-inline">{{ innovationBundle.intent_fingerprint?.short_id || '—' }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="SKILL.md 参与计算">
            {{ innovationBundle.intent_fingerprint?.skill_md_included ? '是' : '否' }}
          </el-descriptions-item>
          <el-descriptions-item label="自主执行面" :span="2">
            <el-tag :type="autonomyTagType(innovationBundle.autonomy_surface?.level)" size="small" effect="dark" style="margin-right: 8px">
              {{ innovationBundle.autonomy_surface?.level === 'high' ? '偏高' : innovationBundle.autonomy_surface?.level === 'medium' ? '中等' : '偏低' }}
            </el-tag>
            <span class="text-muted">
              壳层/脚本类约 {{ innovationBundle.autonomy_surface?.shell_like_file_count ?? 0 }} 个，
              密度 {{ innovationBundle.autonomy_surface?.shell_density ?? '—' }}
            </span>
            <div class="innovation-interpret">{{ innovationBundle.autonomy_surface?.interpretation }}</div>
          </el-descriptions-item>
        </el-descriptions>
        <div class="innovation-signals">
          <div class="innovation-signals-title">声明 vs 表面信号</div>
          <template v-if="innovationSignals.length">
            <el-alert
              v-for="(s, si) in innovationSignals"
              :key="si"
              :type="innovationAlertType(s.severity)"
              :title="s.title"
              :description="s.detail"
              show-icon
              :closable="false"
              class="innovation-alert"
            />
          </template>
          <p v-else class="text-muted">未触发声明—表面张力规则（或结构信息不足）。</p>
        </div>
      </el-card>

      <!-- AI 预处理信息 -->
      <el-card class="preprocess-card" shadow="hover">
        <template #header>
          <span class="card-title-with-icon">
            <el-icon class="card-head-icon"><Cpu /></el-icon>
            AI 预处理信息
          </span>
        </template>
        <el-row :gutter="24" class="preprocess-summary">
          <el-col :xs="24" :sm="12" :md="6">
            <div class="summary-item">
              <div class="label">是否启用</div>
              <div class="value">{{ aiPreprocessingEnabled ? '已启用' : '未启用' }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="summary-item">
              <div class="label">分析文件数</div>
              <div class="value">{{ preprocessed.files_analyzed || 0 }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="summary-item">
              <div class="label">预处理文件数</div>
              <div class="value">{{ preprocessed.files_preprocessed || 0 }}</div>
            </div>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <div class="summary-item">
              <div class="label">平均压缩比</div>
              <div class="value">
                {{ preprocessed.statistics?.average_compression_ratio ? (preprocessed.statistics.average_compression_ratio * 100).toFixed(1) + '%' : '-' }}
              </div>
            </div>
          </el-col>
        </el-row>

        <div v-if="preprocessedFiles.length" class="preprocess-files">
          <div class="file-list-title">预处理文件列表</div>
          <el-collapse>
            <el-collapse-item
              v-for="(file, idx) in preprocessedFiles"
              :key="file.file_path || idx"
              :name="idx"
            >
              <template #title>
                <div class="file-title">
                  <span>{{ file.file_path }}</span>
                  <el-tag size="small" type="success" effect="plain">
                    {{ file.extracted_lines }}/{{ file.original_lines }} 行
                  </el-tag>
                </div>
              </template>
              <div class="file-detail">
                <p class="file-summary">AI 摘要: {{ file.ai_summary || '无' }}</p>
                <div v-if="file.ai_recommendation" class="file-recommendation">
                  <strong>建议：</strong> {{ file.ai_recommendation }}
                </div>
                <code-highlight :content="file.preprocessed_content || ''" language="plaintext" />
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        <el-empty v-else description="暂无预处理文件或未启用 AI 预处理" :image-size="120" />
      </el-card>

      <!-- 风险分布图表 -->
      <el-card class="chart-section" shadow="hover">
        <template #header>
          <span class="card-title-with-icon">
            <el-icon class="card-head-icon"><PieChart /></el-icon>
            风险分布
          </span>
        </template>
        <div ref="chartRef" style="height:320px"></div>
      </el-card>

      <!-- 安全评分模块 -->
      <el-card class="safety-score-section" shadow="hover">
        <template #header>
          <div class="score-header">
            <span class="card-title-with-icon score-header-title">
              <el-icon class="card-head-icon"><Medal /></el-icon>
              安全评分详情
            </span>
            <el-tag :type="scoreTagType" size="large" effect="dark">{{ safetyLevel }}</el-tag>
          </div>
        </template>
        
        <div class="score-alerts-block">
          <el-alert
            v-for="(alert, idx) in scoreAlerts"
            :key="idx"
            :type="alert.type"
            :title="alert.title"
            :description="alert.message"
            show-icon
            :closable="false"
            class="score-alert-item"
          />
        </div>

        <el-row :gutter="48">
          <!-- 左侧：仪表盘 -->
          <el-col :xs="24" :md="10">
            <div ref="gaugeChartRef" class="gauge-container"></div>
          </el-col>
          
          <!-- 右侧：评分详情 -->
          <el-col :xs="24" :md="14">
            <div class="score-details">
              <!-- 综合评分 -->
              <div class="composite-score">
                <div class="score-label">综合安全评分（多维度加权）</div>
                <div class="score-value-wrapper">
                  <span class="score-number" :style="{color: scoreColor}">
                    {{ safetyScore }}
                  </span>
                  <span class="score-total">/ 100</span>
                </div>
                <div class="score-formula">
                  计算公式：综合分 = Σ（维度得分 × 维度权重），各维度权重之和为 100%。
                </div>
                <div class="score-description">
                  {{ overallScoreAdvice }}
                </div>
              </div>

              <!-- 各维度评分 -->
              <div class="dimensions-section">
                <div class="dimensions-title">各维度得分与权重</div>
                
                <div v-for="row in dimensionRows" :key="row.key" class="dimension-item">
                  <div class="dimension-header">
                    <div class="dimension-title-block">
                      <span class="dimension-name">{{ row.name }}</span>
                      <el-tag size="small" :type="row.statusTag" effect="plain">{{ row.statusLabel }}</el-tag>
                    </div>
                    <div class="dimension-meta">
                      <span class="dimension-weight">权重 {{ row.weightPercent }}%</span>
                      <span class="dimension-count" v-if="row.findingCount">· {{ row.findingCount }} 项发现</span>
                      <span class="dimension-contrib">· 贡献 {{ row.contribution.toFixed(1) }} 分</span>
                    </div>
                  </div>
                  <div class="dimension-score-row">
                    <span class="dimension-score" :style="{ color: row.color }">{{ row.score }}</span>
                    <span class="dimension-score-suffix">/ 100</span>
                  </div>
                  <el-progress
                    :percentage="row.score"
                    :color="row.color"
                    :stroke-width="10"
                    :show-text="false"
                  />
                  <p class="dimension-suggestion">{{ row.suggestion }}</p>
                </div>
              </div>

              <!-- 风险等级说明 -->
              <div class="dimension-note">
                <div class="note-title note-title-row">
                  <el-icon class="note-title-icon"><LocationInformation /></el-icon>
                  风险等级说明
                </div>
                <div class="note-grid">
                  <div class="note-item">
                    <span class="note-color" style="background:#dc2626"></span>
                    <span>0-40: 严重风险（拒绝）</span>
                  </div>
                  <div class="note-item">
                    <span class="note-color" style="background:#ea580c"></span>
                    <span>41-60: 高风险（需谨慎）</span>
                  </div>
                  <div class="note-item">
                    <span class="note-color" style="background:#f59e0b"></span>
                    <span>61-80: 中等风险（可接受）</span>
                  </div>
                  <div class="note-item">
                    <span class="note-color" style="background:#10b981"></span>
                    <span>81-100: 低风险（安全）</span>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 详细风险列表 -->
      <el-card class="findings-section" shadow="hover">
        <template #header>
          <div class="findings-header">
            <div class="findings-header-left">
              <span class="findings-section-title">
                <el-icon class="findings-head-icon"><Search /></el-icon>
                详细风险列表
              </span>
              <span class="finding-count">{{ findings.length }}</span>
              <el-tag v-if="showOnlyBookmarked" type="warning" size="small" effect="plain">仅关注</el-tag>
            </div>
            <div class="findings-header-actions">
              <el-select
                v-model="triageFilter"
                placeholder="按处置状态筛选"
                size="small"
                class="triage-filter-select"
              >
                <el-option label="全部发现" value="all" />
                <el-option label="未结案（非误报/已修复）" value="active" />
                <el-option
                  v-for="opt in triageStatusOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <el-switch
                v-model="showOnlyBookmarked"
                active-text="仅看关注"
                inline-prompt
                style="margin-right: 8px"
              />
              <el-button
                type="primary"
                plain
                size="small"
                :disabled="!findings.length"
                @click="exportFindingsCsv"
              >
                <el-icon><Download /></el-icon>
                <span>CSV</span>
              </el-button>
              <el-button
                plain
                size="small"
                :disabled="!findings.length"
                title="导出 SARIF 2.1（静态分析结果交换格式，便于对接代码托管平台）"
                @click="exportSarif"
              >
                <el-icon><Files /></el-icon>
                <span>SARIF</span>
              </el-button>
            </div>
          </div>
        </template>

        <p v-if="filterEmptyHint" class="bookmark-empty-hint">{{ filterEmptyHint }}</p>
        
        <el-collapse v-model="activeCollapse">
          <el-collapse-item 
            v-for="item in displayedFindingItems" 
            :key="item.originalIndex" 
            :name="item.originalIndex"
          >
            <template #title>
              <div class="finding-title-row">
                <el-button
                  class="bookmark-btn"
                  text
                  circle
                  size="small"
                  @click="onToggleBookmark(item.f, item.originalIndex, $event)"
                >
                  <el-icon :size="18" :color="isBookmarked(item.f, item.originalIndex) ? '#e6a23c' : '#c0c4cc'">
                    <StarFilled v-if="isBookmarked(item.f, item.originalIndex)" />
                    <Star v-else />
                  </el-icon>
                </el-button>
                <risk-badge :level="getRiskLevel(item.f)" />
                <span class="finding-title-text">{{ item.f.title || item.f.reason || '风险项' }}</span>
                <el-tag v-if="item.f.type || item.f.rule_id" size="small" type="warning" effect="plain" class="rule-id-tag">
                  {{ item.f.type || item.f.rule_id }}
                </el-tag>
                <el-tag size="small" type="info" effect="plain">{{ item.f.category || item.f.agent || '未知' }}</el-tag>
                <el-tag size="small" effect="plain" :type="triageTagType(triageFor(item).status)">
                  {{ triageLabel(triageFor(item).status) }}
                </el-tag>
              </div>
            </template>
            
            <div>
              <div v-if="evidenceLocation(item.f).file" class="evidence-location">
                <el-icon><DocumentCopy /></el-icon>
                <span><strong>位置</strong> {{ evidenceLocation(item.f).file }}</span>
                <span v-if="evidenceLocation(item.f).line != null"> : 第 {{ evidenceLocation(item.f).line }} 行</span>
              </div>
              <div v-if="cweLinks(item.f).length || cveLinks(item.f).length" class="ref-links">
                <a
                  v-for="c in cweLinks(item.f)"
                  :key="c.id"
                  :href="c.url"
                  target="_blank"
                  rel="noopener"
                  class="ref-link"
                >{{ c.id }}</a>
                <a
                  v-for="c in cveLinks(item.f)"
                  :key="c.id"
                  :href="c.url"
                  target="_blank"
                  rel="noopener"
                  class="ref-link"
                >{{ c.id }}</a>
              </div>
              <div class="triage-row">
                <span class="triage-label">处置状态</span>
                <el-select
                  :model-value="triageFor(item).status"
                  size="small"
                  class="triage-select"
                  @update:model-value="(v) => onTriageStatusChange(item, v)"
                >
                  <el-option
                    v-for="opt in triageStatusOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
                <el-input
                  :model-value="triageFor(item).note"
                  size="small"
                  type="textarea"
                  :rows="2"
                  placeholder="备注：评审结论、工单号、修复 PR 链接等（本地保存）"
                  class="triage-note"
                  @update:model-value="(v) => onTriageNoteChange(item, v)"
                />
              </div>
              <p class="finding-description">{{ item.f.description || item.f.reason || '' }}</p>
              
              <div v-if="item.f.evidence" class="evidence-section">
                <div class="evidence-title">
                  <el-icon><Document /></el-icon>
                  <span>证据</span>
                </div>
                <div class="evidence-content">
                  <!-- 如果是对象，美化展示 -->
                  <div v-if="typeof item.f.evidence === 'object' && !Array.isArray(item.f.evidence)" class="evidence-fields">
                    <div v-for="(value, key) in item.f.evidence" :key="key" class="evidence-field">
                      <span class="field-label">{{ translateEvidenceField(key) }}</span>
                      <span class="field-value">{{ translateEvidenceValue(key, value) }}</span>
                    </div>
                  </div>
                  <!-- 如果是数组或字符串，直接显示 -->
                  <code-highlight v-else :content="formatEvidence(item.f.evidence)" :language="item.f.language || 'plaintext'" />
                </div>
              </div>

              <!-- 每条发现独立展示安全建议（后端优先，缺失时用前端推断兜底），避免与其它区块的建议堆叠混淆 -->
              <div class="finding-security-advice-wrap">
                <el-alert
                  :type="findingAdviceAlertType(item.f)"
                  :closable="false"
                  show-icon
                  class="finding-advice-alert"
                >
                  <template #title>
                    <span class="finding-advice-title-row">
                      <el-icon class="finding-advice-guide-icon"><Guide /></el-icon>
                      <span>安全建议</span>
                      <el-tag
                        v-if="findingAdviceFor(item.f).source === 'inferred'"
                        size="small"
                        type="info"
                        effect="plain"
                        class="advice-source-tag"
                      >智能推断</el-tag>
                      <el-tag
                        v-else
                        size="small"
                        type="success"
                        effect="plain"
                        class="advice-source-tag"
                      >报告字段</el-tag>
                    </span>
                  </template>
                  <div class="finding-advice-body">{{ findingAdviceFor(item.f).text }}</div>
                </el-alert>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
        
        <el-empty v-if="!findings.length" description="未发现风险" :image-size="120">
          <template #image>
            <el-icon :size="72" color="var(--el-color-success)"><CircleCheckFilled /></el-icon>
          </template>
        </el-empty>
      </el-card>
    </div>
    
    <el-empty v-else description="报告加载中..." :image-size="120" />
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getReport, exportReport } from '../../api/report'
import CodeHighlight from '../../components/CodeHighlight.vue'
import RiskBadge from '../../components/RiskBadge.vue'
import {
  buildDimensionRows,
  compositeScoreFromRows,
  getRiskLevelFinding
} from '../../utils/reportMultiDimScore'
import {
  findingBookmarkKey,
  isFindingBookmarked,
  toggleFindingBookmark
} from '../../utils/findingBookmarks'
import {
  TRIAGE_LABEL,
  getTriageRecord,
  setTriageRecord,
  triageKeyForFinding,
  isActiveTriageStatus,
  type TriageStatus
} from '../../utils/findingTriage'
import { computeQualityGate, buildGateJsonPayload } from '../../utils/qualityGate'
import { downloadSarifJson } from '../../utils/sarifExport'
import {
  Aim,
  Compass,
  Histogram,
  FolderOpened,
  Box,
  Cpu,
  PieChart,
  Medal,
  LocationInformation,
  Search,
  CircleCheckFilled,
  DocumentCopy,
  Download,
  Document,
  Files,
  Guide,
  Link,
  Star,
  StarFilled,
  CopyDocument
} from '@element-plus/icons-vue'
import {
  getFindingSecurityAdvice,
  getFindingAdvicePlainText,
  findingAdviceAlertType
} from '../../utils/findingAdvice'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const rawData = ref<any>(null)
const loading = ref(false)
const activeCollapse = ref<number[]>([])
const chartRef = ref<HTMLElement | null>(null)
const gaugeChartRef = ref<HTMLElement | null>(null)

// 计算属性：适配后端数据结构
const summary = computed(() => rawData.value?.summary || rawData.value || {})
const metadata = computed(() => rawData.value?.metadata || {})
const scanProvenance = computed(() => (metadata.value as any)?.scan || {})
const supplyChainMeta = computed(() => (metadata.value as any)?.supply_chain || {})
const hasScanProvenanceBlock = computed(() => {
  const s = scanProvenance.value as Record<string, unknown>
  return !!(s && (s.started_at || s.finished_at || s.duration_ms != null))
})
const licenseLikeFiles = computed(() => {
  const list = (supplyChainMeta.value as any)?.license_files_in_archive
  return Array.isArray(list) ? list : []
})

const formatScanDuration = (ms: number) => {
  if (ms < 1000) return `${ms} ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)} 秒`
  const m = Math.floor(ms / 60000)
  const s = Math.round((ms % 60000) / 1000)
  return `${m} 分 ${s} 秒`
}

const optionsAppliedText = computed(() => {
  const o = scanProvenance.value?.options_applied as Record<string, unknown> | undefined
  if (!o || typeof o !== 'object') return '—'
  const entries = Object.entries(o)
  if (!entries.length) return '—'
  return entries.map(([k, v]) => `${k}: ${v}`).join('，')
})

const agentErrorsText = computed(() => {
  const e = scanProvenance.value?.agent_errors as Record<string, string> | undefined
  if (!e || typeof e !== 'object') return '无'
  const keys = Object.keys(e)
  if (!keys.length) return '无'
  return keys.map((k) => `${k}: ${e[k]}`).join('；')
})

const copyCiSummaryLink = () => {
  const url = `${window.location.origin}/api/reports/${id}/ci-summary`
  void navigator.clipboard.writeText(url).then(
    () => ElMessage.success('已复制 CI 摘要 GET 地址'),
    () => ElMessage.error('复制失败')
  )
}

/** 技能包专用创新块（新报告必有；旧报告无此字段则不展示卡片） */
const innovationBundle = computed(() => (metadata.value as any)?.openclaw_innovation ?? null)
const innovationSignals = computed(() => {
  const list = innovationBundle.value?.declared_vs_surface
  return Array.isArray(list) ? list : []
})

const copyInnovationFingerprint = () => {
  const fp = innovationBundle.value?.intent_fingerprint?.full_hash as string | undefined
  if (!fp) {
    ElMessage.warning('当前报告无完整意图指纹')
    return
  }
  void navigator.clipboard.writeText(fp).then(
    () => ElMessage.success('已复制完整 SHA-256 意图指纹'),
    () => ElMessage.error('复制失败')
  )
}

const innovationAlertType = (sev: string | undefined) => {
  if (sev === 'warning') return 'warning' as const
  if (sev === 'danger' || sev === 'critical') return 'error' as const
  return 'info' as const
}

/** 每条 finding 的安全建议（模板内多次调用成本低；逻辑纯函数） */
const findingAdviceFor = (f: any) => getFindingSecurityAdvice(f)

const autonomyTagType = (level: string | undefined) => {
  if (level === 'high') return 'danger' as const
  if (level === 'medium') return 'warning' as const
  return 'success' as const
}

const findings = computed(() => rawData.value?.findings || [])
const preprocessed = computed(() => rawData.value?.preprocessed || {})

const getRiskLevel = getRiskLevelFinding

const dimensionRows = computed(() => buildDimensionRows((findings.value as any[]) || []))

const safetyScore = computed(() => compositeScoreFromRows(dimensionRows.value))

/** 风险项本地「关注」书签（仅本机） */
const bookmarkRev = ref(0)
const showOnlyBookmarked = ref(false)

const isBookmarked = (f: any, originalIndex: number) => {
  bookmarkRev.value
  return isFindingBookmarked(id, findingBookmarkKey(f, originalIndex))
}

const onToggleBookmark = (f: any, originalIndex: number, e: Event) => {
  e.stopPropagation()
  const on = toggleFindingBookmark(id, findingBookmarkKey(f, originalIndex))
  bookmarkRev.value++
  ElMessage.success(on ? '已加入关注（仅保存在本浏览器）' : '已取消关注')
}

const triageRev = ref(0)
const triageFilter = ref<'all' | 'active' | TriageStatus>('all')

const triageStatusOptions = (Object.entries(TRIAGE_LABEL) as [TriageStatus, string][]).map(
  ([value, label]) => ({ value, label })
)

const severityCounts = computed(() => {
  const d = summary.value.severity_distribution || ({} as any)
  const from: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0, info: 0 }
  ;(findings.value as any[]).forEach((f) => {
    const lv = getRiskLevel(f)
    if (lv in from) from[lv]++
  })
  return {
    critical: Math.max(Number(d.critical) || 0, from.critical),
    high: Math.max(Number(d.high) || 0, from.high),
    medium: Math.max(Number(d.medium) || 0, from.medium),
    low: Math.max(Number(d.low) || 0, from.low),
    info: Math.max(Number(d.info) || 0, from.info)
  }
})

const qualityGateResult = computed(() =>
  computeQualityGate({
    safetyScore: safetyScore.value,
    criticalCount: severityCounts.value.critical,
    highCount: severityCounts.value.high
  })
)

const hotspotRows = computed(() => {
  const m: Record<string, number> = {}
  ;(findings.value as any[]).forEach((f) => {
    const k = String(f.type || f.rule_id || f.agent || 'unknown')
    m[k] = (m[k] || 0) + 1
  })
  return Object.entries(m)
    .map(([rule, count]) => ({ rule, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 24)
})

const displayedFindingItems = computed(() => {
  bookmarkRev.value
  triageRev.value
  const list = (findings.value as any[]) || []
  let out = list.map((f: any, originalIndex: number) => ({ f, originalIndex }))
  if (showOnlyBookmarked.value) {
    out = out.filter(({ f, originalIndex }) =>
      isFindingBookmarked(id, findingBookmarkKey(f, originalIndex))
    )
  }
  if (triageFilter.value === 'active') {
    out = out.filter(({ f, originalIndex }) => {
      const st = getTriageRecord(id, triageKeyForFinding(f, originalIndex)).status
      return isActiveTriageStatus(st)
    })
  } else if (triageFilter.value !== 'all') {
    const tf = triageFilter.value
    out = out.filter(({ f, originalIndex }) => {
      return getTriageRecord(id, triageKeyForFinding(f, originalIndex)).status === tf
    })
  }
  return out
})

const filterEmptyHint = computed(() => {
  if (!findings.value.length) return ''
  if (displayedFindingItems.value.length > 0) return ''
  if (showOnlyBookmarked.value && triageFilter.value !== 'all') {
    return '当前「仅看关注」与处置筛选组合下无匹配项，请放宽筛选条件。'
  }
  if (showOnlyBookmarked.value) return '暂无已关注项。点击标题左侧星标可加入关注。'
  if (triageFilter.value !== 'all') return '当前处置筛选下无匹配项。'
  return ''
})

const triageFor = (item: { f: any; originalIndex: number }) => {
  triageRev.value
  return getTriageRecord(id, triageKeyForFinding(item.f, item.originalIndex))
}

const onTriageStatusChange = (item: { f: any; originalIndex: number }, v: TriageStatus) => {
  const key = triageKeyForFinding(item.f, item.originalIndex)
  const cur = getTriageRecord(id, key)
  setTriageRecord(id, key, { status: v, note: cur.note })
  triageRev.value++
  ElMessage.success('处置状态已保存（本地）')
}

const onTriageNoteChange = (item: { f: any; originalIndex: number }, v: string) => {
  const key = triageKeyForFinding(item.f, item.originalIndex)
  const cur = getTriageRecord(id, key)
  setTriageRecord(id, key, { status: cur.status, note: v })
  triageRev.value++
}

const triageLabel = (s: TriageStatus) => TRIAGE_LABEL[s] || s

const triageTagType = (s: TriageStatus) => {
  if (s === 'false_positive') return 'info'
  if (s === 'fixed') return 'success'
  if (s === 'accepted_risk') return 'warning'
  if (s === 'confirmed') return 'danger'
  return ''
}

const exportGateJson = () => {
  const payload = buildGateJsonPayload({
    reportId: id,
    safetyScore: safetyScore.value,
    gate: qualityGateResult.value,
    skillName: metadata.value?.skill_name
  })
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `quality-gate_${id}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已下载门禁结果 JSON，可供流水线归档')
}

const exportSarif = () => {
  if (!rawData.value) return
  downloadSarifJson(rawData.value, id)
  ElMessage.success('已下载 SARIF 2.1 扫描结果（可与代码托管平台安全能力对接）')
}

const evidenceLocation = (f: any) => {
  const ev = f.evidence
  if (ev && typeof ev === 'object' && !Array.isArray(ev)) {
    const file = ev.file_path || ev.file || ev.path
    const line = ev.line_number ?? ev.line
    if (typeof file === 'string' && file.length > 0) {
      return { file, line: typeof line === 'number' ? line : null }
    }
  }
  if (typeof f.file_path === 'string' && f.file_path.length > 0) {
    return { file: f.file_path, line: typeof f.line_number === 'number' ? f.line_number : null }
  }
  return { file: null as string | null, line: null as number | null }
}

const cweLinks = (f: any): { id: string; url: string }[] => {
  const bag = `${f.cwe || ''} ${f.cwe_id || ''} ${f.type || ''} ${JSON.stringify(f.evidence || '')} ${f.description || ''}`
  const nums = [...bag.matchAll(/CWE-(\d+)/gi)].map((m) => m[1])
  return [...new Set(nums)].map((n) => ({ id: `CWE-${n}`, url: `https://cwe.mitre.org/data/definitions/${n}.html` }))
}

const cveLinks = (f: any): { id: string; url: string }[] => {
  const bag = `${f.cve || ''} ${f.cve_id || ''} ${JSON.stringify(f.evidence || '')} ${f.description || ''}`
  const ids = [...bag.matchAll(/CVE-\d{4}-\d+/gi)].map((m) => m[0].toUpperCase())
  return [...new Set(ids)].map((cid) => ({
    id: cid,
    url: `https://nvd.nist.gov/vuln/detail/${cid}`
  }))
}
const aiPreprocessingEnabled = computed(() => metadata.value?.ai_preprocessing || false)
const preprocessedFiles = computed(() => preprocessed.value?.preprocessed_files || [])

// 风险等级（统一转小写）
const riskLevel = computed(() => {
  const level = summary.value.risk_level || summary.value.level || ''
  return level.toLowerCase()
})

// 置信度（转换为百分比）
const confidencePercent = computed(() => {
  const confidence = summary.value.confidence || 0
  // 如果是 0-1 之间的小数，转为百分比；如果已经是百分比数值，直接返回
  return confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence)
})

// 安全等级
const safetyLevel = computed(() => {
  const score = safetyScore.value
  if (score >= 81) return '安全'
  if (score >= 61) return '可接受'
  if (score >= 41) return '需谨慎'
  return '高风险'
})

// 安全等级标签类型
const scoreTagType = computed(() => {
  const score = safetyScore.value
  if (score >= 81) return 'success'
  if (score >= 61) return ''
  if (score >= 41) return 'warning'
  return 'danger'
})

// 评分颜色
const scoreColor = computed(() => {
  const score = safetyScore.value
  if (score >= 81) return '#67c23a'
  if (score >= 61) return '#409eff'
  if (score >= 41) return '#e6a23c'
  return '#f56c6c'
})

/** 基于综合分的总体建议文案 */
const overallScoreAdvice = computed(() => {
  const s = safetyScore.value
  if (s >= 81) {
    return '综合分由多维度加权得出，当前整体风险可控；请仍核对各维度告警与业务是否可接受。'
  }
  if (s >= 61) {
    return '综合分中等，存在短板维度。建议优先处理得分偏低的维度，并在修复后安排复测验证闭环。'
  }
  if (s >= 41) {
    return '综合分偏低，不建议在未评估风险的情况下直接接入生产；需制定整改计划并跟踪复测结果。'
  }
  return '综合分处于高风险区间，应视为阻断项：先收敛严重/高危发现，再重新执行完整审计。'
})

/** 综合分总览（薄弱维度的具体处置建议已在下文「各维度得分」与每条「安全建议」中展示，避免多条 Alert 堆叠） */
const scoreAlerts = computed(() => {
  const comp = safetyScore.value
  let overallType: 'success' | 'warning' | 'error' | 'info' = 'success'
  if (comp < 41) overallType = 'error'
  else if (comp < 61) overallType = 'warning'
  else if (comp < 81) overallType = 'info'
  return [
    {
      type: overallType,
      title: `综合安全分 ${comp}（多维度加权）`,
      message: overallScoreAdvice.value
    }
  ]
})

onMounted(async () => {
  loading.value = true
  try {
    const res: any = await getReport(id)
    rawData.value = res
    
    // 默认展开所有
    activeCollapse.value = findings.value.map((_: any, i: number) => i)
    await nextTick()
  } catch (e) {
    console.error('Failed to fetch report:', e)
  } finally {
    loading.value = false
  }
})

watch(
  () => rawData.value,
  async (v) => {
    if (!v) return
    await nextTick()
    renderChart()
    renderGaugeChart()
  },
  { deep: true }
)

const copyReportLink = async () => {
  try {
    const path = router.resolve({ name: 'ReportDetail', params: { id } }).href
    const url = `${window.location.origin}${path}`
    await navigator.clipboard.writeText(url)
    ElMessage.success('报告链接已复制')
  } catch {
    ElMessage.error('复制失败，请检查浏览器权限')
  }
}

const csvEscape = (val: unknown) => {
  if (val == null || val === '') return ''
  const s = String(val).replace(/"/g, '""')
  if (/[",\r\n]/.test(s)) return `"${s}"`
  return s
}

const exportFindingsCsv = () => {
  const list = findings.value as any[]
  const header = ['风险等级', '标题', '分类', '描述', '修复建议']
  const lines = [header.join(',')]
  for (const f of list) {
    lines.push(
      [
        csvEscape(getRiskLevel(f)),
        csvEscape(f.title || f.reason || ''),
        csvEscape(f.category || f.agent || ''),
        csvEscape(f.description || f.reason || ''),
        csvEscape(getFindingAdvicePlainText(f))
      ].join(',')
    )
  }
  const blob = new Blob(['\ufeff' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `findings_${id}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('已导出 CSV')
}

// 格式化证据显示
const formatEvidence = (evidence: any) => {
  if (!evidence) return ''
  if (typeof evidence === 'string') return evidence
  if (Array.isArray(evidence)) {
    return evidence.map((e: any) => {
      if (typeof e === 'string') return e
      return JSON.stringify(e, null, 2)
    }).join('\n\n')
  }
  return JSON.stringify(evidence, null, 2)
}

// 翻译证据字段名
const translateEvidenceField = (key: string | number): string => {
  const strKey = String(key)
  const map: Record<string, string> = {
    // 基础字段
    file_path: '文件路径',
    line_number: '行号',
    code_snippet: '代码片段',
    rule_id: '规则标识',
    ruleId: '规则标识',
    severity: '严重程度',
    description: '描述',
    match: '匹配内容',
    context: '上下文',
    url: '链接',
    package_name: '包名',
    version: '版本',
    license: '许可证',
    author: '作者',
    created_at: '创建时间',
    updated_at: '更新时间',
    // 风险相关字段
    type: '风险类型',
    level: '风险等级',
    risk_level: '风险等级',
    message: '风险说明',
    reason: '原因',
    recommendation: '修复建议',
    // 证据相关字段
    evidence: '证据',
    file: '文件',
    line: '行号',
    content: '内容',
    detail: '详情',
    item: '项目',
    module: '模块',
    path: '路径',
    command: '命令',
    pattern: '模式',
    source: '来源',
    // 依赖分析字段
    package: '依赖包',
    title: '标题',
    name: '名称',
    agent: '来源智能体',
    cwe: 'CWE 编号',
    cwe_id: 'CWE 编号',
    cve: 'CVE 编号',
    cve_id: 'CVE 编号',
    html_url: '网页链接',
    repository: '代码仓库',
    commit_sha: '提交哈希',
    sha: '校验和',
    branch: '分支',
    ref: '引用',
    fingerprint: '指纹'
  }
  return map[strKey] || strKey
}

// 翻译证据字段值
const translateEvidenceValue = (key: string | number, value: any): string => {
  if (typeof value !== 'string') return String(value)
  
  const strValue = value as string
  
  // 风险等级翻译
  const levelMap: Record<string, string> = {
    'critical': '严重',
    'high': '高危',
    'medium': '中危',
    'low': '低危',
    'info': '提示'
  }
  
  // 风险类型翻译
  const typeMap: Record<string, string> = {
    'anonymous_publication': '匿名发布',
    'missing_license': '缺少许可证',
    'dangerous_command': '危险命令',
    'sensitive_data': '敏感数据',
    'insecure_dependency': '不安全依赖',
    'prompt_injection': '提示词注入',
    'code_injection': '代码注入',
    'path_traversal': '路径遍历',
    'privilege_escalation': '权限提升',
    'information_disclosure': '信息泄露'
  }
  
  // 根据键名选择对应的翻译映射
  const lowerKey = String(key).toLowerCase()
  if (lowerKey.includes('level') || lowerKey.includes('severity') || lowerKey.includes('等级')) {
    return levelMap[strValue.toLowerCase()] || strValue
  }
  
  if (lowerKey.includes('type') || lowerKey.includes('类型')) {
    return typeMap[strValue.toLowerCase()] || strValue
  }
  
  return strValue
}

// 格式化字段值
const formatFieldValue = (value: any) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value, null, 2)
  
  // 尝试翻译字段值
  const stringValue = String(value)
  return stringValue
}

const renderChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  // 优先使用后端的 severity_distribution，否则统计 findings
  let levelCount: Record<string, number> = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0
  }
  
  // 尝试从 summary 中获取
  const distribution = summary.value.severity_distribution
  if (distribution) {
    levelCount = {
      critical: distribution.critical || 0,
      high: distribution.high || 0,
      medium: distribution.medium || 0,
      low: distribution.low || 0
    }
  } else {
    // 手动统计
    findings.value.forEach((f: any) => {
      const level = getRiskLevel(f)
      if (levelCount[level] !== undefined) {
        levelCount[level]++
      }
    })
  }
  
  const data = [
    { value: levelCount.critical, name: '严重', itemStyle: { color: '#f56c6c' } },
    { value: levelCount.high, name: '高危', itemStyle: { color: '#e6a23c' } },
    { value: levelCount.medium, name: '中危', itemStyle: { color: '#409eff' } },
    { value: levelCount.low, name: '低危', itemStyle: { color: '#67c23a' } }
  ].filter(item => item.value > 0)
  
  // 如果没有任何数据，显示空状态
  if (data.length === 0) {
    chart.setOption({
      title: {
        text: '暂无风险数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#909399',
          fontSize: 16
        }
      }
    })
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: data.map(d => d.name)
    },
    series: [
      {
        name: '风险分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: data
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

// 渲染仪表盘
const renderGaugeChart = () => {
  if (!gaugeChartRef.value) return
  
  const chart = echarts.init(gaugeChartRef.value)
  const score = safetyScore.value
  
  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        splitNumber: 10,
        itemStyle: {
          color: scoreColor.value,
          shadowColor: 'rgba(0,138,255,0.45)',
          shadowBlur: 10,
          shadowOffsetX: 2,
          shadowOffsetY: 2
        },
        progress: {
          show: true,
          roundCap: true,
          width: 18
        },
        pointer: {
          icon: 'path://M2090.36389,615.30999 L2090.36389,615.30999 C2091.48372,615.30999 2092.40383,616.194028 2092.44859,617.312956 L2096.90698,728.755929 C2097.05155,732.369577 2094.2393,735.416212 2090.62566,735.56078 C2090.53845,735.564269 2090.45117,735.566014 2090.36389,735.566014 L2090.36389,735.566014 C2086.74736,735.566014 2083.81557,732.63423 2083.81557,729.017692 C2083.81557,728.930412 2083.81732,728.84314 2083.82081,728.755929 L2088.2792,617.312956 C2088.32396,616.194028 2089.24407,615.30999 2090.36389,615.30999 Z',
          length: '75%',
          width: 16,
          offsetCenter: [0, '5%']
        },
        axisLine: {
          roundCap: true,
          lineStyle: {
            width: 18
          }
        },
        axisTick: {
          splitNumber: 2,
          lineStyle: {
            width: 2,
            color: '#999'
          }
        },
        splitLine: {
          length: 12,
          lineStyle: {
            width: 3,
            color: '#999'
          }
        },
        axisLabel: {
          distance: 30,
          color: '#999',
          fontSize: 14
        },
        title: {
          show: false
        },
        detail: {
          backgroundColor: '#fff',
          borderColor: '#999',
          borderWidth: 2,
          width: '60%',
          lineHeight: 40,
          height: 40,
          borderRadius: 8,
          offsetCenter: [0, '35%'],
          valueAnimation: true,
          formatter: function (value: number) {
            return '{value|' + value.toFixed(0) + '}{unit|分}';
          },
          rich: {
            value: {
              fontSize: 40,
              fontWeight: 'bolder',
              color: '#333'
            },
            unit: {
              fontSize: 16,
              color: '#999',
              padding: [0, 0, -10, 5]
            }
          }
        },
        data: [
          {
            value: score
          }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

const download = async (format: string) => {
  try {
    const response = await exportReport(id, format)
    const blob: Blob = response.data || response
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${id}.${format === 'md' ? 'md' : 'json'}`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Download failed:', e)
  }
}
</script>

<style scoped>
.report-detail {
  padding: 0;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 概览卡片 */
.overview-cards {
  margin-bottom: 24px;
}

.overview-card {
  border-radius: 12px;
  transition: all 0.3s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preprocess-card {
  margin-top: 24px;
  border-radius: 12px;
}

.preprocess-summary {
  margin-bottom: 16px;
}

.summary-item {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}

.summary-item .label {
  color: var(--text-muted);
  font-size: 12px;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 20px;
  font-weight: 700;
}

.file-list-title {
  font-weight: 600;
  margin-bottom: 16px;
}

.file-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.file-detail {
  margin-top: 12px;
}

.file-summary,
.file-recommendation {
  margin: 0 0 12px 0;
}

.overview-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.overview-icon.risk-level {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.overview-icon.confidence {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.overview-icon.findings {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.overview-icon.actions {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.overview-content {
  flex: 1;
  min-width: 0;
}

.overview-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 6px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.overview-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.text-primary {
  color: var(--primary-color) !important;
}

.text-success {
  color: var(--risk-low) !important;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 70px;
}

.pro-audit-row {
  margin-bottom: 24px;
}

.gate-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.gate-title,
.hotspot-title {
  font-weight: 600;
  font-size: 15px;
}

.gate-body {
  padding: 4px 0;
}

.gate-tag {
  margin-bottom: 12px;
}

.gate-reasons {
  margin: 0 0 12px;
  padding-left: 20px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

.gate-hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.hotspot-card {
  border-radius: 12px;
}

.triage-filter-select {
  width: 200px;
  max-width: 100%;
}

.rule-id-tag {
  font-family: ui-monospace, monospace;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.evidence-location {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 10px 12px;
  margin-bottom: 12px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  font-size: 13px;
}

.ref-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}

.ref-link {
  font-size: 12px;
  color: var(--el-color-primary);
}

.triage-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 14px;
  padding: 12px;
  border: 1px dashed var(--border-color);
  border-radius: 10px;
  background: rgba(102, 126, 234, 0.04);
}

.triage-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.triage-select {
  max-width: 220px;
}

.triage-note {
  width: 100%;
}

/* Skill 信息卡片 */
.skill-info-card {
  margin-bottom: 24px;
}

.scan-provenance-card {
  margin-bottom: 24px;
}

.scan-provenance-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.scan-provenance-title {
  font-weight: 600;
  font-size: 16px;
}

.scan-pro-hint {
  margin: 0 0 14px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.scan-desc {
  margin-top: 4px;
}

.license-tag {
  margin: 2px 6px 2px 0;
}

.text-muted {
  color: var(--text-muted, #909399);
  font-size: 13px;
}

.mono-inline {
  font-family: ui-monospace, Consolas, monospace;
  font-size: 13px;
}

.innovation-card {
  margin-bottom: 24px;
}

.innovation-signals {
  margin-top: 16px;
}

.innovation-signals-title {
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 14px;
}

.innovation-alert {
  margin-bottom: 10px;
}

.innovation-interpret {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 风险分布和安全评分卡片 */
.chart-section {
  margin-bottom: 24px;
}

/* 安全评分模块 */
.safety-score-section {
  margin-bottom: 24px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 18px;
}

.score-alerts-block {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.score-alert-item {
  border-radius: 10px;
}

.gauge-container {
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-details {
  padding: 12px 0;
}

.composite-score {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.score-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 8px;
  font-weight: 500;
}

.score-value-wrapper {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.score-number {
  font-size: 56px;
  font-weight: 700;
  line-height: 1;
  text-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.score-total {
  font-size: 20px;
  color: var(--text-muted);
  font-weight: 500;
}

.score-formula {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.score-description {
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.55;
}

.dimensions-section {
  margin-top: 24px;
}

.dimensions-title {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 16px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dimension-item {
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px dashed var(--border-color);
}

.dimension-item:last-of-type {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

.dimension-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  margin-bottom: 8px;
}

.dimension-title-block {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.dimension-name {
  font-size: 15px;
  color: var(--text-primary);
  font-weight: 600;
}

.dimension-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.dimension-weight {
  font-weight: 500;
}

.dimension-score-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 6px;
}

.dimension-score {
  font-size: 22px;
  font-weight: 700;
}

.dimension-score-suffix {
  font-size: 13px;
  color: var(--text-muted);
}

.dimension-suggestion {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.55;
}

.dimension-note {
  margin-top: 28px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.note-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.note-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  font-size: 13px;
}

.note-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

.note-color {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 详细风险列表 */
.findings-section {
  margin-top: 24px;
}

.findings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-weight: 600;
  font-size: 18px;
  flex-wrap: wrap;
}

.findings-header-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.findings-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.finding-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding-right: 8px;
}

.bookmark-btn {
  flex-shrink: 0;
}

.finding-title-text {
  font-weight: 600;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bookmark-empty-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--text-secondary);
}

.finding-count {
  background: var(--gradient-primary);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

/* 折叠面板标题 */
:deep(.el-collapse-item__header) {
  padding: 18px 24px;
  background: white;
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid var(--border-color);
  transition: all 0.3s;
}

:deep(.el-collapse-item__header:hover) {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.04) 0%, transparent 100%);
  border-color: rgba(102, 126, 234, 0.3);
}

:deep(.el-collapse-item__header.is-active) {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(102, 126, 234, 0.02) 100%);
  border-color: var(--primary-light);
}

:deep(.el-collapse-item__wrap) {
  background: white;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-top: none;
}

:deep(.el-collapse-item__content) {
  padding: 20px 24px;
  background: #fafbfc;
}

.finding-description {
  margin: 0 0 16px 0;
  line-height: 1.7;
  color: var(--text-primary);
  font-size: 14px;
}

.evidence-section {
  margin-top: 16px;
}

.evidence-title {
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 14px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.evidence-content {
  background: #fff;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.evidence-fields {
  padding: 12px 16px;
}

.evidence-field {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border-color);
  font-size: 13px;
  line-height: 1.5;
}

.evidence-field:last-child {
  border-bottom: none;
}

.field-label {
  flex-shrink: 0;
  width: 120px;
  color: var(--text-secondary);
  font-weight: 500;
}

.field-value {
  flex: 1;
  color: var(--text-primary);
  word-break: break-all;
  white-space: pre-wrap;
  font-family: var(--font-mono, monospace);
}

.recommendation-box {
  margin-top: 16px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.08) 0%, rgba(66, 153, 225, 0.04) 100%);
  border-left: 4px solid var(--primary-color);
  border-radius: 8px;
}

.recommendation-title {
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 6px;
}

.recommendation-text {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 768px) {
  .overview-cards {
    margin-bottom: 16px;
  }
  
  .overview-item {
    flex-direction: column;
    text-align: center;
  }
  
  .overview-icon {
    width: 48px;
    height: 48px;
  }
  
  .score-value-wrapper {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .score-number {
    font-size: 40px;
  }
  
  .note-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}

/* 证据美化样式 */
.evidence-content {
  margin-top: 12px;
}

.evidence-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.8) 100%);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.evidence-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s;
}

.evidence-field:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.field-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-value {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  word-break: break-word;
}

/* 修复建议美化 */
.recommendation-box {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.08) 0%, rgba(56, 249, 215, 0.08) 100%);
  border-radius: 10px;
  border: 1px solid rgba(67, 233, 123, 0.2);
}

.recommendation-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--risk-low);
  margin-bottom: 12px;
  font-size: 15px;
}

.recommendation-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-primary);
  white-space: pre-wrap;
}

/* 每条发现的安全建议（独立卡片式 Alert） */
.finding-security-advice-wrap {
  margin-top: 18px;
}

.finding-advice-alert {
  border-radius: 10px;
  align-items: flex-start;
}

.finding-advice-title-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-weight: 600;
}

.finding-advice-guide-icon {
  font-size: 18px;
  color: var(--el-color-primary);
}

.advice-source-tag {
  margin-left: 2px;
}

.finding-advice-body {
  margin: 4px 0 0;
  line-height: 1.65;
  font-size: 14px;
  color: var(--text-primary);
}

.card-title-with-icon {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.card-head-icon {
  font-size: 22px;
  color: var(--el-color-primary);
}

.score-header .score-header-title {
  font-size: 16px;
}

.findings-section-title {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.findings-head-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.note-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.note-title-icon {
  font-size: 18px;
  color: var(--el-color-warning);
}

:deep(.finding-advice-alert .el-alert__title) {
  width: 100%;
}

:deep(.finding-advice-alert .el-alert__content) {
  padding-right: 8px;
}
</style>