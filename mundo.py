import anthropic, datetime, json, random

client = anthropic.Anthropic()
MODELO = "claude-haiku-4-5-20251001"

AGENTES = {
    "Arthur": "sarcástico, adora pescar, carrega um passado pesado",
    "Luna": "curiosa, curandeira da vila, acolhedora",
    "Bento": "ferreiro rabugento de bom coração, desconfia de forasteiros",
    "Mila": "jovem mercadora esperta, adora fofoca e negócios",
}

EVENTOS = [
    "Começa a chover forte na vila.",
    "Um mercador misterioso chega com mercadorias estranhas.",
    "É dia de festa na praça da vila.",
    "Um lobo é visto perto do rio.",
    "Um forasteiro ferido aparece na entrada da vila.",
    "O poço da vila secou de repente.",
    "Na noite de lua cheia, um som estranho vem da floresta.",
    "Nada de especial acontece, é um dia tranquilo.",
]

LOG = "mundo.md"
REL = "relacoes.json"
BRT = datetime.timezone(datetime.timedelta(hours=-3))


def agora():
    return datetime.datetime.now(BRT).strftime("%d/%m %H:%M")


def ler_log():
    try:
        return "".join(open(LOG, encoding="utf-8").readlines()[-30:])
    except FileNotFoundError:
        return "(a vila acabou de nascer)"


def ler_rel():
    try:
        return json.load(open(REL, encoding="utf-8"))
    except Exception:
        return {}


def escrever(linha):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


rel = ler_rel()

if random.random() < 0.5:
    escrever(f"- **{agora()} 🌍 Narrador:** {random.choice(EVENTOS)}")

ordem = list(AGENTES.items())
random.shuffle(ordem)

for nome, persona in ordem:
    minhas = rel.get(nome, {})
    outros = [n for n in AGENTES if n != nome]
    prompt = (
        f"Você é {nome}, {persona}.\n"
        f"O que você pensa dos outros: {json.dumps(minhas, ensure_ascii=False) or 'nada ainda'}\n"
        f"Moradores: {', '.join(outros)}.\n"
        f"O que aconteceu na vila:\n{ler_log()}\n\n"
        "Decida o que você faz ou diz agora. Responda SOMENTE em JSON, assim:\n"
        '{"fala": "1-2 frases em primeira pessoa, sem asteriscos", '
        '"relacoes": {"NomeDeAlguem": "opinião curta atualizada sobre essa pessoa"}}\n'
        "Em relacoes, inclua só quem mudou na sua opinião (pode ficar vazio)."
    )
    r = client.messages.create(
        model=MODELO,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = r.content[0].text.strip()
    try:
        dados = json.loads(texto[texto.index("{"): texto.rindex("}") + 1])
        fala = " ".join(str(dados["fala"]).split())
        for outro, nota in dados.get("relacoes", {}).items():
            if outro in AGENTES and outro != nome:
                minhas[outro] = str(nota)[:80]
    except Exception:
        fala = " ".join(texto.split())[:300]
    rel[nome] = minhas
    escrever(f"- **{agora()} {nome}:** {fala.replace('*', '')}")

with open(REL, "w", encoding="utf-8") as f:
    json.dump(rel, f, ensure_ascii=False, indent=1)
