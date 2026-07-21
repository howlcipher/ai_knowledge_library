package main

import (
	"context"
	"strings"
	"testing"

	"github.com/mark3labs/mcp-go/mcp"
)

type MockDockerClient struct {
	ListContainersFn   func(ctx context.Context) (string, error)
	GetContainerLogsFn func(ctx context.Context, containerID string) (string, error)
}

func (m *MockDockerClient) ListContainers(ctx context.Context) (string, error) {
	if m.ListContainersFn != nil {
		return m.ListContainersFn(ctx)
	}
	return "container1\tnginx\tUp 2 days", nil
}

func (m *MockDockerClient) GetContainerLogs(ctx context.Context, containerID string) (string, error) {
	if m.GetContainerLogsFn != nil {
		return m.GetContainerLogsFn(ctx, containerID)
	}
	return "mock logs for " + containerID, nil
}

func TestHandleListContainers(t *testing.T) {
	client := &MockDockerClient{}
	handler := handleListContainers(client)

	req := mcp.CallToolRequest{}
	res, err := handler(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(res.Content) == 0 {
		t.Fatal("expected content")
	}

	textContent, ok := res.Content[0].(mcp.TextContent)
	if !ok {
		t.Fatal("expected text content")
	}

	if !strings.Contains(textContent.Text, "container1") {
		t.Errorf("expected output to contain container1, got %q", textContent.Text)
	}
}

func TestHandleGetContainerLogs(t *testing.T) {
	client := &MockDockerClient{}
	handler := handleGetContainerLogs(client)

	req := mcp.CallToolRequest{
		Params: mcp.CallToolParams{
			Name: "get_container_logs",
			Arguments: map[string]interface{}{
				"container_id": "my_container",
			},
		},
	}

	res, err := handler(context.Background(), req)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if len(res.Content) == 0 {
		t.Fatal("expected content")
	}

	textContent, ok := res.Content[0].(mcp.TextContent)
	if !ok {
		t.Fatal("expected text content")
	}

	if !strings.Contains(textContent.Text, "mock logs for my_container") {
		t.Errorf("expected output to contain mock logs for my_container, got %q", textContent.Text)
	}
}
