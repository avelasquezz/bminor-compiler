# B-Minor Compiler 🧠

A compiler for the **B-Minor** language, implemented in **Python** using the [SLY](https://github.com/dabeaz/sly) library.
It currently supports **lexical**, **syntactic**, and **semantic** analysis, serving as a solid foundation for the stage of intermediate code generation and optimizations.

---

## 🚀 Features

* **Lexer:** Built with SLY, identifies valid B-Minor language tokens.
* **Parser:** Constructs an Abstract Syntax Tree (AST) with structural validation.
* **Checker:** Performs basic semantic analysis (declarations, types, and symbols).
* **CLI (Command-Line Interface):** Executable via `main.py` with multiple options.
* **DOT-format AST generation:** Generate AST as DOT and PDF format.

---

## 📦 Requirements

* Python 3.10 or higher
* Libraries:

  * `sly`
  * `rich`
  * `argparse`
  * `graphviz`
  * `multimethod`

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🧰 Recommended Setup (Virtual Environment)

It is highly recommended to use a **virtual environment** to isolate the project dependencies.

### Create a virtual environment

```bash
python3 -m venv .venv
```

### Activate the virtual environment

* On **Linux / macOS**:

  ```bash
  source .venv/bin/activate
  ```

* On **Windows (PowerShell)**:

  ```bash
  .venv\Scripts\activate
  ```

Once activated, install the dependencies:

```bash
pip install -r requirements.txt
```

To deactivate the environment later:

```bash
deactivate
```

---

## ⚙️ Usage

Run the compiler from the project root:

```bash
python3 main.py [options] filename.bminor
```

### Available options:

| Option          | Description                                         |
| --------------- | --------------------------------------------------- |
| `-h, --help`    | Show program help and exit                          |
| `-v, --version` | Show compiler version and exit                      |
| `--scan`        | Run lexical analysis and display generated tokens   |
| `--dot`         | Generate AST in DOT format (for Graphviz)           |
| `--sym`         | Perform semantic analysis and display symbol tables |

### Examples

Generate the AST for a file:

```bash
python3 main.py --dot examples/sample.bminor
```

Run lexical analysis:

```bash
python3 main.py --scan examples/sample.bminor
```

Display the symbol table:

```bash
python3 main.py --sym examples/sample.bminor
```

---

## 🧠 Project Status

The compiler is **currently under development**.
Planned future stages include:

* Intermediate code generation.
* Basic optimizations.
* Flow analysis and enhanced error handling.

---

## 🎓 Academic Context

This project was developed as part of a **university course on compiler construction**.
The **B-Minor language grammar** used in this project was created by **Professor Ángel Augusto Agudelo Zapata**
📧 [a3udeloz@utp.edu.co](mailto:a3udeloz@utp.edu.co)
Faculty of Engineering — Universidad Tecnológica de Pereira (UTP), Colombia.
