package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/fatih/color"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"github.com/m2arm/cli/internal/sdk"
)

var (
	planTarget string
	planOutput string
)

// planCmd represents the plan command
var planCmd = &cobra.Command{
	Use:   "plan [path]",
	Short: "Create a migration plan for ARM architecture",
	Long: `Plan analyzes scan results and creates a detailed migration plan
for moving your application to ARM architecture.

The plan includes:
• Ordered migration steps with confidence levels
• Build system configuration changes
• Dependency compatibility updates
• Testing strategy recommendations
• Effort estimation

Examples:
  m2arm plan .
  m2arm plan --target arm64
  m2arm plan . --output json
  m2arm plan /path/to/project --target armv7`,
	Args: cobra.MaximumNArgs(1),
	RunE: runPlan,
}

func init() {
	rootCmd.AddCommand(planCmd)

	planCmd.Flags().StringVarP(&planTarget, "target", "t", "arm64", "target ARM architecture (arm64, armv7)")
	planCmd.Flags().StringVar(&planOutput, "format", "text", "output format: text, json")

	// Bind flags
	viper.BindPFlag("plan.target", planCmd.Flags().Lookup("target"))
	viper.BindPFlag("plan.format", planCmd.Flags().Lookup("format"))
}

func runPlan(cmd *cobra.Command, args []string) error {
	// Determine project path
	projectPath := "."
	if len(args) > 0 {
		projectPath = args[0]
	}

	// Convert to absolute path
	absPath, err := filepath.Abs(projectPath)
	if err != nil {
		return fmt.Errorf("invalid path: %w", err)
	}

	if viper.GetBool("verbose") {
		color.Blue("📋 Creating migration plan for: %s", absPath)
		color.Blue("🎯 Target architecture: %s", planTarget)
	}

	// Create a mock migration plan (in real implementation, this would use the SDK)
	plan := createMockMigrationPlan(planTarget)

	// Output results
	switch planOutput {
	case "json":
		return outputPlanJSON(plan)
	case "text":
		fallthrough
	default:
		return outputPlanText(plan)
	}
}

func createMockMigrationPlan(target string) *sdk.MigrationPlan {
	return &sdk.MigrationPlan{
		TargetArchitecture: target,
		CreatedAt:         time.Now(),
		TotalIssues:       3,
		EstimatedEffort:   "medium",
		Steps: []sdk.MigrationStep{
			{
				ID:          1,
				Type:        "file_migration",
				File:        "src/math_utils.c",
				IssuesCount: 2,
				Changes: []sdk.CodeChange{
					{
						Line:        42,
						Category:    "x86_intrinsics",
						Original:    "_mm_add_ps(a, b)",
						Replacement: "vaddq_f32(a, b)",
						Confidence:  "high",
					},
					{
						Line:        56,
						Category:    "x86_intrinsics",
						Original:    "_mm_mul_ps(x, y)",
						Replacement: "vmulq_f32(x, y)",
						Confidence:  "high",
					},
				},
			},
			{
				ID:          2,
				Type:        "file_migration",
				File:        "src/platform.h",
				IssuesCount: 1,
				Changes: []sdk.CodeChange{
					{
						Line:        15,
						Category:    "architecture_checks",
						Original:    "#ifdef __x86_64__",
						Replacement: "#if defined(__x86_64__) || defined(__aarch64__)",
						Confidence:  "high",
					},
				},
			},
		},
		BuildSystemChanges: []sdk.BuildSystemChange{
			{
				File:   "CMakeLists.txt",
				System: "cmake",
				Changes: []string{
					"Add ARM64 target support",
					"Set CMAKE_SYSTEM_PROCESSOR for cross-compilation",
					"Add ARM-specific compiler flags",
					"Update architecture detection logic",
				},
			},
		},
		DependencyUpdates: []sdk.DependencyUpdate{
			{
				Name:           "numpy",
				CurrentVersion: "1.21.0",
				Type:           "python",
				Action:         "verify_arm_support",
				Notes:          []string{"Check for ARM wheel availability"},
			},
		},
		TestingStrategy: sdk.TestingStrategy{
			UnitTests: sdk.TestConfig{
				Required:   true,
				Platforms:  []string{target, "x86_64"},
				FocusAreas: []string{"math operations", "memory access", "SIMD code"},
			},
			IntegrationTests: sdk.TestConfig{
				Required:     true,
				Environments: []string{"native_arm", "emulated_arm", "cross_platform"},
			},
			PerformanceTests: sdk.TestConfig{
				Required:   true,
				Metrics:    []string{"execution_time", "memory_usage", "power_consumption"},
				Comparison: "x86_64",
			},
		},
	}
}

