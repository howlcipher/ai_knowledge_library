package main

import (
	"context"
	"fmt"

	"github.com/mark3labs/mcp-go/mcp"
	"github.com/mark3labs/mcp-go/server"
)

func handleListContainers(client DockerClient) server.ToolHandlerFunc {
	return func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		output, err := client.ListContainers(ctx)
		if err != nil {
			return nil, fmt.Errorf("failed to list containers: %v", err)
		}
		return mcp.NewToolResultText(output), nil
	}
}

func handleGetContainerLogs(client DockerClient) server.ToolHandlerFunc {
	return func(ctx context.Context, request mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		containerID := request.GetString("container_id", "")
		if containerID == "" {
			return mcp.NewToolResultError("container_id must be a string"), nil
		}
		output, err := client.GetContainerLogs(ctx, containerID)
		if err != nil {
			return mcp.NewToolResultError(fmt.Sprintf("failed to get logs: %v", err)), nil
		}
		return mcp.NewToolResultText(output), nil
	}
}

func RegisterTools(s *server.MCPServer, client DockerClient) {
	listTool := mcp.NewTool("list_containers",
		mcp.WithDescription("List all docker containers on the homelab host"),
	)
	s.AddTool(listTool, handleListContainers(client))

	logsTool := mcp.NewTool("get_container_logs",
		mcp.WithDescription("Get the last 100 lines of logs for a container"),
		mcp.WithString("container_id", mcp.Required(), mcp.Description("The ID or name of the container")),
	)
	s.AddTool(logsTool, handleGetContainerLogs(client))
}
