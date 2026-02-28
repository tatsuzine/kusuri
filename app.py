import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 画面の設定（スマホで見やすく）
st.set_page_config(page_title="歯科専用お薬解析", layout="centered")

# スマホ用のCSS（文字サイズと余白の調整）
st.markdown("""
    <style>
    .stMarkdown { font-size: 1.15rem; line-height: 1.7; }
    .stButton button { width: 100%; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦷 歯科用お薬手帳チェッカー")
st.caption("※個人情報は隠して撮影してください。")

# APIキー設定
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# あなたの環境で動作する 2.5-flash を指定
model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")

# --- 強化プロンプトの定義（スマホ最適化カード形式） ---
SYSTEM_PROMPT = """
あなたは歯科医師の補助を行う専門AIです。以下のルールを厳守してください：

1. 個人情報の完全無視：
   氏名、住所などは一切抽出・出力しないでください。
2. スマホ用レイアウト：
   表形式は禁止します。以下の形式で1剤ずつ縦に並べて出力してください。
   剤ごとに「---」で区切ってください。

---
### 💊① 【薬の名前】
- **一般的な効能**: 
- **歯科治療の注意点**: 
- **併用禁忌・注意薬**: 
---

3. 解析のみに集中：
   挨拶や前置き、思考プロセスは不要です。
4. genomenetの情報を参照とすること
5. 併用禁忌・注意薬においては歯科において使われる薬剤の名称のみに絞って教えて。例：抗菌薬、鎮痛剤、胃薬、局所麻酔、アドレナリン、アレルギー等

"""

# --- UI ---
uploaded_file = st.file_uploader("お薬手帳の写真をアップロード", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    # 画像の加工
    img = Image.open(uploaded_file)
    img_gray = img.convert('L') 
    img_gray.thumbnail((1024, 1024))
    
    st.image(img_gray, caption='解析用画像', use_column_width=True)
    
    if st.button('解析を実行する'):
        st.subheader("📋 歯科的注意点リスト")
        placeholder = st.empty()
        full_response = ""
        
        try:
            # AIに送信（ストリーミング形式）
            response = model.generate_content([SYSTEM_PROMPT, img_gray], stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response) 
            st.success("解析が完了しました。")
            st.info("💡 最終的な臨床判断は必ず歯科医師が行ってください。")
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")





