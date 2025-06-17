import streamlit as st
import pandas as pd
import collections

# --- Constantes e Funções Auxiliares ---
NUM_RECENT_RESULTS_FOR_ANALYSIS = 27
MAX_HISTORY_TO_STORE = 1000
NUM_HISTORY_TO_DISPLAY = 100

def get_color(result):
    """Retorna a cor associada ao resultado, conforme as novas definições."""
    if result == 'home':
        return 'red'
    elif result == 'away':
        return 'blue' # Alterado de 'black' para 'blue'
    else: # 'draw'
        return 'yellow' # Alterado de 'green' para 'yellow'

def get_color_emoji(color):
    """Retorna o emoji correspondente à cor."""
    if color == 'red':
        return '🔴'
    elif color == 'blue':
        return '🔵'
    elif color == 'yellow':
        return '🟡'
    return ''

# --- Funções de Análise ---

def analyze_surf(results):
    """Analisa os padrões de "surf" (sequências de Home/Away/Draw) nos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'home_sequence': 0, 'away_sequence': 0, 'draw_sequence': 0,
                'max_home_sequence': 0, 'max_away_sequence': 0, 'max_draw_sequence': 0}
    
    current_home_sequence = 0
    current_away_sequence = 0
    current_draw_sequence = 0
    
    max_home_sequence = 0
    max_away_sequence = 0
    max_draw_sequence = 0

    temp_home_seq = 0
    temp_away_seq = 0
    temp_draw_seq = 0

    for i in range(len(relevant_results)):
        result = relevant_results[i]
        
        if result == 'home':
            temp_home_seq += 1
            temp_away_seq = 0
            temp_draw_seq = 0
        elif result == 'away':
            temp_away_seq += 1
            temp_home_seq = 0
            temp_draw_seq = 0
        else: # draw
            temp_draw_seq += 1
            temp_home_seq = 0
            temp_away_seq = 0
        
        max_home_sequence = max(max_home_sequence, temp_home_seq)
        max_away_sequence = max(max_away_sequence, temp_away_seq)
        max_draw_sequence = max(max_draw_sequence, temp_draw_seq)

    actual_current_home_sequence = 0
    actual_current_away_sequence = 0
    actual_current_draw_sequence = 0

    first_result = relevant_results[0]
    for r in relevant_results:
        if r == first_result:
            if first_result == 'home': actual_current_home_sequence += 1
            elif first_result == 'away': actual_current_away_sequence += 1
            else: actual_current_draw_sequence += 1
        else:
            break

    return {
        'home_sequence': actual_current_home_sequence,
        'away_sequence': actual_current_away_sequence,
        'draw_sequence': actual_current_draw_sequence,
        'max_home_sequence': max_home_sequence,
        'max_away_sequence': max_away_sequence,
        'max_draw_sequence': max_draw_sequence
    }

def analyze_colors(results):
    """Analisa a contagem e as sequências de cores nos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'red': 0, 'blue': 0, 'yellow': 0, 'current_color': '', 'streak': 0, 'color_pattern_27': ''}

    color_counts = {'red': 0, 'blue': 0, 'yellow': 0}

    for result in relevant_results:
        color = get_color(result)
        color_counts[color] += 1

    current_color = get_color(results[0])
    streak = 0
    for result in results: 
        if get_color(result) == current_color:
            streak += 1
        else:
            break
            
    color_pattern_27 = ''.join([get_color(r)[0].upper() for r in relevant_results])

    return {
        'red': color_counts['red'],
        'blue': color_counts['blue'],
        'yellow': color_counts['yellow'],
        'current_color': current_color,
        'streak': streak,
        'color_pattern_27': color_pattern_27
    }

