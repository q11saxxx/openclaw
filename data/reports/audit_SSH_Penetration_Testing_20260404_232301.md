# OpenClaw Skill 供应链安全审计报告

## 1. 审计概述
- **Skill 名称**: SSH Penetration Testing
- **审计结果**: **CRITICAL**
- **处置建议**: `REJECT`
- **置信度**: 93.0%
- **扫描路径**: `F:\skill test`

---

## 1.5 供应链溯源摘要 (Supply Chain Provenance) 🛡️
- **开发者身份**: `⚠️ 匿名 (Anonymous)`
- **许可证声明**: `❌ 未声明`
- **版本合规性**: `1.0.0`
- **信誉评估**: 🔴 风险 - 来源不可信

---

## 2. 风险汇总
> 检测到 1 项严重安全威胁，已直接拦截。

| 严重程度 | 发现数量 |
| :--- | :--- |
| Critical | 1 |
| High | 3 |
| Medium | 1 |
| Low | 1 |

---

## 3. 详细风险列表
### 1. [HIGH] static script analysis
- **来源智能体**: `static_security`
- **描述**: 静态扫描发现script_analysis异常
- **证据详情**: 发现 2 处匹配：
  - `[F:\skill test\semgrep\app.py:15]` : `os.system("echo " + username)  # 危险！`
  - `[F:\skill test\semgrep\app.py:15]` : `os.system("echo " + username)  # 危险！`

---
### 2. [CRITICAL] file permission and sensitive path analysis
- **来源智能体**: `static_security`
- **描述**: 静态扫描发现permission_analysis异常
- **证据详情**: 发现 17 处匹配：
  - `[F:\skill test\SKILL.md:188]` : `/root/.ssh/`
  - `[F:\skill test\SKILL.md:188]` : `/root/.ssh/`
  - `[F:\skill test\SKILL.md:319]` : `cat /etc/passwd | grep -v nologin`
  - `[F:\skill test\SKILL.md:316]` : `cat /etc/ssh/sshd_config`
  - `[F:\skill test\SKILL.md:183]` : `~/.ssh/id_rsa`
  - `[F:\skill test\SKILL.md:184]` : `~/.ssh/id_dsa`
  - `[F:\skill test\SKILL.md:185]` : `~/.ssh/id_ecdsa`
  - `[F:\skill test\SKILL.md:186]` : `~/.ssh/id_ed25519`
  - `[F:\skill test\SKILL.md:188]` : `/root/.ssh/`
  - `[F:\skill test\SKILL.md:189]` : `/home/*/.ssh/`
  - `[F:\skill test\SKILL.md:192]` : `curl -s http://target.com/.ssh/id_rsa`
  - `[F:\skill test\SKILL.md:308]` : `ls -la ~/.ssh/`
  - `[F:\skill test\SKILL.md:309]` : `cat ~/.ssh/known_hosts`
  - `[F:\skill test\SKILL.md:310]` : `cat ~/.ssh/authorized_keys`
  - `[F:\skill test\SKILL.md:313]` : `echo "ssh-rsa AAAAB3..." >> ~/.ssh/authorized_keys`

---
### 3. [HIGH] 检测敏感路径访问
- **来源智能体**: `static_security`
- **描述**: 静态扫描发现rule_engine异常
- **证据详情**: 发现 1 处匹配：
  - `F:\skill test\SKILL.md:319:cat /etc/passwd | grep -v nologin`

---
### 4. [HIGH] static_pattern_match
- **来源智能体**: `semantic_audit`
- **描述**: 匹配到 1 处已知的恶意提示词模式
- **证据详情**: 发现 1 处匹配：
  - `[SKILL.md:Offset: 4445]` : `bypass`

---
### 5. [MEDIUM] anonymous_publication
- **来源智能体**: `provenance`
- **描述**: 该 Skill 未声明有效作者身份，存在匿名投毒和不可追溯风险。
- **证据详情**: 
  - **type**: anonymous_publication
  - **level**: medium
  - **message**: 该 Skill 未声明有效作者身份，存在匿名投毒和不可追溯风险。

---
### 6. [LOW] missing_license
- **来源智能体**: `provenance`
- **描述**: 未检测到开源许可证声明，可能存在合规性隐患。
- **证据详情**: 
  - **type**: missing_license
  - **level**: low
  - **message**: 未检测到开源许可证声明，可能存在合规性隐患。

---


> 报告生成时间: 2026-04-04T23:23:01.351136 | 审计引擎: OpenClaw-Risk-Platform-V1
