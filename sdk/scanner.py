"""
Code scanner module for detecting x86-specific code and dependencies.
"""

import logging
import re
import ast
import subprocess
from typing import Dict, List, Any, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class CodeScanner:
    """
    Scans code for x86-specific instructions, dependencies, and compatibility issues.
    """

    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config

        # Define patterns for x86-specific code
        self.x86_patterns = {
            "inline_assembly": [
                r"__asm__\s*\(",
                r"asm\s*\(",
                r"_asm\s*{",
            ],
            "x86_intrinsics": [
                r"#include\s*<.*mmintrin\.h.*>",
                r"#include\s*<.*xmmintrin\.h.*>",
                r"#include\s*<.*emmintrin\.h.*>",
                r"#include\s*<.*pmmintrin\.h.*>",
                r"#include\s*<.*immintrin\.h.*>",
                r"_mm_\w+",
                r"_mm\d+_\w+",
            ],
            "architecture_checks": [
                r"#ifdef\s+_M_X64",
                r"#ifdef\s+__x86_64__",
                r"#ifdef\s+_M_IX86",
                r"#ifdef\s+__i386__",
            ],
            "platform_specific": [
                r"GetSystemInfo",
                r"IsWow64Process",
                r"SYSTEM_INFO",
            ],
        }

        # File extensions to scan
        self.scannable_extensions = {
            ".c",
            ".cpp",
            ".cc",
            ".cxx",
            ".h",
            ".hpp",
            ".hxx",
            ".py",
            ".go",
            ".rs",
            ".java",
            ".cs",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
        }

    def scan(self) -> Dict[str, Any]:
        """
        Scan the entire project for x86-specific code.

        Returns:
            Dictionary containing scan results
        """
        results = {
            "total_files": 0,
            "scanned_files": 0,
            "issues": [],
            "dependencies": [],
            "build_systems": [],
            "recommendations": [],
        }

        logger.info(f"Scanning project at: {self.project_path}")

        # Scan source files
        for file_path in self._get_source_files():
            results["total_files"] += 1

            try:
                file_issues = self._scan_file(file_path)
                if file_issues:
                    results["issues"].extend(file_issues)
                results["scanned_files"] += 1

            except Exception as e:
                logger.warning(f"Failed to scan {file_path}: {str(e)}")

        # Scan build systems
        results["build_systems"] = self._scan_build_systems()

        # Scan dependencies
        results["dependencies"] = self._scan_dependencies()

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)

        logger.info(
            f"Scan completed: {results['scanned_files']}/{results['total_files']} files"
        )
        return results

    def _get_source_files(self) -> List[Path]:
        """Get list of source files to scan."""
        source_files = []

        for file_path in self.project_path.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.scannable_extensions
                and not self._should_skip_file(file_path)
            ):
                source_files.append(file_path)

        return source_files

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during scanning."""
        skip_patterns = [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "build",
            "dist",
            ".tox",
            ".pytest_cache",
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for x86-specific code."""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check for x86-specific patterns
            for category, patterns in self.x86_patterns.items():
                for pattern in patterns:
                    matches = list(
                        re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    )

                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        issue = {
                            "file": str(file_path.relative_to(self.project_path)),
                            "line": line_num,
                            "category": category,
                            "pattern": pattern,
                            "matched_text": match.group(0),
                            "severity": self._get_severity(category),
                            "suggestion": self._get_suggestion(
                                category, match.group(0)
                            ),
                        }
                        issues.append(issue)

        except Exception as e:
            logger.warning(f"Error scanning file {file_path}: {str(e)}")

        return issues

    def _get_severity(self, category: str) -> str:
        """Get severity level for issue category."""
        severity_map = {
            "inline_assembly": "high",
            "x86_intrinsics": "high",
            "architecture_checks": "medium",
            "platform_specific": "medium",
        }
        return severity_map.get(category, "low")

    def _get_suggestion(self, category: str, matched_text: str) -> str:
        """Get suggestion for fixing the issue."""
        suggestions = {
            "inline_assembly": "Replace with portable C/C++ code or use ARM NEON intrinsics",
            "x86_intrinsics": "Replace with ARM NEON equivalents or portable alternatives",
            "architecture_checks": "Add ARM architecture checks or use runtime detection",
            "platform_specific": "Use cross-platform alternatives or add ARM-specific implementations",
        }
        return suggestions.get(category, "Review for ARM compatibility")

    def _scan_build_systems(self) -> List[Dict[str, Any]]:
        """Scan for build system configurations."""
        build_files = []

        build_patterns = {
            "CMakeLists.txt": "cmake",
            "Makefile": "make",
            "*.mk": "make",
            "build.gradle": "gradle",
            "pom.xml": "maven",
            "package.json": "npm",
            "Cargo.toml": "cargo",
            "go.mod": "go_modules",
            "*.pro": "qmake",
        }

        for pattern, build_system in build_patterns.items():
            matches = list(self.project_path.glob(pattern))
            matches.extend(list(self.project_path.rglob(pattern)))

            for match in matches:
                build_files.append(
                    {
                        "file": str(match.relative_to(self.project_path)),
                        "system": build_system,
                        "needs_review": True,
                    }
                )

        return build_files

    def _scan_dependencies(self) -> List[Dict[str, Any]]:
        """Scan project dependencies for ARM compatibility."""
        dependencies = []

        # Check package.json (Node.js)
        package_json = self.project_path / "package.json"
        if package_json.exists():
            dependencies.extend(self._scan_npm_dependencies(package_json))

        # Check requirements.txt (Python)
        requirements_txt = self.project_path / "requirements.txt"
        if requirements_txt.exists():
            dependencies.extend(self._scan_python_dependencies(requirements_txt))

        # Check Cargo.toml (Rust)
        cargo_toml = self.project_path / "Cargo.toml"
        if cargo_toml.exists():
            dependencies.extend(self._scan_cargo_dependencies(cargo_toml))

        # Check go.mod (Go)
        go_mod = self.project_path / "go.mod"
        if go_mod.exists():
            dependencies.extend(self._scan_go_dependencies(go_mod))

        return dependencies

    def _scan_npm_dependencies(self, package_json: Path) -> List[Dict[str, Any]]:
        """Scan npm dependencies."""
        dependencies = []

        try:
            import json

            with open(package_json, "r") as f:
                data = json.load(f)

            all_deps = {}
            all_deps.update(data.get("dependencies", {}))
            all_deps.update(data.get("devDependencies", {}))

            for name, version in all_deps.items():
                dependencies.append(
                    {
                        "name": name,
                        "version": version,
                        "type": "npm",
                        "arm_compatible": "unknown",  # Would need to check npm registry
                    }
                )

        except Exception as e:
            logger.warning(f"Error scanning package.json: {str(e)}")

        return dependencies

    def _scan_python_dependencies(self, requirements_txt: Path) -> List[Dict[str, Any]]:
        """Scan Python dependencies."""
        dependencies = []

        try:
            with open(requirements_txt, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Parse package name and version
                        if "==" in line:
                            name, version = line.split("==", 1)
                        elif ">=" in line:
                            name, version = line.split(">=", 1)
                        else:
                            name, version = line, "*"

                        dependencies.append(
                            {
                                "name": name.strip(),
                                "version": version.strip(),
                                "type": "python",
                                "arm_compatible": "unknown",  # Would need to check PyPI
                            }
                        )

        except Exception as e:
            logger.warning(f"Error scanning requirements.txt: {str(e)}")

        return dependencies

    def _scan_cargo_dependencies(self, cargo_toml: Path) -> List[Dict[str, Any]]:
        """Scan Rust dependencies."""
        dependencies = []

        try:
            import toml

            with open(cargo_toml, "r") as f:
                data = toml.load(f)

            deps = data.get("dependencies", {})
            for name, config in deps.items():
                if isinstance(config, str):
                    version = config
                else:
                    version = config.get("version", "*")

                dependencies.append(
                    {
                        "name": name,
                        "version": version,
                        "type": "cargo",
                        "arm_compatible": "unknown",  # Would need to check crates.io
                    }
                )

        except Exception as e:
            logger.warning(f"Error scanning Cargo.toml: {str(e)}")

        return dependencies

    def _scan_go_dependencies(self, go_mod: Path) -> List[Dict[str, Any]]:
        """Scan Go dependencies."""
        dependencies = []

        try:
            with open(go_mod, "r") as f:
                content = f.read()

            # Parse require blocks
            require_pattern = r"require\s+\((.*?)\)"
            require_blocks = re.findall(require_pattern, content, re.DOTALL)

            for block in require_blocks:
                lines = block.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("//"):
                        parts = line.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            version = parts[1]

                            dependencies.append(
                                {
                                    "name": name,
                                    "version": version,
                                    "type": "go",
                                    "arm_compatible": "unknown",  # Would need to check
                                }
                            )

        except Exception as e:
            logger.warning(f"Error scanning go.mod: {str(e)}")

        return dependencies

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scan results."""
        recommendations = []

        issue_count = len(results["issues"])
        high_severity_count = sum(
            1 for issue in results["issues"] if issue["severity"] == "high"
        )

        if issue_count == 0:
            recommendations.append("✅ No obvious x86-specific code detected")
        else:
            recommendations.append(
                f"🔍 Found {issue_count} potential compatibility issues"
            )

            if high_severity_count > 0:
                recommendations.append(
                    f"⚠️  {high_severity_count} high-severity issues require immediate attention"
                )

        # Build system recommendations
        build_systems = [bs["system"] for bs in results["build_systems"]]
        if "cmake" in build_systems:
            recommendations.append(
                "📋 CMake detected - review CMakeLists.txt for architecture-specific settings"
            )
        if "make" in build_systems:
            recommendations.append(
                "📋 Makefile detected - review for architecture-specific compiler flags"
            )

        # Dependency recommendations
        dep_count = len(results["dependencies"])
        if dep_count > 0:
            recommendations.append(
                f"📦 {dep_count} dependencies found - verify ARM compatibility"
            )

        return recommendations
