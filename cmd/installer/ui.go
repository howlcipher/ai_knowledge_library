package main

import (
	"fmt"
	"github.com/charmbracelet/huh"
)

// LaunchUI prompts the user to select the Web UI or TUI, and launches the corresponding tool.
func (i *Installer) LaunchUI() {
	var uiType string
	form := huh.NewForm(
		huh.NewGroup(
			huh.NewSelect[string]().
				Title("Select User Interface").
				Description("Choose which interface you would like to use:").
				Options(
					huh.NewOption("Terminal UI (TUI) - Fast, terminal-based, local LLM execution", "tui"),
					huh.NewOption("Web UI (Streamlit) - Rich, browser-based sandboxed interface", "web"),
				).
				Value(&uiType),
		),
	)

	if err := form.Run(); err != nil {
		fmt.Println("UI selection aborted.")
		return
	}

	fmt.Println("\n========================================")
	if uiType == "tui" {
		fmt.Println("Launching Terminal UI (TUI)...")
		err := i.runInteractiveCommand("python3", "tools/tui.py")
		if err != nil {
			err = i.runInteractiveCommand("python", "tools/tui.py")
		}
	} else if uiType == "web" {
		fmt.Println("Launching Web UI (Streamlit)...")
		err := i.runInteractiveCommand("python3", "-m", "streamlit", "run", "tools/web_ui.py")
		if err != nil {
			err = i.runInteractiveCommand("python", "-m", "streamlit", "run", "tools/web_ui.py")
		}
	}
	fmt.Println("========================================")
}
