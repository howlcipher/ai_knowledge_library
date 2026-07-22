package main

import (
	"encoding/json"
	"fmt"
	"os"
	"unicode"
)

type TokenType string

const (
	TokenLParen TokenType = "LPAREN"
	TokenRParen TokenType = "RPAREN"
	TokenSymbol TokenType = "SYMBOL"
	TokenInt    TokenType = "INT"
	TokenString TokenType = "STRING"
	TokenEOF    TokenType = "EOF"
)

type Token struct {
	Type   TokenType
	Value  string
	Line   int
	Column int
}

type ErrorOutput struct {
	Reason string `json:"reason"`
	Line   int    `json:"line"`
	Column int    `json:"column"`
}

func reportError(reason string, line, column int) {
	errOut := ErrorOutput{Reason: reason, Line: line, Column: column}
	b, _ := json.Marshal(errOut)
	fmt.Println(string(b))
	os.Exit(1)
}

// Lexer
type Lexer struct {
	input  string
	pos    int
	line   int
	column int
}

func NewLexer(input string) *Lexer {
	return &Lexer{input: input, line: 1, column: 1}
}

func (l *Lexer) nextChar() rune {
	if l.pos >= len(l.input) {
		return 0
	}
	ch := rune(l.input[l.pos])
	l.pos++
	if ch == '\n' {
		l.line++
		l.column = 1
	} else {
		l.column++
	}
	return ch
}

func (l *Lexer) peekChar() rune {
	if l.pos >= len(l.input) {
		return 0
	}
	return rune(l.input[l.pos])
}

func (l *Lexer) NextToken() Token {
	for {
		ch := l.peekChar()
		if ch == 0 {
			return Token{Type: TokenEOF, Line: l.line, Column: l.column}
		}
		if unicode.IsSpace(ch) {
			l.nextChar()
			continue
		}
		break
	}

	startLine := l.line
	startCol := l.column
	ch := l.nextChar()

	if ch == '(' {
		return Token{Type: TokenLParen, Value: "(", Line: startLine, Column: startCol}
	}
	if ch == ')' {
		return Token{Type: TokenRParen, Value: ")", Line: startLine, Column: startCol}
	}
	if ch == '"' {
		val := ""
		for {
			nextCh := l.nextChar()
			if nextCh == 0 {
				reportError("Unterminated string", startLine, startCol)
			}
			if nextCh == '\\' {
				escapedCh := l.nextChar()
				if escapedCh == 0 {
					reportError("Unterminated string escape", startLine, startCol)
				}
				if escapedCh == 'n' {
					val += "\n"
				} else if escapedCh == 't' {
					val += "\t"
				} else {
					val += string(escapedCh)
				}
				continue
			}
			if nextCh == '"' {
				break
			}
			val += string(nextCh)
		}
		return Token{Type: TokenString, Value: val, Line: startLine, Column: startCol}
	}
	if unicode.IsDigit(ch) {
		val := string(ch)
		for unicode.IsDigit(l.peekChar()) {
			val += string(l.nextChar())
		}
		return Token{Type: TokenInt, Value: val, Line: startLine, Column: startCol}
	}
	if unicode.IsLetter(ch) || ch == '_' || ch == '/' || ch == '-' || ch == '=' || ch == '.' {
		val := string(ch)
		for unicode.IsLetter(l.peekChar()) || unicode.IsDigit(l.peekChar()) || l.peekChar() == '_' || l.peekChar() == '/' || l.peekChar() == '-' || l.peekChar() == '=' || l.peekChar() == '.' {
			val += string(l.nextChar())
		}
		return Token{Type: TokenSymbol, Value: val, Line: startLine, Column: startCol}
	}

	reportError(fmt.Sprintf("Unexpected character: %c", ch), startLine, startCol)
	return Token{}
}

// AST
type Node struct {
	Type     string
	Value    string
	Children []*Node
	Line     int
	Column   int
}

// Parser
type Parser struct {
	lexer *Lexer
	cur   Token
}

func NewParser(lexer *Lexer) *Parser {
	p := &Parser{lexer: lexer}
	p.cur = p.lexer.NextToken()
	return p
}

