# Minipar Channel Communication Tutorial

## Overview

The Minipar compiler now supports **runtime execution** with **client-server communication** using channels! This tutorial shows you how to run programs with two terminals communicating over sockets.

---

## What's New

✅ **Runtime Executor** (`runner.py`) - Execute Minipar programs directly  
✅ **Server Channels** (`s_channel`) - Create socket servers  
✅ **Client Channels** (`c_channel`) - Connect to servers  
✅ **Method Calls** - `channel.send()` and `channel.close()`  
✅ **Multi-threading** - Servers handle multiple clients concurrently  

---

## Architecture

```
┌─────────────────┐         Socket          ┌─────────────────┐
│  Terminal 1     │      Connection         │  Terminal 2     │
│                 │                         │                 │
│  calc_server    │◄────────────────────────┤  calc_client    │
│  .minipar       │      localhost:5000     │  .minipar       │
│                 │                         │                 │
│  runner.py      │                         │  runner.py      │
└─────────────────┘                         └─────────────────┘
```

---

## How It Works

### Server Side (`s_channel`)

1. **Define a function** to handle client requests
2. **Create a server channel** with the function, description, host, and port
3. **Server automatically starts** and listens for connections
4. **Each client request** calls your function with the received data
5. **Function result** is sent back to the client

### Client Side (`c_channel`)

1. **Connect to server** using host and port
2. **Call `channel.send()`** to send data and receive response
3. **Call `channel.close()`** to disconnect

---

## Example: Calculator Server and Client

### Step 1: Create Server (`calc_server.minipar`)

```minipar
# Calculator Server
print("Starting Calculator Server...")

# Define the calculator function
func calcular(op: string, v1: number, v2: number) -> number
{
  var resultado: number = 0
  
  if (op == "+")
  {
    resultado = v1 + v2
  }
  else
  {
    if (op == "-")
    {
      resultado = v1 - v2
    }
    else
    {
      if (op == "*")
      {
        resultado = v1 * v2
      }
      else
      {
        if (op == "/")
        {
          resultado = v1 / v2
        }
      }
    }
  }
  
  return resultado
}

# Create server channel
var desc: string = "Calculadora Servidor - Digite: operacao,num1,num2"
s_channel calculadora_server {calcular, desc, "localhost", 5000}

print("Server is ready and waiting for connections...")
```

### Step 2: Create Client (`calc_client.minipar`)

```minipar
# Calculator Client
print("Starting Calculator Client...")

# Connect to server
c_channel calculadora_client {"localhost", 5000}

print("")
print("Testing calculator operations:")
print("==============================")

# Test operations (results will be printed directly)
print("Sending: 10 + 5")
calculadora_client.send("+", 10, 5)

print("Sending: 20 - 8")
calculadora_client.send("-", 20, 8)

print("Sending: 6 * 7")
calculadora_client.send("*", 6, 7)

print("Sending: 100 / 4")
calculadora_client.send("/", 100, 4)

print("")
print("All tests completed!")

# Close connection
calculadora_client.close()

print("Connection closed.")
```

### Step 3: Run in Two Terminals

#### Terminal 1 (Server)
```bash
py src\runner.py calc_server.minipar
```

**Expected Output:**
```
============================================================
Executing: calc_server.minipar
============================================================

Starting Calculator Server...
✓ Server 'calculadora_server' started on localhost:5000
  Description: Calculadora Servidor - Digite: operacao,num1,num2
Server is ready and waiting for connections...

[Server running - Press Ctrl+C to stop]
```

#### Terminal 2 (Client)
```bash
py src\runner.py calc_client.minipar
```

**Expected Output:**
```
============================================================
Executing: calc_client.minipar
============================================================

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

✓ Runtime cleanup complete
```

#### Server Terminal (After Client Runs)
```
  Client connected from ('127.0.0.1', 55653)
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

---

## Channel Syntax Reference

### Server Channel Declaration

```minipar
s_channel channel_name {function_name, description, host, port}
```

**Parameters:**
- `function_name` - Function to handle client requests (must be defined)
- `description` - Welcome message sent to clients
- `host` - Server host (e.g., `"localhost"`, `"0.0.0.0"`)
- `port` - Port number (e.g., `5000`)

**Example:**
```minipar
func process(data: string) -> string {
    return data
}

