import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import random
from datetime import datetime

from textblob import TextBlob
import matplotlib.pyplot as plt
from collections import Counter
import re


tabs = ["Review Form","About", "Management"]

page = st.sidebar.radio('Page', tabs)


if page == 'Review Form':
    # .streamlit/secrets.toml dosyasındaki bilgileri oku
    credentials_info = st.secrets["gcp_service_account"]

    # Google Sheets API'yi kullanarak kimlik doğrulama yap
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(credentials)

    # Google Sheet'e bağlan
    spreadsheet_id = "1b5zp_8mw9UUtiAnO5OctK4sOiKl-ynMfJ8a7C2Zkp70"
    worksheet_name = "Sayfa1"
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)  # Bu satırın çalıştığından emin olun

    # Streamlit formu ile product developer görüşlerini alma
    st.header("Product Review Form")

    with st.form("review_form"):
        # User Information
        firstname = st.text_input("Firstname", placeholder="Enter your first name")
        lastname = st.text_input("Lastname", placeholder="Enter your last name")
        email = st.text_input("Email", placeholder="Enter your email")
        phone = st.text_input("Phone", placeholder="Enter your phone number")

        # Product Name
        product_name = st.selectbox("Product Name", ["Mouse", "Keyboard", "Gamepad"])

        # User Profile
        usage_frequency = st.selectbox("How often do you use the product?", ["Daily", "Weekly", "Monthly", "Rarely"])

        # Usage habits and scenarios
        frequently_used_features = st.text_area("What are the features of the product that you use most frequently?")
        rarely_used_features = st.text_area(
            "Are there any features of the product that you rarely use? If so, what are they?")

        # Functionality and Performance (Mandatory fields)
        missing_features = st.text_area(
            "Are there any functionalities that you think are missing in the product? (Required)")
        valuable_features = st.text_area("Which of the existing features are the most valuable to you? Why?")
        performance_issues = st.text_area(
            "Do you experience any performance issues while using the product? If yes, please explain.")

        # User Experience (UX)
        ux_issues = st.text_area(
            "Are there any aspects of the product's usability that you find difficult? If so, what are they?")

        # Development and Improvement Suggestions (Mandatory fields)
        feature_requests = st.text_area(
            "Are there any new features or functionalities you would like to see added to the product? (Required)")
        improvements = st.text_area(
            "Are there any existing features that you think need improvement in terms of how they work?")

        # Consent checkbox
        consent = st.checkbox("I agree that my information will be used for product development and marketing purposes.")

        # Form submission button
        submitted = st.form_submit_button("Submit")

    # When the form is submitted, send data to Google Sheets
    if submitted:
        # Check for mandatory fields
        if not missing_features:
            st.error("Please fill in the missing functionalities field.")
        elif not feature_requests:
            st.error("Please fill in the new features or functionalities field.")
        elif not product_name:
            st.error("Please select a product name.")
        elif not consent:
            st.warning("Please agree to the use of your information.")
        else:
            # Get the current date and time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Prepare the data as a list
            data = [
                firstname, lastname, email, phone, product_name, usage_frequency,
                frequently_used_features, rarely_used_features, valuable_features,
                missing_features, performance_issues, ux_issues,
                feature_requests, improvements, current_time
            ]

            # Add data to Google Sheets
            try:
                sheet.append_row(data)  # Adds data to the last row
                st.success("Data successfully added!")
            except Exception as e:
                st.error(f"An error occurred while adding data: {e}")







