import streamlit as st
import requests

from snowflake.snowpark.functions import col

# -----------------------------------------
# TÍTULO
# -----------------------------------------

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------------------
# CONEXÃO COM SNOWFLAKE
# -----------------------------------------

cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------------------
# NOME DO CLIENTE
# -----------------------------------------

name_on_order = st.text_input("Name on Smoothie:")

# -----------------------------------------
# BUSCA AS FRUTAS NO SNOWFLAKE
# -----------------------------------------

my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

# -----------------------------------------
# SELEÇÃO DOS INGREDIENTES
# -----------------------------------------

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# -----------------------------------------
# FRUIT NUTRITION INFORMATION
# Etapa do exercício Snowflake
# -----------------------------------------

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

st.text(smoothiefroot_response.json())

# -----------------------------------------
# PREPARA OS INGREDIENTES DO PEDIDO
# -----------------------------------------

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # -----------------------------------------
    # ENVIAR PEDIDO
    # -----------------------------------------

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        if not name_on_order:

            st.warning(
                "Please enter a name for your Smoothie."
            )

        else:

            my_insert_stmt = """
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                    (INGREDIENTS, NAME_ON_ORDER)
                VALUES
                    (?, ?)
            """

            try:

                session.sql(
                    my_insert_stmt,
                    params=[
                        ingredients_string,
                        name_on_order
                    ]
                ).collect()

                st.success(
                    "Your Smoothie is ordered!",
                    icon="✅"
                )

            except Exception as e:

                st.error(
                    "Something went wrong."
                )

                st.write(e)
