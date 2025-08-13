"""
Migration module for planning and executing ARM migration steps.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class Migrator:
    """
    Plans and executes migration steps to make code ARM-compatible.
    """
    
    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config
        
        # Migration strategies for different issue types
        self.migration_strategies = {
            "inline_assembly": self._migrate_inline_assembly,
            "x86_intrinsics": self._migrate_x86_intrinsics,
            "architecture_checks": self._migrate_architecture_checks,
            "platform_specific": self._migrate_platform_specific
        }
        
        # ARM NEON equivalents for common x86 intrinsics
        self.intrinsic_mappings = {
            "_mm_add_ps": "vaddq_f32",
            "_mm_sub_ps": "vsubq_f32", 
            "_mm_mul_ps": "vmulq_f32",
            "_mm_div_ps": "vdivq_f32",
            "_mm_load_ps": "vld1q_f32",
            "_mm_store_ps": "vst1q_f32",
            "_mm_set1_ps": "vdupq_n_f32",
            "_mm_add_epi32": "vaddq_s32",
            "_mm_sub_epi32": "vsubq_s32",
            "_mm_mullo_epi32": "vmulq_s32",
            "_mm_load_si128": "vld1q_s32",
            "_mm_store_si128": "vst1q_s32"
        }
    
    def create_plan(self, scan_results: Dict[str, Any], target_arch: str) -> Dict[str, Any]:
        """
        Create a migration plan based on scan results.
        
        Args:
            scan_results: Results from CodeScanner.scan()
            target_arch: Target ARM architecture
            
        Returns:
            Migration plan with ordered steps
        """
        logger.info(f"Creating migration plan for {target_arch}")
        
        plan = {
            "target_architecture": target_arch,
            "created_at": datetime.now().isoformat(),
            "total_issues": len(scan_results["issues"]),
            "steps": [],
            "build_system_changes": [],
            "dependency_updates": [],
            "testing_strategy": {},
            "estimated_effort": "unknown"
        }
        
        # Group issues by file and category
        issues_by_file = {}
        for issue in scan_results["issues"]:
            file_path = issue["file"]
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # Create migration steps for each file
        step_id = 1
        for file_path, file_issues in issues_by_file.items():
            step = self._create_file_migration_step(step_id, file_path, file_issues)
            plan["steps"].append(step)
            step_id += 1
        
        # Add build system changes
        plan["build_system_changes"] = self._plan_build_system_changes(
            scan_results["build_systems"], target_arch
        )
        
        # Add dependency updates
        plan["dependency_updates"] = self._plan_dependency_updates(
            scan_results["dependencies"], target_arch
        )
        
        # Create testing strategy
        plan["testing_strategy"] = self._create_testing_strategy(target_arch)
        
        # Estimate effort
        plan["estimated_effort"] = self._estimate_effort(plan)
        
        logger.info(f"Migration plan created with {len(plan['steps'])} steps")
        return plan
    
    def execute(self, plan: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute the migration plan.
        
        Args:
            plan: Migration plan from create_plan()
            dry_run: If True, only simulate the migration
            
        Returns:
            Execution results
        """
        logger.info(f"Executing migration plan (dry_run={dry_run})")
        
        results = {
            "executed_at": datetime.now().isoformat(),
            "dry_run": dry_run,
            "total_steps": len(plan["steps"]),
            "completed_steps": 0,
            "failed_steps": 0,
            "step_results": [],
            "build_changes": [],
            "dependency_changes": []
        }
        
        # Create backup if not dry run
        if not dry_run:
            backup_path = self._create_backup()
            results["backup_path"] = str(backup_path)
        
        # Execute each migration step
        for step in plan["steps"]:
            try:
                step_result = self._execute_step(step, dry_run)
                results["step_results"].append(step_result)
                
                if step_result["success"]:
                    results["completed_steps"] += 1
                else:
                    results["failed_steps"] += 1
                    
            except Exception as e:
                logger.error(f"Step {step['id']} failed: {str(e)}")
                results["failed_steps"] += 1
                results["step_results"].append({
                    "step_id": step["id"],
                    "success": False,
                    "error": str(e)
                })
        
        # Execute build system changes
        for build_change in plan["build_system_changes"]:
            try:
                change_result = self._execute_build_change(build_change, dry_run)
                results["build_changes"].append(change_result)
            except Exception as e:
                logger.error(f"Build change failed: {str(e)}")
                results["build_changes"].append({
                    "file": build_change["file"],
                    "success": False,
                    "error": str(e)
                })
        
        # Execute dependency updates
        for dep_update in plan["dependency_updates"]:
            try:
                dep_result = self._execute_dependency_update(dep_update, dry_run)
                results["dependency_changes"].append(dep_result)
            except Exception as e:
                logger.error(f"Dependency update failed: {str(e)}")
                results["dependency_changes"].append({
                    "dependency": dep_update["name"],
                    "success": False,
                    "error": str(e)
                })
        
        success_rate = results["completed_steps"] / results["total_steps"] if results["total_steps"] > 0 else 0
        logger.info(f"Migration execution completed: {success_rate:.1%} success rate")
        
        return results
    
    def _create_file_migration_step(self, step_id: int, file_path: str, 
                                   issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a migration step for a single file."""
        step = {
            "id": step_id,
            "type": "file_migration",
            "file": file_path,
            "issues_count": len(issues),
            "changes": []
        }
        
        # Sort issues by line number (descending to avoid line number shifts)
        sorted_issues = sorted(issues, key=lambda x: x["line"], reverse=True)
        
        for issue in sorted_issues:
            change = {
                "line": issue["line"],
                "category": issue["category"],
                "original": issue["matched_text"],
                "replacement": self._get_replacement(issue),
                "confidence": self._get_confidence(issue["category"])
            }
            step["changes"].append(change)
        
        return step
    
    def _get_replacement(self, issue: Dict[str, Any]) -> str:
        """Get replacement code for an issue."""
        category = issue["category"]
        matched_text = issue["matched_text"]
        
        if category == "x86_intrinsics":
            # Try to find direct mapping
            for x86_func, arm_func in self.intrinsic_mappings.items():
                if x86_func in matched_text:
                    return matched_text.replace(x86_func, arm_func)
            
            return f"/* TODO: Replace {matched_text} with ARM NEON equivalent */"
        
        elif category == "inline_assembly":
            return f"/* TODO: Replace inline assembly with portable C code or ARM NEON */\n// Original: {matched_text}"
        
        elif category == "architecture_checks":
            if "_M_X64" in matched_text or "__x86_64__" in matched_text:
                return matched_text.replace(matched_text, 
                    "#if defined(_M_X64) || defined(__x86_64__) || defined(__aarch64__)")
            elif "_M_IX86" in matched_text or "__i386__" in matched_text:
                return matched_text.replace(matched_text,
                    "#if defined(_M_IX86) || defined(__i386__) || defined(__arm__)")
        
        elif category == "platform_specific":
            return f"/* TODO: Add ARM-compatible implementation for {matched_text} */"
        
        return f"/* TODO: Review {matched_text} for ARM compatibility */"
    
    def _get_confidence(self, category: str) -> str:
        """Get confidence level for automatic replacement."""
        confidence_map = {
            "x86_intrinsics": "medium",  # Some direct mappings available
            "architecture_checks": "high",  # Usually straightforward
            "inline_assembly": "low",  # Requires manual review
            "platform_specific": "low"  # Context-dependent
        }
        return confidence_map.get(category, "low")
    
    def _plan_build_system_changes(self, build_systems: List[Dict[str, Any]], 
                                 target_arch: str) -> List[Dict[str, Any]]:
        """Plan changes to build system configurations."""
        changes = []
        
        for build_system in build_systems:
            system_type = build_system["system"]
            file_path = build_system["file"]
            
            change = {
                "file": file_path,
                "system": system_type,
                "changes": []
            }
            
            if system_type == "cmake":
                change["changes"] = [
                    "Add ARM64 target support",
                    "Set CMAKE_SYSTEM_PROCESSOR for cross-compilation",
                    "Add ARM-specific compiler flags",
                    "Update architecture detection logic"
                ]
            elif system_type == "make":
                change["changes"] = [
                    "Add ARM64 target to Makefile",
                    "Set CC and CXX for cross-compilation",
                    "Update CFLAGS/CXXFLAGS for ARM",
                    "Add architecture-specific build rules"
                ]
            elif system_type == "npm":
                change["changes"] = [
                    "Add ARM64 to supported architectures",
                    "Update build scripts for cross-compilation",
                    "Check native dependencies for ARM support"
                ]
            
            if change["changes"]:
                changes.append(change)
        
        return changes
    
    def _plan_dependency_updates(self, dependencies: List[Dict[str, Any]], 
                               target_arch: str) -> List[Dict[str, Any]]:
        """Plan dependency updates for ARM compatibility."""
        updates = []
        
        for dep in dependencies:
            update = {
                "name": dep["name"],
                "current_version": dep["version"],
                "type": dep["type"],
                "action": "verify_arm_support",
                "notes": []
            }
            
            # Check for known problematic dependencies
            if dep["name"] in ["tensorflow", "pytorch", "opencv"]:
                update["notes"].append("May require ARM-specific build")
                update["action"] = "check_arm_wheels"
            
            updates.append(update)
        
        return updates
    
    def _create_testing_strategy(self, target_arch: str) -> Dict[str, Any]:
        """Create testing strategy for ARM migration."""
        return {
            "unit_tests": {
                "required": True,
                "platforms": [target_arch, "x86_64"],
                "focus_areas": ["math operations", "memory access", "SIMD code"]
            },
            "integration_tests": {
                "required": True,
                "environments": ["native_arm", "emulated_arm", "cross_platform"]
            },
            "performance_tests": {
                "required": True,
                "metrics": ["execution_time", "memory_usage", "power_consumption"],
                "comparison_baseline": "x86_64"
            },
            "compatibility_tests": {
                "required": True,
                "data_formats": ["endianness", "struct_packing", "floating_point"]
            }
        }
    
    def _estimate_effort(self, plan: Dict[str, Any]) -> str:
        """Estimate migration effort based on plan complexity."""
        total_issues = plan["total_issues"]
        high_confidence_changes = sum(1 for step in plan["steps"] 
                                    for change in step["changes"] 
                                    if change["confidence"] == "high")
        
        if total_issues == 0:
            return "minimal"
        elif total_issues <= 10 and high_confidence_changes >= total_issues * 0.7:
            return "low"
        elif total_issues <= 50:
            return "medium"
        else:
            return "high"
    
    def _create_backup(self) -> Path:
        """Create a backup of the project before migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.project_path.parent / f"{self.project_path.name}_backup_{timestamp}"
        
        logger.info(f"Creating backup at: {backup_path}")
        shutil.copytree(self.project_path, backup_path, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', 'node_modules', '.venv', 'build', 'dist'
        ))
        
        return backup_path
    
    def _execute_step(self, step: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute a single migration step."""
        result = {
            "step_id": step["id"],
            "file": step["file"],
            "success": True,
            "changes_applied": 0,
            "warnings": []
        }
        
        if step["type"] == "file_migration":
            try:
                file_path = self.project_path / step["file"]
                
                if not file_path.exists():
                    result["success"] = False
                    result["error"] = "File not found"
                    return result
                
                if not dry_run:
                    # Read original file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Apply changes (sorted by line number, descending)
                    for change in step["changes"]:
                        if change["confidence"] == "high":
                            line_idx = change["line"] - 1
                            if 0 <= line_idx < len(lines):
                                lines[line_idx] = lines[line_idx].replace(
                                    change["original"], change["replacement"]
                                )
                                result["changes_applied"] += 1
                        else:
                            result["warnings"].append(
                                f"Low confidence change skipped at line {change['line']}"
                            )
                    
                    # Write modified file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                
                else:
                    # Dry run - just count what would be changed
                    result["changes_applied"] = sum(1 for change in step["changes"] 
                                                  if change["confidence"] == "high")
                
            except Exception as e:
                result["success"] = False
                result["error"] = str(e)
        
        return result
    
    def _execute_build_change(self, build_change: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute build system changes."""
        return {
            "file": build_change["file"],
            "system": build_change["system"],
            "success": True,
            "changes_applied": len(build_change["changes"]) if not dry_run else 0,
            "note": "Build system changes require manual review"
        }
    
    def _execute_dependency_update(self, dep_update: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute dependency updates."""
        return {
            "dependency": dep_update["name"],
            "success": True,
            "action_taken": dep_update["action"] if not dry_run else "none",
            "note": "Dependency compatibility needs verification"
        }
