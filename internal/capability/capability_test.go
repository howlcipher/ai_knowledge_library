package capability

import "testing"

func TestIsKnown(t *testing.T) {
	tests := []struct {
		name string
		cap  string
		want bool
	}{
		{"known filesystem capability", "filesystem:repository", true},
		{"known network capability", "network:allowlist", true},
		{"known git capability", "git:push", true},
		{"known secrets capability", "secrets:named_reference", true},
		{"unknown capability", "magic:allow", false},
		{"empty string", "", false},
		{"typo of known capability", "filesystem:Repository", false},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			if got := IsKnown(tc.cap); got != tc.want {
				t.Errorf("IsKnown(%q) = %v, want %v", tc.cap, got, tc.want)
			}
		})
	}
}
