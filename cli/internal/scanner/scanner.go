package scanner

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"github.com/m2arm/cli/internal/sdk"
)

// Scanner handles code scanning for x86-specific patterns
type Scanner struct {
	projectPath string
	config      map[string]interface{}
	
	// Pattern definitions for x86-specific code
	patterns map[string][]string
	
	// File extensions to scan
	extensions map[string]bool
}

// New creates a new scanner instance
func New(projectPath string, config map[string]interface{}) *Scanner {
	scanner := &Scanner{
		projectPath: projectPath,
		config:      config,
		patterns: map[string][]string{
			"inline_assembly": {
				`__asm__\s*\(`,
				`asm\s*\(`,
				`_asm\s*{`,
			},
			"x86_intrinsics": {
				`#include\s*<.*mmintrin\.h.*>`,
				`#include\s*<.*xmmintrin\.h.*>`,
				`#include\s*<.*emmintrin\.h.*>`,
				`#include\s*<.*pmmintrin\.h.*>`,
				`#include\s*<.*immintrin\.h.*>`,
				`_mm_\w+`,
				`_mm\d+_\w+`,
			},
			"architecture_checks": {
				`#ifdef\s+_M_X64`,
				`#ifdef\s+__x86_64__`,
				`#ifdef\s+_M_IX86`,
				`#ifdef\s+__i386__`,
			},
			"platform_specific": {
				`GetSystemInfo`,
				`IsWow64Process`,
				`SYSTEM_INFO`,
			},
		},
		extensions: map[string]bool{
			".c":    true,
			".cpp":  true,
			".cc":   true,
			".cxx":  true,
			".h":    true,
			".hpp":  true,
			".hxx":  true,
			".py":   true,
			".go":   true,
			".rs":   true,
			".java": true,
			".cs":   true,
			".js":   true,
			".ts":   true,
			".jsx":  true,
			".tsx":  true,
		},
	}

	return scanner
}

// Scan performs the code scanning
func (s *Scanner) Scan() (*sdk.ScanResults, error) {
	results := &sdk.ScanResults{
		ScanTime: time.Now(),
	}

	// Get list of files to scan
	files, err := s.getSourceFiles()
	if err != nil {
		return nil, fmt.Errorf("failed to get source files: %w", err)
	}

	results.TotalFiles = len(files)

	// Scan each file
	for _, file := range files {
		issues, err := s.scanFile(file)
		if err != nil {
			if s.isVerbose() {
				fmt.Fprintf(os.Stderr, "Warning: failed to scan %s: %v\n", file, err)
			}
			continue
		}

		results.Issues = append(results.Issues, issues...)
		results.ScannedFiles++
	}

	// Scan build systems
	buildSystems, err := s.scanBuildSystems()
	if err != nil {
		return nil, fmt.Errorf("failed to scan build systems: %w", err)
	}
	results.BuildSystems = buildSystems

	// Scan dependencies
	dependencies, err := s.scanDependencies()
	if err != nil {
		return nil, fmt.Errorf("failed to scan dependencies: %w", err)
	}
	results.Dependencies = dependencies

	// Generate recommendations
	results.Recommendations = s.generateRecommendations(results)

	return results, nil
}

// getSourceFiles returns a list of source files to scan
func (s *Scanner) getSourceFiles() ([]string, error) {
	var files []string

	err := filepath.Walk(s.projectPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		// Skip directories
		if info.IsDir() {
			// Skip common directories that shouldn't be scanned
			name := info.Name()
			if name == ".git" || name == "__pycache__" || name == "node_modules" ||
				name == ".venv" || name == "venv" || name == "build" || name == "dist" ||
				name == ".tox" || name == ".pytest_cache" {
				return filepath.SkipDir
			}
			return nil
		}

		// Check if file extension should be scanned
		ext := strings.ToLower(filepath.Ext(path))
		if s.extensions[ext] {
			files = append(files, path)
		}

		return nil
	})

	return files, err
}