elif page == 'Management':
    # Kullanıcı doğrulama fonksiyonu
    def authenticate(email, password):
        stored_email = st.secrets["user"]["email"]
        stored_password = st.secrets["user"]["password"]
        return stored_email == email and stored_password == password


    # Basit CAPTCHA işlevi
    def generate_captcha():
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        return num1, num2, num1 + num2  # Doğru cevabı döndür


    # Giriş sayfası
    def login_page():
        # Kullanıcı doğrulama fonksiyonu
        def authenticate(email, password):
            stored_email = st.secrets["user"]["email"]
            stored_password = st.secrets["user"]["password"]
            return stored_email == email and stored_password == password

        # Basit CAPTCHA işlevi
        def generate_captcha():
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            return num1, num2, num1 + num2  # Doğru cevabı döndür

        # Giriş sayfası
        def login_page():
            st.title("Login Page")

            if 'logged_in' not in st.session_state:
                st.session_state.logged_in = False
            if 'login_attempts' not in st.session_state:
                st.session_state.login_attempts = 0
            if 'captcha_generated' not in st.session_state:
                st.session_state.captcha_generated = False

            if not st.session_state.logged_in:
                email = st.text_input("UserId")
                password = st.text_input("Password", type="password")

                if st.session_state.login_attempts < 5:
                    if not st.session_state.captcha_generated:
                        st.session_state.captcha_num1, st.session_state.captcha_num2, st.session_state.captcha_answer = generate_captcha()
                        st.session_state.captcha_generated = True

                    answer = st.number_input(
                        f"What is {st.session_state.captcha_num1} + {st.session_state.captcha_num2}?", min_value=0,
                        key="captcha_input")

                    if st.button("Login"):
                        if answer == st.session_state.captcha_answer:  # Doğru yanıt kontrolü
                            if authenticate(email, password):
                                st.session_state.logged_in = True
                                st.session_state.login_attempts = 0
                                st.success("Login successful!")
                                st.session_state.captcha_generated = False  # CAPTCHA'yı sıfırla
                                st.rerun()
                            else:
                                st.session_state.login_attempts += 1
                                st.error("Invalid credentials!")
                        else:
                            st.error("Please solve the CAPTCHA correctly.")
                else:
                    st.error("Too many failed attempts. Please try again later.")
                    time.sleep(5)  # 5 saniye beklet

            else:
                st.success("You are logged in!")

                def load_df():


                    credentials_info = st.secrets["gcp_service_account"]
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
                    client = gspread.authorize(credentials)

                    spreadsheet_id = st.secrets["spreadsheet_id"]
                    worksheet_name = st.secrets["worksheet_name"]

                    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
                    df = sheet.get_all_records()
                    df = pd.DataFrame(df)
                    st.dataframe(df)


###############################################################

                    # Duygu analizi fonksiyonu
                    def analyze_sentiment(text):
                        return TextBlob(text).sentiment.polarity

                    # Duygu analizi uygulama
                    df['sentiment_valuable'] = df['valuable_features'].apply(analyze_sentiment)
                    df['sentiment_missing'] = df['missing_features'].apply(analyze_sentiment)
                    df['sentiment_performance'] = df['performance_issues'].apply(analyze_sentiment)
                    df['sentiment_requests'] = df['feature_requests'].apply(analyze_sentiment)

                    # Sonuçları gösterme
                    st.subheader("Sentiment Analysis Results")
                    st.write(df[['valuable_features', 'sentiment_valuable', 'missing_features', 'sentiment_missing',
                                 'performance_issues', 'sentiment_performance', 'feature_requests',
                                 'sentiment_requests']])

                    # Kelime frekans analizi
                    def word_frequency(texts):
                        words = []
                        for text in texts:
                            words.extend(re.findall(r'\w+', text.lower()))
                        return Counter(words)

                    # Kelime frekanslarını hesaplama
                    valuable_words = word_frequency(df['valuable_features'])
                    missing_words = word_frequency(df['missing_features'])
                    performance_words = word_frequency(df['performance_issues'])
                    request_words = word_frequency(df['feature_requests'])



                    # Grafik oluşturma
                    def plot_word_frequency(counter, title):
                        words, counts = zip(*counter.most_common(10))
                        plt.bar(words, counts)
                        plt.title(title)
                        plt.xticks(rotation=45)
                        plt.ylabel('Frequency')
                        st.pyplot(plt)

                    # Grafik gösterme
                    st.subheader("Word Frequency Charts")
                    plot_word_frequency(valuable_words, 'Word Frequency (Valuable Features)')
                    plot_word_frequency(missing_words, 'Word Frequency (Missing Features)')

                load_df()

                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.info("You have logged out.")
                    st.session_state.captcha_generated = False  # CAPTCHA'yı sıfırla
                    st.rerun()

        # Ana uygulama
        def main():
            login_page()

        # Uygulamayı başlat
        if __name__ == "__main__":
            main()

    # Ana uygulama
    def main():
        login_page()


    # Uygulamayı başlat
    if __name__ == "__main__":
        main()





elif page == 'About':

    st.header("About Tool")
    st.write("This tool allows you to analyze reviews from customers for portfolio purposes and to analyze product development and customer satisfaction.")

    st.markdown("""**[Kaan EROL](https://www.linkedin.com/in/kaan-erol/)** """)

















