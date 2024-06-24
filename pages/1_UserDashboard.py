import streamlit as st
import time
import numpy as np
import pandas as pd

st.set_page_config(page_title="User Dashboard", page_icon="📈")

st.markdown("# User Dashboard")
st.sidebar.header("User Dashboard")
# st.write(
#     """This demo illustrates a combination of plotting and animation with
# Streamlit. We're generating a bunch of random numbers in a loop for around
# 5 seconds. Enjoy!"""
# )

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)
st.header("Latest Non-Reviewed Records")
# df = pd.DataFrame(columns=['Address','age','color'])
data = {
        'Address': [
            'Ζαλόγγου 35, Κατερίνη, GR',
            'Μαρτίου 5, Κατερίνη, GR',
            'Ειρήνης 20, Κατερίνη, GR',
            'Οινόης 15, Κατερίνη, GR',
            'Μεγάλου Αλεξάνδρου 58, Κατερίνη, GR'
        ]
    }

df = pd.DataFrame(data, columns=['Address'])
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
config = {
    'Address' : st.column_config.TextColumn('Address', width='large', required=True)
    # 'age' : st.column_config.NumberColumn('Age (years)', min_value=0, max_value=122),
    # 'color' : st.column_config.SelectboxColumn('Favorite Color', options=colors)
}



result = st.data_editor(df, column_config = config, num_rows='dynamic')

# if st.button('Get results'):
#     st.write(result)
st.button("Edit Selected")

for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    # chart.add_rows(new_rows)
    progress_bar.progress(i)
    # last_rows = new_rows
    time.sleep(0.05)

progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
# st.button("Re-run")