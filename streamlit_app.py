import streamlit as st
import requests

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Título
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Nome do cliente
name_on_order = st.text_input("Name on Smoothie:")

# Sessão Snowflake
session = get_active_session()

# Busca as frutas
my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

# Seleção dos ingredientes
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # -----------------------------------------
    # INFORMAÇÕES NUTRICIONAIS
    # -----------------------------------------

    st.subheader("Fruit Nutrition Information")

    fruit_to_check = ingredients_list[0]

    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/" + fruit_to_check
    )

    if smoothiefroot_response.status_code == 200:

        st.dataframe(
            smoothiefroot_response.json(),
            use_container_width=True
        )

    else:
        st.warning(
            "Nutrition information could not be found for this fruit."
        )

    # -----------------------------------------
    # ENVIAR PEDIDO
    # -----------------------------------------

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        my_insert_stmt = """
            INSERT INTO smoothies.public.orders
                (ingredients, name_on_order)
            VALUES
                (?, ?)
        """

        try:
            session.sql(
                my_insert_stmt,
                params=[ingredients_string, name_on_order]
            ).collect()

            st.success(
                "Your Smoothie is ordered!",
                icon="✅"
            )

        except Exception as e:
            st.error("Something went wrong.")
            st.write(e)
