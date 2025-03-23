import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime

def main():
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.username is None:
        st.title("Login Page")
        username = st.text_input("Username")
        password = st.text_input("Password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                # Check if the username and password are in the users.txt file
                with open("users.txt", "r") as f:
                    for line in f:
                        u, p = line.strip().split(":")
                        if username == u and password == p:
                            st.success("Logged in as {}".format(username))
                            st.session_state.username = username
                            st.rerun()
                            return
                st.error("Incorrect username or password")
        with col2:
            if st.button("Sign up"):
                # Sign up functionality
                st.write("Creating account...")
                # Store the username and password (insecure, replace with a database)
                with open("users.txt", "a") as f:
                    f.write(f"{username}:{password}\n")
                st.success("Account created successfully!")
    else:
        logout_button = st.sidebar.button("Logout", key="logout")
        if logout_button:
            st.session_state.username = None
            st.rerun()
        show_finance_section()

def show_finance_section():
    st.header("AhorraMas")
    st.write("Un lugar donde la gente puede tener un mejor manejo de sus finanzas.")

    if "expense" not in st.session_state:
        st.session_state.expense = ""
    if "category" not in st.session_state:
        st.session_state.category = "Comida"
    if "amount" not in st.session_state:
        st.session_state.amount = 0.0
    if "type" not in st.session_state:
        st.session_state.type = "Ingreso"
    if "date" not in st.session_state:
        import datetime
        st.session_state.date = datetime.date.today()

    expense = st.text_input("Detalle", key="expense")
    category = st.selectbox("Categoria", ["Comida", "Transporte", "Entretenimiento", "Alquiler", "Prestamo", "Other"], key="category", index=["Comida", "Transporte", "Entretenimiento", "Alquiler", "Prestamo", "Other"].index(st.session_state.category))
    amount = st.number_input("Cantidad", key="amount")
    type = st.radio("Tipo", ["Ingreso", "Egreso"], key="type")
    date = st.date_input("Fecha", key="date")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Agregar movimiento"):
            # Save the entry (insecure, replace with a database)
            date_str = date.strftime("%Y-%m-%d")
            with open("finance_data.txt", "a") as f:
                f.write(f"{expense}:{category}:{amount}:{type}:{date_str}\n")
            st.success("Movimiento agregado exitosamente!")
    with col2:
        if st.button("Limpiar Campos"):
            st.session_state.expense = ""
            st.session_state.category = "Comida"
            st.session_state.amount = 0.0
            st.session_state.type = "Ingreso"
            st.session_state.date = datetime.date.today()
            st.rerun()

    if st.button("Limpiar Tabla"):
        with open("finance_data.txt", "w") as f:
            f.write("")
        st.rerun()

    # Read the data from the file
    try:
        with open("finance_data.txt", "r") as f:
            data = [line.split(":") for line in f]
    except FileNotFoundError:
        st.warning("Cuando realice movimientos se veran reflejados aqui.")
        df = pd.DataFrame()
    else:
        # Create a dataframe from the data
        df = pd.DataFrame(data, columns=["Detalle", "Categoria", "Cantidad", "Tipo", "Fecha"])

        # Filter data for income and expense
        income_data = df[df["Tipo"] == "Ingreso"]
        expense_data = df[df["Tipo"] == "Egreso"]

        # Calculate income by category
        income_by_category = income_data.groupby("Categoria")["Cantidad"].sum()

        # Create income pie chart
        fig_income = go.Figure(data=[go.Pie(labels=income_by_category.index, values=income_by_category.values)])
        fig_income.update_layout(title_text="Ingresos por Categoria")
        st.plotly_chart(fig_income)

        # Calculate expense by category
        expense_by_category = expense_data.groupby("Categoria")["Cantidad"].sum()
        fig_expense = go.Figure(data=[go.Pie(labels=expense_by_category.index, values=expense_by_category.values)])
        fig_expense.update_layout(title_text="Egresos por Categoria")
        st.plotly_chart(fig_expense)

        st.dataframe(df)

    add_gemini_chatbot()

import google.generativeai as genai

def add_gemini_chatbot():
    st.markdown(
        """
        <style>
        .fixed-bottom {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 10px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
    st.header("Chatbot Financiero")

    # Configure Gemini API
    genai.configure(api_key="AIzaSyCusMr4ATiSd1wUvxvWU3FVkpEJuuObKBQ")
    model = genai.GenerativeModel('gemini-2.0-flash-001')

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Limpiar Chat", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Consultame lo que necesites acerca de tus finanzas!", key="prompt"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get Gemini response
        response = model.generate_content(prompt)
        short_response = response.text[:100]
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "Eres un asistente financiero inteligente que ayuda a los usuarios a gestionar sus finanzas personales. Tu objetivo es proporcionar análisis claros y consejos basados en los ingresos y gastos del usuario. Sé claro, conciso y proactivo en tus recomendaciones.", "content": response.text})
        # Display assistant message in chat message container
        with st.chat_message("assistant"):
            st.markdown(response.text)

if __name__ == "__main__":
    main()
