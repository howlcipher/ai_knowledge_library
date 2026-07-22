# Zero Transpiler

Zero is an AI-first, Lisp-like coding language designed specifically to be written by Large Language Models (LLMs). It transpiles directly into robust, production-ready Go.

## Why Zero? (Why not just write Go?)

You might wonder: *If Zero just compiles into Go, why not have the AI write Go directly?*

1. **Hallucination-Proof Generation**: Modern LLMs often hallucinate invalid syntax or complex abstractions in strictly typed languages. Zero uses simple, uniformly structured S-expressions (Lisp-like grammar). Because the syntax is so simple, we can use tools like `outlines` (as seen in `orchestrator.py`) to mathematically guarantee the AI generates perfectly balanced, structurally valid code.
2. **Immediate Semantic Feedback**: If the AI attempts to do something semantically invalid (e.g., calling a method that doesn't exist), the Go transpiler immediately catches it and returns a clean, localized JSON error. The Orchestrator automatically feeds this back to the AI for self-correction.
3. **Abstraction Constraints**: The AI is strictly constrained by what the transpiler supports. It cannot hallucinate complex, dangerous, or unintended behavior unless an explicit AST mapping exists for it.

Zero combines the **predictability and simplicity of S-expressions** (for the AI to write) with the **performance, safety, and ecosystem of Go** (for the server to run).

## Hello World Example

Here is a basic HTTP server written in Zero that serves a text response and a JSON endpoint.

Create a file called `hello.zero`:

```lisp
(http_server 8080
  (route "/" (lambda (req)
    (res 200 "text/plain" "Hello, World! Zero language is alive!")
  ))
  
  (route "/json" (lambda (req)
    (let (msg (dict ("status" "success") ("message" "Hello from Zero JSON endpoint!")))
      (res_json 200 msg)
    )
  ))
)
```

### CLI "Hello World" Example

If you want to build a simple command-line script instead of a web server, you can use the `(cli_app ...)` root block instead:

Create `cli_hello.zero`:

```lisp
(cli_app
  (print "Hello, World!")
  (let (name "Zero")
    (print "Welcome to" name)
  )
)
```

## How to Run

1. **Transpile and Run in one step**:
   To immediately transpile your `.zero` code into Go and execute it, run:
   ```bash
   go run zero.go hello.zero && go run server.go
   ```

2. **Build a Standalone Binary**:
   If you want to compile the transpiled Go code into a highly optimized, standalone binary:
   ```bash
   # 1. Transpile to server.go
   go run zero.go hello.zero
   
   # 2. Compile Go into an executable
   go build -o hello server.go
   
   # 3. Run the binary
   ./hello
   ```

The server will spin up on `http://localhost:8080`.
