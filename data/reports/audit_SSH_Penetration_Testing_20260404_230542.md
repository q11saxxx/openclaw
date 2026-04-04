# OpenClaw Skill 供应链安全审计报告

## 1. 审计概述
- **Skill 名称**: SSH Penetration Testing
- **审计结果**: **CRITICAL**
- **处置建议**: `REJECT`
- **置信度**: 96.0%
- **扫描路径**: `F:\skill test`

---

## 2. 风险汇总
> 检测到 1 项严重安全威胁，已直接拦截。

| 严重程度 | 发现数量 |
| :--- | :--- |
| Critical | 1 |
| High | 3 |
| Medium | 1 |
| Low | 0 |

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
### 5. [MEDIUM] semantic_analysis
- **来源智能体**: `semantic_audit`
- **描述**: 该 Skill 是一个公开的攻击技术手册，虽无直接的提示注入、窃密或越权代码执行，但其核心内容构成了诱导执行高危攻击的隐蔽社会工程，并隐含了与其宣称的“安全评估”目的不符的攻击性越权行为。
- **证据详情**: 发现 2 处匹配：
  - `[Semantic:隐蔽社会工程]` : `完整的 Skill 文档，特别是在 `# SSH Enumeration`、`# SSH Configuration Auditing`、`# Credential Attacks`、`# Vulnerability Exploitation`、`# SSH Tunneling and Port Forwarding`、`# Post-Exploitation` 等章节中，提供了详细的、可直接执行...`
  - `[Semantic:越权行为]` : `Skill 功能描述涉及 `brute force SSH credentials`、`exploit SSH vulnerabilities`、`perform SSH tunneling`、`post-exploitation activities`。在具体命令中，例如：`hydra -l admin -P /usr/share/wordlists/rockyou.txt ssh://192....`

---


> 报告生成时间: 2026-04-04T23:05:42.534022 | 审计引擎: OpenClaw-Risk-Platform-V1
