import streamlit as st
import google.generativeai as genai
from PIL import Image

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
   画像からすべての「薬剤名」を特定してください。
3. 歯科的情報の提供：
   抽出した各薬について、以下の形式で1剤ずつ出力してください。表形式は使わないでください。

💊 【薬の名前】
【一般的な効能】 （ここに効能を簡潔に記載）
【歯科治療の注意点】 （ここに箇条書きで注意点を記載）
【併用禁忌薬および併用注意薬】 （ここに箇条書きで注意点を記載）
4. 該当なしの場合：
   薬が見つからない場合は「薬の名前を検出できませんでした」とだけ回答してください。
5. わからない情報は必ずわからないと伝えること。
「挨拶や前置きは一切不要です。解析結果の表のみを即座に出力してください。思考プロセスも出力しないでください。」
"""

# --- UI ---
uploaded_file = st.file_uploader("お薬手帳の写真をアップロード", type=['jpg', 'jpeg', 'png'])

# --- 修正箇所：uploaded_fileがあった後の処理 ---
if uploaded_file:
    # 1. 画像を読み込む
    img = Image.open(uploaded_file)
    
    # 2. 【NEW!】画像を白黒（グレースケール）にする
    # 'L'モードは、輝度（Luminance）だけを持たせるモードです
    img_gray = img.convert('L') 
    
    # 3. 前回の対策：リサイズ（最大幅1024pxに抑える）
    img_gray.thumbnail((1024, 1024))
    
    # --- UIに表示 ---
    st.image(img_gray, caption='解析用画像（白黒・リサイズ済）', use_column_width=True)
    
    # --- 解析実行 ---
    if st.button('解析を実行する'):
        # AIに送る画像を「白黒リサイズ版」にする
        process_and_analyze(img_gray) # （※解析ロジックは前回と同じ）
    st.image(img, caption='プレビュー（この画像が解析されます）', use_column_width=True)
   
            try:# AIに画像と強化プロンプトを送信
                response = model.generate_content([SYSTEM_PROMPT, img], stream=True)

st.subheader("📋 歯科的注意点リスト")
placeholder = st.empty() # 書き換え用の空枠を作成
full_response = ""

for chunk in response:
    full_response += chunk.text
    placeholder.markdown(full_response + "▌") # 執筆中のカーソル風演出
placeholder.markdown(full_response) # 最後に確定表示
                
                st.info("💡 最終的な臨床判断は必ず歯科医師が行ってください。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")







