"""审计统计分析服务。

提供审计历史数据的统计分析功能，支持趋势分析和对比。
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class AuditStatisticsService:
    """审计统计分析服务"""
    
    def __init__(self):
        self.reports_dir = Path("data/reports")
    
    def get_audit_trends(self, days: int = 30) -> Dict[str, Any]:
        """获取审计趋势数据
        
        Args:
            days: 统计天数，默认30天
            
        Returns:
            包含趋势数据的字典
        """
        try:
            reports = self._load_recent_reports(days)
            
            # 按日期分组统计
            daily_stats = {}
            severity_distribution = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
            
            for report in reports:
                date_str = report.get("created_at", "")[:10]
                if not date_str:
                    continue
                
                if date_str not in daily_stats:
                    daily_stats[date_str] = {
                        "date": date_str,
                        "total": 0,
                        "critical": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0
                    }
                
                risk_level = report.get("risk_level", "low").lower()
                daily_stats[date_str]["total"] += 1
                if risk_level in severity_distribution:
                    daily_stats[date_str][risk_level] += 1
                    severity_distribution[risk_level] += 1
            
            # 转换为列表并排序
            trend_data = sorted(daily_stats.values(), key=lambda x: x["date"])
            
            return {
                "trend_data": trend_data,
                "severity_distribution": severity_distribution,
                "total_audits": len(reports),
                "period_days": days
            }
        
        except Exception as e:
            logger.error(f"Error getting audit trends: {e}")
            return {
                "trend_data": [],
                "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "total_audits": 0,
                "period_days": days
            }
    
    def get_skill_comparison(self, skill_name: str) -> Dict[str, Any]:
        """获取同一Skill的历史审计对比数据
        
        Args:
            skill_name: Skill名称
            
        Returns:
            包含对比数据的字典
        """
        try:
            reports = self._load_reports_by_skill(skill_name)
            
            if not reports:
                return {
                    "skill_name": skill_name,
                    "versions": [],
                    "message": "未找到该Skill的审计记录"
                }
            
            # 按时间排序
            reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            versions = []
            for report in reports:
                version_info = {
                    "audit_id": report.get("id", ""),
                    "created_at": report.get("created_at", ""),
                    "risk_level": report.get("risk_level", "unknown"),
                    "confidence": report.get("confidence", 0),
                    "finding_count": report.get("finding_count", 0),
                    "version": report.get("skill_version", "unknown")
                }
                versions.append(version_info)
            
            # 计算趋势
            trend = self._calculate_trend(versions)
            
            return {
                "skill_name": skill_name,
                "versions": versions,
                "trend": trend,
                "total_audits": len(versions)
            }
        
        except Exception as e:
            logger.error(f"Error getting skill comparison: {e}")
            return {
                "skill_name": skill_name,
                "versions": [],
                "trend": "unknown",
                "message": f"获取对比数据失败: {str(e)}"
            }
    
    def get_insights(self) -> Dict[str, Any]:
        """生成智能洞察
        
        Returns:
            包含洞察信息的字典
        """
        try:
            # 获取最近7天和30天的数据
            recent_7days = self._load_recent_reports(7)
            recent_30days = self._load_recent_reports(30)
            
            insights = []
            
            # 洞察1: 审计频率
            if len(recent_7days) > 5:
                insights.append({
                    "type": "info",
                    "title": "审计活跃",
                    "message": f"过去7天进行了 {len(recent_7days)} 次审计，系统使用频繁",
                    "icon": "TrendCharts"
                })
            
            # 洞察2: 高风险比例
            high_risk_count = sum(1 for r in recent_30days if r.get("risk_level", "").lower() in ["high", "critical"])
            if recent_30days and high_risk_count / len(recent_30days) > 0.3:
                insights.append({
                    "type": "warning",
                    "title": "高风险告警",
                    "message": f"过去30天 {high_risk_count}/{len(recent_30days)} 个Skill存在高风险，建议加强审查",
                    "icon": "Warning"
                })
            
            # 洞察3: 改进趋势
            if len(recent_7days) >= 2 and len(recent_30days) >= 2:
                recent_high = sum(1 for r in recent_7days if r.get("risk_level", "").lower() in ["high", "critical"])
                previous_high = sum(1 for r in recent_30days[:-7] if r.get("risk_level", "").lower() in ["high", "critical"])
                
                if recent_high < previous_high:
                    insights.append({
                        "type": "success",
                        "title": "安全状况改善",
                        "message": "近期高风险Skill数量下降，安全状况正在改善",
                        "icon": "SuccessFilled"
                    })
            
            # 如果没有洞察，提供默认信息
            if not insights:
                insights.append({
                    "type": "info",
                    "title": "系统正常运行",
                    "message": "审计系统运行正常，持续监控中",
                    "icon": "InfoFilled"
                })
            
            return {
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "insights": [],
                "generated_at": datetime.now().isoformat()
            }
    
    def _load_recent_reports(self, days: int) -> List[Dict[str, Any]]:
        """加载最近的审计报告
        
        Args:
            days: 天数
            
        Returns:
            报告列表
        """
        reports = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if not self.reports_dir.exists():
            return reports
        
        for report_file in self.reports_dir.glob("*.json"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    
                created_at = report.get("metadata", {}).get("scan_time", "")
                if created_at:
                    try:
                        report_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if report_date >= cutoff_date:
                            # 提取关键信息
                            report_data = {
                                "id": report.get("report_id", report_file.stem),
                                "created_at": created_at,
                                "risk_level": report.get("summary", {}).get("risk_level", "unknown"),
                                "confidence": report.get("summary", {}).get("confidence", 0),
                                "finding_count": report.get("summary", {}).get("finding_count", 0),
                                "skill_name": report.get("metadata", {}).get("skill_name", "unknown"),
                                "skill_version": report.get("metadata", {}).get("version", "unknown")
                            }
                            reports.append(report_data)
                    except (ValueError, TypeError):
                        continue
            except Exception as e:
                logger.warning(f"Error loading report {report_file}: {e}")
                continue
        
        return reports
    
    def _load_reports_by_skill(self, skill_name: str) -> List[Dict[str, Any]]:
        """加载指定Skill的所有审计报告
        
        Args:
            skill_name: Skill名称
            
        Returns:
            报告列表
        """
        reports = []
        
        if not self.reports_dir.exists():
            return reports
        
        for report_file in self.reports_dir.glob("*.json"):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    
                # 从metadata中获取skill_name，并做模糊匹配
                report_skill_name = report.get("metadata", {}).get("skill_name", "")
                
                # 支持模糊匹配：检查skill_name是否包含输入的关键词
                # 例如：输入 "ai-preprocessing-test-skill.zip"
                # 应该匹配 "57b2730efc7e8d8c262bf0a856360391fe87baf2_ai-preprocessing-test-skill.zip"
                if skill_name.lower() in report_skill_name.lower() or report_skill_name.lower() in skill_name.lower():
                    report_data = {
                        "id": report.get("report_id", report_file.stem),
                        "created_at": report.get("metadata", {}).get("scan_time", ""),
                        "risk_level": report.get("summary", {}).get("risk_level", "unknown"),
                        "confidence": report.get("summary", {}).get("confidence", 0),
                        "finding_count": report.get("summary", {}).get("finding_count", 0),
                        "skill_version": report.get("metadata", {}).get("version", "unknown")
                    }
                    reports.append(report_data)
            except Exception as e:
                logger.warning(f"Error loading report {report_file}: {e}")
                continue
        
        return reports
    
    def _calculate_trend(self, versions: List[Dict[str, Any]]) -> str:
        """计算风险趋势
        
        Args:
            versions: 版本列表（按时间倒序）
            
        Returns:
            趋势字符串: improving/worsening/stable/unknown
        """
        if len(versions) < 2:
            return "unknown"
        
        # 风险等级映射
        risk_map = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
        
        latest_risk = risk_map.get(versions[0].get("risk_level", "unknown").lower(), 0)
        previous_risk = risk_map.get(versions[-1].get("risk_level", "unknown").lower(), 0)
        
        if latest_risk < previous_risk:
            return "improving"
        elif latest_risk > previous_risk:
            return "worsening"
        else:
            return "stable"
