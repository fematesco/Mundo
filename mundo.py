import anthropic, datetime, json, random

client = anthropic.Anthropic()
MODELO = "claude-haiku-4-5-20251001"
BRT = datetime.timezone(datetime.timedelta(hours=-3))
LOG, REL, EST = "mundo.md", "relacoes.json", "estado.json"

AGENTES = {
    "Alex": "sarcástico, profissional de T.I., humor ácido porém bondoso",
    "Damaris": "curiosa, muito bem-humorada e carismática",
    "Felipe": "amistoso, um pouco estraga-prazeres e orgulhoso, mas sempre simpático",
    "Gleidy": "humilde, mais séria mas amistosa, um pouco sentimental",
}

FASES = [
    (0, "Primeiras horas", "cuidar dos feridos, juntar o que sobrou do avião, achar água e improvisar um abrigo"),
    (24, "Organização", "achar água fixa, pescar e coletar comida, manter o fogo, melhorar o abrigo, explorar os arredores"),
    (72, "Exploração e tensão", "explorar a ilha, lidar com tempestades, doenças e brigas, guardar mantimentos, criar sinais de SOS"),
    (168, "Esperança e perigo", "consertar rádio e sinalização, lidar com avistamentos falsos, cansaço e moral baixa"),
    (288, "Rumo ao resgate", "esforço final para serem encontrados, jangada, laços fortes entre o grupo"),
]

EVENTOS = [
    [
        "Uma parte da asa do avião é encontrada na praia, com malas espalhadas por perto.",
        "Uma mala com garrafas de água e snacks é achada entre os destroços.",
        "Uma pequena explosão no motor destruído assusta todos e os afasta da fuselagem.",
        "Um ferimento mais sério é notado e precisa ser tratado com o kit de primeiros socorros.",
        "Um bando de caranguejos aparece na areia: comida em potencial.",
        "O sol forte e a falta de sombra causam insolação leve em alguém do grupo.",
        "Um barulho estranho vem da mata: um animal, ou só o vento?",
        "A maré sobe e leva parte dos objetos que estavam na areia.",
        "Uma mochila de mão com isqueiro e canivete é encontrada entre os destroços.",
    ],
    [
        "Uma poça de água da chuva, limpa o bastante, é achada nas pedras.",
        "Um cardume grande aparece perto da praia: ótima chance de pescar.",
        "Chuva forte à noite alaga o abrigo improvisado.",
        "Frutas desconhecidas são achadas numa árvore; ninguém sabe se são seguras.",
        "Um bicho esperto rouba comida do acampamento.",
        "O fogo quase apaga durante a madrugada.",
        "Pegadas de um animal grande aparecem perto do acampamento.",
        "Uma tartaruga desova na praia durante a noite.",
        "Um bambuzal é descoberto: material perfeito para abrigo e ferramentas.",
        "Uma mala com roupas quentes e cobertores boia até a praia.",
    ],
    [
        "Ventos fortes derrubam parte do abrigo.",
        "Alguém tem febre depois de comer algo suspeito.",
        "Uma caverna é encontrada no interior da ilha, com sinais de que já foi usada.",
        "Uma discussão séria começa por causa da divisão de comida.",
        "A água da nascente fica turva e precisa ser fervida.",
        "Fumaça de uma ilha distante é vista no horizonte.",
        "Ferramentas antigas e enferrujadas aparecem na caverna, sugerindo visitantes antigos.",
        "Um enxame de insetos ataca à noite, com picadas dolorosas.",
        "A pesca vai mal por dias seguidos e a comida diminui.",
        "Uma trilha até o topo do morro é aberta e dali se vê a ilha inteira.",
    ],
    [
        "Um avião passa muito alto e distante, mas ninguém consegue sinalizar a tempo.",
        "Um barco aparece no horizonte à tarde e some sem notar a fogueira.",
        "Um deslizamento de terra bloqueia o caminho até a nascente.",
        "Alguém começa a ter pesadelos e a perder a esperança.",
        "Uma baleia passa perto da praia e emociona o grupo.",
        "Os fósforos e isqueiros estão no fim.",
        "Restos de um náufrago antigo, com um diário, são achados numa enseada.",
        "Uma tempestade elétrica atinge o morro e derruba a antena improvisada.",
        "Alguém quer arriscar uma jangada sozinho.",
    ],
    [
        "O rádio chia e capta uma transmissão distante, ainda sem resposta.",
        "Um helicóptero é ouvido ao longe durante a noite.",
        "A jangada fica pronta, mas o mar está agitado.",
        "O grupo faz uma cerimônia em memória dos que morreram no acidente.",
        "Uma frente fria ameaça derrubar o plano de resgate.",
        "Um avião de busca sobrevoa a ilha em círculos, mas não os vê.",
    ],
]