func outputPlanJSON(plan *sdk.MigrationPlan) error {
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	return encoder.Encode(plan)
}

func outputPlanText(plan *sdk.MigrationPlan) error {
	// Header
	color.Green("📋 M2ARM Migration Plan")
	fmt.Printf("Target: %s | Created: %s | Effort: %s\n\n",
		plan.TargetArchitecture,
		plan.CreatedAt.Format("2006-01-02 15:04:05"),
		plan.EstimatedEffort)

	// Migration Steps
	if len(plan.Steps) > 0 {
		color.Yellow("🔧 Migration Steps (%d issues to resolve):", plan.TotalIssues)
		
		for _, step := range plan.Steps {
			fmt.Printf("\n  Step %d: %s\n", step.ID, step.File)
			fmt.Printf("    Issues: %d\n", step.IssuesCount)
			
			for _, change := range step.Changes {
				confidenceIcon := "🟢"
				if change.Confidence == "medium" {
					confidenceIcon = "🟡"
				} else if change.Confidence == "low" {
					confidenceIcon = "🔴"
				}
				
				fmt.Printf("    %s Line %d (%s): %s\n",
					confidenceIcon, change.Line, change.Category, change.Original)
				fmt.Printf("      → %s\n", change.Replacement)
			}
		}
		fmt.Println()
	}

	// Build System Changes
	if len(plan.BuildSystemChanges) > 0 {
		color.Cyan("🏗️  Build System Changes:")
		
		for _, buildChange := range plan.BuildSystemChanges {
			fmt.Printf("\n  %s (%s):\n", buildChange.File, buildChange.System)
			for _, change := range buildChange.Changes {
				fmt.Printf("    • %s\n", change)
			}
		}
		fmt.Println()
	}

	// Dependency Updates
	if len(plan.DependencyUpdates) > 0 {
		color.Magenta("📦 Dependency Updates:")
		
		for _, dep := range plan.DependencyUpdates {
			fmt.Printf("\n  %s (%s) - %s:\n", dep.Name, dep.CurrentVersion, dep.Action)
			for _, note := range dep.Notes {
				fmt.Printf("    • %s\n", note)
			}
		}
		fmt.Println()
	}

	// Testing Strategy
	color.Blue("🧪 Testing Strategy:")
	
	if plan.TestingStrategy.UnitTests.Required {
		fmt.Printf("\n  Unit Tests:\n")
		fmt.Printf("    Platforms: %v\n", plan.TestingStrategy.UnitTests.Platforms)
		fmt.Printf("    Focus Areas: %v\n", plan.TestingStrategy.UnitTests.FocusAreas)
	}
	
	if plan.TestingStrategy.IntegrationTests.Required {
		fmt.Printf("\n  Integration Tests:\n")
		fmt.Printf("    Environments: %v\n", plan.TestingStrategy.IntegrationTests.Environments)
	}
	
	if plan.TestingStrategy.PerformanceTests.Required {
		fmt.Printf("\n  Performance Tests:\n")
		fmt.Printf("    Metrics: %v\n", plan.TestingStrategy.PerformanceTests.Metrics)
		fmt.Printf("    Baseline: %s\n", plan.TestingStrategy.PerformanceTests.Comparison)
	}

	// Next Steps
	fmt.Println()
	color.Blue("🚀 Next Steps:")
	fmt.Println("  1. Review the migration plan carefully")
	fmt.Println("  2. Run 'm2arm migrate --dry-run' to simulate changes")
	fmt.Println("  3. Execute migration with 'm2arm migrate --apply'")
	fmt.Println("  4. Cross-compile with 'm2arm compile'")
	fmt.Println("  5. Test on ARM targets with 'm2arm test'")

	return nil
}
