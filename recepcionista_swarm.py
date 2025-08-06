from swarms import Agent, Swarm
from rich import print

def recibir_mensaje():
    return input("[bold green]Usuario:[/bold green] ")

def enviar_respuesta(respuesta):
    print(f"[bold blue]Rswarm:[/bold blue] {respuesta}")

# Definir un agente simple que responde a mensajes
class Rswarm(Agent):
    def handle(self, mensaje):
        # Aquí puedes agregar lógica más compleja o delegar a otros agentes
        if "cita" in mensaje.lower():
            return "¿Para qué día y hora desea agendar la cita?"
        elif "gracias" in mensaje.lower():
            return "¡De nada! ¿Puedo ayudarte en algo más?"
        else:
            return "Soy Rswarm, el recepcionista. ¿En qué puedo ayudarte?"

# Crear el swarm con un solo agente por ahora
rswarm = Rswarm()
swarm = Swarm([rswarm])

if __name__ == "__main__":
    print("[bold yellow]Rswarm listo para recibir mensajes.[/bold yellow]")
    while True:
        mensaje = recibir_mensaje()
        if mensaje.lower() in ["salir", "exit", "quit"]:
            print("[bold red]Saliendo...[/bold red]")
            break
        respuesta = swarm.handle(mensaje)
        enviar_respuesta(respuesta)