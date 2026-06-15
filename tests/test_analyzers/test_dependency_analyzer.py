"""DependencyAnalyzer tests.

This file validates dependency scanning, code reference detection, and library security checks.
"""

from pathlib import Path
import tempfile

from app.analyzers.dependency_analyzer import DependencyAnalyzer


def test_dependency_analyzer_detects_code_references() -> None:
    analyzer = DependencyAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / 'example.py'
        script_path.write_text(
            'import requests\n'
            'from .local import helper\n'
            'from os import path\n'
        )

        result = analyzer.analyze(tmpdir)

        assert 'code_references' in result
        modules = {ref['module'] for ref in result['code_references']}
        assert 'requests' in modules
        assert 'os' in modules
        assert '.local' not in modules
        assert result['summary']['code_reference_count'] == len(result['code_references'])


def test_dependency_analyzer_detects_js_imports() -> None:
    analyzer = DependencyAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / 'example.js'
        script_path.write_text(
            'const _ = require("lodash");\n'
            'import axios from "axios";\n'
            'import "dotenv/config";\n'
        )

        result = analyzer.analyze(tmpdir)
        modules = {ref['module'] for ref in result['code_references']}

        assert 'lodash' in modules
        assert 'axios' in modules
        assert 'dotenv/config' in modules


def test_library_security_check_safe_packages() -> None:
    """测试安全库的检查结果。"""
    analyzer = DependencyAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / 'example.py'
        script_path.write_text('import requests\nimport flask\n')

        result = analyzer.analyze(tmpdir)
        
        for ref in result['code_references']:
            assert 'security_check' in ref
            if ref['module'] in ['requests', 'flask']:
                assert ref['security_check']['safe'] is True
                assert ref['security_check']['risk_level'] == 'safe'


def test_library_security_check_typosquatting() -> None:
    """测试typosquatting检测。"""
    analyzer = DependencyAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / 'example.py'
        script_path.write_text('import reqests\n')  # 拼写错误，应为 requests

        result = analyzer.analyze(tmpdir)
        
        refs = [r for r in result['code_references'] if r['module'] == 'reqests']
        assert len(refs) > 0
        
        ref = refs[0]
        assert ref['security_check']['risk_level'] == 'high'
        assert any(issue['type'] == 'typosquatting_risk' for issue in ref['security_check']['issues'])


def test_library_security_check_malicious_package() -> None:
    """测试已知恶意包检测。"""
    analyzer = DependencyAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / 'example.js'
        script_path.write_text('require("event-stream");\n')

        result = analyzer.analyze(tmpdir)
        
        refs = [r for r in result['code_references'] if r['module'] == 'event-stream']
        assert len(refs) > 0
        
        ref = refs[0]
        assert ref['security_check']['risk_level'] == 'critical'
        assert any(issue['type'] == 'malicious_package' for issue in ref['security_check']['issues'])


def test_library_security_check_suspicious_patterns() -> None:
    """测试可疑包名模式检测。"""
    analyzer = DependencyAnalyzer()

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / 'example.py'
        script_path.write_text('import backdoor_tool\n')

        result = analyzer.analyze(tmpdir)
        
        refs = [r for r in result['code_references'] if r['module'] == 'backdoor_tool']
        assert len(refs) > 0
        
        ref = refs[0]
        assert ref['security_check']['risk_level'] in ['medium', 'high', 'critical']
        assert any(issue['type'] == 'suspicious_package_name' for issue in ref['security_check']['issues'])
