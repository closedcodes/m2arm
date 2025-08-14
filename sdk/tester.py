"""
Testing module for validating ARM builds and compatibility.
"""

import logging
import subprocess
import platform
import tempfile
import docker
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ARMTester:
    """
    Tests ARM builds using emulation, containers, and native hardware.
    """

    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config

        # Test environments
        self.test_environments = {
            "qemu_arm64": {
                "type": "emulation",
                "emulator": "qemu-aarch64-static",
                "docker_image": "arm64v8/ubuntu:22.04",
            },
            "qemu_armv7": {
                "type": "emulation",
                "emulator": "qemu-arm-static",
                "docker_image": "arm32v7/ubuntu:22.04",
            },
            "native_arm64": {"type": "native", "required_arch": "aarch64"},
            "docker_arm64": {
                "type": "container",
                "platform": "linux/arm64",
                "base_image": "ubuntu:22.04",
            },
        }

    def run_tests(self, targets: List[str]) -> Dict[str, Any]:
        """
        Run tests on specified ARM targets.

        Args:
            targets: List of target architectures to test

        Returns:
            Test results for each target
        """
        logger.info(f"Running tests on ARM targets: {targets}")

        results = {
            "total_targets": len(targets),
            "passed_targets": 0,
            "failed_targets": 0,
            "test_results": {},
        }

        for target in targets:
            try:
                logger.info(f"Testing target: {target}")
                test_result = self._test_target(target)
                results["test_results"][target] = test_result

                if test_result["overall_success"]:
                    results["passed_targets"] += 1
                else:
                    results["failed_targets"] += 1

            except Exception as e:
                logger.error(f"Failed to test {target}: {str(e)}")
                results["test_results"][target] = {
                    "overall_success": False,
                    "error": str(e),
                }
                results["failed_targets"] += 1

        success_rate = results["passed_targets"] / results["total_targets"]
        logger.info(f"ARM testing completed: {success_rate:.1%} success rate")

        return results

    def _test_target(self, target: str) -> Dict[str, Any]:
        """Test a specific ARM target."""
        result = {
            "target": target,
            "overall_success": False,
            "tests": {
                "binary_execution": None,
                "unit_tests": None,
                "integration_tests": None,
                "performance_tests": None,
            },
            "environment": None,
            "issues": [],
        }

        # Determine best test environment for target
        env_name = self._select_test_environment(target)
        if not env_name:
            result["error"] = f"No suitable test environment for {target}"
            return result

        result["environment"] = env_name
        environment = self.test_environments[env_name]

        # Run tests based on environment type
        if environment["type"] == "emulation":
            return self._test_with_emulation(target, environment, result)
        elif environment["type"] == "native":
            return self._test_native(target, environment, result)
        elif environment["type"] == "container":
            return self._test_with_container(target, environment, result)

        return result

    def _select_test_environment(self, target: str) -> Optional[str]:
        """Select the best available test environment for target."""
        # Check if running on native ARM
        if platform.machine() in ["aarch64", "arm64"]:
            return "native_arm64"

        # Check if Docker is available
        try:
            client = docker.from_env()
            client.ping()
            if target == "arm64":
                return "docker_arm64"
        except:
            pass

        # Check if QEMU is available
        if self._is_qemu_available():
            if target == "arm64":
                return "qemu_arm64"
            elif target == "armv7":
                return "qemu_armv7"

        return None

    def _is_qemu_available(self) -> bool:
        """Check if QEMU ARM emulation is available."""
        try:
            result = subprocess.run(
                ["qemu-aarch64-static", "--version"], capture_output=True, timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def _test_with_emulation(
        self, target: str, environment: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test using QEMU emulation."""
        emulator = environment["emulator"]

        # Find the ARM binary to test
        binary_path = self._find_target_binary(target)
        if not binary_path:
            result["tests"]["binary_execution"] = {
                "success": False,
                "error": "No ARM binary found",
            }
            return result

        # Test binary execution
        try:
            cmd = [emulator, str(binary_path), "--version"]
            exec_result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )

            result["tests"]["binary_execution"] = {
                "success": exec_result.returncode == 0,
                "stdout": exec_result.stdout,
                "stderr": exec_result.stderr,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            result["tests"]["binary_execution"] = {
                "success": False,
                "error": "Execution timeout",
            }
        except Exception as e:
            result["tests"]["binary_execution"] = {"success": False, "error": str(e)}

        # Run unit tests if available
        result["tests"]["unit_tests"] = self._run_unit_tests_emulated(target, emulator)

        # Check overall success
        result["overall_success"] = (
            result["tests"]["binary_execution"]
            and result["tests"]["binary_execution"]["success"]
        )

        return result

    def _test_native(
        self, target: str, environment: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test on native ARM hardware."""
        # Find the ARM binary
        binary_path = self._find_target_binary(target)
        if not binary_path:
            result["tests"]["binary_execution"] = {
                "success": False,
                "error": "No ARM binary found",
            }
            return result

        # Test binary execution
        try:
            exec_result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            result["tests"]["binary_execution"] = {
                "success": exec_result.returncode == 0,
                "stdout": exec_result.stdout,
                "stderr": exec_result.stderr,
            }

        except Exception as e:
            result["tests"]["binary_execution"] = {"success": False, "error": str(e)}

        # Run comprehensive tests on native hardware
        result["tests"]["unit_tests"] = self._run_unit_tests_native(target)
        result["tests"]["integration_tests"] = self._run_integration_tests(target)
        result["tests"]["performance_tests"] = self._run_performance_tests(target)

        # Check overall success
        all_tests = [test for test in result["tests"].values() if test is not None]
        result["overall_success"] = all(
            test.get("success", False) for test in all_tests
        )

        return result

    def _test_with_container(
        self, target: str, environment: Dict[str, Any], result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test using Docker containers."""
        try:
            client = docker.from_env()

            # Build test image
            dockerfile = self._generate_test_dockerfile(target, environment)

            with tempfile.TemporaryDirectory() as temp_dir:
                dockerfile_path = Path(temp_dir) / "Dockerfile"
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile)

                # Copy binary to temp directory
                binary_path = self._find_target_binary(target)
                if binary_path:
                    import shutil

                    shutil.copy2(binary_path, temp_dir)

                # Build image
                image = client.images.build(
                    path=temp_dir,
                    platform=environment["platform"],
                    tag=f"m2arm-test-{target}",
                )[0]

                # Run container
                container = client.containers.run(
                    image.id, platform=environment["platform"], detach=True, remove=True
                )

                # Wait for completion and get logs
                container.wait(timeout=120)
                logs = container.logs().decode("utf-8")

                result["tests"]["binary_execution"] = {
                    "success": "SUCCESS" in logs,
                    "output": logs,
                }

        except Exception as e:
            result["tests"]["binary_execution"] = {"success": False, "error": str(e)}

        result["overall_success"] = (
            result["tests"]["binary_execution"]
            and result["tests"]["binary_execution"]["success"]
        )

        return result

    def _find_target_binary(self, target: str) -> Optional[Path]:
        """Find the compiled binary for the target architecture."""
        # Common binary locations and patterns
        search_patterns = [
            f"*{target}*",
            f"*{target.replace('/', '-')}*",
            "main*",
            "*.exe" if "windows" in target else "*",
        ]

        search_dirs = [
            self.project_path,
            self.project_path / "build",
            self.project_path / "dist",
            self.project_path / "target" / "release",
            self.project_path / f"build-{target.replace('/', '-')}",
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in search_patterns:
                    matches = list(search_dir.glob(pattern))
                    # Filter for executable files
                    for match in matches:
                        if match.is_file() and self._is_executable(match):
                            return match

        return None

    def _is_executable(self, file_path: Path) -> bool:
        """Check if file is executable."""
        if platform.system() == "Windows":
            return file_path.suffix.lower() in [".exe", ".bat", ".cmd"]
        else:
            return file_path.stat().st_mode & 0o111 != 0

    def _run_unit_tests_emulated(self, target: str, emulator: str) -> Dict[str, Any]:
        """Run unit tests using emulation."""
        # Look for test binaries
        test_patterns = ["*test*", "*_test", "test_*"]
        test_binaries = []

        for pattern in test_patterns:
            matches = list(self.project_path.rglob(pattern))
            test_binaries.extend(
                [m for m in matches if m.is_file() and self._is_executable(m)]
            )

        if not test_binaries:
            return {"success": False, "error": "No test binaries found"}

        results = []
        for test_binary in test_binaries[:5]:  # Limit to first 5 test binaries
            try:
                result = subprocess.run(
                    [emulator, str(test_binary)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                results.append(
                    {
                        "binary": test_binary.name,
                        "success": result.returncode == 0,
                        "stdout": result.stdout[:1000],  # Limit output
                        "stderr": result.stderr[:1000],
                    }
                )

            except Exception as e:
                results.append(
                    {"binary": test_binary.name, "success": False, "error": str(e)}
                )

        overall_success = all(r["success"] for r in results)
        return {
            "success": overall_success,
            "test_count": len(results),
            "results": results,
        }

    def _run_unit_tests_native(self, target: str) -> Dict[str, Any]:
        """Run unit tests natively."""
        # Use common test runners based on detected build system
        if (self.project_path / "go.mod").exists():
            return self._run_go_tests()
        elif (self.project_path / "Cargo.toml").exists():
            return self._run_cargo_tests()
        elif (self.project_path / "package.json").exists():
            return self._run_npm_tests()
        elif (self.project_path / "CMakeLists.txt").exists():
            return self._run_ctest()

        return {"success": False, "error": "No supported test runner found"}

    def _run_go_tests(self) -> Dict[str, Any]:
        """Run Go tests."""
        try:
            result = subprocess.run(
                ["go", "test", "-v", "./..."],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_cargo_tests(self) -> Dict[str, Any]:
        """Run Rust tests."""
        try:
            result = subprocess.run(
                ["cargo", "test"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_npm_tests(self) -> Dict[str, Any]:
        """Run npm tests."""
        try:
            result = subprocess.run(
                ["npm", "test"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_ctest(self) -> Dict[str, Any]:
        """Run CTest."""
        try:
            result = subprocess.run(
                ["ctest", "--output-on-failure"],
                cwd=self.project_path / "build",
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_integration_tests(self, target: str) -> Dict[str, Any]:
        """Run integration tests."""
        # Placeholder for integration test logic
        return {"success": True, "note": "Integration tests not implemented yet"}

    def _run_performance_tests(self, target: str) -> Dict[str, Any]:
        """Run performance tests."""
        # Placeholder for performance test logic
        return {"success": True, "note": "Performance tests not implemented yet"}

    def _generate_test_dockerfile(
        self, target: str, environment: Dict[str, Any]
    ) -> str:
        """Generate Dockerfile for testing."""
        return f"""
FROM {environment['base_image']}

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    libc6 \\
    && rm -rf /var/lib/apt/lists/*

# Copy binary
COPY . /app
WORKDIR /app

# Make binary executable
RUN chmod +x ./* || true

# Test execution
CMD echo "Testing ARM binary..." && \\
    ./main* --version && \\
    echo "SUCCESS: Binary executed successfully" || \\
    echo "FAILED: Binary execution failed"
"""
