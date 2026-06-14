"""
Minipar Compiler - Gradio Web Interface
Interactive web interface for compiling and running Minipar programs
"""

import gradio as gr
from compiler_api import compile_and_show, compile_and_download, execute_program


# Example programs
EXAMPLES = {
    "Hello World": """# Hello World Example
print("Hello, World!")
print("Welcome to Minipar!")
""",
    
    "Variables and Arithmetic": """# Variables and Arithmetic
var x: number = 10
var y: number = 5

print("x =", x)
print("y =", y)
print("x + y =", x + y)
print("x - y =", x - y)
print("x * y =", x * y)
print("x / y =", x / y)
""",
    
    "Functions": """# Function Example
func add(a: number, b: number) -> number {
    return a + b
}

func multiply(a: number, b: number) -> number {
    return a * b
}

var result1: number = add(10, 5)
var result2: number = multiply(3, 4)

print("10 + 5 =", result1)
print("3 * 4 =", result2)
""",
    
    "Loops": """# Loop Example - Countdown
var num: number = 10

func count(n: number) -> void {
    while(n >= 0) {
        print(n)
        n = n - 1
    }
}

count(num)
print("Liftoff!")
""",
    
    "Conditionals": """# Conditional Example
func check_number(n: number) -> void {
    if (n > 0) {
        print(n, "is positive")
    }
    else {
        if (n < 0) {
            print(n, "is negative")
        }
        else {
            print(n, "is zero")
        }
    }
}

check_number(10)
check_number(-5)
check_number(0)
""",
    
    "Factorial (Recursive)": """# Recursive Factorial
func fatorial(n: number) -> number {
    if (n == 0 || n == 1) {
        return 1
    }
    else {
        return n * fatorial(n - 1)
    }
}

print("Factorial of 5:", fatorial(5))
print("Factorial of 10:", fatorial(10))
""",

    "Input Example": """# Input Example
    var a: number = 10
print(a)
while(a <= 15)
{
  print("oi")
  a = a + 1
  if(a == 12){break}
  print(a)
}

print(a)

if (a < 13)
{
  print("a é maior ou igual que 13")
}

func soma(num1: number, num2: number) -> number
{
  return num1 + num2
}

var res: number = soma(2, (3 + 4)*6)
print("res =", res)

/* PARTE 2 */
var entrada: string = input("Digite algo: ")
print(entrada)
""",

    "OO: Counter Class": """# Object-Oriented Example: Counter Class
class Counter {
    var value: number = 0
    func inc() -> number {
        value = value + 1
        return value
    }
    func get() -> number {
        return value
    }
    func reset() -> void {
        value = 0
    }
}

var c: Counter = new Counter()
print("Initial value:", c.get())
c.inc()
c.inc()
c.inc()
print("After 3 increments:", c.get())
c.reset()
print("After reset:", c.get())
""",

    "OO: Inheritance": """# Object-Oriented Example: Inheritance
class Animal {
    var name: string = "unknown"
    func speak() -> string {
        return "..."
    }
    func getName() -> string {
        return name
    }
}

class Dog extends Animal {
    func fetch() -> string {
        return "fetching!"
    }
}

var d: Dog = new Dog()
print("Animal speaks:", d.speak())
print("Dog fetches:", d.fetch())
print("Name:", d.getName())
""",

    "NN: Perceptron (Neuron)": """# Neural Networks: single Perceptron (Neuron) trained with the step rule.
# Object-oriented example. Run it from the "Execute" tab to watch it learn.
class Neuronio {
    var input_val: number = 0
    var output_desejado: number = 0
    var peso: number = 0.5
    var bias: number = 1
    var peso_bias: number = 0.5
    var taxa_aprendizado: number = 0.01
    var erro: number = 999999
    var iteracao: number = 0

    # Constructor: receives the input and the desired output
    func Neuronio(input_val: number, output_desejado: number) -> void {
        this.input_val = input_val
        this.output_desejado = output_desejado
    }

    # Activation (step): 1 if sum >= 0, otherwise 0
    func ativacao(soma: number) -> number {
        if (soma >= 0) {
            return 1
        }
        return 0
    }

    # Train the neuron until the error reaches zero
    func treinar() -> void {
        print("Input:", this.input_val, "| Desired output:", this.output_desejado)
        while (this.erro != 0) {
            this.iteracao = this.iteracao + 1
            print("")
            print("#### Iteration:", this.iteracao)
            print("Weight:", this.peso)

            var soma: number = (this.input_val * this.peso) + (this.bias * this.peso_bias)
            var saida: number = this.ativacao(soma)
            print("Output:", saida)

            this.erro = this.output_desejado - saida
            print("Error:", this.erro)

            if (this.erro != 0) {
                this.peso = this.peso + (this.taxa_aprendizado * this.input_val * this.erro)
                print("Bias weight:", this.peso_bias)
                this.peso_bias = this.peso_bias + (this.taxa_aprendizado * this.bias * this.erro)
            }
        }
        print("")
        print("Done! The neuron has learned.")
        print("Desired value:", this.output_desejado)
    }
}

var neuronio: Neuronio = new Neuronio(1, 0)
neuronio.treinar()
""",

    "NN: Neural Network (XOR)": """# Neural Networks: a small network that learns the XOR function.
# Hidden layer of 3 neurons + 1 output neuron, trained with feedforward
# and backpropagation. Run it from the "Execute" tab (takes a few seconds).

# Pseudo-random generator (LCG), since the language has no random()
var seed: number = 12345

func rand() -> number {
    seed = (seed * 1103515245 + 12345) % 2147483648
    return seed / 2147483648
}

func sigmoid(x: number) -> number {
    return 1 / (1 + exp(-x))
}

class Neuronio {
    var pesos: list = []
    var bias: number = 0
    var saida: number = 0

    func Neuronio(num_inputs: number) -> void {
        this.pesos = []
        var i: number = 0
        while (i < num_inputs) {
            this.pesos.append(rand())
            i = i + 1
        }
        this.bias = rand()
    }

    func feedforward(entradas: list) -> number {
        var soma: number = 0
        var i: number = 0
        while (i < len(entradas)) {
            soma = soma + (entradas[i] * this.pesos[i])
            i = i + 1
        }
        soma = soma + this.bias
        this.saida = sigmoid(soma)
        return this.saida
    }

    func calcular_derivada() -> number {
        return this.saida * (1 - this.saida)
    }
}

class RedeNeural {
    var taxa_aprendizado: number = 0.5
    var camada_oculta: list = []
    var neuronio_saida: Neuronio
    var saidas_ocultas: list = []
    var saida_final: number = 0

    func RedeNeural() -> void {
        this.camada_oculta = []
        var i: number = 0
        while (i < 3) {
            this.camada_oculta.append(new Neuronio(2))
            i = i + 1
        }
        this.neuronio_saida = new Neuronio(3)
    }

    func feedforward(entradas: list) -> number {
        this.saidas_ocultas = []
        var i: number = 0
        while (i < len(this.camada_oculta)) {
            var n: Neuronio = this.camada_oculta[i]
            this.saidas_ocultas.append(n.feedforward(entradas))
            i = i + 1
        }
        this.saida_final = this.neuronio_saida.feedforward(this.saidas_ocultas)
        return this.saida_final
    }

    func backpropagation(entradas: list, saida_desejada: number) -> void {
        var erro: number = saida_desejada - this.saida_final
        var delta_saida: number = erro * this.neuronio_saida.calcular_derivada()

        # Update the output neuron weights
        var i: number = 0
        while (i < len(this.neuronio_saida.pesos)) {
            this.neuronio_saida.pesos[i] = this.neuronio_saida.pesos[i] + (this.saidas_ocultas[i] * delta_saida * this.taxa_aprendizado)
            i = i + 1
        }
        this.neuronio_saida.bias = this.neuronio_saida.bias + (delta_saida * this.taxa_aprendizado)

        # Update the hidden layer weights
        i = 0
        while (i < len(this.camada_oculta)) {
            var neuronio: Neuronio = this.camada_oculta[i]
            var delta_oculto: number = delta_saida * this.neuronio_saida.pesos[i] * neuronio.calcular_derivada()
            var j: number = 0
            while (j < len(neuronio.pesos)) {
                neuronio.pesos[j] = neuronio.pesos[j] + (entradas[j] * delta_oculto * this.taxa_aprendizado)
                j = j + 1
            }
            neuronio.bias = neuronio.bias + (delta_oculto * this.taxa_aprendizado)
            i = i + 1
        }
    }

    func treinar(entradas: list, saidas_desejadas: list, epocas: number) -> void {
        var e: number = 0
        while (e < epocas) {
            var k: number = 0
            while (k < len(entradas)) {
                this.feedforward(entradas[k])
                this.backpropagation(entradas[k], saidas_desejadas[k])
                k = k + 1
            }
            e = e + 1
        }
    }

    func testar(entradas: list) -> void {
        var k: number = 0
        while (k < len(entradas)) {
            var resultado: number = this.feedforward(entradas[k])
            print("Input:", entradas[k], "Predicted Output:", resultado)
            k = k + 1
        }
    }
}

# XOR data
var entradas: list = [[0, 0], [0, 1], [1, 0], [1, 1]]
var saidas_desejadas: list = [0, 1, 1, 0]

var rede: RedeNeural = new RedeNeural()
# 3000 epochs keeps the web demo under the 10s execution limit while still
# learning XOR (outputs ~0 for 00/11 and ~1 for 01/10).
rede.treinar(entradas, saidas_desejadas, 3000)
rede.testar(entradas)
"""
}


