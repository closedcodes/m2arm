"""
Cross-compilation module for building ARM and x86 targets.
"""

import logging
import subprocess
import platform
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CrossCompiler:
    """
    Handles cross-compilation for multiple architectures and platforms.
    """
    
    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config
        
        # Supported target configurations
        self.targets = {
            "linux/amd64": {
                "os": "linux",
                "arch": "amd64", 
                "cc": "gcc",
                "cxx": "g++",
                "flags": ["-m64"]
            },
            "linux/arm64": {
                "os": "linux", 
                "arch": "arm64",
                "cc": "aarch64-linux-gnu-gcc",
                "cxx": "aarch64-linux-gnu-g++",
                "flags": ["-march=armv8-a"]
            },
            "windows/amd64": {
                "os": "windows",
                "arch": "amd64",
                "cc": "x86_64-w64-mingw32-gcc", 
                "cxx": "x86_64-w64-mingw32-g++",
                "flags": ["-m64"]
            },
            "windows/arm64": {
                "os": "windows",
                "arch": "arm64", 
                "cc": "aarch64-w64-mingw32-gcc",
                "cxx": "aarch64-w64-mingw32-g++",
                "flags": []
            },
            "darwin/amd64": {
                "os": "darwin",
                "arch": "amd64",
                "cc": "clang",
                "cxx": "clang++", 
                "flags": ["-arch", "x86_64"]
            },
            "darwin/arm64": {
                "os": "darwin",
                "arch": "arm64",
                "cc": "clang",
                "cxx": "clang++",
                "flags": ["-arch", "arm64"]
            }
        }
    
    def compile_all(self, target_list: List[str]) -> Dict[str, Any]:
        """
        Cross-compile for all specified targets.
        
        Args:
            target_list: List of target strings (e.g., ["linux/arm64", "windows/amd64"])
            
        Returns:
            Compilation results for each target
        """
        logger.info(f"Cross-compiling for targets: {target_list}")
        
        results = {
            "total_targets": len(target_list),
            "successful_builds": 0,
            "failed_builds": 0,
            "build_results": {}
        }
        
        for target in target_list:
            try:
                logger.info(f"Building for target: {target}")
                build_result = self._compile_target(target)
                results["build_results"][target] = build_result
                
                if build_result["success"]:
                    results["successful_builds"] += 1
                else:
                    results["failed_builds"] += 1
                    
            except Exception as e:
                logger.error(f"Failed to build {target}: {str(e)}")
                results["build_results"][target] = {
                    "success": False,
                    "error": str(e)
                }
                results["failed_builds"] += 1
        
        success_rate = results["successful_builds"] / results["total_targets"]
        logger.info(f"Cross-compilation completed: {success_rate:.1%} success rate")
        
        return results
    
    def _compile_target(self, target: str) -> Dict[str, Any]:
        """Compile for a specific target."""
        if target not in self.targets:
            return {
                "success": False,
                "error": f"Unsupported target: {target}"
            }
        
        target_config = self.targets[target]
        build_type = self._detect_build_system()
        
        if build_type == "go":
            return self._compile_go(target, target_config)
        elif build_type == "cmake":
            return self._compile_cmake(target, target_config)
        elif build_type == "make":
            return self._compile_make(target, target_config)
        elif build_type == "cargo":
            return self._compile_cargo(target, target_config)
        elif build_type == "npm":
            return self._compile_npm(target, target_config)
        else:
            return {
                "success": False,
                "error": f"No supported build system found"
            }
    
    def _detect_build_system(self) -> Optional[str]:
        """Detect the build system used by the project."""
        if (self.project_path / "go.mod").exists():
            return "go"
        elif (self.project_path / "CMakeLists.txt").exists():
            return "cmake"
        elif (self.project_path / "Makefile").exists():
            return "make"
        elif (self.project_path / "Cargo.toml").exists():
            return "cargo"
        elif (self.project_path / "package.json").exists():
            return "npm"
        return None
    
    def _compile_go(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile Go project for target."""
        os_name, arch = target.split("/")
        
        env = {
            "GOOS": os_name,
            "GOARCH": arch,
            "CGO_ENABLED": "1" if self._has_cgo() else "0"
        }
        
        # Set cross-compilation environment for CGO
        if env["CGO_ENABLED"] == "1":
            env["CC"] = config["cc"]
            env["CXX"] = config["cxx"]
        
        output_name = f"main-{target.replace('/', '-')}"
        if os_name == "windows":
            output_name += ".exe"
        
        cmd = [
            "go", "build",
            "-o", output_name,
            "-ldflags", "-s -w",  # Strip symbols and debug info
            "."
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_path,
                env={**subprocess.os.environ, **env},
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "output_file": output_name if result.returncode == 0 else None,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "env": env
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Build timeout (5 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _compile_cmake(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile CMake project for target."""
        os_name, arch = target.split("/")
        
        build_dir = self.project_path / f"build-{target.replace('/', '-')}"
        build_dir.mkdir(exist_ok=True)
        
        # Configure
        cmake_args = [
            "cmake",
            "-B", str(build_dir),
            "-S", str(self.project_path),
            f"-DCMAKE_SYSTEM_NAME={os_name.title()}",
            f"-DCMAKE_SYSTEM_PROCESSOR={arch}",
            f"-DCMAKE_C_COMPILER={config['cc']}",
            f"-DCMAKE_CXX_COMPILER={config['cxx']}",
        ]
        
        if config["flags"]:
            flags_str = " ".join(config["flags"])
            cmake_args.extend([
                f"-DCMAKE_C_FLAGS={flags_str}",
                f"-DCMAKE_CXX_FLAGS={flags_str}"
            ])
        
        try:
            # Configure step
            configure_result = subprocess.run(
                cmake_args,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if configure_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"CMake configure failed: {configure_result.stderr}"
                }
            
            # Build step
            build_result = subprocess.run(
                ["cmake", "--build", str(build_dir), "--parallel"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": build_result.returncode == 0,
                "build_dir": str(build_dir),
                "configure_output": configure_result.stdout,
                "build_output": build_result.stdout,
                "stderr": build_result.stderr if build_result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Build timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _compile_make(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile Makefile project for target."""
        env = {
            "CC": config["cc"],
            "CXX": config["cxx"],
            "CFLAGS": " ".join(config["flags"]),
            "CXXFLAGS": " ".join(config["flags"])
        }
        
        try:
            result = subprocess.run(
                ["make", "clean", "&&", "make", f"TARGET={target}"],
                cwd=self.project_path,
                env={**subprocess.os.environ, **env},
                capture_output=True,
                text=True,
                shell=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "env": env
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _compile_cargo(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile Rust project for target."""
        # Map our target format to Rust target triple
        target_map = {
            "linux/amd64": "x86_64-unknown-linux-gnu",
            "linux/arm64": "aarch64-unknown-linux-gnu", 
            "windows/amd64": "x86_64-pc-windows-gnu",
            "windows/arm64": "aarch64-pc-windows-msvc",
            "darwin/amd64": "x86_64-apple-darwin",
            "darwin/arm64": "aarch64-apple-darwin"
        }
        
        rust_target = target_map.get(target)
        if not rust_target:
            return {
                "success": False,
                "error": f"No Rust target mapping for {target}"
            }
        
        try:
            # Add target if not installed
            subprocess.run(
                ["rustup", "target", "add", rust_target],
                capture_output=True
            )
            
            # Build
            result = subprocess.run(
                ["cargo", "build", "--release", "--target", rust_target],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "target": rust_target,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _compile_npm(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile Node.js project for target."""
        # For Node.js, we mainly deal with native modules
        os_name, arch = target.split("/")
        
        env = {
            "npm_config_target_platform": os_name,
            "npm_config_target_arch": arch,
            "npm_config_disturl": "https://electronjs.org/headers",
            "npm_config_runtime": "node",
            "npm_config_build_from_source": "true"
        }
        
        try:
            # Rebuild native modules for target
            result = subprocess.run(
                ["npm", "rebuild"],
                cwd=self.project_path,
                env={**subprocess.os.environ, **env},
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "env": env
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _has_cgo(self) -> bool:
        """Check if Go project uses CGO."""
        try:
            # Look for CGO usage in Go files
            for go_file in self.project_path.rglob("*.go"):
                with open(go_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'import "C"' in content or '#include' in content:
                        return True
            return False
        except Exception:
            return False
    
    def get_supported_targets(self) -> List[str]:
        """Get list of supported compilation targets."""
        return list(self.targets.keys())
    
    def validate_toolchain(self, target: str) -> Dict[str, Any]:
        """Validate that required toolchain is available for target."""
        if target not in self.targets:
            return {"valid": False, "error": f"Unsupported target: {target}"}
        
        config = self.targets[target]
        missing_tools = []
        
        # Check for compiler
        try:
            result = subprocess.run(
                [config["cc"], "--version"],
                capture_output=True,
                timeout=10
            )
            if result.returncode != 0:
                missing_tools.append(config["cc"])
        except:
            missing_tools.append(config["cc"])
        
        # Check for C++ compiler
        try:
            result = subprocess.run(
                [config["cxx"], "--version"], 
                capture_output=True,
                timeout=10
            )
            if result.returncode != 0:
                missing_tools.append(config["cxx"])
        except:
            missing_tools.append(config["cxx"])
        
        if missing_tools:
            return {
                "valid": False,
                "missing_tools": missing_tools,
                "suggestion": f"Install cross-compilation toolchain for {target}"
            }
        
        return {"valid": True}