s_channel my_server {process, "Welcome!", "localhost", 8080}
```

### Client Channel Declaration

```minipar
c_channel channel_name {host, port}
```

**Parameters:**
- `host` - Server host to connect to
- `port` - Server port

**Example:**
```minipar
c_channel my_client {"localhost", 8080}
```

### Channel Methods

#### send() - Send data and receive response
```minipar
channel.send(arg1, arg2, arg3, ...)
```

- Arguments are sent as comma-separated values
- Server function receives arguments as parameters
- Returns the server's response

**Example:**
```minipar
calculadora_client.send("+", 10, 5)  # Sends "+,10,5"
```

#### close() - Close connection
```minipar
channel.close()
```

- Closes the socket connection
- Removes channel from connection table

---

## Data Type Handling

### Server Side (Receiving)
The server automatically converts received string data:
- **Numbers**: Tries to convert to `int` or `float`
- **Strings**: Keeps as string if conversion fails

### Client Side (Sending)
- All arguments are converted to strings
- Multiple arguments are joined with commas

### Return Values
- Server function return value is converted to string
- Client receives the string
- Runner attempts to convert back to number if possible

---

## Advanced Features

### Multiple Clients
Servers can handle multiple clients concurrently using threads:

```minipar
# Server automatically handles multiple clients
s_channel multi_server {handler, "Multi-client server", "localhost", 5000}
```

Each client connection runs in its own thread!

### Long-Running Servers
Servers run indefinitely until terminated:

```bash
# Press Ctrl+C to stop the server
[Server running - Press Ctrl+C to stop]
```

### Error Handling
- Connection errors are caught and reported
- Client disconnections are handled gracefully
- Server continues running after client errors

---

## Comparison: Compile vs Run

### Compile Mode (Traditional)
```bash
py compile.py program.minipar
```
- **Output**: TAC (Three-Address Code)
- **No execution**: Just generates intermediate code
- **No runtime**: Channels are commented out

### Run Mode (New!)
```bash
py src\runner.py program.minipar
```
- **Output**: Program execution results
- **Full execution**: Runs the program directly
- **Runtime support**: Channels actually work!

---

## Limitations & Notes

### Current Limitations
1. **Type System**: Semantic analyzer may complain about method return types
   - **Workaround**: Don't assign `channel.send()` to typed variables yet

2. **Parallel Execution**: `par` blocks execute sequentially
   - Full parallelism requires thread-safe variable scoping

3. **No Persistence**: Variables don't persist between function calls on server

### Best Practices
- ✅ Start server before client
- ✅ Use descriptive server descriptions
- ✅ Close connections with `.close()`
- ✅ Handle different ports for multiple servers
- ✅ Use `localhost` for testing on one machine

---

## Troubleshooting

### "Connection refused"
**Problem**: Client can't connect to server  
**Solution**: Make sure server is running first

### "Port already in use"
**Problem**: Another process is using the port  
**Solution**: Use a different port number or stop the other process

### "Semantic errors found"
**Problem**: Type checker doesn't understand method calls  
**Solution**: Use `channel.send()` without assigning to variables

### Server doesn't respond
**Problem**: Function has wrong parameter count or error  
**Solution**: Check function parameters match what client sends

---

## Testing Your Own Programs

### 1. Test Simple Programs First
```bash
py src\runner.py test_runner_simple.minipar
```

### 2. Test Server Separately
Start the server and verify it runs:
```bash
py src\runner.py your_server.minipar
```

### 3. Test Client
In another terminal:
```bash
py src\runner.py your_client.minipar
```

### 4. Check Both Outputs
- Client should show sent/received messages
- Server should show client connections and data

---

## Files in This Project

### Runtime System
- `src/runner.py` - Runtime executor with channel support
- `src/ast_nodes.py` - AST node definitions (includes ChannelDecl, MethodCall)

### Example Programs
- `calc_server.minipar` - Calculator server example
- `calc_client.minipar` - Calculator client example
- `test_runner_simple.minipar` - Basic runner test

### Test Programs
- `tests/program_test_1.minipar` - Client-server calculator
- `tests/program_test_2.minipar` - Parallel execution example
- `tests/program_test_3.minipar` - Iterative factorial
- `tests/program_test_4.minipar` - Fibonacci series

---

## Summary

✅ **YES, the current project now supports actual runtime execution with channels!**

You can now:
1. Run programs directly with `py src\runner.py file.minipar`
2. Create socket servers with `s_channel`
3. Connect clients with `c_channel`
4. Exchange data between terminals over the network
5. Build distributed calculator and other client-server applications

The implementation uses Python's `socket` and `threading` libraries to provide real network communication between Minipar programs running in different terminals.

**Enjoy building distributed systems with Minipar! 🚀**

---

**Last Updated**: 2025-10-23  
**Status**: ✅ Fully Functional  
**Tested**: Windows (should work on Linux/Mac with minor path adjustments)
