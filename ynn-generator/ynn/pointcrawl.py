"""Mapa de pontos (point-crawl) de um nível, seguindo o procedimento do
livro: o local de entrada fica no topo (camada 0) e cada passo "mais
fundo" liga o local atual a um novo local na camada seguinte, que pode se
ramificar. Cada local é um sorteio de `d20 + profundidade` em duas tabelas
— o Local (`tables.LOCAIS`, o núcleo) e o Detalhe (`tables.DETALHES`, o
modificador) — então quanto mais fundo, mais estranhos os resultados.

Eventos do livro que ligam locais distantes viram arestas extras: um
"atalho" para um local já explorado, mais raso, e uma "descida" para um
local bem mais fundo. As tabelas são originais; só o mecanismo é do livro.
"""

from . import tables

RELEVO_ORDEM = ["plano", "leve", "acentuado", "irregular"]

ARESTA_TRILHA = "trilha"
ARESTA_ATALHO = "atalho"
ARESTA_DESCIDA = "descida"


def roll_tabela(rng, tabela, profundidade):
    """`d20 + profundidade`, limitado ao tamanho da tabela (35 ou mais cai
    na última entrada). Retorna `(entrada, resultado_bruto)`."""
    resultado = rng.randint(1, 20) + profundidade
    return tabela[min(resultado, len(tabela)) - 1], resultado


def roll_detalhe(rng, profundidade):
    """Sorteia o Detalhe de um local na tabela do livro (`d20 + profundidade`).
    Devolve `texto`, `tipo_relevo`, `efeitos` (a etiqueta do detalhe, se houver) e
    `indice` (o número do detalhe na tabela, 1 a 35)."""
    (texto, relevo, efeito), bruto = roll_tabela(rng, tables.DETALHES, profundidade)
    return {
        "texto": texto,
        "tipo_relevo": relevo,
        "efeitos": [efeito] if efeito else [],
        "indice": min(bruto, len(tables.DETALHES)),
    }


def _novo_no(nos, profundidade, pai):
    no = {"id": len(nos), "profundidade": profundidade, "pai": pai}
    nos.append(no)
    return no


def generate_pointcrawl(rng, profundidade_max=4, max_nos=14, max_por_camada=6, chance_atalho=0.3, chance_descida=0.15):
    """Monta o grafo: nós por camada (0 a `profundidade_max`, sempre pelo
    menos um por camada), arestas "trilha" pai→filho e arestas extras
    "atalho"/"descida". Cada nó recebe `local` (nome), `tipo` (tipo de
    lote) e `detalhe`, sorteados na profundidade dele."""
    nos = []
    arestas = []
    _novo_no(nos, 0, None)
    camadas = [[0]]

    for profundidade in range(1, profundidade_max + 1):
        pais = camadas[-1]
        nova = []
        for pai in pais:
            n_filhos = rng.choice([0, 1, 1, 2, 2, 3])
            for _ in range(n_filhos):
                if len(nos) >= max_nos or len(nova) >= max_por_camada:
                    break
                filho = _novo_no(nos, profundidade, pai)
                arestas.append({"de": pai, "para": filho["id"], "tipo": ARESTA_TRILHA})
                nova.append(filho["id"])
        if not nova:
            pai = rng.choice(pais)
            filho = _novo_no(nos, profundidade, pai)
            arestas.append({"de": pai, "para": filho["id"], "tipo": ARESTA_TRILHA})
            nova.append(filho["id"])
        camadas.append(nova)

    ligados = {frozenset((a["de"], a["para"])) for a in arestas}

    def _tentar_ligar(origem, candidatos, tipo):
        candidatos = [c for c in candidatos if frozenset((origem["id"], c["id"])) not in ligados]
        if not candidatos:
            return
        alvo = rng.choice(candidatos)
        ligados.add(frozenset((origem["id"], alvo["id"])))
        arestas.append({"de": origem["id"], "para": alvo["id"], "tipo": tipo})

    for no in list(nos):
        if no["profundidade"] >= 2 and rng.random() < chance_atalho:
            _tentar_ligar(no, [n for n in nos if n["profundidade"] < no["profundidade"]], ARESTA_ATALHO)
        if no["profundidade"] <= profundidade_max - 2 and rng.random() < chance_descida:
            _tentar_ligar(no, [n for n in nos if n["profundidade"] >= no["profundidade"] + 2], ARESTA_DESCIDA)

    for no in nos:
        (nome, tipo), _ = roll_tabela(rng, tables.LOCAIS, no["profundidade"])
        no["local"] = nome
        no["tipo"] = tipo
        no["detalhe"] = roll_detalhe(rng, no["profundidade"])

    return {"profundidade_max": profundidade_max, "nos": nos, "arestas": arestas}


