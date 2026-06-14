# Quick Start: Running Calculator with Two Terminals

## TL;DR

**Linux/macOS:**
```bash
# Terminal 1 (Server)
python3 src/runner.py examples/calc_server.minipar

# Terminal 2 (Client)
python3 src/runner.py examples/calc_client.minipar
```

**Windows:**
```bat
:: Terminal 1 (Server)
py src\runner.py examples\calc_server.minipar

:: Terminal 2 (Client)
py src\runner.py examples\calc_client.minipar
```

**Result**: Client performs 4 calculations (add, subtract, multiply, divide) and receives results from server! 🎉

---

## Prerequisites

- Python 3.7+
- Two terminal windows
- Works on Windows **and** Linux/macOS (only the interpreter name and path
  separators differ — see each step below)

---

## Step-by-Step Guide

### 1. Open First Terminal (Server)

Navigate to the project directory:

**Linux/macOS:**
```bash
cd ~/path/to/projeto_compiladores
```

**Windows:**
```bat
cd C:\path\to\projeto_compiladores
```

Start the server:

**Linux/macOS:**
```bash
python3 src/runner.py examples/calc_server.minipar
```

**Windows:**
```bat
py src\runner.py examples\calc_server.minipar
```

**You should see:**
```
Starting Calculator Server...
✓ Server 'calculadora_server' started on localhost:5000
  Description: Calculadora Servidor - Digite: operacao,num1,num2
Server is ready and waiting for connections...

[Server running - Press Ctrl+C to stop]
```

✅ **Server is running!** Leave this terminal open.

---

### 2. Open Second Terminal (Client)

Navigate to the same directory:

**Linux/macOS:**
```bash
cd ~/path/to/projeto_compiladores
```

**Windows:**
```bat
cd C:\path\to\projeto_compiladores
```

Run the client:

**Linux/macOS:**
```bash
python3 src/runner.py examples/calc_client.minipar
```

**Windows:**
```bat
py src\runner.py examples\calc_client.minipar
```

**You should see:**
```
Starting Calculator Client...
✓ Client 'calculadora_client' connected to localhost:5000
  Server says: Calculadora Servidor - Digite: operacao,num1,num2

Testing calculator operations:
==============================
Sending: 10 + 5
  Sent to server: +,10,5
  Received from server: 15
Sending: 20 - 8
  Sent to server: -,20,8
  Received from server: 12
Sending: 6 * 7
  Sent to server: *,6,7
  Received from server: 42
Sending: 100 / 4
  Sent to server: /,100,4
  Received from server: 25.0

All tests completed!
✓ Connection 'calculadora_client' closed
Connection closed.
```

✅ **Success!** All calculations completed.

---

### 3. Check Server Terminal

Go back to Terminal 1 (server). You should now see:
```
  Client connected from ('127.0.0.1', XXXXX)
  Received: +,10,5
  Sent: 15
  Received: -,20,8
  Sent: 12
  Received: *,6,7
  Sent: 42
  Received: /,100,4
  Sent: 25.0
  Client disconnected
```

✅ **Server processed all requests!**

---

### 4. Stop Server

In Terminal 1, press:
```
Ctrl+C
```

Server will shutdown gracefully.

---

## What Just Happened?

1. **Server** created a socket on localhost:5000
2. **Client** connected to that socket
3. **Client** sent 4 operation requests:
   - Addition: `+,10,5`
   - Subtraction: `-,20,8`
   - Multiplication: `*,6,7`
   - Division: `/,100,4`
4. **Server** executed the `calcular()` function for each request
5. **Server** sent results back: `15`, `12`, `42`, `25.0`
6. **Client** received and displayed results
7. **Client** closed connection

---

## Architecture

```
Terminal 1                          Terminal 2
┌─────────────────────┐            ┌─────────────────────┐
│ calc_server.minipar │            │ calc_client.minipar │
│                     │            │                     │
│ func calcular(...) │            │ c_channel client    │
│ s_channel server   │◄───────────┤ client.send(...)    │
│                     │   Socket   │ client.close()      │
│ localhost:5000      │            │                     │
└─────────────────────┘            └─────────────────────┘
```

---

## Troubleshooting

### Problem: "Address already in use"
**Solution**: A previous server is still running. Find and kill it:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Problem: "Connection refused"
**Solution**: Start the server first, then the client

### Problem: "Module not found"
**Solution**: Make sure you're in the project root directory

---

## Next Steps

### Create Your Own Server

```minipar
# my_server.minipar
func greet(name: string) -> string {
    return "Hello, " + name + "!"
}

s_channel my_server {greet, "Greeting Server", "localhost", 6000}
```

### Create Your Own Client

```minipar
# my_client.minipar
c_channel my_client {"localhost", 6000}
my_client.send("World")
my_client.close()
```

### Run Them

**Linux/macOS:**
```bash
# Terminal 1
python3 src/runner.py my_server.minipar

# Terminal 2
python3 src/runner.py my_client.minipar
```

**Windows:**
```bat
:: Terminal 1
py src\runner.py my_server.minipar

:: Terminal 2
py src\runner.py my_client.minipar
```

---

## Full Documentation

See `CHANNEL_TUTORIAL.md` for:
- Complete syntax reference
- More examples
- Advanced features
- Error handling
- Best practices

---

## Success Criteria

✅ Server starts without errors  
✅ Client connects successfully  
✅ All 4 calculations return correct results  
✅ Connection closes cleanly  

**If all checkmarks pass, your setup is working perfectly!**

---

**Last Updated**: 2026-06-14  
**Tested On**: Linux (Python 3.14) and Windows 10/11 (Python 3.13)  
**Status**: ✅ Fully Working
