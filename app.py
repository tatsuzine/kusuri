import streamlit as st
import google.generativeai as genai
from PIL import Image

# 使えるモデルを確認するデバッグ用コード
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        st.write(f"利用可能モデル: {m.name}")# --- 設定 ---
st.set_page_config(page_title="歯科専用お薬解析", layout="centered")
st.title("🦷 歯科用お薬手帳チェッカー")
st.caption("※個人情報保護のため、お名前や住所は隠して撮影することを推奨します。")

# APIキー設定（StreamlitのSecretsから取得）
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('models/gemini-2.5-flash')

# --- 強化プロンプトの定義 ---
SYSTEM_PROMPT = """
あなたは歯科医師の補助を行う専門AIです。送られた画像から薬の情報を抽出しますが、以下のルールを厳守してください：

1. 個人情報の完全無視：
   画像内に氏名、生年月日、住所、電話番号、医療機関名、保険者番号などの個人情報が含まれていても、それらを一切読み取らず、出力にも含めないでください。
2. 薬名のみの抽出：
   画像から「薬剤名」を特定してください。
3. 歯科的情報の提供：
   抽出した各薬について、以下の項目を表形式で出力してください。
   - 薬剤名
   - 一般的な効能
   - 歯科治療上の注意点（例：抗凝固薬による出血、ビスホスホネートによる顎骨壊死リスク、麻酔薬との相互作用など）
4. 該当なしの場合：
   薬が見つからない場合は「薬の名前を検出できませんでした」とだけ回答してください。
"""

# --- UI ---
uploaded_file = st.file_uploader("お薬手帳の写真をアップロード", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption='プレビュー（この画像が解析されます）', use_column_width=True)
    
    if st.button('解析を実行する'):
        with st.spinner('薬の名前を照合中... 個人情報は無視されます。'):
            try:
                # AIに画像と強化プロンプトを送信
                response = model.generate_content([SYSTEM_PROMPT, img])
                
                st.subheader("📋 歯科的注意点リスト")
                st.markdown(response.text)
                
                st.info("💡 最終的な臨床判断は必ず歯科医師が行ってください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")


