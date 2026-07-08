package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/charmbracelet/huh"
	"github.com/spf13/cobra"
)

const (
	DefaultRepoURL = "https://github.com/howlcipher/ai_knowledge_library"
	DefaultDirName = "ai_knowledge_library"
)

// Installer encapsulates the setup process.
type Installer struct {
	RepoURL     string
	DestPath    string
	InstallDeps bool
	SetupDocs   bool
	LinkGlobal  bool
	Language    string
}

// NewInstaller creates a new Installer instance with defaults.
func NewInstaller() *Installer {
	home, err := os.UserHomeDir()
	if err != nil {
		home = "."
	}
	return &Installer{
		RepoURL:  DefaultRepoURL,
		DestPath: filepath.Join(home, DefaultDirName),
		Language: "en_US",
	}
}

func (i *Installer) runInteractiveCommand(name string, args ...string) error {
	/* #nosec G204 -- Installer executes user-approved git/python commands */
	cmd := exec.Command(name, args...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

// IsRepoRoot checks if the current directory is the root of the library.
func (i *Installer) IsRepoRoot() bool {
	_, err := os.Stat(".agents")
	return err == nil
}

// CloneRepo clones the repository into the designated destination.
func (i *Installer) CloneRepo() error {
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("Repository Not Found").
				Description("You are running the installer outside the library directory. Let's download it."),
			huh.NewInput().
				Title("Repository URL").
				Value(&i.RepoURL),
			huh.NewInput().
				Title("Destination Path").
				Value(&i.DestPath),
		),
	)

	if err := form.Run(); err != nil {
		return err
	}

	fmt.Printf("Cloning %s into %s...\n", i.RepoURL, i.DestPath)
	err := i.runInteractiveCommand("git", "clone", i.RepoURL, i.DestPath)

	if err != nil {
		fmt.Printf("\nClone failed: %v\n", err)
		return fmt.Errorf("failed to clone repository")
	}

	if err := os.Chdir(i.DestPath); err != nil {
		return fmt.Errorf("failed to change directory to %s: %w", i.DestPath, err)
	}
	return nil
}

// SyncRepo updates the repository via git pull.
func (i *Installer) SyncRepo() {
	var currentRemote string
	out, err := exec.Command("git", "config", "--get", "remote.origin.url").Output()
	if err == nil {
		currentRemote = strings.TrimSpace(string(out))
	}

	var newRemote string = currentRemote
	if newRemote == "" {
		newRemote = i.RepoURL
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
			/* #nosec G204 -- Installer modifies git remote using validated input */
			_ = exec.Command("git", "remote", "set-url", "origin", newRemote).Run()
		} else {
			/* #nosec G204 -- Installer modifies git remote using validated input */
			_ = exec.Command("git", "remote", "add", "origin", newRemote).Run()
		}
	}

	fmt.Println("Fetching latest changes...")
	err = i.runInteractiveCommand("git", "pull", "origin", "main")
	if err != nil {
		fmt.Printf("Error syncing repository: %v\n", err)
	} else {
		fmt.Println("Repository is up to date!")
	}
}

// Uninstall safely removes the symlinks for the library skills and rules.
func (i *Installer) Uninstall() {
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
	home, _ := os.UserHomeDir()
	agyDir := filepath.Join(home, ".gemini", "antigravity-cli")

	skillsDir := filepath.Join(agyDir, "skills")
	rulesDir := filepath.Join(agyDir, "rules")

	sourceSkills := ".agents/skills"
	sourceRules := ".agents/rules"

	entries, _ := os.ReadDir(sourceSkills)
	for _, entry := range entries {
		if entry.IsDir() {
			target := filepath.Join(skillsDir, entry.Name())
			_ = os.RemoveAll(target)
			fmt.Println("Removed skill link:", target)
		}
	}

	entries, _ = os.ReadDir(sourceRules)
	for _, entry := range entries {
		if !entry.IsDir() {
			target := filepath.Join(rulesDir, entry.Name())
			_ = os.Remove(target)
			fmt.Println("Removed rule link:", target)
		}
	}

	fmt.Println("Uninstall complete. The repository files remain on your disk; delete the directory manually if desired.")
}

// SelectLanguage prompts the user to select their language at startup.
func (i *Installer) SelectLanguage() {
	var lang string = i.Language
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewSelect[string]().
				Title("Select Language / 言語を選択 / 选择语言").
				Options(
					huh.NewOption("US English", "en_US"),
					huh.NewOption("Japanese (日本語)", "ja_JP"),
					huh.NewOption("Chinese Simplified (简体中文)", "zh_CN"),
					huh.NewOption("Spanish (Español)", "es_ES"),
					huh.NewOption("German (Deutsch)", "de_DE"),
					huh.NewOption("French (Français)", "fr_FR"),
					huh.NewOption("Russian (Русский)", "ru_RU"),
					huh.NewOption("Korean (한국어)", "ko_KR"),
					huh.NewOption("Hindi (हिन्दी)", "hi_IN"),
					huh.NewOption("Arabic (العربية)", "ar_SA"),
				).
				Value(&lang),
		),
	)
	_ = form.Run()
	i.Language = lang
}