def load_example(example_name):
    """Load an example program"""
    return EXAMPLES.get(example_name, "")


# Custom CSS for better styling
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.output-box {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
}

.code-editor {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
}

#title {
    text-align: center;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.flag-button {
    margin: 5px;
}
"""


# Create the Gradio interface
with gr.Blocks(title="Minipar Compiler") as app:
    
    # Header
    gr.Markdown(
        """
        <div id="title">
            <h1>🚀 Minipar Compiler - Web Interface</h1>
            <p>Compile, analyze, and execute Minipar programs in your browser</p>
        </div>
        """,
        elem_id="title"
    )
    
    with gr.Tabs():
        # Tab 1: Compiler
        with gr.Tab("📝 Compiler"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Source Code")
                    
                    # Example selector
                    example_dropdown = gr.Dropdown(
                        choices=list(EXAMPLES.keys()),
                        label="Load Example Program",
                        value=None
                    )
                    
                    # Source code editor
                    source_input = gr.Textbox(
                        label="Minipar Source Code",
                        lines=18,
                        max_lines=25,
                        value="# Write your Minipar code here\nprint(\"Hello, World!\")",
                        placeholder="Enter your Minipar code here...",
                        elem_classes=["code-editor"],
                    )
                    
                    gr.Markdown("### ⚙️ Compilation Options")
                    
                    with gr.Row():
                        show_tokens = gr.Checkbox(label="🔤 Show Tokens", value=False)
                        show_ast = gr.Checkbox(label="🌳 Show AST", value=False)
                        show_semantic = gr.Checkbox(label="✓ Show Semantic", value=False)
                    
                    with gr.Row():
                        show_tac = gr.Checkbox(label="📝 Show TAC", value=True)
                        show_c = gr.Checkbox(label="⚙️ Show C Code", value=False)
                        show_assembly = gr.Checkbox(label="🔧 Show Assembly", value=False)
                    
                    with gr.Row():
                        compile_btn = gr.Button("🔨 Compile", variant="primary", size="lg")
                        download_btn = gr.Button("💾 Compile & Download .exe", variant="secondary", size="lg")
                    
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Output")
                    
                    output_display = gr.Textbox(
                        label="Compilation Output",
                        lines=25,
                        max_lines=30,
                        elem_classes=["output-box"],
                    )
                    
                    compilation_log = gr.Textbox(
                        label="Compilation Log",
                        lines=5,
                        max_lines=10,
                        visible=False
                    )
                    
                    download_file = gr.File(
                        label="Download Executable",
                        visible=True
                    )
            
            # Connect example selector
            example_dropdown.change(
                fn=load_example,
                inputs=[example_dropdown],
                outputs=[source_input]
            )
            
            # Connect compile button
            compile_btn.click(
                fn=compile_and_show,
                inputs=[source_input, show_tokens, show_ast, show_semantic, 
                       show_tac, show_c, show_assembly],
                outputs=[output_display, compilation_log]
            )
            
            # Connect download button
            download_btn.click(
                fn=compile_and_download,
                inputs=[source_input],
                outputs=[download_file, output_display]
            )
        
        # Tab 2: Executor
        with gr.Tab("▶️ Execute"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📄 Source Code")
                    
                    # Example selector for executor
                    exec_example_dropdown = gr.Dropdown(
                        choices=list(EXAMPLES.keys()),
                        label="Load Example Program",
                        value=None
                    )
                    
                    exec_source_input = gr.Textbox(
                        label="Minipar Source Code",
                        lines=15,
                        max_lines=20,
                        value="# Write your Minipar code here\nprint(\"Hello, World!\")",
                        placeholder="Enter your Minipar code here...",
                        elem_classes=["code-editor"],
                    )
                    
                    gr.Markdown("### 📥 Program Input")
                    user_input = gr.Textbox(
                        label="Input (for programs using input())",
                        lines=3,
                        placeholder="Enter input values here, one per line..."
                    )
                    
                    execute_btn = gr.Button("▶️ Execute Program", variant="primary", size="lg")
                    
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Program Output")
                    
                    execution_output = gr.Textbox(
                        label="Execution Output",
                        lines=23,
                        max_lines=30,
                        elem_classes=["output-box"],
                    )
            
            # Connect example selector for executor
            exec_example_dropdown.change(
                fn=load_example,
                inputs=[exec_example_dropdown],
                outputs=[exec_source_input]
            )
            
            # Connect execute button
            execute_btn.click(
                fn=execute_program,
                inputs=[exec_source_input, user_input],
                outputs=[execution_output]
            )
        
        # Tab 3: Help
        with gr.Tab("❓ Help"):
            gr.Markdown(
                """
                # 📖 Minipar Compiler Help
                
                ## 🚀 Quick Start
                
                1. **Write Code**: Enter your Minipar code in the editor or select an example
                2. **Compile**: Click "Compile" to see compilation stages
                3. **Execute**: Switch to "Execute" tab to run your program
                4. **Download**: Click "Compile & Download .exe" to get executable
                
                ## ⚙️ Compilation Options
                
                - **🔤 Show Tokens**: Display lexical analysis (token stream)
                - **🌳 Show AST**: Display abstract syntax tree
                - **✓ Show Semantic**: Display semantic analysis results
                - **📝 Show TAC**: Display three-address code (intermediate representation)
                - **⚙️ Show C Code**: Display generated C source code
                - **🔧 Show Assembly**: Display generated ARM assembly code
                
                ## 📚 Language Reference
                
                ### Variables
                ```minipar
                var name: type = value
                
                var x: number = 42
                var text: string = "Hello"
                var flag: bool = true
                ```
                
                ### Functions
                ```minipar
                func name(param: type) -> return_type {
                    return value
                }
                
                func add(a: number, b: number) -> number {
                    return a + b
                }
                ```
                
                ### Control Flow
                ```minipar
                # If-else
                if (condition) {
                    # code
                }
                else {
                    # code
                }
                
                # While loop
                while (condition) {
                    # code
                }
                ```
                
                ### Classes and Objects
                ```minipar
                class ClassName {
                    var field: type = default_value
                    func method() -> return_type {
                        return field
                    }
                }

                var obj: ClassName = new ClassName()
                print("value:", obj.method())
                obj.field = 42
                ```

                ### Inheritance
                ```minipar
                class Animal {
                    var name: string = "unknown"
                    func speak() -> string {
                        return "..."
                    }
                }

                class Dog extends Animal {
                    func fetch() -> string {
                        return "fetching!"
                    }
                }

                var d: Dog = new Dog()
                print("speaks:", d.speak())   # inherited method
                print("fetches:", d.fetch())  # own method
                ```

                ### Operators
                - **Arithmetic**: `+` `-` `*` `/` `%`
                - **Comparison**: `==` `!=` `<` `>` `<=` `>=`
                - **Logical**: `&&` `||` `!`

                ### Built-in Functions
                - `print(...)` - Output to console
                - `input(prompt)` - Read user input

                ## 💡 Tips

                1. Start with example programs to learn syntax
                2. Use "Show TAC" to understand intermediate code
                3. Use "Show C Code" to see how code is translated
                4. Check compilation log for errors
                5. Test programs in Execute tab before downloading

                ## 📝 Example Programs

                Select from the dropdown to load:
                - **Hello World** - Basic printing
                - **Variables and Arithmetic** - Basic operations
                - **Functions** - Function declarations and calls
                - **Loops** - While loops and control flow
                - **Conditionals** - If-else statements
                - **Factorial** - Recursive functions
                - **OO: Counter Class** - Classes, fields, methods, reset
                - **OO: Inheritance** - Extends, inherited methods
                - **NN: Perceptron (Neuron)** - A single neuron that learns with the step rule
                - **NN: Neural Network (XOR)** - Hidden layer + backprop learning XOR (run in Execute tab)

                ## 🐛 Troubleshooting
                
                - **Compilation Error**: Check syntax and type errors
                - **Execution Timeout**: Program runs too long (10s limit)
                - **Download Failed**: Compilation must succeed first
                
                ## 📚 More Information
                
                For complete documentation, see:
                - `COMPLETE_GUIDE.md` - Comprehensive guide
                - `README.md` - Project overview
                - `docs/tutorials/` - Detailed tutorials
                """
            )
    
    # Footer
    gr.Markdown(
        """
        ---
        <div style="text-align: center; color: #666;">
            <p>Minipar Compiler v1.0 | Built with Gradio | 
            <a href="https://github.com/daviwll/projeto_compiladores" target="_blank">Documentation</a></p>
        </div>
        """
    )


def launch():
    """Launch the Gradio interface"""
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        css=custom_css,
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Minipar Compiler Web Interface...")
    print("=" * 60)
    print("\n📝 Features:")
    print("  ✓ Interactive code editor")
    print("  ✓ Multiple compilation views")
    print("  ✓ Direct program execution")
    print("  ✓ Executable download")
    print("  ✓ Example programs")
    print("\n🌐 Opening in browser...")
    print("=" * 60)
    
    launch()
