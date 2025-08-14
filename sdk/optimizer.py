"""
Performance optimization module for ARM architectures.
"""

import logging
import subprocess
import psutil
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    Analyzes and optimizes performance for ARM architectures.
    """

    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config

        # ARM-specific optimization strategies
        self.arm_optimizations = {
            "compiler_flags": {
                "arm64": [
                    "-march=armv8-a",
                    "-mtune=cortex-a72",  # Common ARM Cortex-A72
                    "-O3",
                    "-ffast-math",
                    "-funroll-loops",
                    "-ftree-vectorize",
                ],
                "armv7": [
                    "-march=armv7-a",
                    "-mtune=cortex-a9",
                    "-mfpu=neon",
                    "-O3",
                    "-ffast-math",
                    "-funroll-loops",
                ],
            },
            "neon_optimizations": [
                "Use NEON SIMD instructions for vectorizable loops",
                "Replace scalar floating-point operations with vector operations",
                "Optimize memory access patterns for ARM cache hierarchy",
                "Use ARM NEON intrinsics for math-heavy computations",
            ],
            "memory_optimizations": [
                "Align data structures to ARM cache line size (64 bytes)",
                "Use ARM-optimized memory allocation strategies",
                "Minimize memory fragmentation",
                "Optimize for ARM's weaker memory model",
            ],
            "power_optimizations": [
                "Use ARM big.LITTLE scheduling strategies",
                "Optimize for ARM's power management features",
                "Reduce CPU frequency scaling overhead",
                "Use ARM-specific power profiling tools",
            ],
        }

    def optimize(self, target_arch: str) -> Dict[str, Any]:
        """
        Analyze and optimize performance for ARM architecture.

        Args:
            target_arch: Target ARM architecture (arm64, armv7, etc.)

        Returns:
            Performance analysis and optimization results
        """
        logger.info(f"Optimizing performance for {target_arch}")

        results = {
            "target_architecture": target_arch,
            "analysis": {},
            "optimizations": {},
            "benchmarks": {},
            "recommendations": [],
        }

        # Analyze current performance
        results["analysis"] = self._analyze_performance(target_arch)

        # Apply optimizations
        results["optimizations"] = self._apply_optimizations(target_arch)

        # Run benchmarks
        results["benchmarks"] = self._run_benchmarks(target_arch)

        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(
            results["analysis"], target_arch
        )

        logger.info("Performance optimization completed")
        return results

    def _analyze_performance(self, target_arch: str) -> Dict[str, Any]:
        """Analyze current performance characteristics."""
        analysis = {"code_analysis": {}, "build_analysis": {}, "runtime_analysis": {}}

        # Analyze code for performance bottlenecks
        analysis["code_analysis"] = self._analyze_code_performance()

        # Analyze build configuration
        analysis["build_analysis"] = self._analyze_build_performance(target_arch)

        # Analyze runtime characteristics if binary exists
        analysis["runtime_analysis"] = self._analyze_runtime_performance(target_arch)

        return analysis

    def _analyze_code_performance(self) -> Dict[str, Any]:
        """Analyze code for performance patterns."""
        issues = []
        opportunities = []

        # Scan for performance-related patterns
        performance_patterns = {
            "hot_loops": [
                r"for\s*\([^)]*\)\s*{[^}]*for\s*\([^)]*\)",  # Nested loops
                r"while\s*\([^)]*\)\s*{[^}]*while\s*\([^)]*\)",  # Nested while loops
            ],
            "memory_intensive": [
                r"malloc\s*\(",
                r"new\s+\w+\[",
                r"vector\s*<[^>]*>\s*\(",
                r"std::vector",
            ],
            "floating_point": [
                r"float\s+\w+",
                r"double\s+\w+",
                r"\w+\s*[\+\-\*/]\s*\d*\.\d+",
                r"sqrt\s*\(",
                r"sin\s*\(",
                r"cos\s*\(",
            ],
            "simd_candidates": [
                r"for\s*\([^)]*\)\s*{[^}]*[\+\-\*/]=",  # Loop with arithmetic
                r"#pragma\s+omp\s+simd",
                r"#pragma\s+GCC\s+ivdep",
            ],
        }

        try:
            for file_path in self.project_path.rglob("*.c"):
                self._scan_file_performance(
                    file_path, performance_patterns, issues, opportunities
                )
            for file_path in self.project_path.rglob("*.cpp"):
                self._scan_file_performance(
                    file_path, performance_patterns, issues, opportunities
                )
            for file_path in self.project_path.rglob("*.cc"):
                self._scan_file_performance(
                    file_path, performance_patterns, issues, opportunities
                )
        except Exception as e:
            logger.warning(f"Code analysis failed: {str(e)}")

        return {
            "issues": issues,
            "optimization_opportunities": opportunities,
            "total_files_scanned": len(
                list(self.project_path.rglob("*.[ch]"))
                + list(self.project_path.rglob("*.cpp"))
                + list(self.project_path.rglob("*.cc"))
            ),
        }

    def _scan_file_performance(
        self,
        file_path: Path,
        patterns: Dict[str, List[str]],
        issues: List[Dict],
        opportunities: List[Dict],
    ):
        """Scan a single file for performance patterns."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(
                        pattern, content, re.IGNORECASE | re.MULTILINE
                    )

                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        opportunity = {
                            "file": str(file_path.relative_to(self.project_path)),
                            "line": line_num,
                            "category": category,
                            "code": match.group(0),
                            "suggestion": self._get_arm_optimization_suggestion(
                                category
                            ),
                        }

                        if category in ["hot_loops", "memory_intensive"]:
                            issues.append(opportunity)
                        else:
                            opportunities.append(opportunity)

        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {str(e)}")

    def _get_arm_optimization_suggestion(self, category: str) -> str:
        """Get ARM-specific optimization suggestion for category."""
        suggestions = {
            "hot_loops": "Consider loop unrolling and ARM NEON vectorization",
            "memory_intensive": "Optimize for ARM cache hierarchy and memory alignment",
            "floating_point": "Use ARM NEON intrinsics for SIMD operations",
            "simd_candidates": "Perfect candidate for ARM NEON optimization",
        }
        return suggestions.get(category, "Review for ARM-specific optimizations")

    def _analyze_build_performance(self, target_arch: str) -> Dict[str, Any]:
        """Analyze build configuration for performance."""
        build_analysis = {
            "compiler_flags": [],
            "optimization_level": "unknown",
            "arm_specific_flags": False,
            "recommendations": [],
        }

        # Check CMakeLists.txt
        cmake_file = self.project_path / "CMakeLists.txt"
        if cmake_file.exists():
            try:
                with open(cmake_file, "r") as f:
                    content = f.read()

                # Extract compiler flags
                flag_patterns = [
                    r"set\s*\(\s*CMAKE_C_FLAGS[^)]*\"([^\"]*)",
                    r"set\s*\(\s*CMAKE_CXX_FLAGS[^)]*\"([^\"]*)",
                    r"target_compile_options[^)]*\"([^\"]*)",
                ]

                for pattern in flag_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    build_analysis["compiler_flags"].extend(matches)

                # Check optimization level
                if "-O3" in content:
                    build_analysis["optimization_level"] = "O3"
                elif "-O2" in content:
                    build_analysis["optimization_level"] = "O2"
                elif "-O1" in content:
                    build_analysis["optimization_level"] = "O1"
                elif "-O0" in content:
                    build_analysis["optimization_level"] = "O0"

                # Check for ARM-specific flags
                arm_flags = ["-march=arm", "-mtune=", "-mfpu=neon", "-mfloat-abi="]
                build_analysis["arm_specific_flags"] = any(
                    flag in content for flag in arm_flags
                )

            except Exception as e:
                logger.warning(f"Failed to analyze CMakeLists.txt: {str(e)}")

        # Check Makefile
        makefile = self.project_path / "Makefile"
        if makefile.exists():
            try:
                with open(makefile, "r") as f:
                    content = f.read()

                # Extract CFLAGS/CXXFLAGS
                flag_matches = re.findall(r"C(?:XX)?FLAGS\s*[+:=]\s*([^\n]*)", content)
                build_analysis["compiler_flags"].extend(flag_matches)

                # Check optimization level
                if "-O3" in content:
                    build_analysis["optimization_level"] = "O3"
                elif "-O2" in content:
                    build_analysis["optimization_level"] = "O2"

            except Exception as e:
                logger.warning(f"Failed to analyze Makefile: {str(e)}")

        # Generate recommendations
        if build_analysis["optimization_level"] not in ["O2", "O3"]:
            build_analysis["recommendations"].append(
                "Enable higher optimization level (-O2 or -O3)"
            )

        if not build_analysis["arm_specific_flags"]:
            build_analysis["recommendations"].append(
                f"Add ARM-specific compiler flags for {target_arch}"
            )

        return build_analysis

    def _analyze_runtime_performance(self, target_arch: str) -> Dict[str, Any]:
        """Analyze runtime performance if possible."""
        runtime_analysis = {
            "cpu_usage": None,
            "memory_usage": None,
            "execution_time": None,
            "available": False,
        }

        # Try to find and run a benchmark or the main binary
        binary_path = self._find_benchmark_binary() or self._find_main_binary()

        if binary_path and self._is_runnable_on_current_platform(target_arch):
            try:
                # Run with performance monitoring
                start_time = time.time()
                process = subprocess.Popen(
                    [str(binary_path), "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Monitor resource usage
                psutil_process = psutil.Process(process.pid)
                max_memory = 0
                cpu_percent = 0

                while process.poll() is None:
                    try:
                        memory_info = psutil_process.memory_info()
                        max_memory = max(max_memory, memory_info.rss)
                        cpu_percent = max(cpu_percent, psutil_process.cpu_percent())
                        time.sleep(0.1)
                    except psutil.NoSuchProcess:
                        break

                end_time = time.time()

                runtime_analysis.update(
                    {
                        "cpu_usage": cpu_percent,
                        "memory_usage": max_memory,
                        "execution_time": end_time - start_time,
                        "available": True,
                    }
                )

            except Exception as e:
                logger.warning(f"Runtime analysis failed: {str(e)}")

        return runtime_analysis

    def _find_benchmark_binary(self) -> Optional[Path]:
        """Find benchmark binary if available."""
        benchmark_patterns = ["*bench*", "*benchmark*", "*perf*"]

        for pattern in benchmark_patterns:
            matches = list(self.project_path.rglob(pattern))
            for match in matches:
                if match.is_file() and self._is_executable(match):
                    return match

        return None

    def _find_main_binary(self) -> Optional[Path]:
        """Find main executable binary."""
        binary_patterns = ["main*", "*.exe", "**/main", "**/target/release/*"]

        for pattern in binary_patterns:
            matches = list(self.project_path.rglob(pattern))
            for match in matches:
                if match.is_file() and self._is_executable(match):
                    return match

        return None

    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is executable."""
        import platform

        if platform.system() == "Windows":
            return file_path.suffix.lower() in [".exe", ".bat", ".cmd"]
        else:
            return file_path.stat().st_mode & 0o111 != 0

    def _is_runnable_on_current_platform(self, target_arch: str) -> bool:
        """Check if target binary can run on current platform."""
        import platform

        current_arch = platform.machine().lower()

        # Simple compatibility check
        if target_arch == "arm64" and current_arch in ["aarch64", "arm64"]:
            return True
        elif target_arch == "amd64" and current_arch in ["x86_64", "amd64"]:
            return True

        return False

    def _apply_optimizations(self, target_arch: str) -> Dict[str, Any]:
        """Apply ARM-specific optimizations."""
        optimizations = {
            "compiler_flags_added": [],
            "build_configs_updated": [],
            "code_suggestions": [],
            "applied": False,
        }

        # Get ARM-specific compiler flags
        if target_arch in self.arm_optimizations["compiler_flags"]:
            flags = self.arm_optimizations["compiler_flags"][target_arch]
            optimizations["compiler_flags_added"] = flags

        # Add NEON optimization suggestions
        optimizations["code_suggestions"].extend(
            self.arm_optimizations["neon_optimizations"]
        )

        # Add memory optimization suggestions
        optimizations["code_suggestions"].extend(
            self.arm_optimizations["memory_optimizations"]
        )

        # Note: Actual application would require user confirmation
        optimizations["applied"] = False
        optimizations["note"] = "Optimizations identified but not automatically applied"

        return optimizations

    def _run_benchmarks(self, target_arch: str) -> Dict[str, Any]:
        """Run performance benchmarks."""
        benchmarks = {"available": False, "results": {}, "comparisons": {}}

        # Try to find and run benchmarks
        benchmark_binary = self._find_benchmark_binary()

        if benchmark_binary:
            try:
                result = subprocess.run(
                    [str(benchmark_binary)], capture_output=True, text=True, timeout=60
                )

                if result.returncode == 0:
                    benchmarks["available"] = True
                    benchmarks["results"]["output"] = result.stdout
                    # Parse benchmark results if in known format
                    benchmarks["results"]["parsed"] = self._parse_benchmark_output(
                        result.stdout
                    )

            except Exception as e:
                logger.warning(f"Benchmark execution failed: {str(e)}")

        return benchmarks

    def _parse_benchmark_output(self, output: str) -> Dict[str, Any]:
        """Parse benchmark output for key metrics."""
        parsed = {"execution_times": [], "throughput": None, "memory_usage": None}

        # Look for common benchmark patterns
        time_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:ms|milliseconds)",
            r"(\d+(?:\.\d+)?)\s*(?:s|seconds)",
            r"Time:\s*(\d+(?:\.\d+)?)",
        ]

        for pattern in time_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            for match in matches:
                try:
                    parsed["execution_times"].append(float(match))
                except ValueError:
                    pass

        # Look for throughput metrics
        throughput_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:ops/sec|operations/second)",
            r"Throughput:\s*(\d+(?:\.\d+)?)",
        ]

        for pattern in throughput_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                try:
                    parsed["throughput"] = float(matches[0])
                    break
                except ValueError:
                    pass

        return parsed

    def _generate_recommendations(
        self, analysis: Dict[str, Any], target_arch: str
    ) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Code analysis recommendations
        code_analysis = analysis.get("code_analysis", {})
        issues = code_analysis.get("issues", [])
        opportunities = code_analysis.get("optimization_opportunities", [])

        if issues:
            recommendations.append(
                f"🔥 Found {len(issues)} performance hotspots - prioritize optimization"
            )

        if opportunities:
            simd_opportunities = [
                o for o in opportunities if o["category"] == "simd_candidates"
            ]
            if simd_opportunities:
                recommendations.append(
                    f"💡 {len(simd_opportunities)} loops identified for ARM NEON vectorization"
                )

            fp_opportunities = [
                o for o in opportunities if o["category"] == "floating_point"
            ]
            if fp_opportunities:
                recommendations.append(
                    f"🧮 {len(fp_opportunities)} floating-point operations can use NEON intrinsics"
                )

        # Build analysis recommendations
        build_analysis = analysis.get("build_analysis", {})
        if build_analysis.get("optimization_level") not in ["O2", "O3"]:
            recommendations.append(
                "⚡ Enable -O3 optimization for better ARM performance"
            )

        if not build_analysis.get("arm_specific_flags"):
            recommendations.append(f"🎯 Add {target_arch}-specific compiler flags")

        # Runtime analysis recommendations
        runtime_analysis = analysis.get("runtime_analysis", {})
        if runtime_analysis.get("available"):
            memory_mb = runtime_analysis.get("memory_usage", 0) / (1024 * 1024)
            if memory_mb > 100:
                recommendations.append(
                    f"💾 High memory usage ({memory_mb:.1f}MB) - optimize for ARM's cache hierarchy"
                )

        # General ARM recommendations
        recommendations.extend(
            [
                "📚 Consider ARM NEON intrinsics for math-intensive operations",
                "🏗️ Align data structures to 64-byte cache lines for ARM",
                "⚡ Use ARM big.LITTLE scheduling for power efficiency",
                "🔧 Profile with ARM-specific tools (perf, ARM Streamline)",
            ]
        )

        return recommendations
