# Project CLI

This project integrates a command line interface (CLI) for interacting with the GPT-4 Turbo model to execute bash commands directly via subprocess. Users can input text, which is processed by the GPT-4 model to potentially generate bash commands that are then run in the shell environment. This setup is intended for demonstration purposes and should be used with caution in live environments due to the potential execution of arbitrary commands.

## Features

- Input text processing with GPT-4 Turbo model
- Execution of bash commands from model responses
- Real-time command line interaction

## Usage

To start the CLI, run the script with:

```bash
python hello.py
```

Ensure you monitor and control the execution of commands to prevent unintended consequences.

## Safety Warning

Always review commands before execution. The system allows for arbitrary command execution, which can be hazardous if misused.

