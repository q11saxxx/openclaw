import os
import re

"""提示注入检测器。

规则描述：
- 识别 `忽略之前指令`、越权访问、诱导泄露秘密等文本模式。
- 当前阶段可先做规则+关键词检测，后续再接语义增强。
"""



# 风险特征库：涵盖提示注入、数据泄露、越权访问与社工攻击
INJECTION_PATTERNS = [
    # --- 1. 指令劫持与绕过 (Instruction Hijacking & Jailbreak) ---
    r"ignore (?:all|previous) instructions",    # 经典的“忽略之前所有指令”注入攻击
    r"you are now",                             # 强制角色切换（Persona Adoption）试图绕过安全限制
    r"act as",                                  # 诱导 Agent 扮演特定角色以执行非授权操作
    r"bypass",                                  # 明确提及“绕过”安全策略或过滤器
    r"do not follow",                           # 诱导 Agent 拒绝执行系统预设的防御指令
    r"override system",                         # 试图覆盖或重写系统级安全约束

    # --- 2. 提示词泄露 (Prompt Leaking) ---
    r"reveal (?:system|prompt)",                # 诱导 Agent 泄露底层的系统提示词（System Prompt）
    r"output (?:your|original) instructions",   # 要求 Agent 打印其初始化的保护指令

    # --- 3. 敏感数据窃取与外传 (Data Exfiltration) ---
    r"exfiltrate",                              # 明确的“数据外泄”术语
    r"send (?:sensitive|password|token|data) to http", # 试图通过 HTTP 请求将敏感凭证发送到外部服务器
    r"send sensitive information",              # 一般性的数据泄露意图描述
    r"send .* to .*http",                       # 捕获任何试图将内容发送到外部 URL 的行为（高灵敏度）

    # --- 4. 越权访问与文件系统探测 (Privilege Escalation & File Access) ---
    r"access unauthorized data",                # 明确的越权访问尝试
    r"read (?:the )?(?:\/etc\/|\/var\/|\.env|id_rsa)", # 探测 Linux 系统敏感文件（如 SSH 密钥、环境变量）
    r"access (?:root|system|hidden) files",     # 尝试访问系统级或隐藏的敏感文件
    r"list (?:directory|files) in",             # 非法的目录遍历与敏感路径扫描意图

    # --- 5. 社会工程学与身份冒充 (Social Engineering & Impersonation) ---
    r"phishing",                                # 网络钓鱼或凭据收割意图
    r"impersonate",                             # 冒充合法用户、管理员或系统服务进行欺骗
    r"ask the user for (?:password|token|key)", # 诱导 Agent 引导用户输入敏感信息

    # --- 6. 隐蔽性检测 (Evasion & Obfuscation) ---
    r"[A-Za-z0-9+/]{40,}=*",                    # 识别长段 Base64 编码字符串（常用于隐藏恶意攻击载荷）
]


def load_skill_text(skill_path: str) -> str:
    """
    自适应读取：如果是文件夹则遍历，如果是文件则直接读。
    """
    texts = []
    
    # 检查路径是否存在
    if not os.path.exists(skill_path):
        print(f"[Debug] 路径不存在: {skill_path}")
        return ""

    # 情况 A：如果传入的是单个文件
    if os.path.isfile(skill_path):
        if skill_path.lower().endswith((".md", ".txt")):
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"[Debug] 直接读取文件成功，长度: {len(content)}")
                    return content
            except Exception as e:
                print(f"[Debug] 读取文件失败: {e}")
                return ""

    # 情况 B：如果传入的是文件夹（原有逻辑）
    for root, _, files in os.walk(skill_path):
        for file in files:
            if file.lower().endswith((".md", ".txt")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        texts.append(f"--- File: {file} ---\n" + f.read())
                except:
                    pass

    combined_text = "\n\n".join(texts)
    print(f"[Debug] 文件夹遍历完成，总长度: {len(combined_text)}")
    return combined_text


class PromptInjectionDetector:
    def detect(self, skill_path: str):
        text = load_skill_text(skill_path)
        if not text: return None

        findings = []
        for pattern in INJECTION_PATTERNS:
            # 使用 re.finditer 获取完整的匹配对象，从而拿到上下文
            for match in re.finditer(pattern, text, re.IGNORECASE):
                findings.append({
                    "pattern": pattern,
                    "matched_text": match.group(),  # 拿到完整句子
                    "location": f"Offset: {match.start()}"
                })

        if not findings: return None

        return {
            "agent": "semantic_audit",
            "type": "static_pattern_match",
            "risk_level": "high",
            "confidence": 0.8,
            "evidence": findings[:5], # 只取前5个，防止 context 过载
            "reason": f"匹配到 {len(findings)} 处已知的恶意提示词模式",
            "file": "SKILL.md"
        }
