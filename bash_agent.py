from openai import OpenAI
from termcolor import colored
import re
import subprocess

client = OpenAI()

system_prompt = "You are being run in a scaffold in a shell on a Macbook, with the ability to run bash commands as the user requires. When you want to run a shell command, write it in a <bash> XML tag, like so: <bash>python --version</bash>. If you are asked to do something and you know how to do it, then go right ahead and immediately output a command. Do not explain yourself or ask for the user's approval before suggesting a command to run."

conversation_history = [{"role": "system", "content": system_prompt}]

def ask_model(prompt):
    conversation_history.append({"role": "user", "content": prompt})

    return_text = ""
    stream = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=conversation_history,
        stream=True,
    )

    # Print response as it is generated
    print(colored(f"Assistant: ", 'cyan'), end="")
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(colored(chunk.choices[0].delta.content, 'cyan'), end="")
            return_text += chunk.choices[0].delta.content
    print('\n')

    conversation_history.append({"role": "assistant", "content": return_text})
    return return_text

def parse_response(text):
    match = re.search(r"<bash>(.*?)</bash>", text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None

def execute_command(command):
    # Get user permission to run command, otherwise skip it
    print(colored(f"(press enter to execute '{command}')", 'yellow'))
    prompt = input()
    if prompt != '':
        print(colored("Command skipped.", 'yellow'))
        return

    try:
        # Start the process
        process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output = []
        # Read the output byte by byte as it is generated
        while True:
            char = process.stdout.read(1)
            if char == '' and process.poll() is not None:
                break
            if char:
                print(colored(char, 'green'), end='')
                output.append(char)

        full_output = ''.join(output)

        # Check if the process had any errors
        err = process.stderr.read()
        if err:
            print(colored(err.strip(), 'red'))
            return err

        # Ensure the process has finished
        process.stdout.close()
        process.stderr.close()
        process.wait()

        return full_output

    except subprocess.CalledProcessError as e:
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
            if not user_input:
                user_input = "Continue."
                print(user_input)
            
            # Send input to the model and get a response
            print(colored('Asking...\n', 'blue'))
            response_text = ask_model(user_input)

            # Execute a command provided by the model
            command = parse_response(response_text)
            if command is not None:
                output = execute_command(command)
                if not output:
                    output = "Command executed successfully."
                conversation_history.append({"role": "system", "content": output})
        
        except KeyboardInterrupt:
            print(colored("\nExiting due to KeyboardInterrupt", 'red'))
            break
        except Exception as e:
            print(colored(f"An error occurred: {e}", 'red'))
            continue

if __name__ == "__main__":
    main()