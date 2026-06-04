from rich.console import Console
from rich.prompt import Prompt
from brain.llm import chat
from voice.listener import listen
from tools.executor import execute_tool
from memory.remember import save_memory

console = Console()

def main():
    console.print("[bold cyan]JARVIS online.[/bold cyan]")
    console.print("Type [bold]'v'[/bold] to use voice, or just type your message.\n")

    while True:
        user_input = Prompt.ask("[bold green]You[/bold green]")

        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("[cyan]Jarvis shutting down.[/cyan]")
            break

        if user_input.lower() == "v":
            user_input = listen()
            if not user_input:
                console.print("[yellow]Didn't catch that, try again.[/yellow]")
                continue

        tool, argument, reply = chat(user_input)

        if tool and tool != "none":
            result = execute_tool(tool, argument)
            console.print(f"\n[bold cyan]Jarvis:[/bold cyan] {reply}")
            console.print(f"[dim]⚙ {result}[/dim]\n")
        else:
            console.print(f"\n[bold cyan]Jarvis:[/bold cyan] {reply}\n")

        save_memory(user_input, reply)

if __name__ == "__main__":
    main()