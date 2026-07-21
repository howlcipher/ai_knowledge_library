package main

import (
	"fmt"
	"os"

	"github.com/mark3labs/mcp-go/server"
)

func main() {
	host := os.Getenv("HOMELAB_HOST")
	user := os.Getenv("HOMELAB_USER")
	if host == "" {
		host = "localhost"
	}
	if user == "" {
		user = "root"
	}

	client := &SSHDockerClient{
		Host: host,
		User: user,
	}

	s := server.NewMCPServer(
		"Homelab MCP Server",
		"1.0.0",
	)

	RegisterTools(s, client)

	fmt.Fprintln(os.Stderr, "Starting homelab MCP server over stdio...")
	if err := server.ServeStdio(s); err != nil {
		fmt.Fprintf(os.Stderr, "Server error: %v\n", err)
		os.Exit(1)
	}
}