def find_break_patterns(results):
    """Identifica padrões de quebra e padrões específicos (2x2, 3x3, 3x1, 2x1) nos últimos N resultados."""
    patterns = collections.defaultdict(int)
    
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i])
        color2 = get_color(relevant_results[i+1])

        # Padrões de quebra simples (sem especificar qual cor quebrou qual)
        if color1 != color2:
            patterns["Quebra Simples"] += 1

        # Padrões 2x1 (Ex: R R B)
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color1 == color2 and color1 != color3:
                patterns[f"2x1 ({color1.capitalize()} {get_color_emoji(color1)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1
        
        # Padrões 3x1 (Ex: R R R B)
        if i < len(relevant_results) - 3:
            color3 = get_color(relevant_results[i+2])
            color4 = get_color(relevant_results[i+3])
            if color1 == color2 and color2 == color3 and color1 != color4:
                patterns[f"3x1 ({color1.capitalize()} {get_color_emoji(color1)} {color4.capitalize()}{get_color_emoji(color4)})"] += 1
        
        # Padrões 2x2 (Ex: R R B B ou R B R B)
        if i < len(relevant_results) - 3:
            color3 = get_color(relevant_results[i+2])
            color4 = get_color(relevant_results[i+3])
            if color1 == color2 and color3 == color4 and color1 != color3: # R R B B
                patterns[f"2x2 ({color1.capitalize()} {get_color_emoji(color1)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1
            if color1 != color2 and color2 != color3 and color3 != color4 and color1 == color3 and color2 == color4: # R B R B
                patterns[f"Padrão Alternado ({color1.capitalize()}{get_color_emoji(color1)}-{color2.capitalize()}{get_color_emoji(color2)}-...)"] += 1

        # Padrões 3x3 (Ex: R R R B B B)
        if i < len(relevant_results) - 5:
            color3 = get_color(relevant_results[i+2])
            color4 = get_color(relevant_results[i+3])
            color5 = get_color(relevant_results[i+4])
            color6 = get_color(relevant_results[i+5])
            if color1 == color2 and color2 == color3 and color4 == color5 and color5 == color6 and color1 != color4:
                patterns[f"3x3 ({color1.capitalize()} {get_color_emoji(color1)} {color4.capitalize()}{get_color_emoji(color4)})"] += 1

    # Análise específica de padrões para Empate
    for i in range(len(relevant_results) - 1):
        color1 = get_color(relevant_results[i])
        color2 = get_color(relevant_results[i+1])

        # Padrão: X Y Draw (cores diferentes seguidas de empate)
        if color2 == 'yellow' and color1 != 'yellow':
            patterns[f"X Y Draw ({color1.capitalize()}{get_color_emoji(color1)} {color2.capitalize()}{get_color_emoji(color2)})"] += 1
        
        # Padrão: Draw X Y (empate seguido de duas cores diferentes)
        if i < len(relevant_results) - 2:
            color3 = get_color(relevant_results[i+2])
            if color1 == 'yellow' and color2 != 'yellow' and color3 != 'yellow' and color2 != color3:
                patterns[f"Draw X Y ({color1.capitalize()}{get_color_emoji(color1)} {color2.capitalize()}{get_color_emoji(color2)} {color3.capitalize()}{get_color_emoji(color3)})"] += 1

    return dict(patterns)

def analyze_break_probability(results):
    """Analisa a probabilidade de quebra com base no histórico dos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results or len(relevant_results) < 2:
        return {'break_chance': 0, 'last_break_type': ''}
    
    breaks = 0
    total_sequences_considered = 0
    
    for i in range(len(relevant_results) - 1):
        if get_color(relevant_results[i]) != get_color(relevant_results[i+1]):
            breaks += 1
        total_sequences_considered += 1
            
    break_chance = (breaks / total_sequences_considered) * 100 if total_sequences_considered > 0 else 0

    last_break_type = ""
    if len(results) >= 2 and get_color(results[0]) != get_color(results[1]):
        last_break_type = f"Quebrou de {get_color(results[1]).capitalize()} {get_color_emoji(get_color(results[1]))} para {get_color(results[0]).capitalize()} {get_color_emoji(get_color(results[0]))}"
    
    return {
        'break_chance': round(break_chance, 2),
        'last_break_type': last_break_type
    }

def analyze_draw_specifics(results):
    """Análise específica para empates nos últimos N resultados."""
    relevant_results = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]
    if not relevant_results:
        return {'draw_frequency_27': 0, 'time_since_last_draw': -1, 'draw_patterns': {}}

    draw_count_27 = relevant_results.count('draw')
    draw_frequency_27 = (draw_count_27 / len(relevant_results)) * 100 if len(relevant_results) > 0 else 0

    time_since_last_draw = -1
    for i, result in enumerate(results): # Tempo desde o último empate no histórico COMPLETO
        if result == 'draw':
            time_since_last_draw = i
            break
    
    draw_patterns_found = collections.defaultdict(int)
    for i in range(len(relevant_results) - 1):
        if get_color(relevant_results[i]) != get_color(relevant_results[i+1]) and get_color(relevant_results[i+1]) == 'yellow':
            draw_patterns_found[f"Quebra para Empate ({get_color(relevant_results[i]).capitalize()}{get_color_emoji(get_color(relevant_results[i]))} para Empate{get_color_emoji('yellow')})"] += 1
        
        if i < len(relevant_results) - 2:
            color1 = get_color(relevant_results[i])
            color2 = get_color(relevant_results[i+1])
            color3 = get_color(relevant_results[i+2])
            if color3 == 'yellow':
                if color1 == 'red' and color2 == 'blue':
                    draw_patterns_found["Red-Blue-Draw (🔴🔵🟡)"] += 1
                elif color1 == 'blue' and color2 == 'red':
                    draw_patterns_found["Blue-Red-Draw (🔵🔴🟡)"] += 1
    
    return {
        'draw_frequency_27': round(draw_frequency_27, 2),
        'time_since_last_draw': time_since_last_draw,
        'draw_patterns': dict(draw_patterns_found)
    }


def generate_advanced_suggestion(results, surf_analysis, color_analysis, break_probability, break_patterns, draw_specifics):
    """Gera uma sugestão de aposta baseada em múltiplas análises nos últimos N resultados, com foco em segurança."""
    if not results or len(results) < 5: 
        return {'suggestion': 'Aguardando mais resultados para análise detalhada.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A'}

    last_result_color = color_analysis['current_color']
    current_streak = color_analysis['streak']
    
    suggestion = "Manter observação"
    confidence = 50
    reason = "Análise preliminar."
    guarantee_pattern = "N/A" # Armazena qual padrão "garantiu" a aposta

    # Prioridade de análise para apostas "seguras"

    # 1. Sugestão baseada em Sequência Longa e Máximo Histórico de Surf (maior confiança)
    if last_result_color == 'red' and current_streak >= surf_analysis['max_home_sequence'] and surf_analysis['max_home_sequence'] > 0 and current_streak >= 3:
        suggestion = f"APOSTA FORTE em **VISITANTE** {get_color_emoji('blue')}"
        confidence = 95
        reason = f"Sequência atual de Vermelho ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de quebra."
        guarantee_pattern = f"Surf Max Quebra: {last_result_color.capitalize()}"
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    elif last_result_color == 'blue' and current_streak >= surf_analysis['max_away_sequence'] and surf_analysis['max_away_sequence'] > 0 and current_streak >= 3:
        suggestion = f"APOSTA FORTE em **CASA** {get_color_emoji('red')}"
        confidence = 95
        reason = f"Sequência atual de Azul ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de quebra."
        guarantee_pattern = f"Surf Max Quebra: {last_result_color.capitalize()}"
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    elif last_result_color == 'yellow' and current_streak >= surf_analysis['max_draw_sequence'] and surf_analysis['max_draw_sequence'] > 0 and current_streak >= 2:
        suggestion = f"APOSTA FORTE em **CASA** {get_color_emoji('red')} ou **VISITANTE** {get_color_emoji('blue')}"
        confidence = 90
        reason = f"Sequência atual de Empate ({current_streak}x) atingiu ou superou o máximo histórico de surf. Grande chance de retorno às cores principais."
        guarantee_pattern = f"Surf Max Quebra: {last_result_color.capitalize()}"
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 2. Sugestão baseada em padrões recorrentes de quebra (2x1, 3x1) com alta confiança
    # Foco em padrões que se repetem e indicam uma quebra clara.
    for pattern, count in break_patterns.items():
        if count >= 3: # Se o padrão se repetiu 3 ou mais vezes nos últimos 27
            if "2x1 (Red 🔴 Blue 🔵)" in pattern and last_result_color == 'red' and current_streak == 2:
                suggestion = f"Apostar em **VISITANTE** {get_color_emoji('blue')}"
                confidence = max(confidence, 88)
                reason = f"Padrão 2x1 (🔴🔴🔵) altamente recorrente ({count}x). Espera-se a quebra para azul."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            elif "2x1 (Blue 🔵 Red 🔴)" in pattern and last_result_color == 'blue' and current_streak == 2:
                suggestion = f"Apostar em **CASA** {get_color_emoji('red')}"
                confidence = max(confidence, 88)
                reason = f"Padrão 2x1 (🔵🔵🔴) altamente recorrente ({count}x). Espera-se a quebra para vermelho."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            # Adicione mais regras para 3x1, 2x2, 3x3 se forem previsíveis com base em contagem
            elif "3x1 (Red 🔴 Blue 🔵)" in pattern and last_result_color == 'red' and current_streak == 3:
                suggestion = f"Apostar em **VISITANTE** {get_color_emoji('blue')}"
                confidence = max(confidence, 92)
                reason = f"Padrão 3x1 (🔴🔴🔴🔵) altamente recorrente ({count}x). Espera-se a quebra para azul."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
            elif "3x1 (Blue 🔵 Red 🔴)" in pattern and last_result_color == 'blue' and current_streak == 3:
                suggestion = f"Apostar em **CASA** {get_color_emoji('red')}"
                confidence = max(confidence, 92)
                reason = f"Padrão 3x1 (🔵🔵🔵🔴) altamente recorrente ({count}x). Espera-se a quebra para vermelho."
                guarantee_pattern = pattern
                return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 3. Sugestão de Empate (maior assertividade)
    # Se o tempo desde o último empate for alto E a frequência de empates for baixa OU houver padrão de empate claro
    if draw_specifics['time_since_last_draw'] >= 7 and draw_specifics['draw_frequency_27'] < 12: # Ajustar limite da freq.
        suggestion = f"Considerar **EMPATE** {get_color_emoji('yellow')}"
        confidence = max(confidence, 78)
        reason = f"Empate não ocorre há {draw_specifics['time_since_last_draw']} rodadas e frequência baixa ({draw_specifics['draw_frequency_27']}% nos últimos 27)."
        guarantee_pattern = "Empate Atrasado/Baixa Frequência"
        
        # Reforço com padrões de empate
        if "Red-Blue-Draw (🔴🔵🟡)" in draw_specifics['draw_patterns'] and len(results) >= 2 and results[0] == 'away' and results[1] == 'home':
            suggestion += f" - Reforçado por padrão 🔴🔵🟡."
            confidence = max(confidence, 88)
            guarantee_pattern += " + Padrão 🔴🔵🟡"
        elif "Blue-Red-Draw (🔵🔴🟡)" in draw_specifics['draw_patterns'] and len(results) >= 2 and results[0] == 'home' and results[1] == 'away':
            suggestion += f" - Reforçado por padrão 🔵🔴🟡."
            confidence = max(confidence, 88)
            guarantee_pattern += " + Padrão 🔵🔴🟡"
        
        return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}
    
    # Se os últimos 2 foram alternados (R-B ou B-R) e não houve empate em X rodadas
    if len(results) >= 2 and ( (get_color(results[0]) == 'red' and get_color(results[1]) == 'blue') or \
                               (get_color(results[0]) == 'blue' and get_color(results[1]) == 'red') ):
        if draw_specifics['time_since_last_draw'] >= 3: # Ajustar quantas rodadas sem empate para ser um gatilho
            suggestion = f"Considerar **EMPATE** {get_color_emoji('yellow')}"
            confidence = max(confidence, 75)
            reason = "Resultados alternados (🔴🔵 ou 🔵🔴) podem preceder um empate. Empate atrasado."
            guarantee_pattern = "Alternância para Empate"
            return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 4. Outras Sugestões (se as acima não se aplicarem com alta confiança)
    # Se a probabilidade de quebra for alta e a streak não for muito longa
    if break_probability['break_chance'] > 65 and current_streak < 3: 
        if len(results) >= 2:
            prev_color = get_color(results[1])
            if prev_color == 'red':
                suggestion = f"Apostar em **VISITANTE** {get_color_emoji('blue')}"
                confidence = max(confidence, 70)
                reason = f"Alta chance de quebra ({break_probability['break_chance']}%). Prever quebra de sequência de {prev_color.capitalize()}."
                guarantee_pattern = "Alta Probabilidade de Quebra Geral"
            elif prev_color == 'blue':
                suggestion = f"Apostar em **CASA** {get_color_emoji('red')}"
                confidence = max(confidence, 70)
                reason = f"Alta chance de quebra ({break_probability['break_chance']}%). Prever quebra de sequência de {prev_color.capitalize()}."
                guarantee_pattern = "Alta Probabilidade de Quebra Geral"
            
            return {'suggestion': suggestion, 'confidence': confidence, 'reason': reason, 'guarantee_pattern': guarantee_pattern}


    # 5. Default/Manter Observação (se nenhum padrão forte de "garantia" for encontrado)
    suggestion = "Manter observação."
    confidence = 50
    reason = "Nenhum padrão de 'garantia' forte detectado nos últimos 27 resultados para uma aposta segura no momento."
    guarantee_pattern = "Nenhum Padrão Forte"

    return {
        'suggestion': suggestion, 
        'confidence': round(confidence), 
        'reason': reason,
        'guarantee_pattern': guarantee_pattern
    }

def update_analysis(results):
    """Coordena todas as análises e retorna os resultados consolidados, focando nos últimos N."""
    
    relevant_results_for_analysis = results[:NUM_RECENT_RESULTS_FOR_ANALYSIS]

    if not relevant_results_for_analysis:
        return {
            'stats': {'home': 0, 'away': 0, 'draw': 0, 'total': 0},
            'surf_analysis': analyze_surf([]),
            'color_analysis': analyze_colors([]),
            'break_patterns': find_break_patterns([]),
            'break_probability': analyze_break_probability([]),
            'draw_specifics': analyze_draw_specifics([]),
            'suggestion': {'suggestion': 'Aguardando resultados para análise.', 'confidence': 0, 'reason': '', 'guarantee_pattern': 'N/A'}
        }

    stats = {'home': relevant_results_for_analysis.count('home'), 
             'away': relevant_results_for_analysis.count('away'), 
             'draw': relevant_results_for_analysis.count('draw'), 
             'total': len(relevant_results_for_analysis)}
    
    surf_analysis = analyze_surf(results) # Passa todos os resultados para surf, pois max seq pode ser de antes
    color_analysis = analyze_colors(results)
    break_patterns = find_break_patterns(results)
    break_probability = analyze_break_probability(results)
    draw_specifics = analyze_draw_specifics(results) 

    suggestion_data = generate_advanced_suggestion(results, surf_analysis, color_analysis, break_probability, break_patterns, draw_specifics)
    
    return {
        'stats': stats,
        'surf_analysis': surf_analysis,
        'color_analysis': color_analysis,
        'break_patterns': break_patterns,
        'break_probability': break_probability,
        'draw_specifics': draw_specifics, 
        'suggestion': suggestion_data
    }

# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="Football Studio Pro Analyzer")

st.title("⚽ Football Studio Pro Analyzer")
st.write("Sistema Avançado de Análise e Predição")

# --- Gerenciamento de Estado ---
# 'results': Histórico completo de resultados (mais recente primeiro)
# 'analysis_data': Última análise completa
# 'last_suggested_bet': Armazena a última sugestão feita
# 'last_guarantee_pattern': O padrão que 'garantiu' a última aposta
# 'guarantee_failed': Flag para indicar se a garantia falhou na última rodada
if 'results' not in st.session_state:
    st.session_state.results = []
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = update_analysis([])
if 'last_suggested_bet' not in st.session_state:
    st.session_state.last_suggested_bet = None
if 'last_guarantee_pattern' not in st.session_state:
    st.session_state.last_guarantee_pattern = "N/A"
if 'guarantee_failed' not in st.session_state:
    st.session_state.guarantee_failed = False

# --- Função para Adicionar Resultado ---
def add_result(result):
    # Antes de adicionar o novo resultado, verificar se a garantia da aposta anterior falhou
    if st.session_state.last_suggested_bet and not st.session_state.guarantee_failed:
        suggested_color = get_color(st.session_state.last_suggested_bet) # Supondo que 'last_suggested_bet' guarda o resultado esperado
        actual_color = get_color(result)
        
        # Lógica para verificar se a garantia "bateu"
        # Isso precisa ser mais sofisticado dependendo do "guarantee_pattern"
        guarantee_met = True # Assume que bateu, a menos que a lógica abaixo prove o contrário
        
        # Exemplo simples: se a sugestão era CASA e deu VISITANTE, a garantia falhou
        # Você precisará refinar isso para cada tipo de 'guarantee_pattern'
        if suggested_color != actual_color and st.session_state.analysis_data['suggestion']['confidence'] > 70: # Apenas se a confiança era alta
            st.session_state.guarantee_failed = True
            st.warning(f"🚨 **ALERTA: A GARANTIA DO PADRÃO '{st.session_state.last_guarantee_pattern}' FALHOU!** Reavalie a estratégia ou aguarde novos padrões seguros.")
        else:
            st.session_state.guarantee_failed = False # Resetar se a aposta bateu ou não era de alta confiança

    st.session_state.results.insert(0, result) 
    st.session_state.results = st.session_state.results[:MAX_HISTORY_TO_STORE] 
    st.session_state.analysis_data = update_analysis(st.session_state.results)
    
    # Atualiza a última sugestão e seu padrão de garantia APÓS a análise
    current_suggestion = st.session_state.analysis_data['suggestion']
    # Extrair a aposta principal da sugestão (ex: 'CASA', 'VISITANTE', 'EMPATE')
    if "CASA" in current_suggestion['suggestion']:
        st.session_state.last_suggested_bet = 'home'
    elif "VISITANTE" in current_suggestion['suggestion']:
        st.session_state.last_suggested_bet = 'away'
    elif "EMPATE" in current_suggestion['suggestion']:
        st.session_state.last_suggested_bet = 'draw'
    else:
        st.session_state.last_suggested_bet = None # Se não há sugestão clara
        
    st.session_state.last_guarantee_pattern = current_suggestion['guarantee_pattern']
    
# --- Função para Limpar Histórico ---
def clear_history():
    st.session_state.results = []
    st.session_state.analysis_data = update_analysis([])
    st.session_state.last_suggested_bet = None
    st.session_state.last_guarantee_pattern = "N/A"
    st.session_state.guarantee_failed = False
    st.experimental_rerun() 

# --- Layout ---
st.header("Registrar Resultado")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("CASA 🔴", use_container_width=True):
        add_result('home')
with col2:
    if st.button("VISITANTE 🔵", use_container_width=True):
        add_result('away')
with col3:
    if st.button("EMPATE 🟡", use_container_width=True):
        add_result('draw')

st.markdown("---")

# --- Exibir Alerta de Garantia ---
if st.session_state.guarantee_failed:
    st.error(f"🚨 **GARANTIA FALHOU NO PADRÃO: '{st.session_state.last_guarantee_pattern}'**. Reanalisar e buscar novos padrões de segurança.")
    st.write("É recomendado observar as próximas rodadas sem apostar ou redefinir o histórico.")

st.header("Análise IA e Sugestão")
if st.session_state.results:
    suggestion = st.session_state.analysis_data['suggestion']
    
    st.info(f"**Sugestão:** {suggestion['suggestion']}")
    st.metric(label="Confiança", value=f"{suggestion['confidence']}%")
    st.write(f"**Motivo:** {suggestion['reason']}")
    st.write(f"**Padrão de Garantia da Sugestão:** `{suggestion['guarantee_pattern']}`")
else:
    st.info("Aguardando resultados para gerar análises e sugestões.")

st.markdown("---")

# --- Estatísticas e Padrões (Últimos 27 Resultados) ---
st.header(f"Estatísticas e Padrões (Últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS} Resultados)")

stats_col, color_col = st.columns(2)

with stats_col:
    st.subheader("Estatísticas Gerais")
    stats = st.session_state.analysis_data['stats']
    st.write(f"**Casa {get_color_emoji('red')}:** {stats['home']} vezes")
    st.write(f"**Visitante {get_color_emoji('blue')}:** {stats['away']} vezes")
    st.write(f"**Empate {get_color_emoji('yellow')}:** {stats['draw']} vezes")
    st.write(f"**Total de Resultados Analisados:** {stats['total']}")

with color_col:
    st.subheader("Análise de Cores")
    colors = st.session_state.analysis_data['color_analysis']
    st.write(f"**Vermelho:** {colors['red']}x")
    st.write(f"**Azul:** {colors['blue']}x")
    st.write(f"**Amarelo:** {colors['yellow']}x")
    st.write(f"**Sequência Atual:** {colors['streak']}x {colors['current_color'].capitalize()} {get_color_emoji(colors['current_color'])}")
    st.markdown(f"**Padrão (Últimos {NUM_RECENT_RESULTS_FOR_ANALYSIS}):** `{colors['color_pattern_27']}`")

st.markdown("---")

# --- Análise de Quebra, Surf e Empate ---
col_break, col_surf, col_draw_analysis = st.columns(3)

with col_break:
    st.subheader("Análise de Quebra")
    bp = st.session_state.analysis_data['break_probability']
    st.write(f"**Chance de Quebra:** {bp['break_chance']}%")
    st.write(f"**Último Tipo de Quebra:** {bp['last_break_type'] if bp['last_break_type'] else 'N/A'}")
    
    st.subheader("Padrões de Quebra e Específicos")
    patterns = st.session_state.analysis_data['break_patterns']
    if patterns:
        for pattern, count in patterns.items():
            st.write(f"- {pattern}: {count}x")
    else:
        st.write("Nenhum padrão identificado nos últimos 27 resultados.")

with col_surf:
    st.subheader("Análise de Surf")
    surf = st.session_state.analysis_data['surf_analysis']
    st.write(f"**Seq. Atual Casa {get_color_emoji('red')}:** {surf['home_sequence']}x")
    st.write(f"**Seq. Atual Visitante {get_color_emoji('blue')}:** {surf['away_sequence']}x")
    st.write(f"**Seq. Atual Empate {get_color_emoji('yellow')}:** {surf['draw_sequence']}x")
    st.write(f"---")
    st.write(f"**Máx. Seq. Casa:** {surf['max_home_sequence']}x")
    st.write(f"**Máx. Seq. Visitante:** {surf['max_away_sequence']}x")
    st.write(f"**Máx. Seq. Empate:** {surf['max_draw_sequence']}x")

with col_draw_analysis:
    st.subheader("Análise Detalhada de Empates")
    draw_data = st.session_state.analysis_data['draw_specifics']
    st.write(f"**Frequência Empate ({NUM_RECENT_RESULTS_FOR_ANALYSIS}):** {draw_data['draw_frequency_27']}%")
    st.write(f"**Rodadas sem Empate:** {draw_data['time_since_last_draw']} (Desde o último empate)")
    
    st.subheader("Padrões de Empate Históricos")
    if draw_data['draw_patterns']:
        for pattern, count in draw_data['draw_patterns'].items():
            st.write(f"- {pattern}: {count}x")
    else:
        st.write("Nenhum padrão de empate identificado ainda.")

st.markdown("---")

# --- Histórico dos Últimos 100 Resultados ---
st.header(f"Histórico dos Últimos {NUM_HISTORY_TO_DISPLAY} Resultados")
if st.session_state.results:
    history_to_display = st.session_state.results[:NUM_HISTORY_TO_DISPLAY]
    history_df = pd.DataFrame(history_to_display, columns=["Resultado"])
    history_df['Cor'] = history_df['Resultado'].apply(get_color)
    history_df['Emoji'] = history_df['Cor'].apply(get_color_emoji)
    
    st.dataframe(history_df[['Resultado', 'Cor', 'Emoji']], use_container_width=True)
    if st.button("Limpar Histórico Completo", type="secondary"):
        clear_history()
else:
    st.write("Nenhum resultado registrado ainda. Adicione resultados para começar a análise!")
