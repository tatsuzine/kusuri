import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 画面の設定（スマホで見やすく）
st.set_page_config(page_title="歯科専用お薬解析", layout="centered")

# スマホ用のCSS（文字を少し大きく）
st.markdown("""
    <style>
    .stMarkdown { font-size: 1.1rem; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 歯科用お薬手帳チェッカー")
st.caption("※個人情報保護のため、お名前や住所は隠して撮影することを推奨します。")

# APIキー設定
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# モデル名は安定版の 1.5-flash を推奨
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# --- 強化プロンプトの定義（カード形式） ---
SYSTEM_PROMPT = """
あなたは歯科医師の補助を行う専門AIです。送られた画像から薬の情報を抽出しますが、以下のルールを厳守してください：

1. 個人情報の完全無視：
   画像内に氏名、住所、医療機関名などの個人情報が含まれていても、一切抽出・出力しないでください。
2. 形式：表形式は禁止します。
   以下の形式で1剤ずつ縦に並べて出力してください。

---
### 💊 【薬の名前】
- **一般的な効能**: 
- **歯科治療の注意点**: 
- **併用禁忌・注意薬**: 
---

3. その他：
   挨拶や前置きは不要です。解析結果のみを出力してください。
   不明な点は「不明」と記載してください。
"""

# --- UI ---
uploaded_file = st.file_uploader("お薬手帳の写真をアップロード", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # 画像の加工（白黒化・リサイズ）
    img = Image.open(uploaded_file)
    img_gray = img.convert('L') 
    img_gray.thumbnail((1024, 1024))
    
    st.image(img_gray, caption='解析用画像（加工済）', use_column_width=True)
    
    if st.button('解析を実行する'):
        # 結果を表示するエリアを確保
        st.subheader("📋 歯科 professionals 用確認リスト")
        placeholder = st.empty()
        full_response = ""
        
        try:
            # AIに送信（ストリーミング形式）
            response = model.generate_content([SYSTEM_PROMPT, img_gray], stream=True)
            
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response) # 最後に確定表示
            st.info("💡 最終的な臨床判断は必ず歯科医師が行ってください。")
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
