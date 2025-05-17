from flask import Flask, render_template, request, url_for
import google.generativeai as genai
import os
import re
from datetime import datetime
from dotenv import load_dotenv # Importa a biblioteca python-dotenv

# Carrega as variáveis de ambiente do ficheiro .env (se existir)
# Isto deve vir ANTES de tentar aceder às variáveis de ambiente
load_dotenv() 

# Cria uma instância do nosso aplicativo Flask
app = Flask(__name__)

# --- Configuração da API Key do Google e do Modelo Gemini ---
# Agora, a API Key será lida EXCLUSIVAMENTE da variável de ambiente
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') 

model = None # Inicializa a variável do modelo
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        print("Modelo Gemini configurado com sucesso através da variável de ambiente!")
    except Exception as e:
        print(f"Erro ao configurar a API Gemini ou o modelo com a chave da variável de ambiente: {e}")
        print("Verifique se sua API Key é válida e se não há problemas de conexão.")
else:
    # Esta mensagem aparecerá se a chave não for encontrada no .env ou nas variáveis de ambiente do sistema
    print("###########################################################################")
    print("### ATENÇÃO: GOOGLE_API_KEY NÃO ENCONTRADA NAS VARIÁVEIS DE AMBIENTE! ###")
    print("###                                                                     ###")
    print("### Para rodar localmente, crie um ficheiro chamado '.env' na raiz      ###")
    print("### do projeto e adicione a linha:                                    ###")
    print("### GOOGLE_API_KEY=SUA_CHAVE_API_REAL_AQUI                            ###")
    print("### (Substitua SUA_CHAVE_API_REAL_AQUI pela sua chave real, sem aspas)###")
    print("###                                                                     ###")
    print("### O assistente não poderá usar a IA do Gemini sem uma API Key válida. ###")
    print("###########################################################################")

