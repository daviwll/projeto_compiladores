# 🌐 Minipar Compiler Web Interface (Gradio) - Quick Start

The web interface is a **Gradio** app that lets you compile, inspect, and run Minipar
programs in your browser. It works on **Windows and Linux/macOS**.

## ⚡ One-Command Start (Launcher Script)

**Linux/macOS:**
```bash
cd interface
chmod +x start.sh   # first time only
./start.sh
```

**Windows:**
```bat
cd interface
start.bat
```

The launcher checks Python, installs Gradio if needed, and starts the server.

## 📦 Manual Start

If you prefer to do it by hand (or the launcher fails):

**Linux/macOS:**
```bash
pip install gradio        # one time
cd interface
python3 app.py
```

**Windows:**
```bat
pip install gradio        :: one time
cd interface
py app.py
```

## 🌐 Access

Open your browser to: **http://localhost:7860**

## ✨ Features

- ✅ Interactive code editor with example programs
- ✅ Multiple compilation views (tokens, AST, semantic, TAC, C, ARM assembly)
- ✅ Direct program execution in the browser (**Execute** tab)
- ✅ One-click executable download
- ✅ Built-in help and language reference

## 📚 Example Programs

Pick one from the **Load Example Program** dropdown (available in both the *Compiler*
and *Execute* tabs):

- Hello World, Variables and Arithmetic, Functions, Loops, Conditionals
- Factorial (Recursive), Input Example
- OO: Counter Class, OO: Inheritance
- **NN: Perceptron (Neuron)** — a single neuron that learns with the step rule
- **NN: Neural Network (XOR)** — hidden layer + backpropagation learning XOR

> 💡 The **NN: Neural Network (XOR)** example trains for a few seconds — run it from the
> **Execute** tab and watch the predicted outputs approach `0` for `[0,0]`/`[1,1]` and
> `1` for `[0,1]`/`[1,0]`.

## 📖 Full Documentation

See [README.md](README.md) and [INSTALLATION.md](INSTALLATION.md) for the complete guide.

---

**Quick Test:**
1. Start the interface (launcher or manual)
2. Open the **Execute** tab
3. Load **NN: Perceptron (Neuron)**
4. Click **▶️ Execute Program** and watch it learn!

🚀 **Ready to code!**

---

**Last Updated:** 2026-06-14
**Tested On:** Linux (Python 3.14, Gradio 6) and Windows 10/11