// CustomizeProfile walks the user through setting up a personalized profile.
func (i *Installer) CustomizeProfile() {
	var name, email, linkedin, github, summary, uiPreference, agentMode string
	var langPreference = i.Language

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("Customize User Profile").
				Description("Generates a custom USER_PROFILE.md. All fields are optional. Rerun anytime to update."),
			huh.NewInput().Title("Full Name (optional)").Value(&name),
			huh.NewInput().Title("Email (optional)").Value(&email),
			huh.NewInput().Title("LinkedIn URL (optional)").Value(&linkedin),
			huh.NewInput().Title("GitHub Username (optional)").Value(&github),
			huh.NewText().Title("Professional Summary (optional)").Value(&summary),
		),
	)

	if err := form.Run(); err != nil {
		fmt.Println("Customization aborted.")
		return
	}

	if name == "" {
		name = "Anonymous"
	}

	content := fmt.Sprintf(`---
name: %s
preferred_ui: %s
agent_mode: %s
language_module: %s
---

# %s User Profile
`, name, uiPreference, agentMode, langPreference, name)

	if email != "" || linkedin != "" || github != "" {
		content += "\n## Contact and Links\n"
		if email != "" {
			content += fmt.Sprintf("* Email: %s\n", email)
		}
		if linkedin != "" {
			content += fmt.Sprintf("* LinkedIn: %s\n", linkedin)
		}
		if github != "" {
			content += fmt.Sprintf("* GitHub: github.com/%s\n", github)
		}
	}

	content += "\n## Professional Summary\n"
	if summary != "" {
		content += fmt.Sprintf("%s\n", summary)
	} else {
		content += "Add your professional summary here.\n"
	}

	content += "\n## Core Skills\n* Add your core skills here.\n\n## Professional Experience\n* Add your experience here.\n\n## Education and Certifications\n* Add your education here.\n"

	err := os.WriteFile("USER_PROFILE.md", []byte(content), 0600)
	if err != nil {
		fmt.Println("Failed to save profile:", err)
		return
	}

	i.Language = langPreference
	fmt.Println("\nSuccessfully generated your custom USER_PROFILE.md!")
}

// ShowHelp displays an interactive FAQ and troubleshooting guide.
func (i *Installer) ShowHelp() {
	var category string
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewSelect[string]().
				Title("Help & Troubleshooting FAQ").
				Description("Select a topic for immediate solutions").
				Options(
					huh.NewOption("Python Virtual Environment (venv) Errors", "venv"),
					huh.NewOption("Git Rebase / Conflict Errors", "git"),
					huh.NewOption("Go Binary Build Errors", "go"),
					huh.NewOption("Go back to Main Menu", "back"),
				).
				Value(&category),
		),
	)

	if err := form.Run(); err != nil {
		return
	}

	fmt.Println("\n========================================")
	switch category {
	case "venv":
		fmt.Println("VENV ERRORS:")
		fmt.Println("- Ensure you run `source venv/bin/activate` before using python tools.")
		fmt.Println("- If pdoc or pytest is missing, run `pip install -r requirements.txt` again.")
	case "git":
		fmt.Println("GIT ERRORS:")
		fmt.Println("- If you get a 'divergent branches' error, run `git pull --rebase`.")
		fmt.Println("- Automated badge updates may cause this if you push simultaneously.")
	case "go":
		fmt.Println("GO ERRORS:")
		fmt.Println("- You need Go version 1.22+. Run `go version` to check.")
		fmt.Println("- If 'go run' fails, try 'go mod tidy' to sync dependencies.")
	}
	fmt.Println("========================================")
}

