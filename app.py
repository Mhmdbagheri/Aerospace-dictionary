import streamlit as st
import time
import random
from fuzzywuzzy import fuzz, process
import pandas as pd
from streamlit_mic_recorder import speech_to_text
import speech_recognition as sr

# تنظیمات صفحه
st.set_page_config(page_title="آیرا - دستیار هوشمند هوانوردی")

# دیتاست هوانوردی (همون قبلی)
aviation_dataset = [
    {"category": "پرواز", "term_en": "Boarding", "term_fa": "سوار شدن", "definition": "فرآیند سوار شدن به هواپیما.", "suggestions": "به موقع به گیت برو | کارت پروازت رو آماده کن | از خدمه راهنمایی بخواه", "pronunciation": "بوردینگ"},
    {"category": "پرواز", "term_en": "Takeoff", "term_fa": "بلند شدن", "definition": "لحظه جدا شدن هواپیما از زمین.", "suggestions": "کمربندت رو ببند | به اعلام خلبان گوش کن | پنجره رو چک کن", "pronunciation": "تیک‌آف"},
    {"category": "پرواز", "term_en": "Landing", "term_fa": "فرود", "definition": "فرآیند نشستن هواپیما روی زمین.", "suggestions": "صندلیت رو صاف کن | وسایلت رو جمع کن | منتظر اعلام خدمه باش", "pronunciation": "لندینگ"},
    {"category": "ناوبری", "term_en": "Altitude", "term_fa": "ارتفاع", "definition": "فاصله عمودی از سطح دریا.", "suggestions": "ارتفاع رو چک کن | به خلبان اطلاع بده | ابزارها رو بررسی کن", "pronunciation": "التیتود"},
    {"category": "کنترل", "term_en": "ATC", "term_fa": "کنترل ترافیک هوایی", "definition": "واحدی که ترافیک هوایی رو مدیریت می‌کنه.", "suggestions": "به دستورات گوش کن | ارتباط رو حفظ کن | زمان‌بندی رو رعایت کن", "pronunciation": "ای‌تی‌سی"},
    {"category": "پرواز", "term_en": "Cruising", "term_fa": "پرواز کروز", "definition": "پرواز پایدار در ارتفاع مشخص.", "suggestions": "آرام باش | از پنجره لذت ببر | به خدمه اطلاع بده", "pronunciation": "کروزینگ"},
    {"category": "ناوبری", "term_en": "IFR", "term_fa": "قوانین پرواز با ابزار", "definition": "پرواز با ابزار در شرایط دید کم.", "suggestions": "به ابزارها اعتماد کن | با ATC هماهنگ باش | مسیر رو چک کن", "pronunciation": "آی‌اف‌آر"},
    {"category": "ناوبری", "term_en": "VFR", "term_fa": "قوانین پرواز بصری", "definition": "پرواز با دید مستقیم در شرایط جوی خوب.", "suggestions": "هوا رو بررسی کن | دید رو حفظ کن | با برج هماهنگ باش", "pronunciation": "وی‌اف‌آر"},
    {"category": "پرواز", "term_en": "Taxiing", "term_fa": "تاکسی کردن", "definition": "حرکت هواپیما روی زمین قبل یا بعد پرواز.", "suggestions": "به اطراف نگاه کن | منتظر دستور باش | سرعت رو کم کن", "pronunciation": "تاکسی‌ینگ"},
    {"category": "کنترل", "term_en": "Clearance", "term_fa": "مجوز", "definition": "اجازه رسمی برای پرواز یا حرکت.", "suggestions": "مجوز رو بگیر | با ATC چک کن | صبر کن تا تأیید بشه", "pronunciation": "کلیرنس"},
]

