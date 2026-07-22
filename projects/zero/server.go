package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"net/http"
	"fmt"
)
func main() {
	var _ = sql.Open
	var _ = os.Getenv
	var _ = json.Marshal
	
	fmt.Println("Starting server on port 8080...")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		fmt.Println("Server error:", err)
	}
}
