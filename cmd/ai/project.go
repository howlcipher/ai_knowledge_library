package main

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/howlcipher/howlplane/internal/project"
	"github.com/spf13/cobra"
)

var projectCmd = &cobra.Command{
	Use:   "project",
	Short: "Manage and inspect project integrations",
}

var projectValidateCmd = &cobra.Command{
	Use:   "validate [path]",
	Short: "Validate the project manifest and local integration",
	Run: func(cmd *cobra.Command, args []string) {
		startDir := "."
		if len(args) > 0 {
			startDir = args[0]
		}

		root, err := project.DiscoverRoot(startDir)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error discovering project root: %v\n", err)
			os.Exit(1)
		}

		manifestPath := filepath.Join(root, ".ai-project.toml")
		fmt.Printf("Validating manifest at %s\n", manifestPath)

		manifest, err := project.LoadManifest(manifestPath)
		if err != nil {
			if os.IsNotExist(err) {
				fmt.Fprintf(os.Stderr, "Manifest file not found at project root: %s\n", manifestPath)
			} else {
				fmt.Fprintf(os.Stderr, "Manifest validation failed:\n%v\n", err)
			}
			os.Exit(1)
		}

		fmt.Println("Manifest loaded successfully:")
		fmt.Printf("  Project Name: %s\n", manifest.Name)
		fmt.Printf("  Schema Version: %d\n", manifest.SchemaVersion)
		fmt.Println("Validation passed.")
	},
}

func init() {
	rootCmd.AddCommand(projectCmd)
	projectCmd.AddCommand(projectValidateCmd)
}
