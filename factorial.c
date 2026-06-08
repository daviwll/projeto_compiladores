#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

// Input handling
#define INPUT_BUFFER_SIZE 1024
char __input_buffer[INPUT_BUFFER_SIZE];

// Read string input (returns dynamically allocated string)
char* __read_string_input(const char* prompt) {
    if (prompt != NULL) {
        printf("%s", prompt);
    }
    if (fgets(__input_buffer, INPUT_BUFFER_SIZE, stdin) != NULL) {
        // Remove trailing newline if present
        size_t len = strlen(__input_buffer);
        if (len > 0 && __input_buffer[len-1] == '\n') {
            __input_buffer[len-1] = '\0';
        }
        // Return a copy of the input
        char* result = (char*)malloc(strlen(__input_buffer) + 1);
        strcpy(result, __input_buffer);
        return result;
    }
    return NULL;
}

// Read number input
int __read_number_input(const char* prompt) {
    char* str_input = __read_string_input(prompt);
    if (str_input != NULL) {
        int result = atoi(str_input);
        free(str_input);
        return result;
    }
    return 0;
}

// Forward declarations
int fatorial(int n);

// Global variables
int valor;  // Global variable

int fatorial(int n) {
    // Temporary variables
    int t0 = 0;
    int t1 = 0;
    int t2 = 0;
    int t3 = 0;
    int t4 = 0;
    int t5 = 0;

    t0 = n == 0;
    t1 = n == 1;
    t2 = t0 || t1;
    if (!t2) goto L0;
    return 1;
    goto L1;
L0:
    t3 = n - 1;
    t4 = fatorial(t3);
    t5 = n * t4;
    return t5;
L1:
    ;  // Empty statement after label
}

int main() {
    // Temporary variables
    int t6 = 0;
    int t7 = 0;
    int t8 = 0;

    printf("%s\n", "CALCULA O FATORIAL RECURSIVO");
    valor = 10;
    t7 = fatorial(valor);
    printf("%s %d\n", "Fatorial: ", t7);

    return 0;
}