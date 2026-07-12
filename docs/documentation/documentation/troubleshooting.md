# Troubleshooting Guide
## Python Venv Issues
If `pdoc` or `pytest` is missing, ensure you activated your venv:
`source venv/bin/activate`

## Git Rebase Conflicts
If automated workflows push badges and cause conflicts:
`git pull --rebase`

## Go Binary Errors
If `go build` fails, ensure you are using Go 1.22+.
