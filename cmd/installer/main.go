package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/charmbracelet/huh"
)

func runInteractiveCommand(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func isRepoRoot() bool {
	_, err := os.Stat(".agents")
	return err == nil
}

func getHomeDir() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return "."
	}
	return home
}

func cloneRepo() error {
	var repoURL string = "https://github.com/howlcipher/ai_knowledge_library"
	var destPath string = filepath.Join(getHomeDir(), "ai_knowledge_library")

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("Repository Not Found").
				Description("You are running the installer outside the library directory. Let's download it."),
			huh.NewInput().
				Title("Repository URL").
				Value(&repoURL),
			huh.NewInput().
				Title("Destination Path").
				Value(&destPath),
		),
	)

	if err := form.Run(); err != nil {
		return err
	}

	fmt.Printf("\nCloning %s into %s...\n", repoURL, destPath)
	err := runInteractiveCommand("git", "clone", repoURL, destPath)
	if err != nil {
		return fmt.Errorf("failed to clone repository: %w", err)
	}

	// Change working directory to the newly cloned repo so the rest of the script works
	if err := os.Chdir(destPath); err != nil {
		return fmt.Errorf("failed to change directory to %s: %w", destPath, err)
	}
	return nil
}

func syncRepo() {
	var currentRemote string
	out, err := exec.Command("git", "config", "--get", "remote.origin.url").Output()
	if err == nil {
		currentRemote = strings.TrimSpace(string(out))
	}

	var newRemote string = currentRemote
	if newRemote == "" {
		newRemote = "https://github.com/howlcipher/ai_knowledge_library"
	}

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("Sync / Update").
				Description("Check for updates and verify repository source."),
			huh.NewInput().
				Title("Repository Remote Origin").
				Description("If you forked this repo, you can change the URL here.").
				Value(&newRemote),
		),
	)

	if err := form.Run(); err != nil {
		fmt.Println("Sync aborted.")
		return
	}

	if newRemote != currentRemote {
		fmt.Println("Updating remote origin...")
		if currentRemote != "" {
			_ = exec.Command("git", "remote", "set-url", "origin", newRemote).Run()
		} else {
			_ = exec.Command("git", "remote", "add", "origin", newRemote).Run()
		}
	}

	fmt.Println("Fetching latest changes...")
	err = runInteractiveCommand("git", "pull", "origin", "main")
	if err != nil {
		fmt.Println("Error syncing repository. You might have local changes or the branch might differ.")
	} else {
		fmt.Println("Repository is up to date!")
	}
}

func uninstall() {
	var confirm bool
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewConfirm().
				Title("Are you sure you want to uninstall?").
				Description("This will remove the global AGY links to skills and rules.").
				Value(&confirm),
		),
	)

	if err := form.Run(); err != nil || !confirm {
		fmt.Println("Uninstall aborted.")
		return
	}

	fmt.Println("Uninstalling global links...")
	agyDir := filepath.Join(getHomeDir(), ".gemini", "antigravity-cli")
	
	skillsDir := filepath.Join(agyDir, "skills")
	rulesDir := filepath.Join(agyDir, "rules")

	// Read source directories to know what to unlink
	sourceSkills := ".agents/skills"
	sourceRules := ".agents/rules"

	// Remove skills
	entries, _ := os.ReadDir(sourceSkills)
	for _, entry := range entries {
		if entry.IsDir() {
			target := filepath.Join(skillsDir, entry.Name())
			os.RemoveAll(target) // RemoveAll handles junctions on Windows and symlinks on Linux
			fmt.Println("Removed skill link:", target)
		}
	}

	// Remove rules
	entries, _ = os.ReadDir(sourceRules)
	for _, entry := range entries {
		if !entry.IsDir() {
			target := filepath.Join(rulesDir, entry.Name())
			os.Remove(target)
			fmt.Println("Removed rule link:", target)
		}
	}

	fmt.Println("Uninstall complete. The repository files remain on your disk; delete the directory manually if desired.")
}

func install() {
	var (
		installDeps    bool = true
		setupDocs      bool = false
		linkGlobal     bool = true
	)

	form := huh.NewForm(
		huh.NewGroup(
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
		return
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

func main() {
	// If the user downloaded the binary and runs it outside the repo, help them clone it first.
	if !isRepoRoot() {
		if err := cloneRepo(); err != nil {
			fmt.Println("Error:", err)
			os.Exit(1)
		}
	}

	var action string
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("AI Knowledge Library").
				Description("Manage your local AI environment."),
			huh.NewSelect[string]().
				Title("What would you like to do?").
				Options(
					huh.NewOption("Install / Setup Environment", "install"),
					huh.NewOption("Sync / Update Repository", "sync"),
					huh.NewOption("Uninstall Global Links", "uninstall"),
					huh.NewOption("Exit", "exit"),
				).
				Value(&action),
		),
	)

	err := form.Run()
	if err != nil || action == "exit" {
		fmt.Println("Goodbye!")
		os.Exit(0)
	}

	switch action {
	case "install":
		install()
	case "sync":
		syncRepo()
	case "uninstall":
		uninstall()
	}
}
