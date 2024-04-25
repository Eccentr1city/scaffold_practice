from openai import OpenAI
from termcolor import colored
import re
import subprocess

client = OpenAI()

system_prompt = "You are being run in a scaffold in a shell on a Macbook, with the ability to run bash commands as the user requires. When you want to run a shell command, write it in a <bash> XML tag, like so: <bash>python --version</bash>. If you are asked to do something and you know how to do it, then go right ahead and immediately output a command. Do not explain yourself or ask for the user's approval before suggesting a command to run."

conversation_history = [{"role": "system", "content": system_prompt}]

def ask_model(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=conversation_history
    )
    return completion.choices[0].message

def parse_response(text):
    match = re.search(r"<bash>(.*?)</bash>", text)
    if match:
        return match.group(1)
    else:
        return None

def execute_command(command):
    print(colored(f"(press enter to execute '{command}')", 'yellow'))
    prompt = input()
    if prompt != '':
        print(colored("Command skipped.", 'yellow'))
        return

    try:
        # `shell=True` interprets the bash command as a string
        # `check=True` forces it to raise an exception on a non-zero exit code
        # `text=True` returns output as a string rather than bytes
        # `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE` capture both standard output and standard error
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
        # If the command was successful, return the output
        print(colored(result.stdout, 'green'))
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Return the error message if the command failed
        print(colored(e.stderr, 'red'))
        return e.stderr

def main():
    print(colored(f"System: {system_prompt}", 'blue'))
    while True:
        try:
            # Get input from the user
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                print(colored("Exiting the CLI interface.", 'red'))
                break
            
            # Send input to the model and get a response
            model_response = ask_model(user_input)
            conversation_history.append(model_response)
            response_text = model_response.content
            print(colored(f"Assistant: {response_text}", 'cyan'))
            command = parse_response(response_text)
            if command is not None:
                output = execute_command(command)
                conversation_history.append({"role": "system", "content": output})
        
        except KeyboardInterrupt:
            print(colored("\nExiting due to KeyboardInterrupt", 'red'))
            break
        except Exception as e:
            print(colored(f"An error occurred: {e}", 'red'))
            continue

if __name__ == "__main__":
    main()