func (p *Parser) parseExpression() *Node {
	if p.cur.Type == TokenLParen {
		node := &Node{Type: "List", Line: p.cur.Line, Column: p.cur.Column}
		p.cur = p.lexer.NextToken() // consume '('
		for p.cur.Type != TokenRParen && p.cur.Type != TokenEOF {
			node.Children = append(node.Children, p.parseExpression())
		}
		if p.cur.Type != TokenRParen {
			reportError("Expected ')'", p.cur.Line, p.cur.Column)
		}
		p.cur = p.lexer.NextToken() // consume ')'
		return node
	}
	if p.cur.Type == TokenSymbol || p.cur.Type == TokenInt || p.cur.Type == TokenString {
		node := &Node{Type: string(p.cur.Type), Value: p.cur.Value, Line: p.cur.Line, Column: p.cur.Column}
		p.cur = p.lexer.NextToken()
		return node
	}
	reportError(fmt.Sprintf("Unexpected token: %s", p.cur.Value), p.cur.Line, p.cur.Column)
	return nil
}

// Code Generator
func generateCode(node *Node) string {
	if node.Type != "List" || len(node.Children) == 0 {
		reportError("Expected list at root", node.Line, node.Column)
	}
	head := node.Children[0]
	if head.Type != "SYMBOL" || head.Value != "http_server" {
		reportError("Expected http_server as root symbol", head.Line, head.Column)
	}
	if len(node.Children) < 3 {
		reportError("http_server expects at least a port and 1 route", head.Line, head.Column)
	}
	portNode := node.Children[1]
	if portNode.Type != "INT" {
		reportError("Expected integer for port", portNode.Line, portNode.Column)
	}

	code := `package main

import (
	"database/sql"
	"fmt"
	"net/http"
)

func main() {
	var _ = sql.Open
`

	for i := 2; i < len(node.Children); i++ {
		routeNode := node.Children[i]
		if routeNode.Type != "List" || len(routeNode.Children) == 0 || routeNode.Children[0].Value != "route" {
			reportError("Expected (route path handler)", routeNode.Line, routeNode.Column)
		}
		if len(routeNode.Children) != 3 {
			reportError("route expects path and handler", routeNode.Line, routeNode.Column)
		}

		pathNode := routeNode.Children[1]
		if pathNode.Type != "STRING" {
			reportError("Expected string for route path", pathNode.Line, pathNode.Column)
		}

		handlerNode := routeNode.Children[2]
		if handlerNode.Type != "List" || len(handlerNode.Children) == 0 || handlerNode.Children[0].Value != "lambda" {
			reportError("Expected (lambda (req) ...) for handler", handlerNode.Line, handlerNode.Column)
		}
		if len(handlerNode.Children) != 3 {
			reportError("lambda expects arguments list and body", handlerNode.Line, handlerNode.Column)
		}

		reqNodeList := handlerNode.Children[1]
		if reqNodeList.Type != "List" || len(reqNodeList.Children) != 1 {
			reportError("Expected exactly 1 argument in lambda (req)", reqNodeList.Line, reqNodeList.Column)
		}
		reqVar := reqNodeList.Children[0].Value

		bodyNode := handlerNode.Children[2]
		bodyCode := generateStatement(bodyNode, reqVar)

		code += fmt.Sprintf(`	http.HandleFunc(%q, func(w http.ResponseWriter, %s *http.Request) {
%s
	})
`, pathNode.Value, reqVar, bodyCode)
	}

	code += fmt.Sprintf(`	
	fmt.Println("Starting server on port %s...")
	if err := http.ListenAndServe(":%s", nil); err != nil {
		fmt.Println("Server error:", err)
	}
}
`, portNode.Value, portNode.Value)

	return code
}

