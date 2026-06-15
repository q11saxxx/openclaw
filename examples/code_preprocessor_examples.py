"""
代码预处理功能使用示例
===========================

此示例展示如何在项目中使用新的代码预处理功能。
"""

from app.core.pipeline import AuditPipeline
from app.core.context import AuditContext
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 示例 1: 基础使用 - 运行完整审计流程（自动包含预处理）
# ============================================================================

def example_1_basic_audit():
    """最简单的使用方式 - 自动进行代码预处理。"""
    print("\n" + "="*70)
    print("示例 1: 基础审计（自动包含预处理）")
    print("="*70 + "\n")
    
    # 创建审计管道
    pipeline = AuditPipeline()
    
    # 运行审计（ParserAgent 会自动调用代码预处理）
    skill_path = "/path/to/your/skill"
    result = pipeline.run(skill_path)
    
    # 访问预处理结果
    preprocessing_info = result.get("preprocessed", {})
    
    print(f"✓ 审计完成")
    print(f"  预处理的文件数: {preprocessing_info.get('files_preprocessed', 0)}")
    print(f"  平均压缩比: {preprocessing_info.get('statistics', {}).get('average_compression_ratio', 0):.1%}")


# ============================================================================
# 示例 2: 分析预处理结果
# ============================================================================

def example_2_analyze_preprocessing_results():
    """分析预处理后的代码结构。"""
    print("\n" + "="*70)
    print("示例 2: 分析预处理结果")
    print("="*70 + "\n")
    
    pipeline = AuditPipeline()
    skill_path = "/path/to/your/skill"
    result = pipeline.run(skill_path)
    
    preprocessing_info = result["preprocessed"]
    
    # 遍历每个预处理的文件
    for file_info in preprocessing_info["preprocessed_files"]:
        file_path = file_info["file_path"]
        original_lines = file_info["original_lines"]
        extracted_lines = file_info["extracted_lines"]
        extraction_ratio = file_info["extraction_ratio"]
        
        print(f"\n📄 文件: {file_path}")
        print(f"   原始行数:   {original_lines:6d}")
        print(f"   提炼行数:   {extracted_lines:6d}")
        print(f"   压缩比:     {extraction_ratio:6.1%}")
        
        # 统计关键位置类型
        key_locations = file_info["key_locations"]
        location_types = {}
        for loc in key_locations:
            ctx_type = loc["context_type"]
            location_types[ctx_type] = location_types.get(ctx_type, 0) + 1
        
        print(f"   关键位置统计:")
        for ctx_type, count in sorted(location_types.items()):
            print(f"     - {ctx_type:12s}: {count:3d}")


# ============================================================================
# 示例 3: 在自定义 Agent 中使用预处理结果
# ============================================================================

def example_3_use_in_custom_agent():
    """演示如何在自定义 Agent 中利用预处理结果。"""
    print("\n" + "="*70)
    print("示例 3: 在自定义 Agent 中使用预处理结果")
    print("="*70 + "\n")
    
    from app.agents.base_agent import BaseAgent
    
    class OptimizedAnalyzer(BaseAgent):
        """优化的分析器 - 优先分析大文件的关键部分。"""
        name = "optimized_analyzer"
        
        def run(self, context: AuditContext) -> None:
            preprocessing = context.preprocessed
            
            if not preprocessing.get("preprocessed_files"):
                logger.info("没有需要预处理的文件，使用完整分析")
                return
            
            logger.info(f"发现 {preprocessing['files_preprocessed']} 个需要预处理的文件")
            
            # 对每个预处理的文件进行分析
            for file_info in preprocessing["preprocessed_files"]:
                file_path = file_info["file_path"]
                key_locations = file_info["key_locations"]
                
                # 关注危险代码
                dangerous_locations = [
                    loc for loc in key_locations
                    if loc["context_type"] == "dangerous"
                ]
                
                if dangerous_locations:
                    logger.warning(
                        f"⚠️ 在 {file_path} 中发现 {len(dangerous_locations)} 个危险操作"
                    )
                    for loc in dangerous_locations:
                        logger.warning(
                            f"   L{loc['line_number']}: {loc['content']}"
                        )
                
                # 也关注配置信息
                config_locations = [
                    loc for loc in key_locations
                    if loc["context_type"] == "config"
                ]
                
                if config_locations:
                    logger.info(
                        f"ℹ️ 在 {file_path} 中发现 {len(config_locations)} 个配置项"
                    )
    
    # 使用示例
    analyzer = OptimizedAnalyzer()
    context = AuditContext(skill_path="/path/to/skill")
    
    # 首先运行预处理
    pipeline = AuditPipeline()
    result = pipeline.run(context.skill_path)
    
    # 然后运行自定义分析器
    analyzer.run(context)


