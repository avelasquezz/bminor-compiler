# B-Minor compiler 🚀

## Steps to execute project

- Create a virtual environment (recommended):
  - macOS / Linux: 

    `python3 -m venv virtual-environment-name`

  - Windows: 
  
    `py -3 -m venv virtual-environment-name`

    (If `py` does not exist, try `python -m venv virtual-environment-name`)

- Activate virtual environment:
  - macOS / Linux: 
  
    `source virtual-environment-name/bin/activate`

  - Windows (Powershell): 
  
    `virtual-environment-name\Scripts\Activate.ps1`

- Install dependencies:
  - At the root of the project:
    
    `pip install -r requirements.txt`

- Execute the project:
  - With the virtual environment activated:
  
    `python main.py path/to/bminor/file`
    
    (or `python3 main.py path/to/bminor/file` if it is necessary)