Você trabalha para o Gerente de Produção do ep013 do PipoPop, como DESENVOLVEDOR do kit2d (G3, "Desenvolvedores": recurso visual novo que o cenas.json não consegue expressar). Prazo: pronto e no git até 10h30 de hoje (26/11), antes do O2 começar.
Rode tudo a partir de /home/claude/pipo-canal. Leia antes: kit2d/CENAS.md (seções 1, 3, 4), kit2d/render2d.py (como um "tipo" é desenhado e animado) e um elemento parecido como modelo (pipo/humano em kit2d/).

PROBLEMA: o ep013 (série "E se os animais tivessem olhos pra frente?") precisa de bichos, e o motor não tem nenhum.
FAÇA um elemento novo `"tipo": "bicho"` no nosso traço (contorno grosso, cor chapada com sombra simples, olhos grandes expressivos), com:
- `especie`: pombo, gato, vaca, galinha, cavalo, coelho (cachorro e coruja se sobrar tempo; não são obrigatórios).
- `olhos`: "lado" (como é de verdade: um olho de cada lado da cabeça, de frente só se vê 1 olho de cada lado no limite do contorno) ou "frente" (os dois olhos juntos na frente da cara, olhar de gente encarando, com sobrancelhinha). Gato sempre "frente".
- `vista`: "frente" (encarando a câmera), "perfil" e "cima" (bicho visto do alto). Em "cima", `campo` (graus, ex. 340 ou 120) desenha o cone de visão translúcido saindo dos olhos, e `cego`: true pinta a zona cega em vermelho translúcido (anime `campo` com `muda`).
- `olhar` (camera, esq, dir, cima, baixo), `expressao` (neutro, desconfiado, julgando, assustado, feliz), `pose` (parado, bicando, agachado [gato pronto pra pular], voando [pombo/galinha batendo asa]).
- Vida própria: piscar, respirar, rabo ou orelha mexendo; o pombo balança a cabeça ao andar.
- Funciona com as ações existentes: entra, sai, move, escala, pula, treme, squash, soco, muda, e com `ancora` (ex.: "calcada" na rua). Tamanho base: com `escala` 1, ~420 px de altura.
- Entra no QA de cena como personagem (rosto na faixa da legenda acusa, como o humano).
Sem copiar personagem, mascote ou desenho de terceiros: traço próprio.

TESTE: um cenas.json de teste em /tmp ou kit2d/testes/ com as 6 espécies nas 3 vistas e os 2 olhos; rode `python3 kit2d/render2d.py <dir> --previa` e olhe a folha com os seus olhos (o olho "frente" tem que ler como "cara de gente" sem som). Meça o custo por quadro (não pode dobrar o tempo de render).
DOCUMENTE: linha do `bicho` na tabela de elementos do kit2d/CENAS.md, com um exemplo JSON curto. Commit e push no main com mensagem clara (sem chave de API).

Responda ao gerente em até 10 linhas: propriedades finais (nomes exatos), caminho da folha de teste, ms por quadro, o que ficou de fora e o hash do commit.
ACEITE: 6 espécies desenhadas nos 2 olhos e 3 vistas; cone de visão com zona cega em "cima"; ações e âncoras funcionando; folha de teste sem defeito visível; CENAS.md atualizado; commit no git; render não fica mais de 1,3x mais lento.
