import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Conexão do Community Cloud com o Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

my_dataframe = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_list = [
    row["FRUIT_NAME"]
    for row in my_dataframe.collect()
]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    st.subheader("Fruit Nutrition Information")

    fruit_to_check = ingredients_list[0]

    try:
        url = (
            "https://my.smoothiefroot.com/api/fruit/"
            + fruit_to_check
        )

        smoothiefroot_response = requests.get(
            url,
            timeout=10
        )

        if smoothiefroot_response.status_code == 200:
            st.dataframe(
                smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.warning(
                f"Nutrition information could not be found for {fruit_to_check}."
            )

    except requests.exceptions.RequestException as e:
        st.error("Could not connect to the nutrition API.")
        st.write(e)

    time_to_insert = st.button("Submit Order")

    if time_to_insert:

        if not name_on_order.strip():
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
                        name_on_order.strip()
                    ]
                ).collect()

                st.success(
                    "Your Smoothie is ordered!",
                    icon="✅"
                )

            except Exception as e:
                st.error("Something went wrong.")
                st.write(e)
