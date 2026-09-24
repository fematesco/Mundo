import anthropic, datetime

client = anthropic.Anthropic()
AGENTES = {
    "Arthur": "sarcástico, adora pescar",
    "Luna": "curiosa, curandeira da vila",
}
LOG = "mundo.md"

def ler():
    try:
        return "".join(open(LOG, encoding="utf-8").readlines()[-30:])
    except FileNotFoundError:
        return "(a vila acabou de nascer)"

for nome, persona in AGENTES.items():
    r = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content":
            f"Você é {nome}, {persona}.\nO que aconteceu na vila:\n{ler()}\n"
            "O que você faz ou diz agora? 1-2 frases, primeira pessoa."}],
    )
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- **{datetime.datetime.now():%d/%m %H:%M} {nome}:** {r.content[0].text}\n")
