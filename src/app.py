import streamlit as st
import pandas as pd
import plotly.express as px
import io
import time


@st.cache_data
def load_csv(file):
    df = pd.read_csv(file, decimal=",")
    df.replace("-", pd.NA, inplace=True)
    return df


st.title("Entrada de turistas estrangeiros no Brasil, em percentual")
st.text(
    """
    1. Turismo e suas Curiosidades: Algumas cidades dessa lista são aquelas que todo mundo conhece por serem destinos queridinhos dos turistas do mundo inteiro. Se a gente parar pra olhar como o número de visitantes muda de um ano pro outro, dá pra enxergar umas tendências bem interessantes. Isso é ótimo tanto pra quem trabalha com turismo, quanto pra quem faz planejamento público ou até pra quem só gosta de acompanhar essas coisas.
    2. Cidades pra Todo Gosto: O legal é que o levantamento pega cidades de várias regiões do Brasil, então a gente tem uma visão mais geral, sabe? Dá pra perceber quais lugares têm atraído mais turistas e como esse fluxo vai mudando ao longo do tempo. Isso ajuda a sacar melhor o que está rolando no país em termos de turismo.
    3. O Tempo e o Turismo: Quando a gente olha os dados ano a ano, fica claro como o turismo em cada cidade foi mudando. Essa análise é bem bacana pra entender o impacto de grandes eventos, melhorias na cidade ou qualquer outra coisa que possa ter dado uma mexida no número de turistas.
    """
)

if "preferences" not in st.session_state:
    st.session_state.preferences = {
        "cidade": None,
        "ano": None,
        "mostrar_dados": False,
        "color_fonte": "#FFFFFF",
        "color_painel": "#FFFFFF",
    }

uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None and "df" not in st.session_state:
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.005)
        progress_bar.progress(i + 1)

    st.session_state.df = load_csv(uploaded_file)

if "df" in st.session_state:
    df = st.session_state.df

    cidades = df["Cidades"].tolist()
    anos = df.columns[1:].tolist()

    col1, col2, col3 = st.columns(3)

    with col1:
        cidade = st.radio(
            "Escolha uma cidade:",
            cidades,
            index=cidades.index(st.session_state.preferences["cidade"])
            if st.session_state.preferences["cidade"]
            else 0,
        )

    st.session_state.preferences["cidade"] = cidade
    with col2:
        ano = st.selectbox(
            "Escolha o ano",
            anos,
            index=anos.index(st.session_state.preferences["ano"])
            if st.session_state.preferences["ano"]
            else 0,
        )
    st.session_state.preferences["ano"] = ano

    selected_value = df.loc[df["Cidades"] == cidade, ano].values
    filtered_data = pd.DataFrame(
        {"Cidade": [cidade], "Ano": [ano], "%": selected_value}
    )
    with col3:
        resposta = st.checkbox(
            "Mostrar dados?", value=st.session_state.preferences["mostrar_dados"]
        )
    st.session_state.preferences["mostrar_dados"] = resposta
    if resposta:
        with st.spinner("Carregando o arquivo CSV..."):
            time.sleep(1.5)
            st.write("Dados filtrados:")
            st.dataframe(filtered_data)

    df_cleaned = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")

    st.write("Total de registros:", len(df_cleaned))
    st.write("Média de valores por cidade e ano:", df_cleaned.mean().mean())

    def convert_df_to_csv(df):
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue()

    csv = convert_df_to_csv(filtered_data)

    st.download_button(
        label="Download CSV filtrado",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv",
    )

    col1, col2 = st.columns(2)
    with col1:
        color_fonte = st.color_picker(
            "Escolha a cor da fonte:", st.session_state.preferences["color_fonte"]
        )

        st.session_state.preferences["color_fonte"] = color_fonte

    with col2:
        color_painel = st.color_picker(
            "Escolha a cor do fundo do painel:",
            st.session_state.preferences["color_painel"],
        )

        st.session_state.preferences["color_painel"] = color_painel

    st.markdown(
        f"""
        <style>
            body {{
                background-color: {color_painel};
            }}
            h1, h2, h3, h4, h5, h6, p, li, span {{
                color: {color_fonte} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    def apply_background_color(fig, color):
        fig.update_layout(paper_bgcolor=color, plot_bgcolor=color)
        return fig

    st.header("Gráficos")

    st.subheader("Gráfico de Barras")
    df_barras = df.set_index("Cidades").T
    fig_barras = px.bar(
        df_barras, x=df_barras.index, y=cidade, title=f"Gráfico de barras para {cidade}"
    )

    fig_barras = apply_background_color(fig_barras, color_painel)
    st.plotly_chart(fig_barras)

    st.subheader("Gráfico de Linhas")
    fig_linhas = px.line(
        df_barras, x=df_barras.index, y=cidade, title=f"Gráfico de linhas para {cidade}"
    )

    fig_linhas = apply_background_color(fig_linhas, color_painel)
    st.plotly_chart(fig_linhas)

    st.subheader("Gráfico de Pizza")
    cidade_pie = df.set_index("Cidades").loc[cidade].dropna()
    fig_pizza = px.pie(
        cidade_pie,
        names=cidade_pie.index,
        values=cidade_pie.values,
        title=f"Distribuição dos valores para {cidade}",
    )

    fig_pizza = apply_background_color(fig_pizza, color_painel)
    st.plotly_chart(fig_pizza)

    st.subheader("Histograma")
    df_hist = df.melt(id_vars="Cidades", var_name="Ano", value_name="%")
    df_hist = df_hist.dropna(subset=["%"])
    fig_hist = px.histogram(
        df_hist, x="%", color="Cidades", title="Distribuição dos Valores por Cidades"
    )

    fig_hist = apply_background_color(fig_hist, color_painel)
    st.plotly_chart(fig_hist)

    st.subheader("Gráfico de Dispersão")
    df_scatter = df.dropna()
    df_scatter_melted = df_scatter.melt(
        id_vars="Cidades", var_name="Ano", value_name="%"
    )

    fig_scatter = px.scatter(
        df_scatter_melted,
        x="Ano",
        y="%",
        color="Cidades",
        title="Valores das Cidades por Ano",
    )

    fig_scatter = apply_background_color(fig_scatter, color_painel)
    st.plotly_chart(fig_scatter)
