package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/fatih/color"
	"github.com/jedib0t/go-pretty/v6/table"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"github.com/m2arm/cli/internal/scanner"
	"github.com/m2arm/cli/internal/sdk"
)

var (
	scanPath      string
	scanRecursive bool
	scanOutput    string
)

// scanCmd represents the scan command
var scanCmd = &cobra.Command{
	Use:   "scan [path]",
	Short: "Scan code for x86-specific instructions and dependencies",
	Long: `Scan analyzes your codebase for x86-specific instructions, inline assembly,
architecture-dependent code, and platform-specific dependencies that may need
attention when migrating to ARM.

The scan will identify:
• Inline assembly code
• x86 SIMD intrinsics (SSE, AVX, etc.)
• Architecture-specific #ifdef blocks
• Platform-specific API calls
• Dependencies that may not support ARM

Examples:
  m2arm scan .
  m2arm scan /path/to/project --recursive
  m2arm scan . --output json
  m2arm scan . --output table`,
	Args: cobra.MaximumNArgs(1),
	RunE: runScan,
}

func init() {
	rootCmd.AddCommand(scanCmd)

	scanCmd.Flags().BoolVarP(&scanRecursive, "recursive", "r", true, "recursively scan subdirectories")
	scanCmd.Flags().StringVar(&scanOutput, "format", "table", "output format: table, json, summary")

	// Bind flags
	viper.BindPFlag("scan.recursive", scanCmd.Flags().Lookup("recursive"))
	viper.BindPFlag("scan.format", scanCmd.Flags().Lookup("format"))
}

func runScan(cmd *cobra.Command, args []string) error {
	// Determine scan path
	if len(args) > 0 {
		scanPath = args[0]
	} else {
		scanPath = "."
	}

	// Convert to absolute path
	absPath, err := filepath.Abs(scanPath)
	if err != nil {
		return fmt.Errorf("invalid path: %w", err)
	}

	// Check if path exists
	if _, err := os.Stat(absPath); os.IsNotExist(err) {
		return fmt.Errorf("path does not exist: %s", absPath)
	}

	if viper.GetBool("verbose") {
		color.Blue("🔍 Scanning project at: %s", absPath)
	}

	// Initialize scanner
	scanner := scanner.New(absPath, map[string]interface{}{
		"recursive": scanRecursive,
		"verbose":   viper.GetBool("verbose"),
	})

	// Perform scan
	results, err := scanner.Scan()
	if err != nil {
		return fmt.Errorf("scan failed: %w", err)
	}

	// Output results
	switch scanOutput {
	case "json":
		return outputJSON(results)
	case "summary":
		return outputSummary(results)
	case "table":
		fallthrough
	default:
		return outputTable(results)
	}
}

func outputJSON(results *sdk.ScanResults) error {
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	return encoder.Encode(results)
}

func outputSummary(results *sdk.ScanResults) error {
	color.Green("📊 Scan Summary")
	fmt.Printf("  Total files: %d\n", results.TotalFiles)
	fmt.Printf("  Scanned files: %d\n", results.ScannedFiles)
	fmt.Printf("  Issues found: %d\n", len(results.Issues))
	fmt.Printf("  Dependencies: %d\n", len(results.Dependencies))
	fmt.Printf("  Build systems: %d\n", len(results.BuildSystems))

	if len(results.Issues) > 0 {
		fmt.Println("\n🔴 Issue Categories:")
		categories := make(map[string]int)
		for _, issue := range results.Issues {
			categories[issue.Category]++
		}
		for category, count := range categories {
			fmt.Printf("  %s: %d\n", category, count)
		}
	}

	if len(results.Recommendations) > 0 {
		fmt.Println("\n💡 Recommendations:")
		for _, rec := range results.Recommendations {
			fmt.Printf("  • %s\n", rec)
		}
	}

	return nil
}

func outputTable(results *sdk.ScanResults) error {
	// Header
	color.Green("🔍 M2ARM Code Scan Results")
	fmt.Printf("Scanned %d files in %s\n\n", results.ScannedFiles, time.Now().Format("2006-01-02 15:04:05"))

	// Issues table
	if len(results.Issues) > 0 {
		color.Yellow("🚨 Found %d compatibility issues:", len(results.Issues))
		
		t := table.NewWriter()
		t.SetOutputMirror(os.Stdout)
		t.AppendHeader(table.Row{"File", "Line", "Category", "Severity", "Issue"})

		for _, issue := range results.Issues {
			severity := issue.Severity
			if severity == "high" {
				severity = color.RedString("🔴 HIGH")
			} else if severity == "medium" {
				severity = color.YellowString("🟡 MEDIUM")
			} else {
				severity = color.GreenString("🟢 LOW")
			}

			// Truncate long file paths
			file := issue.File
			if len(file) > 40 {
				file = "..." + file[len(file)-37:]
			}

			// Truncate matched text
			matchedText := issue.MatchedText
			if len(matchedText) > 30 {
				matchedText = matchedText[:27] + "..."
			}

			t.AppendRow(table.Row{
				file,
				issue.Line,
				issue.Category,
				severity,
				matchedText,
			})
		}

		t.SetStyle(table.StyleColoredBright)
		t.Render()
		fmt.Println()
	} else {
		color.Green("✅ No obvious compatibility issues found!")
		fmt.Println()
	}

	// Dependencies
	if len(results.Dependencies) > 0 {
		color.Cyan("📦 Dependencies found: %d", len(results.Dependencies))
		
		t := table.NewWriter()
		t.SetOutputMirror(os.Stdout)
		t.AppendHeader(table.Row{"Name", "Version", "Type", "ARM Support"})

		for _, dep := range results.Dependencies {
			armSupport := dep.ARMCompatible
			if armSupport == "unknown" {
				armSupport = color.YellowString("❓ Unknown")
			} else if armSupport == "yes" {
				armSupport = color.GreenString("✅ Yes")
			} else {
				armSupport = color.RedString("❌ No")
			}

			t.AppendRow(table.Row{
				dep.Name,
				dep.Version,
				dep.Type,
				armSupport,
			})
		}

		t.SetStyle(table.StyleColoredBright)
		t.Render()
		fmt.Println()
	}

	// Build systems
	if len(results.BuildSystems) > 0 {
		color.Magenta("🔧 Build systems detected:")
		for _, bs := range results.BuildSystems {
			status := "✅"
			if bs.NeedsReview {
				status = "⚠️ "
			}
			fmt.Printf("  %s %s (%s)\n", status, bs.File, bs.System)
		}
		fmt.Println()
	}

	// Recommendations
	if len(results.Recommendations) > 0 {
		color.Blue("💡 Recommendations:")
		for _, rec := range results.Recommendations {
			fmt.Printf("  %s\n", rec)
		}
		fmt.Println()
	}

	// Next steps
	if len(results.Issues) > 0 {
		color.Blue("🚀 Next Steps:")
		fmt.Println("  1. Run 'm2arm plan' to create a migration strategy")
		fmt.Println("  2. Review high-severity issues first")
		fmt.Println("  3. Check dependency ARM compatibility")
		fmt.Println("  4. Update build system configurations")
	}

	return nil
}
