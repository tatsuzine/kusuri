import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 設定 ---
# ここに取得した自分のAPIキーを入れてください
ST_API_KEY = "あなたのAPIキーをここに貼り付け"
genai.configure(api_key=ST_API_KEY)

# アプリのタイトル
st.title("💊 お薬手帳・AI解析アシスタント")
st.write("お薬手帳や処方箋の写真をアップロードすると、AIが薬の内容を解説します。")

# 画像のアップロード
uploaded_file = st.file_uploader("お薬手帳の写真をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 画像を表示
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_container_width=True)
    
    # 解析ボタン
    if st.button("AIで薬を解析する"):
        with st.spinner("AIが画像を確認中..."):
            try:
                # Gemini 1.5 Flashモデルを使用（画像認識に強く、高速）
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # プロンプト（AIへの指示）
                prompt = """
                この画像は「お薬手帳」または「処方箋」の写真です。
                画像から薬の名前をすべて抽出し、以下の項目を表形式で出力してください。
                1. 薬の名前
                2. 一般的な効能（何に効くか）
                3. 主な副作用
                4. 飲む際の注意点
                
                ※最後に必ず「この情報はAIによる推測です。必ず医師や薬剤師の指示に従ってください」という注意書きを添えてください。
                """
                
                # AIに画像とプロンプトを渡して実行
                response = model.generate_content([prompt, image])
                
                # 結果の表示
                st.subheader("📝 解析結果")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# 免責事項
st.sidebar.warning("【注意】このアプリは学習・検証用です。診断や処方の判断には使用しないでください。")