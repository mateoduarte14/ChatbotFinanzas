import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import datetime
from smolagents import CodeAgent, DuckDuckGoSearchTool, LiteLLMModel

# Initialize SQLite database
conn = sqlite3.connect('finance_tracker.db')
c = conn.cursor()

# Create transactions table if it doesn't exist
try:
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    """)
    conn.commit()
except sqlite3.OperationalError as e:
    print(f"Error creating transactions table: {e}")

# Drop user_id column if it exists
try:
    c.execute("""
        ALTER TABLE transactions
        DROP COLUMN user_id
    """)
    conn.commit()
except sqlite3.OperationalError as e:
    if "no such column: user_id" in str(e):
        print("Column 'user_id' does not exist in 'transactions' table.")
    else:
        print(f"Error dropping user_id column: {e}")

# --- Initialize ---
st.title('AhorraMás')

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# --- Financial Assistant Persona ---
st.write(
    "Soy tu asistente financiero inteligente. Estoy aquí para ayudarte a administrar tus finanzas personales proporcionándote análisis claros y consejos basados en tus ingresos y gastos."
)

# --- Input form ---
with st.form("transaction_form"):
    transaction_type = st.selectbox("Tipo", ["Ingreso", "Gasto"])
    amount = st.number_input("Monto", value=0.0)
    category = st.text_input("Categoría")
    date = st.date_input("Fecha", datetime.date.today())
    submitted = st.form_submit_button("Agregar Transacción")

    if submitted:
        transaction = {
            "Type": transaction_type,
            "Amount": amount,
            "Category": category,
            "Date": date
        }
        st.session_state.transactions.append(transaction)

        # Insertar transacción en la base de datos SQLite
        c.execute(
            "INSERT INTO transactions (type, amount, category, date) VALUES (?, ?, ?, ?)",
            (transaction_type, amount, category, str(date)),
        )
        conn.commit()

        st.success("¡Transacción agregada!")

# --- Mostrar transacciones ---
st.write("### Transacciones")

# Obtener transacciones de la base de datos SQLite
c.execute("SELECT * FROM transactions")
transactions = c.fetchall()

if transactions:
    df = pd.DataFrame(transactions, columns=['id', 'type', 'amount', 'category', 'date'])
    st.dataframe(df)

    # --- Informes ---
    st.write("### Informes")
    if not df.empty:
        # DataFrames separados para ingresos y gastos
        income_df = df[df['type'] == 'Ingreso']
        expense_df = df[df['type'] == 'Gasto']

        # Crear gráfico de ingresos
        if not income_df.empty:
            income_summary = income_df.groupby('category')['amount'].sum().reset_index()
            fig_income = px.pie(
                income_summary, values='amount', names='category', title='Ingresos por Categoría'
            )
            st.plotly_chart(fig_income)
        else:
            st.write("No hay transacciones de ingresos para mostrar.")

        # Crear gráfico de gastos
        if not expense_df.empty:
            expense_summary = (
                expense_df.groupby('category')['amount'].sum().reset_index()
            )
            fig_expense = px.pie(
                expense_summary, values='amount', names='category', title='Gastos por Categoría'
            )
            st.plotly_chart(fig_expense)
        else:
            st.write("No hay transacciones de gastos para mostrar.")

        # --- Análisis Financiero y Recomendaciones ---
        total_income = df[df['type'] == 'Ingreso']['amount'].sum()
        total_expense = df[df['type'] == 'Gasto']['amount'].sum()
        net_balance = total_income - total_expense

        st.write("### Análisis Financiero")
        st.write(f"Ingresos Totales: ${total_income:.2f}")
        st.write(f"Gastos Totales: ${total_expense:.2f}")
        st.write(f"Balance Neto: ${net_balance:.2f}")

        if net_balance >= 0:
            st.write("¡Tus finanzas están en buena forma! Sigue así.")
        else:
            st.write(
                "Considera reducir los gastos o aumentar los ingresos para mejorar tu salud financiera."
            )

        # --- Detección de Patrones de Gasto ---
        st.write("### Patrones de Gasto")
        if total_expense > 0:
            most_expensive_category = expense_summary.sort_values(
                by='amount', ascending=False
            ).iloc[0]
            st.write(
                f"Tu categoría de gasto más grande es {most_expensive_category['category']} con ${most_expensive_category['amount']:.2f}."
            )
            st.write("Considera formas de reducir los gastos en esta categoría.")
        else:
            st.write("No se han registrado gastos todavía.")
    else:
        st.write("No hay transacciones para mostrar.")
else:
    st.write("¡Aún no hay transacciones! ¡Agrega algunas!")

# --- Chatbot ---
st.write("### Chatbot Financiero")

# Replace with your actual API key
api_key = "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"

modelo = LiteLLMModel(
    model_id="llama3-70b-8192",
    api_key=api_key,
    provider="groq",
    temperature=0.0,
    max_tokens=2048
)

agent = CodeAgent(
    model=modelo,
    tools=[DuckDuckGoSearchTool()]
)

user_question = st.text_input(
    "Hola soy tu asistente financiero, dime lo que quieras saber:"
)

if user_question:
    if transactions:
        # Use the AI agent to generate a response
        response = agent.run(user_question)
        st.write(response)
    else:
        st.write(
            "No hay transacciones para analizar. Agrega algunas transacciones para obtener una respuesta."
        )

# Cerrar conexión
conn.close()
