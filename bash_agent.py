from openai import OpenAI
from termcolor import colored
import re
import subprocess
import select
import sys
import time

client = OpenAI()

system_prompt = "You are being run in a scaffold in a shell on a Macbook, with the ability to run bash commands as the user requires. When you want to run a shell command, write it in a <bash> XML tag, like so: <bash>python --version</bash>. If you are asked to do something and you know how to do it, then go right ahead and immediately output a command. Do not explain yourself or ask for the user's approval before suggesting a command to run."

conversation_history = [{"role": "system", "content": system_prompt}]
timeout = 10

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
    # Return any bash command the model has outputted
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
        return "Command skipped by user."

    output_text = ''
    
    try:
        # Start the process
        process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start_time = time.time()

        while True:
            try:
                elapsed_time = time.time() - start_time
                remaining_time = timeout - elapsed_time

                if remaining_time <= 0:
                    # Timeout occurred
                    timeout_msg = f"Command timed out after {timeout} seconds."
                    output_text += timeout_msg
                    print(colored(timeout_msg, 'red'))
                    process.kill()
                    break

                ready, _, _ = select.select([process.stdout], [], [], remaining_time)

                if ready:
                    # Print output as it is generated
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(colored(output.strip(), 'green'))
                        output_text += output

            except KeyboardInterrupt:
                print(colored("\nKeyboardInterrupt", 'red'))
                output_text += "\nKeyboardInterrupt"
                break
        
        process.wait()

        # Print any remaining output
        for line in process.stdout:
            print(colored(line.strip(), 'green'))
            output_text += line

        # Check if the process had any errors
        err = process.stderr.read()
        if err:
            print(colored(err.strip(), 'red'))
            output_text += err.strip()

        process.stdout.close()
        process.stderr.close()

    except subprocess.CalledProcessError as e:
        print(colored(e.stderr, 'red'))
        output_text += e.stderr.strip()
        return output_text.strip()

    return output_text.strip()

def main():
    global timeout
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

            user_split = user_input.lower().split()
            if user_split[0] == "set_timeout":
                t_requested = int(user_split[1])
                if t_requested > 0:
                    timeout = t_requested
                    print(colored(f'Timeout set to {timeout} seconds\n', 'blue'))
                else:
                    print(colored(f'Invalid timeout value: {t_requested}\n', 'red'))
                continue
            
            # Send input to the model and get a response
            print(colored('Asking...\n', 'blue'))
            response_text = ask_model(user_input)

            # Execute a command provided by the model
            command = parse_response(response_text)
            if command is not None:
                output = execute_command(command)
                if not output:
                    output = "Command executed successfully."
                conversation_history.append({"role": "user", "content": output})
        
        except KeyboardInterrupt:
            print(colored("\nExiting due to KeyboardInterrupt", 'red'))
            break
        except Exception as e:
            print(colored(f"An error occurred: {e}", 'red'))
            continue

if __name__ == "__main__":
    main()