# --- CONTEÚDO FIXO PARA AS REVISÕES PADRÕES ---
conteudo_fixo_revisoes = {
    "troca-oleo-motor": {
        "titulo": "Troca de Óleo do Motor",
        "detalhes_html": """
            <div>
                <strong>1. O que é e qual sua função?</strong>
                <p>O óleo do motor é vital para lubrificar as peças móveis do motor, reduzir o atrito, limpar impurezas, ajudar no arrefecimento e proteger contra a corrosão. A troca de óleo consiste em remover o óleo usado e o filtro de óleo, e substituí-los por novos.</p>
            </div>
            <div>
                <strong>2. Por que é importante?</strong>
                <p>Negligenciar a troca de óleo pode levar ao desgaste prematuro do motor, superaquecimento, formação de borra, perda de desempenho e, em casos extremos, à fundição do motor, resultando em reparos muito caros.</p>
            </div>
            <div>
                <strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong>
                <p><strong>Tempo:</strong> Geralmente a cada 6 meses ou 12 meses.</p>
                <p><strong>Quilometragem (KM):</strong> Comumente a cada 5.000 km, 7.500 km ou 10.000 km.</p>
                <p><strong>Observação:</strong> Sempre verifique o manual do proprietário do seu veículo! O tipo de óleo (mineral, semissintético, sintético) e o tipo de uso do carro (urbano severo, estrada) influenciam o intervalo.</p>
            </div>
            <div>
                <strong>4. Como verificar (para leigos, se aplicável e seguro):</strong>
                <p>Com o motor frio e o carro em local plano, retire a vareta de óleo, limpe-a com um pano, insira-a totalmente e retire novamente. Verifique se o nível está entre as marcas "MÍN" e "MÁX". Observe também a cor e a viscosidade do óleo (deve estar límpido ou âmbar, não muito escuro ou grosso).</p>
            </div>
            <div>
                <strong>5. Sinais de Problema ou Desgaste:</strong>
                <p>Luz de advertência do óleo acesa no painel, barulhos metálicos vindos do motor (batidas), fumaça excessiva saindo do escapamento, nível de óleo baixando rapidamente.</p>
            </div>
            <div>
                <strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong>
                <p><strong>Peças (Óleo + Filtro):</strong> R$ 80 - R$ 250 (varia muito com tipo de óleo e marca).</p>
                <p><strong>Mão de obra:</strong> R$ 50 - R$ 150.</p>
                <p><strong>Aviso:</strong> Valores altamente ESTIMATIVOS. Consulte oficinas para orçamentos precisos.</p>
            </div>
            <p><em>Sempre consulte o manual do proprietário e um mecânico de confiança.</em></p>
        """
    },
    "filtro-oleo": {
        "titulo": "Filtro de Óleo",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>O filtro de óleo tem a função de reter partículas e impurezas (metálicas, borra, sujeira) que circulam no óleo do motor. Ele garante que o óleo que lubrifica as peças esteja o mais limpo possível.</p></div><div><strong>2. Por que é importante?</strong><p>Um filtro de óleo sujo ou obstruído perde sua capacidade de filtragem. Isso permite que impurezas circulem pelo motor, acelerando o desgaste das peças, podendo entupir galerias de lubrificação e comprometer a vida útil do motor.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Recomendação:</strong> É altamente recomendado trocar o filtro de óleo TODA VEZ que o óleo do motor for trocado.</p><p><strong>Observação:</strong> O custo do filtro é relativamente baixo comparado aos benefícios de proteger o motor. Não vale a pena economizar neste item.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p>A verificação direta do estado interno do filtro não é prática para leigos. A melhor prática é seguir a recomendação de troca conjunta com o óleo.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Geralmente não há sinais diretos de um filtro de óleo ruim até que problemas maiores no motor comecem a surgir devido à má lubrificação. A luz de advertência do óleo pode acender se houver restrição severa, mas isso já indica um problema crítico.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Peças (Filtro):</strong> R$ 20 - R$ 60.</p><p><strong>Mão de obra:</strong> Geralmente inclusa no custo da troca de óleo, pois é feito no mesmo momento.</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS.</p></div><p><em>Sempre consulte o manual do proprietário e um mecânico de confiança.</em></p>
        """
    },
    "filtro-ar-motor": {
        "titulo": "Filtro de Ar do Motor",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>O filtro de ar do motor impede que impurezas do ambiente (poeira, fuligem, insetos) entrem no motor junto com o ar necessário para a combustão. Um ar limpo é essencial para a queima eficiente do combustível.</p></div><div><strong>2. Por que é importante?</strong><p>Um filtro sujo restringe o fluxo de ar, o que pode aumentar o consumo de combustível, diminuir a potência do motor e, a longo prazo, causar desgaste em componentes internos devido à entrada de partículas abrasivas.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Quilometragem (KM):</strong> Geralmente entre 10.000 km e 15.000 km.</p><p><strong>Observação:</strong> Em locais com muita poeira ou poluição, a troca pode ser necessária mais cedo. Verifique o manual do seu veículo.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p>Em muitos carros, a caixa do filtro de ar é de fácil acesso. Com o motor desligado, pode-se abrir a caixa (geralmente com presilhas ou parafusos simples) e inspecionar visualmente o filtro. Se estiver muito escuro, com muita sujeira visível ou detritos, provavelmente precisa ser trocado.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Perda de potência do motor, aumento no consumo de combustível, motor "engasgando" ou falhando, fumaça escura no escapamento (em alguns casos).</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Peças (Filtro):</strong> R$ 20 - R$ 80.</p><p><strong>Mão de obra:</strong> R$ 20 - R$ 60 (muitas vezes a troca é simples e rápida, ou feita junto com outras revisões).</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS. Consulte oficinas.</p></div><p><em>Consulte o manual do proprietário e um mecânico de confiança.</em></p>
        """
    },
    "filtro-combustivel": {
        "titulo": "Filtro de Combustível",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>O filtro de combustível remove impurezas e partículas presentes no combustível (álcool, gasolina, diesel) antes que ele chegue ao sistema de injeção ou carburador do motor. Protege componentes sensíveis como bicos injetores e bomba de combustível.</p></div><div><strong>2. Por que é importante?</strong><p>Um filtro de combustível sujo ou entupido pode restringir o fluxo de combustível para o motor, causando falhas, perda de potência, dificuldade na partida e, em casos graves, danos à bomba de combustível (que pode superaquecer ao tentar puxar combustível através de um filtro obstruído) ou aos bicos injetores.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Quilometragem (KM):</strong> Geralmente entre 10.000 km e 15.000 km. Alguns manuais podem recomendar intervalos diferentes.</p><p><strong>Observação:</strong> A qualidade do combustível utilizado pode influenciar a vida útil do filtro. Combustíveis de má qualidade podem entupi-lo mais rapidamente.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p>A verificação visual do estado interno do filtro de combustível geralmente não é possível ou recomendada para leigos, pois envolve mexer na linha de combustível, que pode estar pressurizada. A troca preventiva no intervalo recomendado é a melhor abordagem.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Dificuldade na partida do motor, motor falhando ou "engasgando" especialmente em acelerações, perda de potência, aumento do consumo de combustível, marcha lenta irregular.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Peças (Filtro):</strong> R$ 20 - R$ 70.</p><p><strong>Mão de obra:</strong> R$ 40 - R$ 100.</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS. Consulte oficinas.</p></div><p><em>Sempre consulte o manual do proprietário e um mecânico de confiança.</em></p>
        """
    },
    "velas-ignicao": {
        "titulo": "Velas de Ignição",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>As velas de ignição são responsáveis por gerar a faísca elétrica dentro da câmara de combustão do motor, que inflama a mistura ar-combustível. Essa queima controlada é o que gera a força para movimentar o veículo.</p></div><div><strong>2. Por que é importante?</strong><p>Velas desgastadas ou defeituosas podem causar falhas na ignição, resultando em perda de potência, aumento do consumo de combustível, dificuldade na partida, marcha lenta irregular e aumento na emissão de poluentes. Ignorar o problema pode levar a danos em outros componentes, como o catalisador.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Quilometragem (KM):</strong> Varia muito dependendo do tipo de vela (comum, platina, irídio) e do veículo. Pode ser de 15.000 km a 20.000 km para velas comuns, e até 60.000 km a 100.000 km para velas de longa duração.</p><p><strong>Observação:</strong> Consulte o manual do proprietário para o tipo e intervalo específico para seu carro. Os cabos de vela (se aplicável ao seu veículo) também devem ser verificados e trocados se necessário.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p>A remoção e inspeção das velas requer ferramentas específicas (chave de vela) e cuidado para não danificar as roscas no cabeçote do motor ou as próprias velas. Não é uma tarefa recomendada para leigos sem experiência. Um mecânico pode avaliar o estado dos eletrodos e a folga correta.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Dificuldade na partida (motor "pesado" para pegar), falhas do motor (especialmente em marcha lenta ou aceleração), perda de desempenho, aumento do consumo de combustível, luz da injeção eletrônica acesa.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Peças (Jogo de Velas):</strong> R$ 60 - R$ 300 (dependendo do tipo e marca).</p><p><strong>Mão de obra:</strong> R$ 80 - R$ 200.</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS. Se precisar trocar cabos de vela, o custo será adicional.</p></div><p><em>Sempre consulte o manual do proprietário e um mecânico de confiança.</em></p>
        """
    },
    "correia-dentada": {
        "titulo": "Correia Dentada",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>A correia dentada é uma correia de borracha com dentes internos que sincroniza o movimento do virabrequim (que está ligado aos pistões) com o comando de válvulas (que controla a abertura e fechamento das válvulas de admissão e escape). Ela garante que as válvulas abram e fechem no momento exato em relação ao movimento dos pistões.</p><p><em>Alguns veículos utilizam corrente de comando em vez de correia dentada, que geralmente tem maior durabilidade mas também requer verificação.</em></p></div><div><strong>2. Por que é importante?</strong><p>A quebra da correia dentada com o motor em funcionamento é um dos problemas mais graves e caros que podem ocorrer. Se ela arrebentar, o sincronismo é perdido, e os pistões podem colidir com as válvulas, causando empenamento de válvulas, danos aos pistões e até ao cabeçote do motor. O reparo é complexo e custoso.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Quilometragem (KM) ou Tempo:</strong> Varia significativamente entre os fabricantes e modelos, geralmente entre 40.000 km e 100.000 km, ou a cada 3 a 5 anos, o que ocorrer primeiro. É CRUCIAL consultar o manual do proprietário.</p><p><strong>Observação:</strong> Ao trocar a correia dentada, é altamente recomendável trocar também o tensionador (esticador) da correia e, em muitos casos, a bomba d'água, se ela for acionada pela correia dentada, pois a mão de obra para acessá-los é a mesma.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p>A inspeção visual da correia dentada geralmente requer a remoção de capas protetoras e não é simples para leigos. Deve-se procurar por trincas, ressecamento, dentes gastos ou faltando, ou contaminação por óleo. O ideal é seguir rigorosamente o plano de troca preventiva indicado no manual.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Ruídos incomuns vindos da região da correia (chiados, estalos), dificuldade na partida, falhas no motor. No entanto, a correia pode arrebentar sem aviso prévio, por isso a troca preventiva é fundamental.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Peças (Kit Correia Dentada + Tensor):</strong> R$ 150 - R$ 500.</p><p><strong>Mão de obra:</strong> R$ 200 - R$ 600 (pode variar bastante devido à complexidade do acesso).</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS. Se incluir bomba d'água, o custo das peças e possivelmente da mão de obra aumentará.</p></div><p><em>Consulte o manual do proprietário e um mecânico de confiança. A troca preventiva da correia dentada é essencial!</em></p>
        """
    },
    "sistema-arrefecimento": {
        "titulo": "Sistema de Arrefecimento",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>O sistema de arrefecimento (ou refrigeração) é responsável por controlar a temperatura do motor, evitando o superaquecimento. Ele utiliza um líquido (uma mistura de água desmineralizada e aditivo) que circula pelo motor, absorvendo calor e dissipando-o no radiador. Componentes principais incluem radiador, bomba d'água, válvula termostática, mangueiras e reservatório de expansão.</p></div><div><strong>2. Por que é importante?</strong><p>O superaquecimento do motor pode causar danos severos e caros, como queima da junta do cabeçote, empenamento do cabeçote e até a fundição do motor. Manter o sistema de arrefecimento em bom estado é crucial para a saúde e longevidade do motor.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Líquido de Arrefecimento:</strong> A troca completa do líquido geralmente é recomendada a cada 1 a 2 anos, ou conforme a quilometragem especificada no manual (ex: 30.000 km a 60.000 km).</p><p><strong>Componentes:</strong> Mangueiras, válvula termostática e bomba d'água devem ser inspecionados regularmente e trocados se apresentarem sinais de desgaste, vazamento ou mau funcionamento.</p><p><strong>Observação:</strong> Utilize sempre o aditivo recomendado pelo fabricante na proporção correta. Nunca use apenas água pura (especialmente de torneira) por longos períodos.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p>Com o MOTOR FRIO, verifique o nível do líquido de arrefecimento no reservatório de expansão (deve estar entre as marcas "MÍN" e "MÁX"). Observe a coloração do líquido (deve estar límpida e com a cor do aditivo, não turva ou enferrujada). Inspecione visualmente as mangueiras em busca de ressecamento, trincas ou inchaços. Verifique se há sinais de vazamento sob o carro.</p><p><strong>CUIDADO:</strong> Nunca abra a tampa do radiador ou do reservatório com o motor quente, pois o sistema está pressurizado e o líquido quente pode causar queimaduras graves.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Ponteiro da temperatura do motor subindo além do normal, luz de advertência de superaquecimento acesa, vazamentos de líquido colorido (geralmente verde, rosa ou azul) sob o carro, vapor saindo do capô, mangueiras inchadas ou ressecadas, baixo nível frequente do líquido no reservatório.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Troca do Líquido de Arrefecimento (Aditivo + Água Desmineralizada + Limpeza simples):</strong> R$ 100 - R$ 300.</p><p><strong>Troca de Mangueiras (por unidade):</strong> R$ 50 - R$ 150 (peça + mão de obra).</p><p><strong>Troca da Válvula Termostática:</strong> R$ 100 - R$ 300 (peça + mão de obra).</p><p><strong>Troca da Bomba d'Água:</strong> R$ 250 - R$ 700 (peça + mão de obra, pode variar muito).</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS.</p></div><p><em>Sempre consulte o manual do proprietário e um mecânico de confiança.</em></p>
        """
    },
    "pneus": {
        "titulo": "Pneus (Calibragem, Rodízio, Desgaste)",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>Os pneus são o único ponto de contato do veículo com o solo. Suas funções incluem suportar o peso do carro, transmitir as forças de tração e frenagem, absorver irregularidades do piso, e permitir as mudanças de direção. A manutenção envolve calibragem, rodízio, alinhamento e balanceamento, além da verificação do desgaste.</p></div><div><strong>2. Por que é importante?</strong><p>Pneus em bom estado e corretamente calibrados são essenciais para a segurança, estabilidade, conforto e economia do veículo. Pneus desgastados ou mal calibrados aumentam o risco de acidentes (derrapagens, aquaplanagem, estouros), aumentam o consumo de combustível e desgastam irregularmente outros componentes da suspensão.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Calibragem:</strong> Semanalmente ou, no máximo, a cada 15 dias, com os pneus frios, utilizando a pressão indicada no manual do veículo ou na etiqueta na porta/tampa do combustível.</p><p><strong>Rodízio:</strong> Geralmente a cada 5.000 km a 10.000 km, para promover um desgaste mais uniforme entre os pneus. Consulte o manual para o esquema de rodízio correto.</p><p><strong>Alinhamento e Balanceamento:</strong> A cada 10.000 km, sempre que trocar os pneus, após impactos fortes em buracos, ou se notar desgaste irregular ou o volante puxando.</p><p><strong>Troca dos Pneus:</strong> Quando atingirem o indicador TWI (Tread Wear Indicator - pequenas elevações nos sulcos do pneu que indicam o limite legal de desgaste de 1.6mm de profundidade), ou se apresentarem bolhas, cortes profundos, deformações ou ressecamento excessivo.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p><strong>Calibragem:</strong> Use um calibrador em postos de combustível. <strong>Desgaste:</strong> Verifique visualmente os sulcos e procure pelos indicadores TWI. Se a banda de rodagem estiver no mesmo nível do TWI, o pneu precisa ser trocado. Procure por bolhas nas laterais, cortes ou objetos encravados. <strong>Pressão:</strong> Verifique a etiqueta no carro para a pressão correta.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Desgaste irregular da banda de rodagem, vibrações no volante ou na carroceria, veículo puxando para um dos lados, perda de aderência em curvas ou chuva, barulhos incomuns vindos dos pneus, bolhas ou deformações visíveis.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Calibragem:</strong> Geralmente gratuita ou de baixo custo em postos.</p><p><strong>Rodízio:</strong> R$ 40 - R$ 100.</p><p><strong>Alinhamento:</strong> R$ 80 - R$ 200.</p><p><strong>Balanceamento (por roda):</strong> R$ 20 - R$ 50.</p><p><strong>Pneu Novo (unidade, aro 13/14 popular):</strong> R$ 250 - R$ 500+ (varia enormemente com marca, modelo e medida).</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS.</p></div><p><em>Pneus são itens de segurança cruciais. Mantenha-os sempre em bom estado!</em></p>
        """
    },
    "freios": {
        "titulo": "Freios (Pastilhas, Discos, Fluido)",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p>O sistema de freios é responsável por reduzir a velocidade e parar o veículo com segurança. Os componentes mais comuns que exigem manutenção são as pastilhas de freio (que pressionam os discos para criar atrito), os discos de freio (que giram com as rodas), e o fluido de freio (que transmite a força do pedal para as rodas).</p></div><div><strong>2. Por que é importante?</strong><p>A segurança do veículo e de seus ocupantes depende diretamente do bom funcionamento dos freios. Componentes desgastados ou falhas no sistema podem levar à perda da capacidade de frenagem, aumentando drasticamente o risco de acidentes.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Pastilhas de Freio:</strong> Verificação a cada 10.000 km. A troca depende do desgaste, geralmente entre 20.000 km e 40.000 km, mas pode variar muito com o estilo de condução e tipo de uso (cidade vs. estrada).</p><p><strong>Discos de Freio:</strong> Verificação junto com as pastilhas. A troca ocorre quando atingem a espessura mínima de segurança (especificada pelo fabricante) ou se estiverem empenados ou com sulcos profundos. Geralmente duram mais que as pastilhas (ex: 2 trocas de pastilha para 1 de disco).</p><p><strong>Fluido de Freio:</strong> Recomenda-se a troca completa a cada 1 ou 2 anos, ou conforme o manual (ex: 20.000 km), pois o fluido absorve umidade com o tempo, o que reduz seu ponto de ebulição e eficiência.</p></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p><strong>Ruídos:</strong> Preste atenção a chiados agudos, assobios ou ruídos metálicos ao frear (podem indicar pastilhas gastas). <strong>Pedal:</strong> Pedal muito baixo, esponjoso ou que exige muita força pode indicar problemas. <strong>Fluido:</strong> Verifique o nível do fluido de freio no reservatório (geralmente transparente no compartimento do motor). A cor do fluido deve ser clara; se estiver muito escuro, pode precisar de troca. A espessura das pastilhas e discos é melhor avaliada por um mecânico.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p>Chiados ou assobios ao frear, ruído de metal raspando, pedal de freio baixo ou esponjoso, vibrações no pedal ou volante ao frear, necessidade de mais força para parar o carro, luz de advertência do freio acesa no painel, veículo puxando para um lado durante a frenagem.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Troca de Pastilhas de Freio (par dianteiro):</strong> Peças R$ 80 - R$ 250; Mão de obra R$ 80 - R$ 150.</p><p><strong>Troca de Discos de Freio (par dianteiro):</strong> Peças R$ 150 - R$ 400; Mão de obra (geralmente feita junto com pastilhas) R$ 100 - R$ 200.</p><p><strong>Troca do Fluido de Freio:</strong> Produto + Mão de obra R$ 80 - R$ 200.</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS. Freios traseiros (lona/tambor ou disco/pastilha) têm custos diferentes.</p></div><p><em>A manutenção dos freios é vital para sua segurança. Não negligencie!</em></p>
        """
    },
    "alinhamento-balanceamento": {
        "titulo": "Alinhamento e Balanceamento",
        "detalhes_html": """
            <div><strong>1. O que é e qual sua função?</strong><p><strong>Alinhamento da Direção:</strong> Ajusta os ângulos das rodas para que fiquem paralelas entre si e perpendiculares ao solo, conforme as especificações do fabricante. Garante que o veículo rode reto e que os pneus tenham contato ideal com o piso.</p><p><strong>Balanceamento das Rodas:</strong> Corrige desequilíbrios de peso no conjunto pneu/roda. Pequenos contrapesos de chumbo são adicionados à roda para que ela gire de forma uniforme, sem causar vibrações.</p></div><div><strong>2. Por que é importante?</strong><p><strong>Alinhamento:</strong> Evita o desgaste irregular e prematuro dos pneus, melhora a estabilidade e dirigibilidade do veículo, e pode economizar combustível. Um carro desalinhado tende a "puxar" para um lado.</p><p><strong>Balanceamento:</strong> Evita vibrações no volante, no piso do carro ou nos assentos, especialmente em velocidades mais altas. Essas vibrações podem causar desconforto, fadiga ao dirigir e desgaste prematuro de componentes da suspensão e direção.</p></div><div><strong>3. Intervalo Recomendado para Manutenção/Troca (Brasil):</strong><p><strong>Recomendação:</strong> A cada 10.000 km, ou sempre que:</p><ul><li>Fizer o rodízio dos pneus.</li><li>Trocar um ou mais pneus.</li><li>Após passar por buracos ou impactos fortes na suspensão.</li><li>Se notar desgaste irregular nos pneus.</li><li>Se o volante estiver torto com o carro andando em linha reta.</li><li>Se o carro estiver puxando para um dos lados.</li><li>Se sentir vibrações incomuns.</li></ul></div><div><strong>4. Como verificar (para leigos, se aplicável e seguro):</strong><p><strong>Alinhamento:</strong> Em uma via reta e segura, solte o volante por um instante e veja se o carro continua reto ou puxa para algum lado. Observe se o volante está centralizado quando o carro anda reto. Verifique se há desgaste irregular nos ombros dos pneus. <strong>Balanceamento:</strong> Preste atenção a vibrações no volante ou na carroceria, especialmente entre 80 km/h e 120 km/h.</p></div><div><strong>5. Sinais de Problema ou Desgaste:</strong><p><strong>Desalinhamento:</strong> Carro puxando para um lado, volante torto, desgaste irregular dos pneus (mais em um dos ombros). <strong>Falta de Balanceamento:</strong> Vibrações no volante ou carroceria em determinadas velocidades.</p></div><div><strong>6. Estimativa de Custo do Serviço (Brasil - Carro Popular):</strong><p><strong>Alinhamento da Direção (dianteiro ou total):</strong> R$ 80 - R$ 200.</p><p><strong>Balanceamento (por roda):</strong> R$ 20 - R$ 50.</p><p><strong>Aviso:</strong> Valores ESTIMATIVOS. Muitas oficinas oferecem pacotes.</p></div><p><em>Alinhamento e balanceamento regulares prolongam a vida dos pneus e melhoram a segurança e o conforto.</em></p>
        """
    }
}

