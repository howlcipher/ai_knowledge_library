package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
)
func main() {
	var _ = sql.Open
	var _ = os.Getenv
	var _ = json.Marshal
		fmt.Println("Hello, World!")
		{
			name := "Zero"
			_ = name
		fmt.Println("Welcome to", name)
		}
}
