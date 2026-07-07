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
	}
}

func (i *Installer) runInteractiveCommand(name string, args ...string) error {
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

	fmt.Printf("\nCloning %s into %s...\n", i.RepoURL, i.DestPath)
	err := i.runInteractiveCommand("git", "clone", i.RepoURL, i.DestPath)
	if err != nil {
		return fmt.Errorf("failed to clone repository: %w", err)
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
			_ = exec.Command("git", "remote", "set-url", "origin", newRemote).Run()
		} else {
			_ = exec.Command("git", "remote", "add", "origin", newRemote).Run()
		}
	}

	fmt.Println("Fetching latest changes...")
	err = i.runInteractiveCommand("git", "pull", "origin", "main")
	if err != nil {
		fmt.Println("Error syncing repository. You might have local changes or the branch might differ.")
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
			os.RemoveAll(target)
			fmt.Println("Removed skill link:", target)
		}
	}

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

// CustomizeProfile walks the user through setting up a personalized profile.
func (i *Installer) CustomizeProfile() {
	var name, email, linkedin, github, summary string

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewNote().
				Title("Customize User Profile").
				Description("This will generate a custom USER_PROFILE.md for your library."),
			huh.NewInput().Title("Full Name").Value(&name),
			huh.NewInput().Title("Email").Value(&email),
			huh.NewInput().Title("LinkedIn URL (optional)").Value(&linkedin),
			huh.NewInput().Title("GitHub Username (optional)").Value(&github),
			huh.NewText().Title("Professional Summary").Value(&summary),
		),
	)

	if err := form.Run(); err != nil {
		fmt.Println("Customization aborted.")
		return
	}

	content := fmt.Sprintf("# %s User Profile\n\n## Contact and Links\n* Email: %s\n", name, email)
	if linkedin != "" {
		content += fmt.Sprintf("* LinkedIn: %s\n", linkedin)
	}
	if github != "" {
		content += fmt.Sprintf("* GitHub: github.com/%s\n", github)
	}
	
	content += fmt.Sprintf("\n## Professional Summary\n%s\n\n## Core Skills\n* Add your core skills here.\n\n## Professional Experience\n* Add your experience here.\n\n## Education and Certifications\n* Add your education here.\n", summary)

	err := os.WriteFile("USER_PROFILE.md", []byte(content), 0644)
	if err != nil {
		fmt.Println("Failed to save profile:", err)
		return
	}
	
	fmt.Println("\nSuccessfully generated your custom USER_PROFILE.md!")
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
}

func main() {
	installer := NewInstaller()

	if !installer.IsRepoRoot() {
		if err := installer.CloneRepo(); err != nil {
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
					huh.NewOption("Customize Profile", "customize"),
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
		installer.Install()
	case "customize":
		installer.CustomizeProfile()
	case "sync":
		installer.SyncRepo()
	case "uninstall":
		installer.Uninstall()
	}
}
