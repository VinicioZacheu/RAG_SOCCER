import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
if not key or not key.startswith("sk-"):
    raise RuntimeError("🔑 OPENAI_API_KEY ausente ou inválida em .env")

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,
    openai_api_key=key
)

def generate_balanced_teams(players):
    system = SystemMessage(
        content=(
            "Você é um treinador especialista em futebol de 7 (Fut7). "
            "Divida estes jogadores em dois times equilibrados (leve em considereção os Atributos de cada jogador) Utilize todos os jogadores. "
            "Retorne **exatamente** neste formato **em português**:\n\n"
            "Pontuação de Equilíbrio: Principal atributo Time A <Attributo> <número> / Principal atributo Time B <Atributo> <número>\n\n"
            "Time A:\n- Jogador 1\n- Jogador 2\n\n"
            "Time B:\n- Jogador 3\n- Jogador 4\n\n"
            "Explicação:\n• Força do Time A, Fraquezas do Time A\n• Força do Time B, Fraquezas do Time B\n\n"
        )
    )

    lines = [
        f"- {p['name']} (IQ: {p['iq']}, Velocidade: {p['speed']}, Resistência: {p['stamina']}, "
        f"Passe: {p['passing']}, Finalização: {p['shooting']}, Drible: {p['dribbling']}, "
        f"Defesa: {p['defense']}, Força: {p['physical']}, Goleiro: {'Sim' if p['goalkeeper'] else 'Não'})"
        for p in players
    ]

    human = HumanMessage(
        content="Aqui estão os jogadores:\n" + "\n".join(lines)
    )

    # chama o modelo e devolve o texto puro
    result = llm([system, human])
    text = (result.generations[0][0].text
            if hasattr(result, "generations") 
            else result.content)
    return text.strip()

