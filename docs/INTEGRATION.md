# MiniPar Integration Guide

How to use the MiniPar compiler via the **CLI**, **HTTP API**, and **Web UI**.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Entry points                          │
│                                                          │
│  CLI (src/minipar_cli.py)                                │
│  HTTP API + Web UI (interface/compiler_api.py / Flask)   │
│  Gradio UI (interface/app.py)                            │
└──────────────┬───────────────────────────────────────────┘
               │ calls
               ▼
┌──────────────────────────────────────────────────────────┐
│              src/compiler.py                             │
│  compile_source(source, ...) → (codegen, c_gen, arm_gen) │
└──────┬───────┬───────┬───────────────────────────────────┘
       │       │       │
   Lexer   Parser   Semantic → CodeGen → C/ARM backend
```

All three entry points reuse the same `compile_source` function; no logic is duplicated.

---

## 1. CLI

### Install / activate the venv

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install flask pytest
```

### Commands

| Command | Description |
|---------|-------------|
| `compile <file>` | Full compilation pipeline (TAC + optional targets) |
| `ast <file>` | Print abstract syntax tree |
| `tac <file>` | Print three-address code |
| `generate-c <file> [--out out.c]` | Generate C source |
| `generate-arm <file>` | Generate ARMv7 assembly |
| `test` | Run the full pytest suite |

### Examples

```bash
# Compile with TAC output (default)
python src/minipar_cli.py compile examples/ex1.minipar

# Show AST only
python src/minipar_cli.py ast examples/fatorial_rec.minipar

# Generate C and ARM
python src/minipar_cli.py generate-c  examples/ex5.minipar --out /tmp/ex5.c
python src/minipar_cli.py generate-arm examples/ex5.minipar

# Compile to native binary (requires GCC)
python src/minipar_cli.py compile examples/ex5.minipar --exe

# Run tests
python src/minipar_cli.py test
```

---

## 2. HTTP API

Start the server:

```bash
python interface/compiler_api.py
# Listening on http://127.0.0.1:8000
```

### Endpoints

#### `GET /health`

Readiness check.

```
HTTP 200  {"ok": true}
```

#### `POST /compile`

Compile MiniPar source and return artifacts as JSON.

**Request body** (JSON):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | string | — | MiniPar source code (required) |
| `show_tokens` | bool | false | Include token stream |
| `show_ast` | bool | false | Include AST text |
| `show_semantic` | bool | false | Include semantic details |
| `show_tac` | bool | true | Include TAC listing |
| `generate_c` | bool | false | Include generated C code |
| `generate_asm` | bool | false | Include ARM assembly |

**Response** (JSON):

```json
{
  "ok": true,
  "errors": [],
  "tac": "  0: FUNC_BEGIN fatorial ...",
  "ast": "",
  "tokens": "",
  "c_code": "",
  "assembly": "",
  "output": "=== Lexical Analysis === ..."
}
```

**curl example:**

```bash
curl -s http://127.0.0.1:8000/compile \
  -H 'Content-Type: application/json' \
  -d '{"source": "print(\"Hello!\")", "show_tac": true}' | python -m json.tool
```

#### `POST /generate`

Generate C or ARM code; returns plain text.

**Request body** (JSON):

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | string | — | MiniPar source code (required) |
| `target` | string | `"c"` | `"c"` or `"arm"` |

**Response**: `text/plain` — the generated code.

**curl examples:**

```bash
# Generate C
curl -s http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"source": "print(\"Hi\")", "target": "c"}'

# Generate ARM assembly
curl -s http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"source": "print(\"Hi\")", "target": "arm"}'
```

---

## 3. Web UI

Start the same server as above:

```bash
python interface/compiler_api.py
```

Open **http://127.0.0.1:8000** in a browser.

The single-page UI lets you:
- Write or load example MiniPar programs
- Select which artifacts to view (Tokens / AST / TAC / C / ARM)
- Compile (`Ctrl+Enter` shortcut) or generate C/ARM directly
- Browse results in tabbed panels

No framework dependencies — plain HTML + `fetch()`.

---

## 4. Running tests

```bash
# All tests (unit + integration)
.venv/bin/python -m pytest -q

# Integration only
.venv/bin/python -m pytest tests/test_integration_api.py -q

# Original unit suite
.venv/bin/python -m pytest tests/test_compilerok.py -q
```

---

## 5. Security notes

- The Flask API binds to `127.0.0.1` by default — not reachable over the network.
- All compilation is **in-memory**; no user files are written unless `generate_c`/`generate_asm` is requested (which writes `output.c` / `output.s` in the working directory).
- No authentication is provided; intended for local development only.
- To expose publicly, add authentication and restrict file-write paths.

---

## 6. Extending the UI

`interface/static/index.html` is plain HTML + JS with no build step.

- Add a new button → `onclick="doGenerate('arm')"` (already wired up)
- Add a new API option → extend the `opts` object in `doCompile()` and add the corresponding `show_*` / `generate_*` field to the `/compile` handler in `compiler_api.py`
- Styling: all CSS is embedded in `<style>` — uses CSS custom properties compatible with the Catppuccin Mocha palette
