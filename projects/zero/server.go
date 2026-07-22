package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
)

func add(a int, b int) int {
	{
		c := (a + b)
		_ = c
		return c
	}
}

func main() {
	var _ = sql.Open
	var _ = os.Getenv
	var _ = json.Marshal
}