# Função para interagir com o Gemini
def interagir_gemini(prompt_usuario):
    if not model: 
        return "Erro: Modelo Gemini não está configurado. Verifique a API Key e as mensagens de inicialização do servidor."
    try:
        response = model.generate_content(prompt_usuario)
        text_response = None
        if hasattr(response, 'text') and response.text:
            text_response = response.text
        elif response.parts:
            all_text_parts = [part.text for part in response.parts if hasattr(part, 'text')]
            if all_text_parts:
                text_response = "\n".join(all_text_parts)
        
        if text_response:
            # Substitui **TEXTO** por <strong>TEXTO</strong>
            text_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text_response)
            # Remove asteriscos soltos que podem ter sido usados para listas
            text_response = re.sub(r'(?<!\*)\*(?!\*)', '', text_response) 
            return text_response
        
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            return f"A resposta foi bloqueada pela API. Razão: {response.prompt_feedback.block_reason}"
        
        print(f"Resposta inesperada do Gemini: {response}") 
        return "Não foi possível obter uma resposta em formato de texto do modelo Gemini."
    except Exception as e:
        print(f"Exceção ao chamar a API Gemini: {e}") 
        return f"Ocorreu um erro técnico ao tentar se comunicar com a IA: {e}"

# Adicionar um processador de contexto para ter o ano atual em todos os templates
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
def pagina_menu_principal():
    return render_template('menu.html')

