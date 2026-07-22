import outlines
from outlines import models
import subprocess
import json
import sys

def main():
    print("Initializing Outlines...")
    
    # Using local Ollama via OpenAI compatibility layer
    # Note: Ensure you have `openai` and `outlines` installed and Ollama running.
    # Replace "llama3" with your local model's name (e.g., "phi3").
    try:
        from openai import OpenAI
        client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        model = models.openai(client, "llama3")
        
        # Alternatively, if you want guaranteed strict decoding via llama-cpp-python:
        # model = models.llamacpp("path/to/model.gguf")
    except Exception as e:
        print(f"Failed to load model. Error: {e}")
        sys.exit(1)

    # We enforce a generic S-expression format using a simplified CFG.
    # This prevents Outlines from running out of memory building massive state machines
    # for deeply nested language features, while still guaranteeing balanced parentheses.
    # Semantic validation is deferred to the Go transpiler's error loop.
    grammar = """
        ?start: exp
        exp: "(" symbol ( " " (exp | string | number) )* ")"
        number: /[0-9]+/
        string: /"[^"]*"/
        symbol: /[a-zA-Z_=\.\-]+/
    """
    
    print("Compiling CFG generator... (this may take several minutes for large local models)")
    generator = outlines.generate.cfg(model, grammar)

    prompt = "Build a web server on port 8080 with a root route returning 'root' and an /api route returning 'api'."
    max_retries = 3
    current_prompt = prompt

    for attempt in range(max_retries):
        print(f"\n--- Attempt {attempt+1} ---")
        print(f"Prompt: {current_prompt}")
        print("Generating Zero code... (waiting for local model response)")
        
        # Generate S-expression
        code = generator(current_prompt)
        print(f"Generated Code:\n{code}\n")
        
        with open("app.zero", "w") as f:
            f.write(code)
            
        print("Running Go transpiler...")
        result = subprocess.run(["go", "run", "zero.go", "app.zero"], capture_output=True, text=True)
        
        if result.returncode != 0:
            output = result.stdout.strip() or result.stderr.strip()
            try:
                err_data = json.loads(output)
                print(f"Compilation error detected at line {err_data.get('line')}, column {err_data.get('column')}: {err_data.get('reason')}")
                
                # Feedback loop
                current_prompt = f"{prompt}\n\nYour previous output was invalid. The transpiler returned this JSON error:\n{json.dumps(err_data)}\nPlease fix the S-expression."
            except json.JSONDecodeError:
                print("Failed to parse JSON error from Go transpiler. Unexpected output:")
                print(output)
                break
        else:
            print("Transpilation successful. 'server.go' has been generated.")
            print("Compiling Go binary...")
            build_result = subprocess.run(["go", "build", "-o", "server", "server.go"], capture_output=True, text=True)
            if build_result.returncode == 0:
                print("Compilation successful! Executing the server...")
                # Automatically execute the compiled binary as requested
                try:
                    subprocess.run(["./server"])
                except KeyboardInterrupt:
                    print("\nServer stopped.")
            else:
                print("Go build failed:")
                print(build_result.stderr)
            break

if __name__ == "__main__":
    main()