# دیتاست تعاملی جدید
interaction_dataset = [
    {"pattern": "یعنی چی", "similarity_keywords": ["یعنی", "چیه", "معنی"], "response": "می‌خوای معنی یه اصطلاح رو برات توضیح بدم؟ بگو کدوم کلمه رو می‌خوای!"},
    {"pattern": "چیه", "similarity_keywords": ["چیه", "چیست", "یعنی"], "response": "می‌پرسی این چیه؟ بگو کدوم اصطلاح رو می‌خوای برات باز کنم!"},
    {"pattern": "معنی", "similarity_keywords": ["معنی", "یعنی", "تعریف"], "response": "دنبال معنی یه کلمه هستی؟ بگو چی رو برات توضیح بدم!"},
    {"pattern": "سلام", "similarity_keywords": ["سلام", "درود", "هی"], "response": "سلام دوست من! ✈️ چطور می‌تونم کمکت کنم؟"},
    {"pattern": "ممنون", "similarity_keywords": ["ممنون", "تشکر", "مرسی"], "response": "خواهش می‌کنم! اگه سوال دیگه‌ای داری، بگو!"},
    {"pattern": "خداحافظ", "similarity_keywords": ["خداحافظ", "بای", "فعلاً"], "response": "خداحافظ! امیدوارم دوباره ببینمت. پرواز خوبی داشته باشی! ✈️"},
    {"pattern": "چیکار می‌کنی", "similarity_keywords": ["چیکار", "چه", "داری"], "response": "من اینجام و آماده‌ام تا درباره هوانوردی باهات حرف بزنم! سوالی داری؟"},
]

