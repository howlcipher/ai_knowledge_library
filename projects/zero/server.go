package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

func main() {
	var _ = sql.Open
	var _ = os.Getenv
	var _ = json.Marshal
	var _ = io.ReadAll
	var _ = http.DefaultClient
	{
		body, err := func() ([]byte, error) {
			req, err := http.NewRequest("GET", "https://api.example.com", nil)
			if err != nil {
				return nil, err
			}
			resp, err := http.DefaultClient.Do(req)
			if err != nil {
				return nil, err
			}
			defer resp.Body.Close()
			return io.ReadAll(resp.Body)
		}()
		if err != nil {
			fmt.Println("Error:", err)
		} else {
			_ = body
			fmt.Println("Fetched bytes:", body)
		}
	}
}