// scanFile scans a single file for x86-specific patterns
func (s *Scanner) scanFile(filePath string) ([]sdk.Issue, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var issues []sdk.Issue
	scanner := bufio.NewScanner(file)
	lineNum := 0

	for scanner.Scan() {
		lineNum++
		line := scanner.Text()

		// Check each category of patterns
		for category, patterns := range s.patterns {
			for _, pattern := range patterns {
				regex, err := regexp.Compile(pattern)
				if err != nil {
					continue // Skip invalid regex
				}

				if match := regex.FindString(line); match != "" {
					relPath, _ := filepath.Rel(s.projectPath, filePath)
					
					issue := sdk.Issue{
						File:        relPath,
						Line:        lineNum,
						Category:    category,
						Pattern:     pattern,
						MatchedText: match,
						Severity:    s.getSeverity(category),
						Suggestion:  s.getSuggestion(category, match),
					}
					issues = append(issues, issue)
				}
			}
		}
	}

	return issues, scanner.Err()
}

// getSeverity returns the severity level for an issue category
func (s *Scanner) getSeverity(category string) string {
	severityMap := map[string]string{
		"inline_assembly":     "high",
		"x86_intrinsics":     "high",
		"architecture_checks": "medium",
		"platform_specific":   "medium",
	}
	if severity, ok := severityMap[category]; ok {
		return severity
	}
	return "low"
}

// getSuggestion returns a suggestion for fixing an issue
func (s *Scanner) getSuggestion(category, matchedText string) string {
	suggestions := map[string]string{
		"inline_assembly":     "Replace with portable C/C++ code or use ARM NEON intrinsics",
		"x86_intrinsics":     "Replace with ARM NEON equivalents or portable alternatives",
		"architecture_checks": "Add ARM architecture checks or use runtime detection",
		"platform_specific":   "Use cross-platform alternatives or add ARM-specific implementations",
	}
	if suggestion, ok := suggestions[category]; ok {
		return suggestion
	}
	return "Review for ARM compatibility"
}

// scanBuildSystems scans for build system configurations
func (s *Scanner) scanBuildSystems() ([]sdk.BuildSystem, error) {
	var buildSystems []sdk.BuildSystem

	buildPatterns := map[string]string{
		"CMakeLists.txt": "cmake",
		"Makefile":       "make",
		"build.gradle":   "gradle",
		"pom.xml":        "maven",
		"package.json":   "npm",
		"Cargo.toml":     "cargo",
		"go.mod":         "go_modules",
	}

	for pattern, system := range buildPatterns {
		matches, err := filepath.Glob(filepath.Join(s.projectPath, pattern))
		if err != nil {
			continue
		}

		for _, match := range matches {
			relPath, _ := filepath.Rel(s.projectPath, match)
			buildSystems = append(buildSystems, sdk.BuildSystem{
				File:        relPath,
				System:      system,
				NeedsReview: true,
			})
		}

		// Also check subdirectories
		err = filepath.Walk(s.projectPath, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return err
			}

			if !info.IsDir() && info.Name() == pattern {
				relPath, _ := filepath.Rel(s.projectPath, path)
				buildSystems = append(buildSystems, sdk.BuildSystem{
					File:        relPath,
					System:      system,
					NeedsReview: true,
				})
			}

			return nil
		})
	}

	return buildSystems, nil
}

// scanDependencies scans project dependencies
func (s *Scanner) scanDependencies() ([]sdk.Dependency, error) {
	var dependencies []sdk.Dependency

	// Check package.json (Node.js)
	if deps, err := s.scanNpmDependencies(); err == nil {
		dependencies = append(dependencies, deps...)
	}

	// Check requirements.txt (Python)
	if deps, err := s.scanPythonDependencies(); err == nil {
		dependencies = append(dependencies, deps...)
	}

	// Check Cargo.toml (Rust)
	if deps, err := s.scanCargoDependencies(); err == nil {
		dependencies = append(dependencies, deps...)
	}

	// Check go.mod (Go)
	if deps, err := s.scanGoDependencies(); err == nil {
		dependencies = append(dependencies, deps...)
	}

	return dependencies, nil
}

// scanNpmDependencies scans npm dependencies from package.json
func (s *Scanner) scanNpmDependencies() ([]sdk.Dependency, error) {
	packageJsonPath := filepath.Join(s.projectPath, "package.json")
	if _, err := os.Stat(packageJsonPath); os.IsNotExist(err) {
		return nil, err
	}

	// For simplicity, we'll just note that package.json exists
	// In a real implementation, you'd parse the JSON
	return []sdk.Dependency{
		{
			Name:          "npm-dependencies",
			Version:       "detected",
			Type:          "npm",
			ARMCompatible: "unknown",
		},
	}, nil
}

