from swarms import Agent, SwarmRouter as Swarm
from rich import print
import time

def enviar_respuesta(respuesta):
    print(f"[bold blue]Rswarm:[/bold blue] {respuesta}")

# Definir un agente simple que responde a mensajes
class Rswarm(Agent):
    def handle(self, mensaje: str) -> str:
        # Aquí puedes agregar lógica más compleja o delegar a otros agentes
        if "cita" in mensaje.lower():
            return "¿Para qué día y hora desea agendar la cita?"
        elif "gracias" in mensaje.lower():
            return "¡De nada! ¿Puedo ayudarte en algo más?"
        else:
            return "Soy Rswarm, el recepcionista. ¿En qué puedo ayudarte?"

# Crear el swarm con un solo agente por ahora
rswarm = Rswarm()
swarm = Swarm(agents=[rswarm])

if __name__ == "__main__":
    print("[bold yellow]Rswarm (modo no-interactivo) procesando mensajes de ejemplo...[/bold yellow]")

    mensajes_de_ejemplo = [
        "hola",
        "necesito una cita",
        "muchas gracias",
    ]

    for mensaje in mensajes_de_ejemplo:
        print(f"\n[bold green]Usuario:[/bold green] {mensaje}")
        time.sleep(1)
        respuesta = swarm.run(mensaje)
        enviar_respuesta(respuesta)

    print("\n[bold red]Demostración finalizada.[/bold red]")