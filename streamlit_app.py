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

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # -----------------------------------------
    # INFORMAÇÕES NUTRICIONAIS - API
    # -----------------------------------------

    st.subheader("Fruit Nutrition Information")

    fruit_to_check = ingredients_list[0]

    try:

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_to_check,
            timeout=10
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

    except requests.exceptions.RequestException as e:

        st.error("Could not connect to the nutrition API.")
        st.write(e)

    # -----------------------------------------
    # ENVIAR PEDIDO
    # -----------------------------------------

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        if not name_on_order:

            st.warning("Please enter a name for your Smoothie.")

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

                st.error("Something went wrong.")
                st.write(e)
import requests  
smoothiefroot_response = requests.get("[https://my.smoothiefroot.com/api/fruit/watermelon](https://my.smoothiefroot.com/api/fruit/watermelon)")  
st.text(smoothiefroot_response)
