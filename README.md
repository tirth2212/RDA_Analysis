# Reaching Definition Analysis Tool

A powerful tool for performing Reaching Definition Analysis (RDA) on code, featuring Control Flow Graph (CFG) visualization and LLM-based verification.

## 🚀 Features

- Control Flow Graph (CFG) generation and visualization
- Reaching Definition Analysis (RDA) computation
- Support for multiple programming languages (Python, JavaScript, Java)
- LLM-based verification of RDA results
- Interactive web interface using Streamlit
- Built-in test cases and custom code upload support

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Graphviz (for CFG visualization)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Current_Codebase
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your LLM API credentials if needed

## 🏃‍♂️ Running the Application

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

## 💻 Usage

### Using Built-in Test Code
1. Toggle "Use Built-in Test Code" in the sidebar
2. The application will use a predefined test case:
```python
x = 1
if x > 0:
    y = x + 1
else:
    y = x - 1
z = y
```

### Using Custom Code
1. Upload your code file (.py, .js, or .java)
2. Select the appropriate language from the dropdown
3. The application will automatically analyze your code

### Understanding the Results
1. **Control Flow Graph**: Visual representation of your code's control flow
2. **RDA Table**: Shows for each node:
   - Node ID
   - Code snippet
   - IN set (reaching definitions entering the node)
   - GEN set (definitions generated in the node)
   - KILL set (definitions killed in the node)
   - OUT set (reaching definitions leaving the node)
3. **LLM Verification**: Automated verification of RDA results with detailed feedback

## 📚 Test Cases

The project includes several test cases in the `code_input` directory:
- `example.py`: Complex control flow example
- `for_example.py`: Loop-based example
- `func_example.py`: Function-based example
- `hw3_test.py`: Additional test case

## 🏗️ Project Structure

```
Current_Codebase/
├── app.py                 # Main Streamlit application
├── cfg_builder.py         # CFG construction logic
├── cfg_node.py           # CFG node implementation
├── dataflow.py           # Dataflow analysis implementation
├── requirements.txt      # Project dependencies
├── code_input/          # Test cases
│   ├── example.py
│   ├── for_example.py
│   ├── func_example.py
│   └── hw3_test.py
├── utils/               # Utility functions
├── llm/                # LLM integration
└── prompts/            # LLM prompt templates
```

## 🔍 Example Output

When analyzing the built-in test code, you should see:
1. A CFG with 4-5 nodes
2. RDA table showing reaching definitions for variables x, y, and z
3. LLM verification results with:
   - Node-by-node analysis
   - Overall correctness percentage
   - Detailed feedback for each node

## ⚠️ Troubleshooting

### Common Issues

1. **Application fails to start**
   - Verify all dependencies are installed
   - Check if virtual environment is activated
   - Ensure Python version is compatible

2. **CFG generation fails**
   - Check input code syntax
   - Verify language selection matches input code

3. **LLM verification fails**
   - Check API credentials in .env
   - Verify internet connection
   - Confirm model name in sidebar
