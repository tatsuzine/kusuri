import streamlit as st
import openai
import base64

# --- 初期設定 ---
st.set_page_config(page_title="歯科用お薬チェッカー")
st.title("🦷 歯科用お薬手帳解析")
st.write("お薬手帳の写真をアップロードしてください。")

# APIキーの設定（Streamlit CloudのSecretsから取得）
openai.api_key = st.secrets["OPENAI_API_KEY"]

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- UI部分 ---
uploaded_file = st.file_uploader("写真を撮るか選択してください", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    st.image(uploaded_file, caption='アップロード画像', use_column_width=True)
    
    if st.button('薬を解析する'):
        with st.spinner('解析中...'):
            base64_image = encode_image(uploaded_file)
            
            # GPT-4oに画像を送り、解析を依頼
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "この画像から薬の名前をすべて抽出し、それぞれについて「一般的な効能」と「歯科治療（抜歯、麻酔、出血、顎骨壊死など）における注意点」を日本語の表形式で出力してください。"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ],
                    }
                ],
                max_tokens=1000,
            )
            
            # 結果表示
            st.subheader("💊 解析結果")
            st.write(response.choices[0].message.content)
            st.warning("※この結果はAIによる生成です。必ず専門家が最終確認を行ってください。")