// scanPythonDependencies scans Python dependencies from requirements.txt
func (s *Scanner) scanPythonDependencies() ([]sdk.Dependency, error) {
	requirementsPath := filepath.Join(s.projectPath, "requirements.txt")
	file, err := os.Open(requirementsPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var dependencies []sdk.Dependency
	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Parse package name and version
		var name, version string
		if strings.Contains(line, "==") {
			parts := strings.Split(line, "==")
			name = strings.TrimSpace(parts[0])
			if len(parts) > 1 {
				version = strings.TrimSpace(parts[1])
			}
		} else if strings.Contains(line, ">=") {
			parts := strings.Split(line, ">=")
			name = strings.TrimSpace(parts[0])
			if len(parts) > 1 {
				version = ">=" + strings.TrimSpace(parts[1])
			}
		} else {
			name = line
			version = "*"
		}

		dependencies = append(dependencies, sdk.Dependency{
			Name:          name,
			Version:       version,
			Type:          "python",
			ARMCompatible: "unknown",
		})
	}

	return dependencies, scanner.Err()
}

// scanCargoDependencies scans Rust dependencies from Cargo.toml
func (s *Scanner) scanCargoDependencies() ([]sdk.Dependency, error) {
	cargoTomlPath := filepath.Join(s.projectPath, "Cargo.toml")
	if _, err := os.Stat(cargoTomlPath); os.IsNotExist(err) {
		return nil, err
	}

	// For simplicity, we'll just note that Cargo.toml exists
	// In a real implementation, you'd parse the TOML
	return []sdk.Dependency{
		{
			Name:          "cargo-dependencies",
			Version:       "detected",
			Type:          "cargo",
			ARMCompatible: "unknown",
		},
	}, nil
}

// scanGoDependencies scans Go dependencies from go.mod
func (s *Scanner) scanGoDependencies() ([]sdk.Dependency, error) {
	goModPath := filepath.Join(s.projectPath, "go.mod")
	file, err := os.Open(goModPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var dependencies []sdk.Dependency
	scanner := bufio.NewScanner(file)
	inRequireBlock := false

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		
		if strings.HasPrefix(line, "require (") {
			inRequireBlock = true
			continue
		}
		
		if inRequireBlock && line == ")" {
			inRequireBlock = false
			continue
		}

		if inRequireBlock && line != "" && !strings.HasPrefix(line, "//") {
			parts := strings.Fields(line)
			if len(parts) >= 2 {
				name := parts[0]
				version := parts[1]

				dependencies = append(dependencies, sdk.Dependency{
					Name:          name,
					Version:       version,
					Type:          "go",
					ARMCompatible: "unknown",
				})
			}
		}
	}

	return dependencies, scanner.Err()
}

// generateRecommendations generates recommendations based on scan results
func (s *Scanner) generateRecommendations(results *sdk.ScanResults) []string {
	var recommendations []string

	issueCount := len(results.Issues)
	highSeverityCount := 0
	for _, issue := range results.Issues {
		if issue.Severity == "high" {
			highSeverityCount++
		}
	}

	if issueCount == 0 {
		recommendations = append(recommendations, "✅ No obvious x86-specific code detected")
	} else {
		recommendations = append(recommendations, fmt.Sprintf("🔍 Found %d potential compatibility issues", issueCount))
		
		if highSeverityCount > 0 {
			recommendations = append(recommendations, fmt.Sprintf("⚠️  %d high-severity issues require immediate attention", highSeverityCount))
		}
	}

	// Build system recommendations
	buildSystemTypes := make(map[string]bool)
	for _, bs := range results.BuildSystems {
		buildSystemTypes[bs.System] = true
	}

	if buildSystemTypes["cmake"] {
		recommendations = append(recommendations, "📋 CMake detected - review CMakeLists.txt for architecture-specific settings")
	}
	if buildSystemTypes["make"] {
		recommendations = append(recommendations, "📋 Makefile detected - review for architecture-specific compiler flags")
	}

	// Dependency recommendations
	depCount := len(results.Dependencies)
	if depCount > 0 {
		recommendations = append(recommendations, fmt.Sprintf("📦 %d dependencies found - verify ARM compatibility", depCount))
	}

	return recommendations
}

// isVerbose returns true if verbose mode is enabled
func (s *Scanner) isVerbose() bool {
	if verbose, ok := s.config["verbose"].(bool); ok {
		return verbose
	}
	return false
}