func generateStatement(node *Node, reqVar string) string {
	if node.Type != "List" || len(node.Children) == 0 {
		reportError("Expected list for statement", node.Line, node.Column)
	}
	head := node.Children[0].Value
	if head == "res" {
		if len(node.Children) != 4 {
			reportError("res expects status, contentType, and body", node.Line, node.Column)
		}
		status := node.Children[1].Value
		contentType := node.Children[2].Value
		resBody := node.Children[3].Value
		if node.Children[3].Type == "SYMBOL" {
			// Variable reference
			return fmt.Sprintf(`		w.Header().Set("Content-Type", %q)
		w.WriteHeader(%s)
		fmt.Fprint(w, %s)`, contentType, status, resBody)
		} else {
			return fmt.Sprintf(`		w.Header().Set("Content-Type", %q)
		w.WriteHeader(%s)
		fmt.Fprint(w, %q)`, contentType, status, resBody)
		}
	} else if head == "let" {
		if len(node.Children) != 3 {
			reportError("let expects (let (var val) body)", node.Line, node.Column)
		}
		binds := node.Children[1]
		if binds.Type != "List" || len(binds.Children) != 2 {
			reportError("let binding expects (var val)", binds.Line, binds.Column)
		}
		varName := binds.Children[0].Value
		valNode := binds.Children[1]
		var valStr string
		if valNode.Type == "STRING" {
			valStr = fmt.Sprintf("%q", valNode.Value)
		} else {
			valStr = valNode.Value
		}
		bodyCode := generateStatement(node.Children[2], reqVar)
		return fmt.Sprintf("		%s := %s\n%s", varName, valStr, bodyCode)
	} else if head == "if" {
		if len(node.Children) != 4 {
			reportError("if expects (if cond then else)", node.Line, node.Column)
		}
		condNode := node.Children[1]
		if condNode.Type != "List" || len(condNode.Children) != 3 {
			reportError("cond expects (= a b)", condNode.Line, condNode.Column)
		}
		op := condNode.Children[0].Value
		if op != "=" {
			reportError("only '=' supported in if cond", condNode.Line, condNode.Column)
		}
		left := condNode.Children[1].Value
		if left == "req.method" {
			left = reqVar + ".Method"
		}
		right := condNode.Children[2]
		rightStr := right.Value
		if right.Type == "STRING" {
			rightStr = fmt.Sprintf("%q", rightStr)
		}

		thenCode := generateStatement(node.Children[2], reqVar)
		elseCode := generateStatement(node.Children[3], reqVar)

		return fmt.Sprintf(`		if %s == %s {
%s
		} else {
%s
		}`, left, rightStr, thenCode, elseCode)
	} else if head == "db_connect" {
		if len(node.Children) != 4 {
			reportError("db_connect expects (db_connect var driver dsn)", node.Line, node.Column)
		}
		varName := node.Children[1].Value
		driverNode := node.Children[2]
		dsnNode := node.Children[3]
		return fmt.Sprintf("		%s, _ := sql.Open(%q, %q)\n		_ = %s", varName, driverNode.Value, dsnNode.Value, varName)
	} else if head == "sql_query" {
		if len(node.Children) != 3 {
			reportError("sql_query expects (sql_query db query)", node.Line, node.Column)
		}
		dbVar := node.Children[1].Value
		queryNode := node.Children[2]
		queryStr := queryNode.Value
		if queryNode.Type == "STRING" {
			queryStr = fmt.Sprintf("%q", queryStr)
		}
		return fmt.Sprintf("		%s.Query(%s)", dbVar, queryStr)
	}
	reportError(fmt.Sprintf("Unknown statement: %s", head), node.Line, node.Column)
	return ""
}

func main() {
	if len(os.Args) < 2 {
		reportError("Missing file argument", 0, 0)
	}
	content, err := os.ReadFile(os.Args[1])
	if err != nil {
		reportError(fmt.Sprintf("Cannot read file: %v", err), 0, 0)
	}

	lexer := NewLexer(string(content))
	parser := NewParser(lexer)
	ast := parser.parseExpression()

	if parser.cur.Type != TokenEOF {
		reportError("Unexpected tokens after EOF", parser.cur.Line, parser.cur.Column)
	}

	goCode := generateCode(ast)

	err = os.WriteFile("server.go", []byte(goCode), 0644)
	if err != nil {
		reportError(fmt.Sprintf("Failed to write server.go: %v", err), 0, 0)
	}
}
