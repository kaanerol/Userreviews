import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import random
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import nltk
from transformers import pipeline


tabs = ["Review Form", "About", "Management"]

page = st.sidebar.radio('Page', tabs)

if page == 'Review Form':
    # .streamlit/secrets.toml dosyasındaki bilgileri oku
    credentials_info = st.secrets["gcp_service_account"]
    # Google Sheets API'yi kullanarak kimlik doğrulama yap
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(credentials)

    # Google Sheet'e bağlan
    # spreadsheet_id = st.secrets["spreadsheet_id"]
    # worksheet_name = st.secrets["worksheet_name"]

    spreadsheet_id = "1b5zp_8mw9UUtiAnO5OctK4sOiKl-ynMfJ8a7C2Zkp70"
    worksheet_name = "Sayfa1"

    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)  # Bu satırın çalıştığından emin olun

    # Streamlit formu ile fatura bilgilerini alma
    st.header("Review")


    with st.form("Form"):


        st.subheader("Disclaimer")
        st.write(
            "By participating in this survey, you agree that the information you provide may be used for product development, research, and marketing purposes. "
            "If you choose to enter the raffle, your contact information (name, phone number, or email) will be used both for notifying the winner and for future marketing communications. "
            "Your responses will be stored and used in accordance with these purposes, and we do not hold any legal liability for the information or suggestions provided.")

        # Checkbox for agreeing to the disclaimer
        agree_to_disclaimer = st.checkbox("I agree to the terms and conditions stated above.")

        st.subheader("Basic Information")
        # Multiple select for models
        models = st.multiselect(
            "select model",
            ["a1","a2","a3","a4"]
        )


        ownership_duration = st.radio(
            "How long have you owned your battery-powered 40V machine?",
            ["Less than 6 months", "6 months to 1 year", "More than 1 year"]
        )

        # Radio buttons for frequency of use
        usage_frequency = st.radio(
            "How often do you use your machine?",
            ["Weekly", "Every 2 weeks", "Monthly", "Other (please specify)"]
        )

        # Selectbox for lawn size
        lawn_size = st.selectbox(
            "What size is your lawn?",
            ["Small (Less than ¼ acre)", "Medium (¼ to ½ acre)", "Large (More than ½ acre)"]
        )

        st.subheader("Machine Performance")
        # Slider for satisfaction rating
        satisfaction = st.slider("How satisfied are you with your machine performance?", 1, 5, 3)

        # Ratings for different aspects
        battery_life = st.slider("Battery life", 1, 5, 3)
        cutting_performance = st.slider("Cutting performance", 1, 5, 3)
        handling = st.slider("Ease of handling", 1, 5, 3)
        noise_level = st.slider("Noise level", 1, 5, 3)
        maintenance = st.slider("Ease of maintenance", 1, 5, 3)

        # Issue encountered
        issues_encountered = st.radio("Have you encountered any issues while using your machine?", ["Yes", "No"])
        if issues_encountered == "Yes":
            issue_description = st.text_area("Please specify the issues you have encountered")

        # Open-ended question for improvements
        improvements = st.text_area("What do you think could be improved on your machine?")

        st.subheader("General Product Feedback")
        # Open-ended question for recommendation
        recommendation = st.text_area("What are the positives and negatives about the product?")

        # Open-ended question for new features
        future_features = st.text_area("What new features or improvements would you like to see in future models?")

        st.subheader("Raffle Entry (Optional)")
        # Contact information
        name = st.text_input("Name and Last Name:")
        contact_info = st.text_input("Phone Number or Email:")

        # Form submission
        submitted = st.form_submit_button("Submit")

    # Action on form submission
    if submitted:
        if not agree_to_disclaimer:
            st.error("You must agree to the terms and conditions to submit the survey.")
        else:
            # Collect all the data
            survey_data = {
                "Models": ", ".join(models),
                "Ownership Duration": ownership_duration,
                "Usage Frequency": usage_frequency,
                "Lawn Size": lawn_size,
                "Satisfaction": satisfaction,
                "Battery Life": battery_life,
                "Cutting Performance": cutting_performance,
                "Handling": handling,
                "Noise Level": noise_level,
                "Maintenance": maintenance,
                "Issues Encountered": issues_encountered,
                "Issue Description": issue_description if issues_encountered == "Yes" else "",
                "Improvements": improvements,
                "Recommendation": recommendation,
                "Future Features": future_features,
                "Name": name,
                "Contact Info": contact_info
            }

            # Verileri Google Sheets'e ekleme
            try:
                sheet.append_row(list(survey_data.values()))
                st.success("Thank you! Your responses have been recorded.")
            except Exception as e:
                st.error(f"An error occurred while submitting the form: {e}")











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

                    spreadsheet_id = "1b5zp_8mw9UUtiAnO5OctK4sOiKl-ynMfJ8a7C2Zkp70"
                    worksheet_name = "Sayfa1"

                    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
                    df = sheet.get_all_records()
                    df = pd.DataFrame(df)
                    st.dataframe(df)

                    ###############################################################
                    # NLTK'deki VADER sözlüğünü indir
                    nltk.download('vader_lexicon')

                    # Başlık
                    st.title("Sentiment Analysis result")

                    # VADER ile sentiment analizi
                    sia = SentimentIntensityAnalyzer()

                    # Her recommendation için duygusal skorları hesapla
                    df['Scores'] = df['recommendation'].apply(lambda x: sia.polarity_scores(x))

                    # Skorları ayır
                    df['Positive'] = df['Scores'].apply(lambda x: x['pos'])
                    df['Negative'] = df['Scores'].apply(lambda x: x['neg'])
                    df['Neutral'] = df['Scores'].apply(lambda x: x['neu'])
                    df['Compound'] = df['Scores'].apply(lambda x: x['compound'])


                    st.write(df[['recommendation', 'Positive', 'Negative', 'Neutral', 'Compound']])

                    # Görselleştirme
                    st.subheader("Sentiment Distribution")
                    st.bar_chart(df[['Positive', 'Negative', 'Neutral']].sum())

                    #####################
                    st.write('Türkçe')
                    classifier = pipeline("sentiment-analysis", model="dbmdz/distilbert-base-turkish-cased")

                    df['Sentiment'] = df['recommendation'].apply(lambda x: classifier(x)[0])
                    # Skorları ayır
                    df['Label'] = df['Sentiment'].apply(lambda x: x['label'])
                    df['Score'] = df['Sentiment'].apply(lambda x: x['score'])

                    # Sonuçları göster
                    st.subheader("Sentiment Analizi Sonuçları")
                    st.write(df[['recommendation', 'Label', 'Score']])

                    # Görselleştirme
                    sentiment_counts = df['Label'].value_counts()
                    st.subheader("Sentiment Dağılımı")
                    st.bar_chart(sentiment_counts)


                    #  Model Preference
                    st.subheader("1. Model Preference")
                    model_count = df["Models"].value_counts().reset_index()
                    model_count.columns = ['Models', 'Count']  # Renaming columns for clarity
                    st.bar_chart(model_count.set_index('Models'))

                    # Define the metrics you want to analyze
                    metrics = ["satisfaction", "battery_life", "cutting_performance", "handling", "noise_level",
                               "maintenance"]
                    # Create a subheader for the metrics
                    st.subheader("Average Metrics by Model")

                    # Create columns for displaying the charts
                    num_columns = 2  # Number of columns per row
                    num_metrics = len(metrics)

                    # Loop through metrics and display them in rows of two
                    for i in range(0, num_metrics, num_columns):
                        cols = st.columns(num_columns)  # Create a row with two columns

                        for j in range(num_columns):
                            if i + j < num_metrics:  # Check to avoid index out of range
                                metric = metrics[i + j]
                                df_metric = df.groupby('Models')[metric].mean().reset_index()

                                # Set color palette for the bar chart
                                colors = sns.color_palette(
                                    "pastel")  # Choose a color palette (e.g., "pastel", "muted", "deep")

                                # Plot the bar chart for the current metric
                                with cols[j]:
                                    fig, ax = plt.subplots()
                                    sns.barplot(x='Models', y=metric, data=df_metric, palette=colors, ax=ax)
                                    ax.set_title(f"Average {metric.replace('_', ' ').title()} by Model")
                                    ax.set_ylabel(metric.replace('_', ' ').title())
                                    ax.set_xlabel("Models")
                                    plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
                                    st.pyplot(fig)
                                    st.write("")  # Adding an empty line for spacing
                                    st.markdown("<br>", unsafe_allow_html=True)  # Extra space using HTML line break



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
    st.write(
        "This tool allows you to analyze reviews from customers for portfolio purposes and to analyze product development and customer satisfaction.")

    st.markdown("""**[Kaan EROL](https://www.linkedin.com/in/kaan-erol/)** """)
















