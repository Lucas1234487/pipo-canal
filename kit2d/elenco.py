"""Elenco fixo do PipoPop: personagens recorrentes prontos para o tipo humano.
Uso no cenas.json: {"tipo": "humano", "preset": "gala", ...}. Qualquer propriedade escrita no elemento vale por cima do preset.
Regra: a piada é o traço e a atitude, nunca o grupo (raça, etnia, religião, deficiência ou corpo como humilhação)."""

ELENCO = {
    "vizinho_exagerado": dict(cabelo="calvicie", cabelo_cor="castanho", pele="clara", corpo="forte", cabeca="quadrada", nariz="batata",
                              sobrancelha="grossa", barba="bigodao", roupa="#D8322A", estampa="natal", expressao="gargalhada"),
    "tia_do_zap": dict(cabelo="cacheado", cabelo_cor="ruivo", pele="media", cabeca="pera", oculos=True, oculos_tipo="ponta", oculos_cor="#C8318A",
                       segura="celular", olhar="celular", pinta="esq", roupa="#16A57A", estampa="havaiana", expressao="feliz"),
    "gala": dict(cabelo="topete", cabelo_cor="preto", pele="morena", queixo="quadrado", sobrancelha="grossa", brilho=True, corpo="forte",
                 roupa="#FFF3E0", manga="longa", expressao="feliz"),
    # crush (refeita em 25/11/2026 a pedido do dono: "loira de olho azul com um corpão"): bonita de verdade, cartoon de estúdio,
    # elegante e NÃO reveladora. Cabelão loiro até a cintura com ondas, brilho e balanço; olhos azuis amendoados com cílios;
    # rosto delicado; batom; corpo curvilíneo (cintura fina, quadril) com blusa justa de decote canoa alto e jeans de cintura alta com cinto.
    "crush": dict(cabelo="sereia", cabelo_cor="dourado", luzes="mel", pele="clara", corpo="curvilineo", cabeca="delicada",
                  olhos="marcantes", iris="#2E8BEA", sobrancelha="arqueada", labios="#E0436B", nariz="delicado",
                  brilho="sutil", aura="#FFE9B8", roupa="#E8354A", gola="canoa", manga="curta", calca="#3F6FC8", cintura_alta=True,
                  cinto="#7A4A2A", brincos="gota", colar="#F2C14E", sapato="#D93A5E", expressao="charmoso"),
    # crush_ele: a versão masculina, igualmente bonito (nada de caricato): ondulado com volume, barba por fazer, sorriso de canto
    "crush_ele": dict(cabelo="ondulado", cabelo_cor="preto", pele="escura", olhos="grandes", iris="#6B3E1F", sobrancelha="marcada",
                      barba="rala", brilho="sutil", aura="#D9ECFF", roupa="#FFFFFF", jaqueta="#2747C9", manga="longa",
                      colar="#E6E6EE", calca="#2B2440", sapato="#FFFFFF", expressao="charmoso"),
    "chefe": dict(cabelo="calvicie", cabelo_cor="grisalho", pele="clara", corpo="forte", cabeca="feijao", sobrancelha="monocelha",
                  gravata="#2A3FD1", roupa="#FFF8EC", manga="longa", queixo="furinho", expressao="bravo"),
    "estagiario": dict(cabelo="arrepiado", cabelo_cor="castanho", pele="media", corpo="magro", olheiras=True, fone="#2A7DE1", dentes="dentuco",
                       cabeca="lua", orelhas="abano", mochila="#FFC21A", roupa="#8A8FA8", expressao="cansado"),
    "vovo_turbo": dict(idade="idoso", cabelo="coque", cabelo_cor="branco", pele="escura", oculos=True, oculos_tipo="escuro", faixa="#FF5A8A",
                       manga="regata", roupa="#2747C9", expressao="gargalhada", pose="comemorando"),
    "crianca_terrivel": dict(idade="crianca", cabelo="arrepiado", cabelo_cor="ruivo", pele="clara", sardas=True, dentes="banguela",
                             orelhas="abano", roupa="#FFC21A", estampa="listras", expressao="feliz", nariz="arrebitado"),
    "tiozao_do_churrasco": dict(cabelo="curto", cabelo_cor="preto", pele="morena", corpo="forte", cabeca="pera", barba="bigode", nariz="batata",
                                avental="#E8452C", pochete="#3A2E52", bone="#FFF3E0", roupa="#1F5FD1", expressao="feliz"),
    "nerd": dict(cabelo="franja_reta", cabelo_cor="castanho", pele="media", dentes="aparelho", oculos=True, oculos_tipo="fundo_de_garrafa",
                 gravata="#E8452C", roupa="#C8E6FF", estampa="xadrez", sobrancelha="fina", expressao="feliz", pescoco="longo"),
    # marombeiro: o esportista do elenco (sem futebol, sem pessoa real): braço enorme, regata, garrafinha gigante, veia na testa, bronze
    "marombeiro": dict(cabelo="raspado", cabelo_cor="preto", pele="media", bronzeado=True, corpo="maromba", manga="regata", roupa="#E8352A",
                       veia=True, segura="garrafa", queixo="quadrado", pescoco="curto", sobrancelha="grossa", calca="#2B2440", sapato="#FFFFFF",
                       expressao="esforco", pose="muque"),
    # maratonista de domingo: faixa, relógio, roupa neon, número de peito, suor voando, ofegante
    "maratonista": dict(cabelo="curto", cabelo_cor="ruivo", pele="clara", corpo="magro", faixa="#FF3DA8", relogio="#FF3DA8",
                        roupa="#C6FF1A", manga="regata", numero="42", suor=True, calca="#2747C9", sapato="#FF7A1A", expressao="ofegante", pose="correndo"),
    # neymaro: EXCEÇÃO aprovada pelo dono em 24/11/2026 (caricatura simpática; camisa amarela GENÉRICA: sem escudo, número, patrocínio ou logo)
    "neymaro": dict(cabelo="moicano", cabelo_cor="platinado", pele="media", faixa="#FFFFFF", brincos="brilhante", sobrancelha="marcada",
                    barba="rala", roupa="#FFD21F", calca="#1F5FD1", sapato="#FF3DA8", chuteira=True, corpo="magro",
                    expressao="gargalhada", pose="comemorando"),
    "influencer": dict(cabelo="rabo_de_cavalo", cabelo_cor="rosa", pele="clara", cilios=True, brilho="sutil", segura="celular", olhar="celular",
                       roupa="#FFF3E0", sobrancelha="fina", nariz="arrebitado", expressao="apaixonado"),
    "seu_ze_da_banca": dict(idade="idoso", cabelo="careca", pele="media", barba="cheia", cabelo_cor="grisalho", nariz="batata", orelhas="abano",
                            corpo="magro", roupa="#C8844A", estampa="xadrez", bone="#2B2440", expressao="nervoso"),
}

ELENCO["esportista"] = ELENCO["marombeiro"]   # nome antigo continua valendo