def layout_grafo(rng, grafo, field_width=105.0, field_depth=68.0, margem=9.0, folga=16.0, raios=None, grupos=None):
    """Posiciona os nós no campo como o mapa de papel do livro: a entrada
    no topo (z menor) e cada camada numa fileira mais abaixo. Dentro da
    fileira os nós ficam perto do pai, separados por `folga` metros — ou pelo que couber os dois, se `raios` (id do nó -> raio que ele ocupa, ex. uma estufa imensa) pedir mais. `grupos` (id -> rótulo) afasta nós do mesmo grupo (ex. várias estufas minúsculas) por pelo menos `DISTANCIA_MESMO_GRUPO`. No fim, um relaxamento afasta qualquer par que ainda se sobreponha, mesmo de fileiras diferentes.
    Devolve a lista de lotes (`tipo`, `x`, `z` e os dados do nó)."""
    raios = raios or {}
    grupos = grupos or {}
    profundidade_max = max(grafo["profundidade_max"], 1)
    passo_z = (field_depth - 2 * margem) / profundidade_max
    limite_x = field_width / 2 - 8.0

    por_camada = {}
    for no in grafo["nos"]:
        por_camada.setdefault(no["profundidade"], []).append(no)

    x_de = {0: 0.0}
    for profundidade in sorted(por_camada):
        if profundidade == 0:
            continue
        camada = sorted(por_camada[profundidade], key=lambda n: (x_de[n["pai"]], n["id"]))
        alvos = []
        for no in camada:
            irmaos = [m for m in camada if m["pai"] == no["pai"]]
            alvos.append(x_de[no["pai"]] + (irmaos.index(no) - (len(irmaos) - 1) / 2) * folga)
        xs = []
        for alvo, no in zip(alvos, camada):
            if not xs:
                xs.append(alvo)
            else:
                anterior = camada[len(xs) - 1]
                gap = max(folga, raios.get(anterior["id"], 6.0) + raios.get(no["id"], 6.0) + 3.0)
                if grupos.get(anterior["id"]) is not None and grupos.get(anterior["id"]) == grupos.get(no["id"]):
                    gap = max(gap, DISTANCIA_MESMO_GRUPO)
                xs.append(max(alvo, xs[-1] + gap))
        if xs[-1] - xs[0] > 2 * limite_x:
            largura = xs[-1] - xs[0]
            xs = [-limite_x + (x - xs[0]) * 2 * limite_x / largura for x in xs]
        else:
            if xs[-1] > limite_x:
                xs = [x - (xs[-1] - limite_x) for x in xs]
            if xs[0] < -limite_x:
                xs = [x + (-limite_x - xs[0]) for x in xs]
        for no, x in zip(camada, xs):
            x_de[no["id"]] = x

    plots = []
    for no in grafo["nos"]:
        z = -field_depth / 2 + margem + no["profundidade"] * passo_z
        plots.append(
            {
                "tipo": no["tipo"],
                "x": x_de[no["id"]] + rng.uniform(-1.5, 1.5),
                "z": z + rng.uniform(-1.5, 1.5),
                "no_id": no["id"],
                "profundidade": no["profundidade"],
                "local": no["local"],
                "detalhe": no["detalhe"],
            }
        )
    _separar(plots, raios, grupos, field_width, field_depth)
    return plots


DISTANCIA_MESMO_GRUPO = 24.0


def _separar(plots, raios, grupos, field_width, field_depth, passos=160):
    """Relaxamento: afasta, ao longo da reta que os une, todo par de lotes
    cujos raios ocupados se sobrepõem (ou, no mesmo grupo, que estejam mais
    perto que `DISTANCIA_MESMO_GRUPO`), e mantém cada centro dentro do campo."""
    r = [raios.get(p["no_id"], 6.0) for p in plots]
    g = [grupos.get(p["no_id"]) for p in plots]
    meio_x, meio_z = field_width / 2, field_depth / 2
    for _ in range(passos):
        moveu = False
        for i in range(len(plots)):
            for j in range(i + 1, len(plots)):
                dx = plots[j]["x"] - plots[i]["x"]
                dz = plots[j]["z"] - plots[i]["z"]
                dist = (dx * dx + dz * dz) ** 0.5
                minimo = r[i] + r[j] + 2.0
                if g[i] is not None and g[i] == g[j]:
                    minimo = max(minimo, DISTANCIA_MESMO_GRUPO)
                if dist < minimo:
                    moveu = True
                    if dist < 1e-6:
                        dx, dz, dist = 1.0, 0.0, 1.0
                    empurra = (minimo - dist) / 2.0
                    ux, uz = dx / dist, dz / dist
                    plots[i]["x"] -= ux * empurra
                    plots[i]["z"] -= uz * empurra
                    plots[j]["x"] += ux * empurra
                    plots[j]["z"] += uz * empurra
        for p in plots:
            p["x"] = max(-meio_x, min(meio_x, p["x"]))
            p["z"] = max(-meio_z, min(meio_z, p["z"]))
        if not moveu:
            break
