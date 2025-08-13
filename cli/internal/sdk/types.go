package sdk

import "time"

// ScanResults represents the results of a code scan
type ScanResults struct {
	TotalFiles      int                 `json:"total_files"`
	ScannedFiles    int                 `json:"scanned_files"`
	Issues          []Issue             `json:"issues"`
	Dependencies    []Dependency        `json:"dependencies"`
	BuildSystems    []BuildSystem       `json:"build_systems"`
	Recommendations []string            `json:"recommendations"`
	ScanTime        time.Time           `json:"scan_time"`
}

// Issue represents a compatibility issue found during scanning
type Issue struct {
	File        string `json:"file"`
	Line        int    `json:"line"`
	Category    string `json:"category"`
	Pattern     string `json:"pattern"`
	MatchedText string `json:"matched_text"`
	Severity    string `json:"severity"`
	Suggestion  string `json:"suggestion"`
}

// Dependency represents a project dependency
type Dependency struct {
	Name          string `json:"name"`
	Version       string `json:"version"`
	Type          string `json:"type"`
	ARMCompatible string `json:"arm_compatible"`
}

// BuildSystem represents a detected build system
type BuildSystem struct {
	File        string `json:"file"`
	System      string `json:"system"`
	NeedsReview bool   `json:"needs_review"`
}

// MigrationPlan represents a migration plan
type MigrationPlan struct {
	TargetArchitecture   string                 `json:"target_architecture"`
	CreatedAt           time.Time              `json:"created_at"`
	TotalIssues         int                    `json:"total_issues"`
	Steps               []MigrationStep        `json:"steps"`
	BuildSystemChanges  []BuildSystemChange    `json:"build_system_changes"`
	DependencyUpdates   []DependencyUpdate     `json:"dependency_updates"`
	TestingStrategy     TestingStrategy        `json:"testing_strategy"`
	EstimatedEffort     string                 `json:"estimated_effort"`
}

// MigrationStep represents a single migration step
type MigrationStep struct {
	ID          int           `json:"id"`
	Type        string        `json:"type"`
	File        string        `json:"file"`
	IssuesCount int           `json:"issues_count"`
	Changes     []CodeChange  `json:"changes"`
}

// CodeChange represents a code change within a migration step
type CodeChange struct {
	Line        int    `json:"line"`
	Category    string `json:"category"`
	Original    string `json:"original"`
	Replacement string `json:"replacement"`
	Confidence  string `json:"confidence"`
}

// BuildSystemChange represents changes needed in build systems
type BuildSystemChange struct {
	File    string   `json:"file"`
	System  string   `json:"system"`
	Changes []string `json:"changes"`
}

// DependencyUpdate represents a dependency update
type DependencyUpdate struct {
	Name           string   `json:"name"`
	CurrentVersion string   `json:"current_version"`
	Type           string   `json:"type"`
	Action         string   `json:"action"`
	Notes          []string `json:"notes"`
}

// TestingStrategy represents the testing approach
type TestingStrategy struct {
	UnitTests        TestConfig `json:"unit_tests"`
	IntegrationTests TestConfig `json:"integration_tests"`
	PerformanceTests TestConfig `json:"performance_tests"`
	CompatibilityTests TestConfig `json:"compatibility_tests"`
}

// TestConfig represents configuration for a type of test
type TestConfig struct {
	Required    bool     `json:"required"`
	Platforms   []string `json:"platforms,omitempty"`
	FocusAreas  []string `json:"focus_areas,omitempty"`
	Environments []string `json:"environments,omitempty"`
	Metrics     []string `json:"metrics,omitempty"`
	Comparison  string   `json:"comparison_baseline,omitempty"`
}

// CompilationResults represents cross-compilation results
type CompilationResults struct {
	TotalTargets     int                           `json:"total_targets"`
	SuccessfulBuilds int                           `json:"successful_builds"`
	FailedBuilds     int                           `json:"failed_builds"`
	BuildResults     map[string]CompilationResult  `json:"build_results"`
}

