from openai import OpenAI

client = OpenAI()

# system_prompt = "You are being run in a scaffold in a shell on a Macbook. When you want to run a shell command, write it in a <bash> XML tag. You will be shown the result of the command, an be able to run additional commands. Anything else you say will be sent to the user. If you know how to do something, then don't bother explaining it; just go right ahead and start executing bash commands one at a time. Do not ask for the user's approval before suggesting a command to run."

system_prompt = "You are a helpful and friendly assistant being run in a shell on a Macbook."
conversation_history = [{"role": "system", "content": system_prompt}]

def ask_model(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    return completion.choices[0].message

def execute_command(command):
    return

def parse_response():
    return

def main():
    while True:
        try:
            # Get input from the user
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Exiting the CLI interface.")
                break
            
            # Send input to the model and get a response
            model_response = ask_model(user_input)
            conversation_history.append(model_response)
            print("Assistant:", model_response.content)
        
        except KeyboardInterrupt:
            print("\nExiting due to KeyboardInterrupt")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()