@app.route('/diagnostico', methods=['GET', 'POST'])
def pagina_diagnostico():
    resultado_da_analise = None
    sintoma_enviado = "" 
    if request.method == 'POST':
        sintoma_usuario = request.form.get('user_input', '').strip()
        sintoma_enviado = sintoma_usuario 
        if sintoma_usuario:
            prompt_completo = f"""
            Você é 'Meu amigo Mecânico', um chatbot especialista em diagnóstico automotivo no Brasil,
            com foco em ajudar usuários leigos. Seja amigável, didático e, acima de tudo, CAUTELOSO.

            Um usuário descreveu o seguinte sintoma em seu veículo:
            '{sintoma_usuario}'

            Com base neste sintoma, por favor, forneça as seguintes informações de forma organizada:

            1.  POSSÍVEIS CAUSAS PROVÁVEIS:
                * Liste de 2 a 4 possíveis causas para o sintoma descrito. Comece pela(s) mais comum(ns) ou provável(is).
                * Para cada causa, explique brevemente (1-2 frases) por que ela poderia gerar o sintoma.

            2.  VERIFICAÇÕES SIMPLES E SEGURAS (SE APLICÁVEL):
                * Sugira 1 ou 2 verificações MUITO SIMPLES e SEGURAS que o proprietário poderia fazer ANTES de levar ao mecânico.
                * Se NÃO houver verificação segura para um leigo fazer relacionada a alguma causa, deixe isso CLARO.

            3.  QUANDO PROCURAR UM MECÂNICO:
                * Indique claramente se o sintoma requer atenção IMEDIATA de um mecânico.

            4.  AVISO IMPORTANTE:
                * "Lembre-se: Este é um diagnóstico preliminar e serve apenas como orientação. Apenas um mecânico qualificado, após inspecionar o veículo, poderá fazer um diagnóstico preciso e seguro."

            Formate sua resposta de maneira clara. NÃO use asteriscos para negrito nos títulos das seções; em vez disso, use LETRAS MAIÚSCULAS para os títulos principais.
            Para ênfase dentro do texto, se necessário, pode usar **palavra em negrito com asteriscos duplos**.
            Evite usar markdown para listas com asteriscos simples, use frases corridas ou parágrafos simples para os itens de lista.
            """
            if GOOGLE_API_KEY and model: 
                resultado_da_analise = interagir_gemini(prompt_completo)
            else:
                resultado_da_analise = "A funcionalidade de IA não está disponível. Verifique a configuração da API Key."
        else:
            resultado_da_analise = "Por favor, descreva um sintoma para análise."
    return render_template('index.html', resultado_gemini=resultado_da_analise, sintoma_previo=sintoma_enviado)