# (hora na ilha, evento, sinalização mínima, é o final?)
MARCOS = [
    (6, "O sol começa a se pôr e o grupo percebe que precisa de fogo e abrigo antes da primeira noite.", 0, False),
    (24, "Amanhece o segundo dia: a água quase acabou e é urgente achar uma fonte.", 0, False),
    (48, "Uma nascente de água doce é finalmente encontrada. O grupo decide fazer dela a base.", 0, False),
    (72, "A primeira grande tempestade tropical atinge a ilha.", 0, False),
    (120, "O cansaço e a tensão explodem em pequenas brigas dentro do grupo.", 0, False),
    (168, "Uma semana na ilha: o grupo lembra de quem ficou em casa e renova o compromisso de sobreviver.", 0, False),
    (192, "Um rádio parcialmente danificado é encontrado no cockpit do avião.", 0, False),
    (240, "O rádio volta a funcionar por alguns segundos e emite um pedido de socorro fraco.", 0, False),
    (336, "Uma equipe de resgate avista a fumaça da fogueira e se aproxima da ilha. Salvos!", 40, True),
]

ICONES = {"agua": "💧", "comida": "🍖", "abrigo": "🏕️", "fogo": "🔥",
          "saude": "❤️", "moral": "🙂", "sinalizacao": "📡"}


def carregar(caminho, padrao):
    try:
        return json.load(open(caminho, encoding="utf-8"))
    except Exception:
        return padrao


