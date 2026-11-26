# 07. Dados: tudo vira dado (Lucas, 26/11)

Ideia: cada vídeo é um experimento. Guardamos O QUE FIZEMOS (características) e O QUE ACONTECEU (métricas por rede e por janela de tempo), no git, em formato estruturado, para comparar, achar padrão e decidir. Ferramenta: kit/dados.py. Pasta: dados/.

## O que registrar
- dados/videos.jsonl (1 por vídeo): pilar, aposta (seguro/ousado/evolução), tema, emoção, o que tem de reconhecível, gancho, título (tamanho, número, pergunta), descrição, hashtags, comentário do canal, duração, horário, voz, música, estilo de animação, versão da Pipo, foto real, meme, erro proposital, série/parte, nota do Gemini, experimentos. Quem produz o vídeo grava ao colocar na fila (`python3 kit/dados.py video <pasta>`); campos novos no meta.json entram sozinhos se o script for atualizado.
- dados/posts.jsonl (1 por vídeo x rede): id, horário, caminho (metricool/buffer/studio/chrome).
- dados/metricas.jsonl (1 por vídeo x rede x janela 24h/72h/7d/30d): views, alcance, curtidas, comentários, compartilhamentos, salvamentos, seguidores ganhos, retenção média, % Visualizado vs. Deslizado, duração média assistida, cliques no perfil. Também a soma das 3 redes (rede = "total").
Fontes: Metricool (getAnalyticsDataByMetrics / getAnalyticsAvailableMetrics), Buffer (API), YouTube Studio e painel profissional do Instagram/Facebook pelo Chrome quando ele estiver aberto (retenção e "deslizado" só aparecem lá).

## Quem coleta e quando
- Vigia das 20:23: métricas 24h, 72h e 7d dos vídeos que fizeram aniversário nessa janela.
- Semanal: janela 30d, `python3 kit/dados.py tabela` + `analise`, e a leitura vira decisões (06_CRESCIMENTO).
- Mensal (primeiro domingo do mês, dentro da semanal): análise profunda em docs/diretor/analises/AAAA-MM.md: o que separa os 20% melhores dos 20% piores, por rede; regressão/classificação simples SÓ com n >= 60 e poucas variáveis (para não enganar a gente com ruído); hipóteses para o mês seguinte.

## Cuidado com ruído (sinceridade)
Canal novo tem views muito instáveis no começo (o algoritmo ainda está testando o público). Uma diferença só vale quando se repete em vários vídeos. Mudança grande com base em 1 ou 2 vídeos é palpite, não dado; registrar como palpite.

## Plataforma por plataforma
As redes são diferentes. Se algo funciona numa e não na outra (até a Pipo, o estilo, a duração, o horário), pode mudar só naquela rede. O G6 compara sempre por rede.