# ============================================================================
# 示例 4: 条件处理 - 根据文件大小采用不同策略
# ============================================================================

def example_4_conditional_processing():
    """根据预处理结果决定分析策略。"""
    print("\n" + "="*70)
    print("示例 4: 条件处理 - 根据预处理结果调整策略")
    print("="*70 + "\n")
    
    pipeline = AuditPipeline()
    skill_path = "/path/to/your/skill"
    result = pipeline.run(skill_path)
    
    preprocessing_info = result["preprocessed"]
    
    # 根据预处理结果制定策略
    if preprocessing_info["files_preprocessed"] == 0:
        print("✓ 所有文件都在可管理范围内，进行完整分析")
        strategy = "full_analysis"
    else:
        total_original = preprocessing_info["statistics"]["total_original_lines"]
        total_extracted = preprocessing_info["statistics"]["total_extracted_lines"]
        
        if total_original > 50000:
            print(f"⚠️ 大型代码库（{total_original:,} 行）")
            print(f"   优先分析关键部分（{total_extracted:,} 行）")
            strategy = "priority_analysis"
        else:
            print(f"ℹ️ 中等规模代码库（{total_original:,} 行）")
            print(f"   进行完整但优化的分析（{total_extracted:,} 行）")
            strategy = "optimized_analysis"
    
    print(f"\n采用策略: {strategy}")
    
    return strategy


# ============================================================================
# 示例 5: 生成增强的审计报告
# ============================================================================