def salvar(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def escrever(linha, modo="a"):
    with open(LOG, modo, encoding="utf-8") as f:
        f.write(linha + "\n")


def ler_log(n=20):
    try:
        return "".join(open(LOG, encoding="utf-8").readlines()[-n:])
    except FileNotFoundError:
        return ""


def limpar(x):
    return " ".join(str(x).replace("*", "").split())


def pedir(prompt, max_tokens):
    r = client.messages.create(model=MODELO, max_tokens=max_tokens,
                               messages=[{"role": "user", "content": prompt}])
    t = r.content[0].text.strip()
    try:
        return json.loads(t[t.index("{"): t.rindex("}") + 1]), t
    except Exception:
        return None, t


def travar(rec):
    for k in rec:
        rec[k] = max(0, min(100, rec[k]))


t = datetime.datetime.now(BRT)
est = carregar(EST, None)
rel = carregar(REL, {})

if est is None:
    est = {"inicio": t.isoformat(), "ultimo": t.isoformat(),
           "recursos": {"agua": 20, "comida": 15, "abrigo": 5, "fogo": 0,
                        "saude": 60, "moral": 50, "sinalizacao": 0},
           "marcos": [], "usados": [], "historia": [],
           "itens": ["destroços do avião na praia"], "fim": False}
    rel = {}
    escrever("# ✈️ Diário da Ilha\n", "w")
    escrever(f"- **D1 · {t:%H:%M} 🌍 Narrador:** O avião cai no oceano. Alex, Damaris, "
             "Felipe e Gleidy chegam à praia de uma ilha deserta, feridos e em choque. "
             "A luta pela sobrevivência começa.")
    horas = 1.0
else:
    if est.get("fim"):
        raise SystemExit
    ultimo = datetime.datetime.fromisoformat(est["ultimo"])
    horas = min(24, max(0.25, (t - ultimo).total_seconds() / 3600))

inicio = datetime.datetime.fromisoformat(est["inicio"])
horas_ilha = (t - inicio).total_seconds() / 3600
dia = int(horas_ilha // 24) + 1
hora = f"D{dia} · {t:%H:%M}"
periodo = ("madrugada" if t.hour < 6 else "manhã" if t.hour < 12
           else "tarde" if t.hour < 18 else "noite")
fi = max(i for i, f in enumerate(FASES) if f[0] <= horas_ilha)

rec = est["recursos"]
rec["agua"] -= 2 * horas
rec["comida"] -= 1 * horas
rec["fogo"] -= 1 * horas
rec["moral"] -= 0.3 * horas
travar(rec)

evento, fim = None, False
for i, (h, txt, minsin, final) in enumerate(MARCOS):
    if i not in est["marcos"] and h <= horas_ilha and rec["sinalizacao"] >= minsin:
        evento, fim = txt, final
        est["marcos"].append(i)
        break
if not evento and random.random() < 0.7:
    livres = [e for e in EVENTOS[fi] if e not in est["usados"]]
    if livres:
        evento = random.choice(livres)
        est["usados"].append(evento)
if evento:
    escrever(f"- **{hora} 🌍 Narrador:** {evento}")

resumo = "\n".join(est["historia"][-8:]) or "(a história está começando)"
estado_txt = json.dumps({k: int(v) for k, v in rec.items()}, ensure_ascii=False)
itens = ", ".join(est["itens"])

ordem = list(AGENTES.items())
random.shuffle(ordem)
linhas = []

for nome, persona in ordem:
    minhas = rel.get(nome, {})
    outros = ", ".join(n for n in AGENTES if n != nome)
    prompt = (
        f"Você é {nome}, {persona}. Sobrevivente de um acidente aéreo numa ilha deserta, "
        f"junto com {outros}.\n"
        f"Agora é dia {dia} na ilha, {periodo} ({t:%H:%M}). Passaram-se {horas:.1f}h desde o último registro.\n"
        f"Fase: {FASES[fi][1]}. Foco do grupo: {FASES[fi][2]}.\n"
        f"Recursos do grupo (0-100): {estado_txt}\n"
        f"Itens do grupo: {itens}\n"
        f"O que você pensa dos outros: {json.dumps(minhas, ensure_ascii=False) or 'nada ainda'}\n"
        f"Resumo da história até agora:\n{resumo}\n"
        f"Evento agora: {evento or 'nada de novo'}\n"
        f"Últimas linhas do diário:\n{ler_log()}\n\n"
        f"Conte o que você FEZ nessas {horas:.1f}h: atividades concretas e proporcionais ao tempo "
        "(1h = tarefa pequena; 6h ou mais = trabalho grande). Se for noite ou madrugada, o grupo "
        "descansa, vigia o fogo ou conversa; trabalho pesado fica para o dia. "
        "Não repita ações antigas: faça a história avançar. Reaja ao evento, se houver.\n"
        "Responda SOMENTE em JSON, assim:\n"
        '{"acao": "1-2 frases no passado, sobre o que você fez", '
        '"fala": "uma frase curta que você diz (pode ser vazia)", '
        '"relacoes": {"NomeDeAlguem": "opinião curta atualizada"}}\n'
        "Em relacoes, inclua só quem mudou na sua opinião (pode ficar vazio)."
    )
    dados, txt = pedir(prompt, 350)
    if dados and "acao" in dados:
        acao = limpar(dados["acao"])
        fala = limpar(dados.get("fala", ""))
        if isinstance(dados.get("relacoes"), dict):
            for o, nota in dados["relacoes"].items():
                if o in AGENTES and o != nome:
                    minhas[o] = limpar(nota)[:80]
    else:
        acao, fala = limpar(txt)[:250], ""
    rel[nome] = minhas
    linha = f"- **{hora} {nome}:** {acao}" + (f' — "{fala}"' if fala else "")
    linhas.append(linha)
    escrever(linha)

extra = ("ESTE É O DESFECHO: o resgate chegou. Escreva um final emocionante. "
         if fim else "")
prompt = (
    f"Você é o narrador de uma história de sobrevivência numa ilha deserta (dia {dia}, {periodo}). "
    f"Passaram-se {horas:.1f}h desde o último balanço. {extra}\n"
    f"Fase: {FASES[fi][1]}. Evento: {evento or 'nenhum'}.\n"
    f"Recursos atuais (0-100): {estado_txt}\n"
    f"Resumo até agora:\n{resumo}\n"
    "O que cada um fez agora:\n" + "\n".join(linhas) + "\n\n"
    "Resuma o progresso REAL do grupo nessas horas, de forma proporcional ao tempo. "
    "Se algum recurso estiver abaixo de 20, mostre a tensão. "
    "Responda SOMENTE em JSON:\n"
    '{"balanco": "2-3 frases sobre o que o grupo conquistou ou perdeu", '
    '"delta": {"agua": 0, "comida": 0, "abrigo": 0, "fogo": 0, "saude": 0, "moral": 0, "sinalizacao": 0}, '
    '"itens_novos": []}\n'
    "Em delta, use números (positivos ou negativos) que reflitam o efeito das ações."
)
dados, txt = pedir(prompt, 450)
lim = min(30, 6 * horas + 2)
if dados:
    balanco = limpar(dados.get("balanco", ""))
    if isinstance(dados.get("delta"), dict):
        for k, v in dados["delta"].items():
            if k in rec:
                try:
                    rec[k] += max(-lim, min(lim, float(v)))
                except (TypeError, ValueError):
                    pass
    if isinstance(dados.get("itens_novos"), list):
        for i in dados["itens_novos"]:
            i = limpar(i)
            if i and i not in est["itens"]:
                est["itens"].append(i)
        est["itens"] = est["itens"][-15:]
else:
    balanco = limpar(txt)[:300]
travar(rec)

escrever(f"- **{hora} 📊 Balanço:** {balanco}")
escrever("- " + " ".join(f"{ICONES[k]}{int(v)}" for k, v in rec.items()))

est["historia"].append(f"{hora}: {balanco}")
est["historia"] = est["historia"][-40:]
est["ultimo"] = t.isoformat()
if fim:
    est["fim"] = True
salvar(EST, est)
salvar(REL, rel)