// CompilationResult represents the result of compiling for a single target
type CompilationResult struct {
	Success     bool              `json:"success"`
	OutputFile  string            `json:"output_file,omitempty"`
	BuildDir    string            `json:"build_dir,omitempty"`
	Stdout      string            `json:"stdout,omitempty"`
	Stderr      string            `json:"stderr,omitempty"`
	Command     string            `json:"command,omitempty"`
	Environment map[string]string `json:"environment,omitempty"`
	Error       string            `json:"error,omitempty"`
}

// TestResults represents ARM testing results
type TestResults struct {
	TotalTargets  int                     `json:"total_targets"`
	PassedTargets int                     `json:"passed_targets"`
	FailedTargets int                     `json:"failed_targets"`
	TestResults   map[string]TestResult   `json:"test_results"`
}

// TestResult represents the result of testing a single target
type TestResult struct {
	Target          string                 `json:"target"`
	OverallSuccess  bool                   `json:"overall_success"`
	Tests           map[string]interface{} `json:"tests"`
	Environment     string                 `json:"environment"`
	Issues          []string               `json:"issues"`
	Error           string                 `json:"error,omitempty"`
}

// PerformanceResults represents performance optimization results
type PerformanceResults struct {
	TargetArchitecture string                 `json:"target_architecture"`
	Analysis           PerformanceAnalysis    `json:"analysis"`
	Optimizations      Optimizations          `json:"optimizations"`
	Benchmarks         BenchmarkResults       `json:"benchmarks"`
	Recommendations    []string               `json:"recommendations"`
}

// PerformanceAnalysis represents performance analysis results
type PerformanceAnalysis struct {
	CodeAnalysis    CodeAnalysis    `json:"code_analysis"`
	BuildAnalysis   BuildAnalysis   `json:"build_analysis"`
	RuntimeAnalysis RuntimeAnalysis `json:"runtime_analysis"`
}

// CodeAnalysis represents code performance analysis
type CodeAnalysis struct {
	Issues                     []PerformanceIssue `json:"issues"`
	OptimizationOpportunities  []PerformanceIssue `json:"optimization_opportunities"`
	TotalFilesScanned         int                `json:"total_files_scanned"`
}

// PerformanceIssue represents a performance issue or opportunity
type PerformanceIssue struct {
	File       string `json:"file"`
	Line       int    `json:"line"`
	Category   string `json:"category"`
	Code       string `json:"code"`
	Suggestion string `json:"suggestion"`
}

// BuildAnalysis represents build configuration analysis
type BuildAnalysis struct {
	CompilerFlags      []string `json:"compiler_flags"`
	OptimizationLevel  string   `json:"optimization_level"`
	ARMSpecificFlags   bool     `json:"arm_specific_flags"`
	Recommendations    []string `json:"recommendations"`
}

// RuntimeAnalysis represents runtime performance analysis
type RuntimeAnalysis struct {
	CPUUsage      float64 `json:"cpu_usage,omitempty"`
	MemoryUsage   int64   `json:"memory_usage,omitempty"`
	ExecutionTime float64 `json:"execution_time,omitempty"`
	Available     bool    `json:"available"`
}

// Optimizations represents applied optimizations
type Optimizations struct {
	CompilerFlagsAdded   []string `json:"compiler_flags_added"`
	BuildConfigsUpdated  []string `json:"build_configs_updated"`
	CodeSuggestions      []string `json:"code_suggestions"`
	Applied              bool     `json:"applied"`
	Note                 string   `json:"note"`
}

// BenchmarkResults represents benchmark results
type BenchmarkResults struct {
	Available   bool                   `json:"available"`
	Results     map[string]interface{} `json:"results"`
	Comparisons map[string]interface{} `json:"comparisons"`
}