def example_5_enhanced_report():
    """生成包含预处理信息的增强报告。"""
    print("\n" + "="*70)
    print("示例 5: 生成增强的审计报告")
    print("="*70 + "\n")
    
    pipeline = AuditPipeline()
    skill_path = "/path/to/your/skill"
    result = pipeline.run(skill_path)
    
    preprocessing_info = result["preprocessed"]
    
    # 构建报告数据
    report_data = {
        "审计基础信息": {
            "skill_path": result["skill_path"],
            "审计时间": result["start_time"],
        },
        "代码预处理统计": {
            "分析的文件数": preprocessing_info.get("files_analyzed", 0),
            "预处理的文件数": preprocessing_info.get("files_preprocessed", 0),
            "总原始行数": preprocessing_info.get("statistics", {}).get("total_original_lines", 0),
            "总提炼行数": preprocessing_info.get("statistics", {}).get("total_extracted_lines", 0),
            "平均压缩比": f"{preprocessing_info.get('statistics', {}).get('average_compression_ratio', 0):.1%}",
            "节省行数": (
                preprocessing_info.get("statistics", {}).get("total_original_lines", 0) -
                preprocessing_info.get("statistics", {}).get("total_extracted_lines", 0)
            ),
        },
        "预处理文件详情": [],
    }
    
    # 添加每个文件的详情
    for file_info in preprocessing_info.get("preprocessed_files", []):
        report_data["预处理文件详情"].append({
            "文件": file_info["file_path"],
            "原始行数": file_info["original_lines"],
            "提炼行数": file_info["extracted_lines"],
            "压缩比": f"{file_info['extraction_ratio']:.1%}",
            "关键位置数": len(file_info["key_locations"]),
            "位置类型": {
                loc["context_type"]: sum(
                    1 for l in file_info["key_locations"]
                    if l["context_type"] == loc["context_type"]
                )
                for loc in file_info["key_locations"]
            }
        })
    
    # 打印报告
    print("\n📊 审计报告\n")
    
    for section, data in report_data.items():
        print(f"\n【{section}】")
        if isinstance(data, dict):
            for key, value in data.items():
                if key != "预处理文件详情":
                    print(f"  {key:20s}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data, 1):
                print(f"\n  文件 {i}:")
                for key, value in item.items():
                    if key != "位置类型":
                        print(f"    {key:20s}: {value}")


# ============================================================================
# 示例 6: 性能对比
# ============================================================================

def example_6_performance_comparison():
    """演示预处理带来的性能提升。"""
    print("\n" + "="*70)
    print("示例 6: 性能对比")
    print("="*70 + "\n")
    
    import time
    
    pipeline = AuditPipeline()
    skill_path = "/path/to/your/skill"
    
    # 记录执行时间
    start_time = time.time()
    result = pipeline.run(skill_path)
    total_time = time.time() - start_time
    
    preprocessing_info = result["preprocessed"]
    
    # 计算预期的性能提升
    if preprocessing_info["files_preprocessed"] > 0:
        total_original = preprocessing_info["statistics"]["total_original_lines"]
        total_extracted = preprocessing_info["statistics"]["total_extracted_lines"]
        compression_ratio = 1 - (total_extracted / total_original)
        
        print(f"✓ 审计完成")
        print(f"\n📊 性能统计:")
        print(f"  总执行时间:     {total_time:.2f}s")
        print(f"  预处理文件数:   {preprocessing_info['files_preprocessed']}")
        print(f"  总代码行数:     {total_original:,}")
        print(f"  提炼代码行数:   {total_extracted:,}")
        print(f"  压缩比:         {compression_ratio:.1%}")
        print(f"\n💡 预期性能提升（针对后续分析）:")
        print(f"   最多可提升约 {compression_ratio:.0%}")
    else:
        print(f"✓ 审计完成")
        print(f"  总执行时间: {total_time:.2f}s")
        print(f"  （所有文件都在可管理范围内）")


# ============================================================================
# 示例 7: 回溯到原始代码
# ============================================================================

def example_7_trace_back_to_source():
    """演示如何从预处理结果回溯到原始代码。"""
    print("\n" + "="*70)
    print("示例 7: 回溯到原始代码位置")
    print("="*70 + "\n")
    
    pipeline = AuditPipeline()
    skill_path = "/path/to/your/skill"
    result = pipeline.run(skill_path)
    
    preprocessing_info = result["preprocessed"]
    
    print("危险代码位置追踪:\n")
    
    for file_info in preprocessing_info["preprocessed_files"]:
        dangerous_locs = [
            loc for loc in file_info["key_locations"]
            if loc["context_type"] == "dangerous"
        ]
        
        if dangerous_locs:
            print(f"\n📄 {file_info['file_path']}")
            for loc in dangerous_locs:
                print(f"   ⚠️ L{loc['line_number']:6d}: {loc['content']}")
            
            print(f"\n   💡 可以直接在编辑器中打开该文件，跳到上述行号进行详细检查")


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def main():
    """运行所有示例。"""
    print("\n" + "="*70)
    print("代码预处理功能 - 使用示例")
    print("="*70)
    
    # 注意: 这些示例需要真实的 skill 路径才能运行
    # 此处只展示代码结构和用法
    
    examples = [
        ("示例 1", example_1_basic_audit),
        ("示例 2", example_2_analyze_preprocessing_results),
        ("示例 4", example_4_conditional_processing),
        ("示例 5", example_5_enhanced_report),
        ("示例 6", example_6_performance_comparison),
        ("示例 7", example_7_trace_back_to_source),
    ]
    
    print("\n可用的示例:\n")
    for i, (name, func) in enumerate(examples, 1):
        print(f"  {i}. {name}: {func.__doc__.strip()}")
    
    print("\n💡 提示:")
    print("  - 修改 skill_path 为你的实际 skill 路径")
    print("  - 运行具体示例前，请确保 skill 包含超过1000行的代码文件")
    print("  - 查看 CODE_PREPROCESSOR_GUIDE.md 了解更多详情")


if __name__ == "__main__":
    main()
