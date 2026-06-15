"""代码预处理器 - 处理超过1000行代码的优化分析。

规则描述：
- 负责对超过1000行的代码文件进行预处理和提炼
- 提取关键代码部分（导入、函数定义、类定义、异常处理、危险操作等）
- 生成优化版本的代码供审计使用
- 保留原始代码位置信息用于追踪
"""
import logging
import os
import re
import shutil
import tarfile
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class CodeLocation:
    """代码位置信息"""
    file_path: str
    line_number: int
    line_content: str
    context_type: str  # 'import', 'class', 'function', 'exception', 'dangerous', 'config'


class CodePreprocessor:
    """代码预处理器。
    
    对超过1000行的代码文件进行深度分析和提炼，提取出关键的审计部分，
    同时保留原始代码位置信息以便追踪。
    """
    
    # 支持的脚本扩展名
    SCRIPT_EXTENSIONS = {'.sh', '.py', '.rb', '.pl', '.js', '.bash', '.ksh', '.zsh', '.php', '.ts'}

    def __init__(self):
        self.llm_service: Optional[LLMService] = None
    
    # 关键代码特征的正则表达式
    PATTERNS = {
        # Python
        'py_import': r'^(?:from|import)\s+[\w\.]+(?: import .*)?$',
        'py_class': r'^\s*class\s+(\w+)(?:\(.*?\))?:',
        'py_function': r'^\s*(?:async\s+)?def\s+(\w+)\s*\(',
        'py_exception': r'(?:raise|except|try|finally)\s',
        'py_dunder': r'^\s*def\s+__\w+__\s*\(',
        'py_decorator': r'^\s*@\w+',
        
        # Bash
        'sh_function': r'^\s*(\w+)\s*\(\)\s*\{',
        'sh_source': r'^\s*(?:source|\.)\s+',
        'sh_trap': r'^\s*trap\s+',
        'sh_shebang': r'^#!',
        
        # JavaScript/TypeScript
        'js_import': r'^\s*(?:import|export|require)\s',
        'js_function': r'^\s*(?:async\s+)?(?:export\s+)?(?:function|\w+\s*=\s*(?:async\s+)?\()',
        'js_class': r'^\s*(?:export\s+)?class\s+\w+',
        'js_try': r'^\s*(?:try|catch|finally)',
    }
    
    # 危险操作关键词
    DANGEROUS_KEYWORDS = {
        'eval', 'exec', 'system', 'popen', 'subprocess',
        'os.system', 'os.remove', 'os.chmod', 'os.chown',
        'rm', 'chmod', 'chown', 'dd', 'curl', 'wget',
        'nc', 'bash', 'sh', 'shell', 'spawn', 'exec',
        'iptables', 'firewall', 'cron', 'sudo', 'root',
        '__import__', 'globals', 'locals', 'vars',
    }
    
    # 配置相关关键词
    CONFIG_KEYWORDS = {
        'config', 'settings', 'options', 'params', 'environment',
        'api_key', 'password', 'token', 'secret', 'credential',
        'url', 'endpoint', 'host', 'port', 'database',
        'aws', 'azure', 'gcp', 'github', 'gitlab',
    }
    
    # 行数阈值（降低到50行，让更多文件可以触发预处理功能）
    LINE_THRESHOLD = 50
    
    
    # 提取比例（保留重要代码行数 / 原始行数）
    EXTRACTION_RATIO = 0.3  # 保留约30%的关键代码
    
    def preprocess(self, skill_path: str, use_ai: bool = False) -> Dict[str, Any]:
        """预处理skill中的所有代码文件。
        
        Args:
            skill_path: skill目录路径
            use_ai: 是否启用 AI 预处理摘要
            
        Returns:
            包含预处理结果的字典，格式为：
            {
                "files_analyzed": int,        # 分析的文件数
                "files_preprocessed": int,   # 需要预处理的文件数
                "preprocessed_files": [      # 预处理详情列表
                    {
                        "file_path": str,
                        "original_lines": int,
                        "extracted_lines": int,
                        "extraction_ratio": float,
                        "key_locations": list,
                        "preprocessed_content": str,
                        "ai_summary": str
                    }
                ],
                "statistics": {
                    "total_original_lines": int,
                    "total_extracted_lines": int,
                    "average_compression_ratio": float
                },
                "ai_preprocessing_enabled": bool
            }
        """
        logger.debug(f"Starting code preprocessing for path: {skill_path} use_ai={use_ai}")
        
        if use_ai:
            self.llm_service = self._get_llm_service()
        
        result = {
            "files_analyzed": 0,
            "files_preprocessed": 0,
            "preprocessed_files": [],
            "statistics": {
                "total_original_lines": 0,
                "total_extracted_lines": 0,
                "average_compression_ratio": 0.0
            }
        }
        
        try:
            # 先判断是否为压缩包，如果是则临时解压后扫描
            with self._extract_archive_if_needed(skill_path) as scan_path:
                # 查找所有代码文件
                code_files = self._find_code_files(scan_path)
                result["files_analyzed"] = len(code_files)
                
                if not code_files:
                    logger.debug(f"No code files found in {scan_path}")
                    return result
                
                # 逐个处理需要预处理的文件
                for file_path in code_files:
                    try:
                        content = self._read_file_safe(file_path)
                        if not content:
                            continue
                        
                        lines = content.split('\n')
                        
                        # 只对超过阈值行数的文件进行预处理
                        if len(lines) > self.LINE_THRESHOLD:
                            preprocessed = self._preprocess_file(file_path, content, lines)
                            result["preprocessed_files"].append(preprocessed)
                            result["files_preprocessed"] += 1
                            
                            # 更新统计信息
                            result["statistics"]["total_original_lines"] += preprocessed["original_lines"]
                            result["statistics"]["total_extracted_lines"] += preprocessed["extracted_lines"]
                            
                            logger.info(
                                f"Preprocessed {file_path}: "
                                f"{preprocessed['original_lines']} -> {preprocessed['extracted_lines']} lines "
                                f"({preprocessed['extraction_ratio']:.1%})"
                            )
                    except Exception as e:
                        logger.warning(f"Error preprocessing file {file_path}: {str(e)}")
                        continue
                
                # 计算平均压缩比
                if result["preprocessed_files"]:
                    total_original = result["statistics"]["total_original_lines"]
                    total_extracted = result["statistics"]["total_extracted_lines"]
                    if total_original > 0:
                        result["statistics"]["average_compression_ratio"] = total_extracted / total_original

                if use_ai and result["preprocessed_files"] and self.llm_service:
                    self._apply_ai_summaries(result["preprocessed_files"])
                    result["ai_preprocessing_enabled"] = True
                else:
                    result["ai_preprocessing_enabled"] = False
            
            return result
        
        except Exception as e:
            logger.error(f"Error during code preprocessing: {str(e)}", exc_info=True)
            return result
    
    def _find_code_files(self, path: str) -> List[str]:
        """递归查找目录中的所有代码文件。
        
        Args:
            path: 目录路径
            
        Returns:
            代码文件路径列表
        """
        code_files = []
        
        try:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
                return code_files
            
            if os.path.isfile(path):
                if self._is_code_file(path):
                    code_files.append(path)
            else:
                for root, dirs, files in os.walk(path):
                    # 跳过隐藏目录和常见的非代码目录
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                        '__pycache__', 'node_modules', 'dist', 'build', '.git', '.venv'
                    ]]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._is_code_file(file_path):
                            code_files.append(file_path)
        
        except Exception as e:
            logger.warning(f"Error finding code files: {str(e)}")
        
        return code_files
    
    @contextmanager
    def _extract_archive_if_needed(self, path: str):
        """如果 path 是压缩包，则临时解压后返回解压目录，否则直接返回原路径。"""
        supported_archives = {'.zip', '.tar', '.gz'}
        ext = Path(path).suffix.lower()
        if ext not in supported_archives or not os.path.isfile(path):
            yield path
            return

        temp_dir = tempfile.mkdtemp(prefix='code_preprocessor_')
        try:
            if ext == '.zip':
                with zipfile.ZipFile(path, 'r') as zf:
                    zf.extractall(temp_dir)
            elif ext in {'.tar', '.gz'}:
                with tarfile.open(path, 'r:*') as tf:
                    tf.extractall(temp_dir)
            else:
                yield path
                return
            yield temp_dir
        except Exception as e:
            logger.warning(f"Failed to extract archive {path}: {e}")
            yield path
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

    def _is_code_file(self, path: str) -> bool:
        """检查文件是否为代码文件。
        
        Args:
            path: 文件路径
            
        Returns:
            True 如果是代码文件，False 否则
        """
        ext = Path(path).suffix.lower()
        if ext in self.SCRIPT_EXTENSIONS:
            return True
        
        # 检查 shebang
        try:
            with open(path, 'rb') as f:
                first_line = f.readline().decode('utf-8', errors='ignore')
                if first_line.startswith('#!'):
                    return True
        except Exception:
            pass
        
        return False
    
    def _read_file_safe(self, path: str) -> Optional[str]:
        """安全地读取文件内容。
        
        Args:
            path: 文件路径
            
        Returns:
            文件内容，或 None 如果读取失败
        """
        try:
            # 限制文件大小（10MB）
            max_size = 10 * 1024 * 1024
            if os.path.getsize(path) > max_size:
                logger.warning(f"File too large, skipping: {path}")
                return None
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.debug(f"Error reading file {path}: {str(e)}")
            return None
    
    def _preprocess_file(self, file_path: str, content: str, lines: List[str]) -> Dict[str, Any]:
        """预处理单个文件。
        
        Args:
            file_path: 文件路径
            content: 文件内容
            lines: 文件行列表
            
        Returns:
            预处理结果字典
        """
        logger.debug(f"Preprocessing file: {file_path}")
        
        # 确定文件类型
        file_ext = Path(file_path).suffix.lower()
        
        # 提取关键代码位置
        key_locations = self._extract_key_locations(file_path, lines, file_ext)
        
        # 生成提炼后的代码
        extracted_lines = self._build_extracted_content(lines, key_locations, file_ext)
        
        # 计算压缩比
        original_lines = len(lines)
        extracted_count = len(extracted_lines)
        extraction_ratio = extracted_count / original_lines if original_lines > 0 else 0
        
        # 构建预处理内容（保留行号信息）
        preprocessed_content = self._build_preprocessed_content(extracted_lines)
        
        return {
            "file_path": file_path,
            "original_lines": original_lines,
            "extracted_lines": extracted_count,
            "extraction_ratio": extraction_ratio,
            "key_locations": [
                {
                    "line_number": loc.line_number,
                    "context_type": loc.context_type,
                    "content": loc.line_content[:100]  # 截断长行
                }
                for loc in key_locations
            ],
            "preprocessed_content": preprocessed_content
        }
    
    def _extract_key_locations(self, file_path: str, lines: List[str], file_ext: str) -> List[CodeLocation]:
        """提取文件中的关键代码位置。
        
        Args:
            file_path: 文件路径
            lines: 文件行列表
            file_ext: 文件扩展名
            
        Returns:
            关键代码位置列表
        """
        key_locations: List[CodeLocation] = []
        
        # 选择合适的模式集
        patterns = self._get_patterns_for_language(file_ext)
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 跳过空行和注释
            if not stripped or self._is_comment_line(stripped, file_ext):
                continue
            
            # 检查各种关键代码特征
            context_type = None
            
            # 检查导入
            if any(re.search(patterns.get(k, ''), line) for k in patterns if 'import' in k):
                context_type = 'import'
            
            # 检查类定义
            elif any(re.search(patterns.get(k, ''), line) for k in patterns if 'class' in k):
                context_type = 'class'
            
            # 检查函数定义
            elif any(re.search(patterns.get(k, ''), line) for k in patterns if 'function' in k or 'def' in k):
                context_type = 'function'
            
            # 检查异常处理
            elif any(re.search(patterns.get(k, ''), line) for k in patterns if 'exception' in k or 'try' in k):
                context_type = 'exception'
            
            # 检查危险操作
            elif self._contains_dangerous_keyword(line):
                context_type = 'dangerous'
            
            # 检查配置
            elif self._contains_config_keyword(line):
                context_type = 'config'
            
            if context_type:
                key_locations.append(CodeLocation(
                    file_path=file_path,
                    line_number=line_num,
                    line_content=line,
                    context_type=context_type
                ))
        
        # 按关键度排序并限制数量
        key_locations = self._prioritize_locations(key_locations, len(lines))
        
        return key_locations
    
    def _get_patterns_for_language(self, file_ext: str) -> Dict[str, str]:
        """根据文件扩展名获取合适的正则表达式。
        
        Args:
            file_ext: 文件扩展名
            
        Returns:
            该语言的正则表达式字典
        """
        if file_ext in ['.py']:
            return {k: v for k, v in self.PATTERNS.items() if k.startswith('py_')}
        elif file_ext in ['.sh', '.bash', '.ksh', '.zsh']:
            return {k: v for k, v in self.PATTERNS.items() if k.startswith('sh_')}
        elif file_ext in ['.js', '.ts']:
            return {k: v for k, v in self.PATTERNS.items() if k.startswith('js_')}
        else:
            return self.PATTERNS
    
    def _is_comment_line(self, line: str, file_ext: str) -> bool:
        """检查行是否为注释。
        
        Args:
            line: 代码行
            file_ext: 文件扩展名
            
        Returns:
            True 如果是注释，False 否则
        """
        if file_ext in ['.py', '.sh', '.bash', '.ksh', '.zsh']:
            return line.startswith('#')
        elif file_ext in ['.js', '.ts']:
            return line.startswith('//') or line.startswith('/*')
        return False
    
    def _contains_dangerous_keyword(self, line: str) -> bool:
        """检查行是否包含危险关键词。
        
        Args:
            line: 代码行
            
        Returns:
            True 如果包含危险关键词，False 否则
        """
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in self.DANGEROUS_KEYWORDS)
    
    def _contains_config_keyword(self, line: str) -> bool:
        """检查行是否包含配置关键词。
        
        Args:
            line: 代码行
            
        Returns:
            True 如果包含配置关键词，False 否则
        """
        line_lower = line.lower()
        return any(keyword in line_lower for keyword in self.CONFIG_KEYWORDS)
    
    def _prioritize_locations(self, locations: List[CodeLocation], total_lines: int) -> List[CodeLocation]:
        """根据关键度排序并限制数量。
        
        修正点：
        1. 修复了原代码中 total_lines * ratio / 100 导致的计算结果过小（300行代码算出来只能留0.9行）的问题。
        2. 调整了优先级：将 dangerous（危险操作）和 exception（异常处理）置于最高优先级。
        3. 增加逻辑：如果识别到的关键点总数未达到上限，则全部保留，不进行截断。
        """
        # 为不同类型分配优先级：安全相关 > 结构相关
        priority_map = {
            'dangerous': 10,   # 危险操作最重要
            'exception': 9,    # 报错处理往往隐藏逻辑漏洞
            'config': 8,       # 配置信息
            'import': 7,       # 外部依赖
            'class': 6,        # 类定义
            'function': 5,     # 函数定义
        }
        
        # 计算允许保留的最大关键位置数量
        # 去掉之前的 / 100。例如：300行 * 0.3 = 90个位置
        limit = int(total_lines * self.EXTRACTION_RATIO)
        max_count = max(20, limit) # 确保即使是很小的文件也能留出至少20个关键点
        
        # 如果找出来的关键位置本来就少于上限，直接按行号排序返回，不做截断
        if len(locations) <= max_count:
            return sorted(locations, key=lambda x: x.line_number)
            
        # 如果超出上限，按优先级排序并截取
        sorted_locations = sorted(
            locations,
            key=lambda x: priority_map.get(x.context_type, 0),
            reverse=True
        )
        
        # 截取前 max_count 个最重要的位置
        top_locations = sorted_locations[:max_count]
        
        # 最后按行号重新排序，确保提取代码时是顺序的
        return sorted(top_locations, key=lambda x: x.line_number)

    def _build_extracted_content(self, lines: List[str], key_locations: List[CodeLocation], file_ext: str) -> List[Tuple[int, str]]:
        """构建提炼后的内容。
        
        优化点：
        1. 增加了“向上扫描”逻辑：安全审计通常需要看危险函数前面的变量定义。
        2. 动态调整窗口：对于关键行，保留前4行（看来源）和后2行（看影响）。
        3. 自动合并：如果两个关键点距离很近，它们之间的代码会被连贯保留。
        """
        extracted = []
        key_line_numbers = {loc.line_number for loc in key_locations}
        
        # 定义上下文窗口
        # 对于安全审计，向上看（Before）通常比向下看（After）更重要（寻找变量来源）
        BEFORE_WINDOW = 4 
        AFTER_WINDOW = 2

        for line_num in sorted(key_line_numbers):
            # line_num 是从 1 开始的，lines 索引从 0 开始
            target_idx = line_num - 1
            
            # 计算这一块代码的起始和结束索引
            start_idx = max(0, target_idx - BEFORE_WINDOW)
            end_idx = min(len(lines), target_idx + AFTER_WINDOW + 1)
            
            for i in range(start_idx, end_idx):
                # 存储元组 (行号, 内容)
                extracted.append((i + 1, lines[i]))
        
        # 去重：因为不同关键点的上下文可能会重叠
        seen_line_numbers = set()
        unique_extracted = []
        
        for line_num, content in extracted:
            if line_num not in seen_line_numbers:
                seen_line_numbers.add(line_num)
                unique_extracted.append((line_num, content))
        
        # 按行号排序返回
        return sorted(unique_extracted, key=lambda x: x[0])
    
    def _build_preprocessed_content(self, extracted_lines: List[Tuple[int, str]]) -> str:
        """构建预处理后的代码内容。
        
        Args:
            extracted_lines: 提炼后的代码行列表
            
        Returns:
            格式化的预处理代码字符串
        """
        lines = []
        last_line_num = 0
        
        for line_num, content in extracted_lines:
            # 如果行号跳跃较大，添加省略号
            if line_num - last_line_num > 2:
                lines.append(f"# ... (lines {last_line_num + 1} - {line_num - 1} omitted) ...")
            
            # 添加行号注释（保留原始位置信息）
            lines.append(f"# L{line_num}: {content}")
            last_line_num = line_num
        
        return '\n'.join(lines)

    def _get_llm_service(self) -> Optional[LLMService]:
        """延迟加载 LLM 服务，避免未配置时直接失败。"""
        try:
            service = LLMService()
            if service.available:
                return service
        except Exception as e:
            logger.warning(f"Failed to initialize LLM service for preprocessing: {e}")
        return None

    def _apply_ai_summaries(self, preprocessed_files: List[dict[str, Any]]) -> None:
        """为已预处理文件生成 AI 摘要和建议。"""
        for file_data in preprocessed_files:
            try:
                content = file_data.get("preprocessed_content", "")
                if not content:
                    file_data["ai_summary"] = "No preprocessed content available for AI analysis."
                    continue

                ai_result = self._generate_ai_insight(file_data["file_path"], content)
                file_data["ai_summary"] = ai_result.get("summary", "AI 预处理未生成摘要。")
                if "recommendation" in ai_result:
                    file_data["ai_recommendation"] = ai_result["recommendation"]
                if "suspicious" in ai_result:
                    file_data["ai_suspicious"] = ai_result["suspicious"]
            except Exception as e:
                logger.warning(f"AI preprocessing failed for {file_data.get('file_path')}: {e}")
                file_data["ai_summary"] = "AI 预处理失败，已回退为常规模式。"

    def _generate_ai_insight(self, file_path: str, content: str) -> dict[str, Any]:
        """使用 LLM 对已提炼内容生成 AI 摘要。"""
        if not self.llm_service:
            return {"summary": "LLM 未配置或不可用，未生成 AI 摘要。"}

        prompt = f"""
你是一个安全审核助手，正在对以下已提炼的代码片段做审查：
文件路径: {file_path}

请输出 JSON：
{{
  "summary": "一句话总结该代码片段的主要作用和风险",
  "suspicious": true/false,
  "recommendation": "如果有潜在风险，给出简要修复建议，否则写 'No action needed'."
}}

代码片段:
---
{content[:12000]}
---
"""
        response = self.llm_service.call_model(self.llm_service.fast_model, prompt)
        parsed = self.llm_service.parse_json(response)
        if not parsed:
            return {"summary": "LLM 未返回有效 JSON，无法生成摘要。"}
        return parsed
