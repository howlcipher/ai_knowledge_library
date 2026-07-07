package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"

	"github.com/charmbracelet/huh"
)

func runInteractiveCommand(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func main() {
	var (
		installDeps    bool = true
		setupDocs      bool = false
		linkGlobal     bool = true
	)

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("AI Knowledge Library Installer").
				Description("Welcome! Let's get your environment set up."),
			huh.NewConfirm().
				Title("Install Python dependencies?").
				Description("Installs requirements.txt (pytest, google-api, etc).").
				Value(&installDeps),
			huh.NewConfirm().
				Title("Set up Google Docs integration? (Optional)").
				Description("Requires a Google Cloud OAuth Client ID (credentials.json).").
				Value(&setupDocs),
			huh.NewConfirm().
				Title("Link skills and rules globally?").
				Description("Makes this library's rules available to all your AI agents.").
				Value(&linkGlobal),
		),
	)

	err := form.Run()
	if err != nil {
		fmt.Println("Installation aborted.")
		os.Exit(1)
	}

	fmt.Println("\n========================================")
	fmt.Println("Starting installation...")
	fmt.Println("========================================")

	if installDeps {
		fmt.Println("\n[+] Installing Python dependencies...")
		err := runInteractiveCommand("pip3", "install", "-r", "requirements.txt")
		if err != nil {
			err = runInteractiveCommand("pip", "install", "-r", "requirements.txt")
		}
		if err != nil {
			fmt.Println("Failed to install dependencies. Please install Python and pip from python.org.")
		} else {
			fmt.Println("Dependencies installed successfully.")
		}
	}

	if setupDocs {
		fmt.Println("\n[+] Setting up Google Docs integration...")
		err := runInteractiveCommand("python3", "scripts/setup_google_docs_auth.py")
		if err != nil {
			err = runInteractiveCommand("python", "scripts/setup_google_docs_auth.py")
		}
		if err != nil {
			fmt.Println("Google Docs setup encountered an error or was aborted.")
		}
	}

	if linkGlobal {
		fmt.Println("\n[+] Linking skills and rules globally...")
		var err error
		if runtime.GOOS == "windows" {
			err = runInteractiveCommand("powershell", "-ExecutionPolicy", "Bypass", "-File", filepath.Join("scripts", "install_global.ps1"))
		} else {
			err = runInteractiveCommand("bash", filepath.Join("scripts", "install_global.sh"))
		}
		if err != nil {
			fmt.Println("Failed to link globally:", err)
		} else {
			fmt.Println("Global linking complete.")
		}
	}

	fmt.Println("\n========================================")
	fmt.Println("Installation finished successfully!")
}
