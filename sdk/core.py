"""
Core M2ARM functionality and main orchestrator class.
"""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .scanner import CodeScanner
from .migrator import Migrator
from .compiler import CrossCompiler
from .tester import ARMTester
from .optimizer import PerformanceOptimizer

logger = logging.getLogger(__name__)


class M2ARMCore:
    """
    Main orchestrator class for M2ARM SDK functionality.
    
    This class coordinates all the components of the M2ARM toolkit:
    - Code scanning and analysis
    - Migration planning and execution
    - Cross-compilation
    - Testing and validation
    - Performance optimization
    """
    
    def __init__(self, project_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize M2ARM core with project path and configuration.
        
        Args:
            project_path: Path to the project to be migrated
            config: Optional configuration dictionary
        """
        self.project_path = Path(project_path)
        self.config = config or {}
        
        # Initialize components
        self.scanner = CodeScanner(self.project_path, self.config)
        self.migrator = Migrator(self.project_path, self.config)
        self.compiler = CrossCompiler(self.project_path, self.config)
        self.tester = ARMTester(self.project_path, self.config)
        self.optimizer = PerformanceOptimizer(self.project_path, self.config)
        
        logger.info(f"M2ARM initialized for project: {self.project_path}")
    
    def scan_project(self) -> Dict[str, Any]:
        """
        Scan the project for x86-specific code and dependencies.
        
        Returns:
            Dictionary containing scan results and recommendations
        """
        logger.info("Starting project scan...")
        results = self.scanner.scan()
        logger.info(f"Scan completed. Found {len(results.get('issues', []))} potential issues")
        return results
    
    def create_migration_plan(self, target_arch: str = "arm64") -> Dict[str, Any]:
        """
        Create a migration plan based on scan results.
        
        Args:
            target_arch: Target architecture (arm64, armv7, etc.)
            
        Returns:
            Migration plan with steps and recommendations
        """
        logger.info(f"Creating migration plan for target: {target_arch}")
        scan_results = self.scan_project()
        plan = self.migrator.create_plan(scan_results, target_arch)
        logger.info("Migration plan created successfully")
        return plan
    
    def execute_migration(self, plan: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute the migration plan.
        
        Args:
            plan: Migration plan from create_migration_plan()
            dry_run: If True, only simulate the migration
            
        Returns:
            Migration execution results
        """
        logger.info(f"Executing migration (dry_run={dry_run})...")
        results = self.migrator.execute(plan, dry_run)
        if not dry_run:
            logger.info("Migration executed successfully")
        else:
            logger.info("Migration simulation completed")
        return results
    
    def cross_compile(self, targets: List[str]) -> Dict[str, Any]:
        """
        Cross-compile the project for specified targets.
        
        Args:
            targets: List of target architectures/platforms
            
        Returns:
            Compilation results for each target
        """
        logger.info(f"Cross-compiling for targets: {targets}")
        results = self.compiler.compile_all(targets)
        logger.info("Cross-compilation completed")
        return results
    
    def run_tests(self, targets: List[str]) -> Dict[str, Any]:
        """
        Run tests on specified ARM targets.
        
        Args:
            targets: List of ARM targets to test on
            
        Returns:
            Test results for each target
        """
        logger.info(f"Running tests on targets: {targets}")
        results = self.tester.run_tests(targets)
        logger.info("Testing completed")
        return results
    
    def optimize_performance(self, target_arch: str = "arm64") -> Dict[str, Any]:
        """
        Analyze and optimize performance for ARM architecture.
        
        Args:
            target_arch: Target ARM architecture
            
        Returns:
            Performance analysis and optimization results
        """
        logger.info(f"Optimizing performance for {target_arch}")
        results = self.optimizer.optimize(target_arch)
        logger.info("Performance optimization completed")
        return results
    
    def full_migration_workflow(self, target_arch: str = "arm64", 
                               compile_targets: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the complete migration workflow.
        
        Args:
            target_arch: Primary target architecture
            compile_targets: Additional compilation targets
            
        Returns:
            Complete workflow results
        """
        if compile_targets is None:
            compile_targets = [target_arch, "amd64"]  # Always include x86 for compatibility
            
        workflow_results = {
            "scan": None,
            "plan": None,
            "migration": None,
            "compilation": None,
            "tests": None,
            "optimization": None
        }
        
        try:
            # 1. Scan project
            workflow_results["scan"] = self.scan_project()
            
            # 2. Create migration plan
            workflow_results["plan"] = self.create_migration_plan(target_arch)
            
            # 3. Execute migration (dry run first)
            workflow_results["migration"] = self.execute_migration(
                workflow_results["plan"], dry_run=True
            )
            
            # 4. Cross-compile
            workflow_results["compilation"] = self.cross_compile(compile_targets)
            
            # 5. Run tests
            workflow_results["tests"] = self.run_tests([target_arch])
            
            # 6. Optimize performance
            workflow_results["optimization"] = self.optimize_performance(target_arch)
            
            logger.info("Full migration workflow completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            workflow_results["error"] = str(e)
            
        return workflow_results