# تزریق CSS (بدون تغییر)
st.markdown("""
<style>
.stApp {
    background: #1A1A2E;
    color: #E0E1DD;
    font-family: 'Vazir', sans-serif;
    direction: rtl;
}
h1 {
    color: #E0E1DD;
    text-shadow: 0 2px 6px rgba(162, 89, 255, 0.5);
    text-align: center;
    animation: glow 2s infinite alternate;
    font-size: 32px;
}
.user-message {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(162, 89, 255, 0.4);
    border-radius: 10px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 70%;
    color: #E0E1DD;
    text-shadow: 0 1px 3px rgba(162, 89, 255, 0.2);
    animation: slideInFromRight 0.5s ease-out;
    display: inline-block;
    text-align: right;
}
.assistant-message {
    background: rgba(162, 89, 255, 0.05);
    border: 1px solid rgba(108, 99, 255, 0.3);
    border-radius: 15px;
    padding: 25px;
    margin: 10px 0;
    max-width: 90%;
    color: #E0E1DD;
    box-shadow: 0 4px 15px rgba(162, 89, 255, 0.1);
    animation: slideInFromLeft 0.6s ease-out;
    display: inline-block;
    text-align: right;
}
.assistant-message .main-term {
    font-size: 20px;
    font-weight: bold;
    color: #A259FF;
    margin-bottom: 20px;
    padding: 10px;
    background: rgba(162, 89, 255, 0.1);
    border-radius: 8px;
    text-align: right;
    box-shadow: 0 2px 8px rgba(162, 89, 255, 0.2);
}
.assistant-message .plain-text {
    font-size: 16px;
    color: #E0E1DD;
    margin-bottom: 15px;
    line-height: 1.7;
}
.assistant-message .section {
    background: linear-gradient(135deg, rgba(162, 89, 255, 0.2) 0%, rgba(108, 99, 255, 0.1) 100%);
    border: 1px solid rgba(162, 89, 255, 0.3);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    animation: fadeInUp 0.5s ease-out;
}
.assistant-message .section:nth-child(1) { animation-delay: 0.1s; }
.assistant-message .section:nth-child(2) { animation-delay: 0.2s; }
.assistant-message .section:nth-child(3) { animation-delay: 0.3s; }
.assistant-message .section-title {
    font-size: 18px;
    font-weight: bold;
    color: #A259FF;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}
.assistant-message .section-title.category::after { content: "🏷️"; margin-left: 8px; }
.assistant-message .section-title.definition::after { content: "ℹ️"; margin-left: 8px; }
.assistant-message .section-title.suggestions::after { content: "💡"; margin-left: 8px; }
.assistant-message .section-title.pronunciation::after { content: "🔊"; margin-left: 8px; }
.assistant-message .section-content {
    font-size: 16px;
    color: #D3D3D3;
    line-height: 1.7;
    padding-right: 30px;
}
.assistant-message .section-content b { color: #E0E1DD; }
.assistant-message .suggestion-list {
    list-style-type: none;
    padding: 0;
}
.assistant-message .suggestion-list li::before {
    content: "• ";
    color: #A259FF;
}
.recommendation-header {
    font-size: 18px;
    color: #A259FF;
    margin-top: 20px;
    margin-bottom: 10px;
    text-align: right;
    font-weight: bold;
}
.recommendation-container {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
}
.recommendation-item {
    background: linear-gradient(135deg, rgba(162, 89, 255, 0.4) 0%, rgba(108, 99, 255, 0.3) 100%);
    border: 1px solid rgba(162, 89, 255, 0.5);
    border-radius: 10px;
    padding: 10px 15px;
    width: 150px;
    text-align: right;
    color: #E0E1DD;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: fadeInUp 0.5s ease-out;
}
.recommendation-item:nth-child(1) { animation-delay: 0.6s; }
.recommendation-item:nth-child(2) { animation-delay: 0.7s; }
.recommendation-item:nth-child(3) { animation-delay: 0.8s; }
.recommendation-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(162, 89, 255, 0.4);
}
.recommendation-title {
    font-size: 16px;
    font-weight: bold;
    color: #A259FF;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}
.recommendation-title::after {
    content: "➡️";
    margin-left: 5px;
    font-size: 14px;
    color: #A259FF;
}
.recommendation-desc {
    font-size: 12px;
    color: #D3D3D3;
    margin-top: 5px;
}
.similarity-score {
    font-size: 12px;
    color: #E0E1DD;
    background: rgba(162, 89, 255, 0.3);
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 5px;
    box-shadow: 0 0 5px rgba(162, 89, 255, 0.5);
}
.chat-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
.chat-container .user-message { align-self: flex-end; }
.chat-container .assistant-message { align-self: flex-start; }
.step-text {
    font-size: 14px;
    padding: 5px 10px;
    background: rgba(128, 128, 128, 0.3);
    border-radius: 12px;
    display: inline-block;
    box-shadow: none;
    color: #B0B0B0;
    animation: none;
    text-align: right;
}
.timer {
    color: #A259FF;
    font-size: 14px;
    background: rgba(162, 89, 255, 0.3);
    padding: 3px 10px;
    border-radius: 15px;
    margin-right: 10px;
    box-shadow: 0 0 5px rgba(162, 89, 255, 0.5);
}
.tick {
    display: inline-block;
    margin-right: 10px;
    animation: spinGlow 0.5s ease-in forwards;
}
.tick svg {
    stroke: #A259FF;
    filter: drop-shadow(0 0 3px rgba(162, 89, 255, 0.5));
}
.radar-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 10;
}
.radar-animation {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    padding: 15px;
}
.radar-blur {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(27, 38, 59, 0.6);
    backdrop-filter: blur(5px);
    border-radius: 12px;
    z-index: -1;
}
.radar-dot {
    width: 12px;
    height: 12px;
    background: #A259FF;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
}
.radar-dot:nth-child(2) { animation-delay: 0.3s; }
.radar-dot:nth-child(3) { animation-delay: 0.6s; }
.radar-animation::before {
    content: '';
    position: absolute;
    width: 40px;
    height: 40px;
    border: 2px solid rgba(162, 89, 255, 0.5);
    border-radius: 50%;
    animation: radarWave 2s infinite;
}
.stExpander {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(162, 89, 255, 0.3);
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    direction: rtl;
}
.stExpander[open] {
    transform: scale(1.02);
    box-shadow: 0 6px 25px rgba(162, 89, 255, 0.2);
}
.stExpander > div > div {
    color: #E0E1DD;
    text-align: right;
}
.step-item {
    padding: 8px 15px;
    margin: 5px 0;
    background: rgba(162, 89, 255, 0.1);
    border-right: 4px solid #A259FF;
    border-radius: 5px;
    transition: transform 0.2s ease;
    text-align: right;
}
.step-item:hover {
    transform: translateX(-5px);
    box-shadow: 0 2px 10px rgba(162, 89, 255, 0.3);
}
.total-time {
    margin-top: 10px;
    padding: 10px;
    background: rgba(162, 89, 255, 0.2);
    border-radius: 8px;
    font-weight: bold;
    text-align: center;
    color: #A259FF;
}
.sidebar .sidebar-content {
    background: #2A2A4A;
    padding: 20px;
    border-radius: 10px;
}
.sidebar-title {
    color: #A259FF;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 15px;
    text-align: right;
}
.landing-container {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin: 20px 0;
}
.landing-box {
    background: linear-gradient(135deg, rgba(162, 89, 255, 0.2) 0%, rgba(108, 99, 255, 0.1) 100%);
    border: 1px solid rgba(162, 89, 255, 0.5);
    border-radius: 15px;
    padding: 20px;
    width: 250px;
    text-align: center;
    color: #E0E1DD;
    box-shadow: 0 4px 15px rgba(162, 89, 255, 0.2);
    transition: transform 0.3s ease;
}
.landing-box:hover {
    transform: translateY(-10px);
}
.landing-box h3 {
    color: #A259FF;
    font-size: 20px;
    margin-bottom: 10px;
}
.landing-box p {
    font-size: 14px;
    color: #D3D3D3;
}
@keyframes slideInFromRight { 0% { opacity: 0; transform: translateX(-20px); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes slideInFromLeft { 0% { opacity: 0; transform: translateX(20px); } 100% { opacity: 1; transform: translateX(0); } }
@keyframes fadeInUp { 0% { opacity: 0; transform: translateY(15px); } 100% { opacity: 1; transform: translateY(0); } }
@keyframes spinGlow { 0% { opacity: 0; transform: rotate(0deg) scale(0.5); } 100% { opacity: 1; transform: rotate(360deg) scale(1); } }
@keyframes pulse { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.6); opacity: 0.6; } 100% { transform: scale(1); opacity: 1; } }
@keyframes radarWave { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(2); opacity: 0; } }
@keyframes glow { 0% { text-shadow: 0 2px 6px rgba(162, 89, 255, 0.3); } 100% { text-shadow: 0 2px 12px rgba(162, 89, 255, 0.7); } }
</style>
<link href="https://fonts.googleapis.com/css2?family=Vazir:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# عنوان صفحه
st.title("آیرا - دستیار هوشمند هوانوردی ✈️")

# تابع شبیه‌ساز پاسخ (اصلاح‌شده)
def response_generator(prompt, streaming_time):
    # شکستن ورودی به کلمات جداگانه
    words = prompt.lower().strip().split()
    all_terms_en = [item["term_en"].lower() for item in aviation_dataset]
    all_terms_fa = [item["term_fa"] for item in aviation_dataset]
    all_pronunciations = [item["pronunciation"] for item in aviation_dataset]
    
    # کلمات غیرمرتبط که باید نادیده گرفته بشن
    common_words = {"یعنی", "چیه", "چی", "معنی", "تعریف", "چیست", "رو", "برام", "بگو"}
    
    # پیدا کردن کلمه‌ای که ممکنه اصطلاح هوانوردی باشه
    potential_terms = [word for word in words if word not in common_words]
    
    # چک کردن دیتاست تعاملی
    for interaction in interaction_dataset:
        match = process.extractOne(prompt.lower(), interaction["similarity_keywords"], scorer=fuzz.token_sort_ratio)
        if match[1] > 70:  # اگه شباهت بالای 70% باشه
            sections = [f"<div class='plain-text'>{interaction['response']}</div>"]
            if potential_terms:  # اگه کلمه احتمالی پیدا شده
                sections.append(f"<div class='plain-text'>فکر کنم منظورت <b>{potential_terms[0]}</b> باشه، درسته؟ اگه آره، صبر کن برات توضیح بدم!</div>")
            return sections
    
    # اگه توی دیتاست تعاملی نبود، بریم سراغ دیتاست هوانوردی
    if potential_terms:
        term = potential_terms[0]  # اولین کلمه احتمالی رو می‌گیریم
        match_en = process.extractOne(term, all_terms_en, scorer=fuzz.token_sort_ratio)
        match_fa = process.extractOne(term, all_terms_fa, scorer=fuzz.token_sort_ratio)
        match_pron = process.extractOne(term, all_pronunciations, scorer=fuzz.token_sort_ratio)
        
        matches = [(match_en, "term_en"), (match_fa, "term_fa"), (match_pron, "pronunciation")]
        best_match = max(matches, key=lambda x: x[0][1])
        matched_term, score, field = best_match[0][0], best_match[0][1], best_match[1]
        
        if score > 40:
            matched_item = next(item for item in aviation_dataset if item[field].lower() == matched_term.lower())
            sections = [
                f"<div class='main-term'><b>{matched_item['term_en']}</b>: <b>{matched_item['term_fa']}</b></div>",
                "<div class='plain-text'>خوش اومدی! 😊</div>" + (f"<div class='plain-text'>فکر کنم منظورت <b>{matched_item['term_fa']}</b> بود، درسته؟</div>" if term != matched_term.lower() else ""),
                f"<div class='section'><div class='section-title category'>دسته‌بندی</div><div class='section-content'>{matched_item['category']}</div></div>",
                f"<div class='section'><div class='section-title definition'>تعریف</div><div class='section-content'>{matched_item['definition']}</div></div>",
                f"<div class='section'><div class='section-title suggestions'>پیشنهادات</div><div class='section-content'><ul class='suggestion-list'>" + "".join([f"<li>{s.strip()}</li>" for s in matched_item['suggestions'].split('|')]) + "</ul></div></div>",
                f"<div class='section'><div class='section-title pronunciation'>تلفظ</div><div class='section-content'>{matched_item['pronunciation']}</div></div>",
                "<div class='plain-text'>اگه سوال دیگه‌ای داری، بگو! ✈️</div>",
            ]
            related = process.extract(matched_item["term_en"].lower(), [item["term_en"].lower() for item in aviation_dataset if item["term_en"].lower() != matched_item["term_en"].lower()], scorer=fuzz.token_sort_ratio, limit=3)
            recommendation = "<div class='recommendation-header'>مسافران این کلمات را نیز پرسیده‌اند</div><div class='recommendation-container'>" + "".join(
                [f"<div class='recommendation-item'><div class='recommendation-title'>{r[0]}</div><div class='recommendation-desc'>{next(item['term_fa'] for item in aviation_dataset if item['term_en'].lower() == r[0])}</div><div class='similarity-score'>{r[1]}%</div></div>" for r in related]
            ) + "</div>"
            sections.append(recommendation)
            return sections
    
    # اگه هیچی پیدا نشد
    sections = [
        "<div class='main-term'><b>چیزی پیدا نشد</b></div>",
        "<div class='plain-text'>متأسفم، اینو نفهمیدم! 😔</div>",
        "<div class='plain-text'>می‌تونی واضح‌تر بگی یا یه اصطلاح دیگه بپرسی؟ ✈️</div>",
        "<div class='recommendation-header'>مسافران این کلمات را نیز پرسیده‌اند</div><div class='recommendation-container'>" + "".join(
            [f"<div class='recommendation-item'><div class='recommendation-title'>{item['term_en']}</div><div class='recommendation-desc'>{item['term_fa']}</div><div class='similarity-score'>-</div></div>" for item in aviation_dataset[:3]]
        ) + "</div>"
    ]
    return sections

# تابع پردازش پیام (تغییر جزئی)
def process_message(prompt):
    start_time = time.time()
    with st.chat_message("user"):
        st.markdown(f"<div class='user-message'>{prompt}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        steps_placeholder = st.empty()
        steps = ["دریافت ورودی کاربر", "تحلیل درخواست", "جست‌وجوی داده‌ها", "تولید پاسخ"]
        step_times = []
        
        total_time = min(10, max(5, 5 + len(prompt) / 20))
        step_total_time = total_time * 0.7
        radar_time = total_time * 0.15
        streaming_time = total_time * 0.15
        
        remaining_time = step_total_time
        for i, step in enumerate(steps):
            if i == len(steps) - 1:
                step_duration = remaining_time
            else:
                min_time = 0.5
                max_time = min(2.0, remaining_time - (len(steps) - i - 1) * 0.5)
                step_duration = random.uniform(min_time, max_time)
                remaining_time -= step_duration
            
            steps_placeholder.markdown(
                f"<span class='step-text'>{step}</span> <span class='timer'>{step_duration:.2f} ثانیه</span>",
                unsafe_allow_html=True
            )
            time.sleep(0.5)
            if step == "تولید پاسخ":
                total_time_so_far = sum(time for _, time in step_times) + step_duration
                steps_placeholder.markdown(
                    f"<span class='step-text'>{step}</span> <span class='timer'>{step_duration:.2f} ثانیه (کل: {total_time_so_far:.2f} ثانیه)</span> "
                    f"<span class='tick'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke-width='2'><path d='M20 6L9 17l-5-5'/></svg></span>",
                    unsafe_allow_html=True
                )
            else:
                steps_placeholder.markdown(
                    f"<span class='step-text'>{step}</span> <span class='timer'>{step_duration:.2f} ثانیه</span> "
                    f"<span class='tick'><svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke-width='2'><path d='M20 6L9 17l-5-5'/></svg></span>",
                    unsafe_allow_html=True
                )
            time.sleep(step_duration - 0.5)
            step_times.append((step, step_duration))
        
        with st.expander("جزئیات پردازش"):
            total_time_so_far = sum(time for _, time in step_times)
            steps_text = "".join([f"<div class='step-item'>{step} ({time:.2f} ثانیه)</div>" for step, time in step_times])
            st.markdown(f"{steps_text}<div class='total-time'>زمان کل فکر کردن دستیار: {total_time_so_far:.2f} ثانیه</div>", unsafe_allow_html=True)
        
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("""
        <div class='radar-container'>
            <div class='radar-animation'>
                <div class='radar-blur'></div>
                <div class='radar-dot'></div>
                <div class='radar-dot'></div>
                <div class='radar-dot'></div>
            </div>
            <p style='text-align: center; color: #E0E1DD;'>در حال تکمیل...</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(radar_time * 0.75)
        thinking_placeholder.markdown("""
        <div class='radar-container'>
            <div class='radar-animation'>
                <div class='radar-dot'></div>
                <div class='radar-dot'></div>
                <div class='radar-dot'></div>
            </div>
            <p style='text-align: center; color: #E0E1DD;'>در حال تکمیل...</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(radar_time * 0.25)
        
        thinking_placeholder.empty()
        response_placeholder = st.empty()
        response = ""
        for section in response_generator(prompt, streaming_time):  # تغییر به حلقه ساده‌تر
            response += section
            response_placeholder.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
            time.sleep(0.3)
        st.session_state.messages.append({"role": "assistant", "content": response})

# سایدبار (بدون تغییر نسبت به نسخه قبلی)
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True, caption="Aira Logo", output_format="PNG")
    except:
        st.warning("فایل لوگو پیدا نشد. لطفاً 'logo.png' رو توی پوشه پروژه بذارید.")
    st.markdown("<div class='sidebar-title'>ابزارها</div>", unsafe_allow_html=True)
    
    st.markdown("### آپلود دیتاست CSV")
    uploaded_csv = st.file_uploader("فایل CSV رو آپلود کن", type=["csv"])
    if uploaded_csv is not None:
        try:
            df = pd.read_csv(uploaded_csv)
            aviation_dataset.clear()
            aviation_dataset.extend(df.to_dict(orient="records"))
            st.success("دیتاست با موفقیت آپلود شد!")
        except Exception as e:
            st.error(f"خطا در خواندن فایل: {e}")
    
    st.markdown("### ضبط صدا")
    st.markdown("**پیش‌نمایش پیام**")
    speech_output = speech_to_text(
        language='fa',
        start_prompt="🎙️ شروع ضبط",
        stop_prompt="⏹️ توقف ضبط",
        use_container_width=True,
    )
    if speech_output:
        process_message(speech_output)
    elif "speech_attempted" in st.session_state and st.session_state.speech_attempted and speech_output is None:
        st.session_state.messages.append({"role": "assistant", "content": "نتونستم چیزی رو متوجه بشم. لطفاً دوباره امتحان کن یا سوالت رو تایپ کن! 😕"})
        with st.chat_message("assistant"):
            st.markdown("<div class='assistant-message'>نتونستم چیزی رو متوجه بشم. لطفاً دوباره امتحان کن یا سوالت رو تایپ کن! 😕</div>", unsafe_allow_html=True)
    st.session_state.speech_attempted = True if speech_output is not None else st.session_state.get("speech_attempted", False)

# مقداردهی اولیه تاریخچه چت
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "سلام! من آیرا هستم، دستیار هوشمندت توی دنیای هوانوردی. از اصطلاحات پیچیده تا نکات سفر، هر سوالی داری بپرس، با هم پرواز می‌کنیم به سمت جواب! ✈️"}
    ]

# صفحه لندینگ
if len(st.session_state.messages) == 1:
    st.markdown("""
    <div class='landing-container'>
        <div class='landing-box'>
            <h3>✈️ خوش اومدی!</h3>
            <p>با آیرا هر سوالی داری بپرس، از اصطلاحات هوانوردی تا نکات سفر.</p>
        </div>
        <div class='landing-box'>
            <h3>📋 دیتاستت رو آپلود کن</h3>
            <p>یه فایل CSV آپلود کن تا اصطلاحات دلخواهت رو به سیستم اضافه کنی.</p>
        </div>
        <div class='landing-box'>
            <h3>🎙️ با صدا بپرس</h3>
            <p>میکروفونت رو روشن کن و سوالت رو بگو، ما برات تبدیل به متن می‌کنیم.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# نمایش تاریخچه چت
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-message'>{message['content']}</div>", unsafe_allow_html=True)

# چت اینپوت
prompt = st.chat_input("سوالی داری؟ بپرس!")
if prompt:
    process_message(prompt)