@app.route('/revisoes')
def pagina_revisoes():
    return render_template('revisoes_lista.html')

@app.route('/revisao/<item_revisao_slug>')
def detalhe_revisao(item_revisao_slug):
    item_selecionado = conteudo_fixo_revisoes.get(item_revisao_slug)
    if not item_selecionado:
        return render_template('404.html', mensagem_erro="Item de revisão não encontrado."), 404
    return render_template('revisao_detalhe.html', 
                           titulo_item=item_selecionado['titulo'], 
                           detalhes_html=item_selecionado['detalhes_html'])

@app.route('/orcamentos', methods=['GET', 'POST'])
def pagina_orcamentos():
    resultado_da_analise = None
    orcamento_enviado = ""
    if request.method == 'POST':
        orcamento_usuario = request.form.get('orcamento_input', '').strip()
        orcamento_enviado = orcamento_usuario
        if orcamento_usuario:
            prompt_orcamento = f"""
            Você é 'Meu amigo Mecânico', um chatbot especialista em manutenção automotiva no Brasil.
            Sua função é ajudar usuários leigos a entenderem melhor diagnósticos e orçamentos de mecânicos.
            Seja didático, imparcial e foque em fornecer informações claras e úteis.
            NUNCA desqualifique o trabalho de um mecânico, apenas forneça contexto.

            Um usuário recebeu o seguinte diagnóstico/lista de serviços de um mecânico:
            '{orcamento_usuario}'

            Com base nisso, por favor, analise e explique para o usuário, organizando da seguinte forma:

            1.  EXPLICAÇÃO DOS ITENS/SERVIÇOS MENCIONADOS:
            2.  ANÁLISE GERAL DA NECESSIDADE E CRITICIDADE:
            3.  PERGUNTAS ÚTEIS PARA FAZER AO MECÂNICO:
            4.  AVISO IMPORTANTE:

            Formate sua resposta de maneira clara. NÃO use asteriscos para negrito nos títulos das seções; em vez disso, use LETRAS MAIÚSCULAS para os títulos principais.
            Para ênfase dentro do texto, se necessário, pode usar **palavra em negrito com asteriscos duplos**.
            Evite usar markdown para listas com asteriscos simples, use frases corridas ou parágrafos simples para os itens de lista.
            """
            if GOOGLE_API_KEY and model: 
                resultado_da_analise = interagir_gemini(prompt_orcamento)
            else:
                resultado_da_analise = "A funcionalidade de IA não está disponível. Verifique a configuração da API Key."
        else:
            resultado_da_analise = "Por favor, insira o orçamento ou diagnóstico do mecânico para análise."
    return render_template('orcamentos.html', resultado_analise_orcamento=resultado_da_analise, orcamento_previo=orcamento_enviado)

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def erro_interno_servidor(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='127.0.0.1', port=port)
