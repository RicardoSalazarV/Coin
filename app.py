import pandas as pd
import scipy.stats
import streamlit as st
import time

# Variables de estado que se conservan cuando Streamlit vuelve a ejecutar este script
if 'experiment_no' not in st.session_state:
    st.session_state['experiment_no'] = 0

if 'df_experiment_results' not in st.session_state:
    st.session_state['df_experiment_results'] = pd.DataFrame(columns=['no', 'iterations', 'mean'])

st.header('Lanzar una moneda')

# Gráfico inicial con un valor fijo
chart = st.line_chart([0.5])

# Función para realizar los lanzamientos de moneda
def toss_coin(n):
    trial_outcomes = scipy.stats.bernoulli.rvs(p=0.5, size=n)

    mean = None
    outcome_no = 0
    outcome_1_count = 0

    for r in trial_outcomes:
        outcome_no += 1
        if r == 1:
            outcome_1_count += 1
        mean = outcome_1_count / outcome_no
        chart.add_rows([mean])
        time.sleep(0.05)  # Simulación del proceso de forma visual

    return mean

# Selector de número de intentos
number_of_trials = st.slider('¿Número de intentos?', 1, 1000, 10)

# Botón para iniciar el experimento
start_button = st.button('Ejecutar')

if start_button:  # Asegúrate de que esta línea esté alineada correctamente y que el botón esté declarado antes de este uso
    st.write(f'Experimento con {number_of_trials} intentos en curso.')
    st.session_state['experiment_no'] += 1
    mean = toss_coin(number_of_trials)

    # Agregar resultados al DataFrame de experimentos
    st.session_state['df_experiment_results'] = pd.concat(
        [
            st.session_state['df_experiment_results'],
            pd.DataFrame(
                data=[[st.session_state['experiment_no'], number_of_trials, mean]],
                columns=['no', 'iterations', 'mean']
            )
        ],
        axis=0
    ).reset_index(drop=True)

# Mostrar el DataFrame de resultados
st.write(st.session_state['df_experiment_results'])