// Install runs the setup processes based on user input.
func (i *Installer) Install() {
	i.InstallDeps = true
	i.SetupDocs = false
	i.LinkGlobal = true

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewConfirm().
				Title("Install Python dependencies?").
				Description("Installs requirements.txt (pytest, google-api, etc).").
				Value(&i.InstallDeps),
			huh.NewConfirm().
				Title("Set up Google Docs integration? (Optional)").
				Description("Requires a Google Cloud OAuth Client ID (credentials.json).").
				Value(&i.SetupDocs),
			huh.NewConfirm().
				Title("Link skills and rules globally?").
				Description("Makes this library's rules available to all your AI agents.").
				Value(&i.LinkGlobal),
		),
	)

	if err := form.Run(); err != nil {
		fmt.Println("Installation aborted.")
		return
	}

	fmt.Println("\n========================================")
	fmt.Println("Starting installation...")
	fmt.Println("========================================")

	if i.InstallDeps {
		fmt.Println("\n[+] Installing Python dependencies...")
		err := i.runInteractiveCommand("pip3", "install", "-r", "requirements.txt")
		if err != nil {
			err = i.runInteractiveCommand("pip", "install", "-r", "requirements.txt")
		}
		if err != nil {
			fmt.Println("Failed to install dependencies. Please install Python and pip from python.org.")
		} else {
			fmt.Println("Dependencies installed successfully.")
		}
	}

	if i.SetupDocs {
		fmt.Println("\n[+] Setting up Google Docs integration...")
		err := i.runInteractiveCommand("python3", "scripts/setup_google_docs_auth.py")
		if err != nil {
			err = i.runInteractiveCommand("python", "scripts/setup_google_docs_auth.py")
		}
		if err != nil {
			fmt.Println("Google Docs setup encountered an error or was aborted.")
		}
	}

	if i.LinkGlobal {
		fmt.Println("\n[+] Linking skills and rules globally...")
		var err error
		if runtime.GOOS == "windows" {
			err = i.runInteractiveCommand("powershell", "-ExecutionPolicy", "Bypass", "-File", filepath.Join("scripts", "install_global.ps1"))
		} else {
			err = i.runInteractiveCommand("bash", filepath.Join("scripts", "install_global.sh"))
		}
		if err != nil {
			fmt.Println("Failed to link globally:", err)
		} else {
			fmt.Println("Global linking complete.")
		}
	}

	fmt.Println("\n========================================")
	fmt.Println("Installation finished successfully!")

	if i.Language != "en_US" {
		fmt.Println("\n[!] Triggering AI Language Translation for project files...")
		_ = i.runInteractiveCommand("python3", "scripts/translate_project.py", "--lang", i.Language)
	}
}

func interactiveMenu(installer *Installer) {
	installer.SelectLanguage()

	var action string
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title(T(installer.Language, "Title")).
				Description("Manage your local AI environment."),
			huh.NewSelect[string]().
				Title(T(installer.Language, "MenuTitle")).
				Options(
					huh.NewOption("Launch RAG Interface (TUI/Web)", "launch_ui"),
					huh.NewOption(T(installer.Language, "Install"), "install"),
					huh.NewOption(T(installer.Language, "Customize"), "customize"),
					huh.NewOption(T(installer.Language, "Sync"), "sync"),
					huh.NewOption(T(installer.Language, "Uninstall"), "uninstall"),
					huh.NewOption(T(installer.Language, "Help"), "help"),
					huh.NewOption(T(installer.Language, "Exit"), "exit"),
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
	case "launch_ui":
		installer.LaunchUI()
	case "install":
		installer.Install()
	case "customize":
		installer.CustomizeProfile()
	case "sync":
		installer.SyncRepo()
	case "uninstall":
		installer.Uninstall()
	case "help":
		installer.ShowHelp()
		interactiveMenu(installer) // Restart loop
	}
}

func main() {
	installer := NewInstaller()

	var rootCmd = &cobra.Command{
		Use:   "ai_installer",
		Short: "AI Knowledge Library Installer",
		Run: func(cmd *cobra.Command, args []string) {
			if !installer.IsRepoRoot() {
				if err := installer.CloneRepo(); err != nil {
					fmt.Println("Error:", err)
					os.Exit(1)
				}
			}
			interactiveMenu(installer)
		},
	}

	var installCmd = &cobra.Command{
		Use:   "install",
		Short: "Install the AI environment and dependencies",
		Run: func(cmd *cobra.Command, args []string) {
			installer.Install()
		},
	}

	var customizeCmd = &cobra.Command{
		Use:   "customize",
		Short: "Customize your USER_PROFILE.md",
		Run: func(cmd *cobra.Command, args []string) {
			installer.CustomizeProfile()
		},
	}

	var syncCmd = &cobra.Command{
		Use:   "sync",
		Short: "Sync and update the repository",
		Run: func(cmd *cobra.Command, args []string) {
			installer.SyncRepo()
		},
	}

	var uninstallCmd = &cobra.Command{
		Use:   "uninstall",
		Short: "Uninstall global AGY links",
		Run: func(cmd *cobra.Command, args []string) {
			installer.Uninstall()
		},
	}

	rootCmd.AddCommand(installCmd, customizeCmd, syncCmd, uninstallCmd)

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}
