import streamlit as st
import pandas as pd
import io
import plotly.express as px
import pygwalker as pyg
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("📋データ可視化アプリ「paste2plot」📊（貼り付け／Excelアップロード対応）")

# --- 入力方法の選択 ---
st.subheader("① データの入力")
input_mode = st.radio("データの入力方法を選んでください", ["貼り付け（Excel/BigQuery）", "ファイルアップロード"])

df = None

# --- 貼り付けモード ---
if input_mode == "貼り付け（Excel/BigQuery）":
    pasted_text = st.text_area("Excelからコピー＆ペースト or BigQuery結果を貼り付け", height=300)

    if pasted_text:
        try:
            df = pd.read_csv(io.StringIO(pasted_text.strip()), sep="\t")
            st.success("貼り付けデータを読み込みました")
        except Exception as e:
            st.error(f"読み込みエラー: {e}")

# --- ファイルアップロードモード ---
elif input_mode == "ファイルアップロード":
    uploaded_file = st.file_uploader("CSV または Excel（.xlsx）ファイルをアップロード", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            st.success("ファイルを読み込みました")
        except Exception as e:
            st.error(f"読み込みエラー: {e}")

# --- 可視化処理 ---
if df is not None:
    st.subheader("② データプレビュー")
    st.dataframe(df)

    st.subheader("③ 可視化方法を選択")
    vis_mode = st.radio("可視化方法", ["Pygwalkerでノーコード分析", "Plotlyでカスタムグラフ"])

    if vis_mode == "Pygwalkerでノーコード分析":
        st.markdown("#### Pygwalker による可視化")
        pyg_html = pyg.to_html(df)
        components.html(pyg_html, height=800, scrolling=True)

    elif vis_mode == "Plotlyでカスタムグラフ":
        st.markdown("#### Plotly によるグラフ描画")

        col_x = st.selectbox("X軸", df.columns)
        col_y_options = df.select_dtypes(include='number').columns.tolist()
        if col_y_options:
            col_y = st.selectbox("Y軸（数値）", col_y_options)
            chart_type = st.selectbox("グラフタイプ", ["bar", "line", "scatter", "area", "box", "pie"])

            if chart_type == "bar":
                fig = px.bar(df, x=col_x, y=col_y)
            elif chart_type == "line":
                fig = px.line(df, x=col_x, y=col_y)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=col_x, y=col_y)
            elif chart_type == "area":
                fig = px.area(df, x=col_x, y=col_y)
            elif chart_type == "box":
                fig = px.box(df, x=col_x, y=col_y)  
            elif chart_type == "pie":
                fig = px.pie(df, names=col_x, values=col_y)
            
            st.plotly_chart(fig, use_container_width=True)
            # グラフのダウンロード機能
            graph_download = st.radio("グラフのダウンロード形式", ["PNG", "SVG"])
            if st.button("グラフをダウンロード"):
                if graph_download == "PNG":
                    img_bytes = fig.to_image(format="png")
                    st.download_button(
                        label="PNGとしてダウンロード",
                        data=img_bytes,
                        file_name="plot.png",
                        mime="image/png"
                    )
                elif graph_download == "SVG":
                    img_bytes = fig.to_image(format="svg")
                    st.download_button(
                        label="SVGとしてダウンロード",
                        data=img_bytes,
                        file_name="plot.svg",
                        mime="image/svg+xml"
                    )
        else:
            st.warning("数値列が見つかりません。Y軸に指定できる列がありません。")

else:
    st.info("データを入力・アップロードしてください。")

