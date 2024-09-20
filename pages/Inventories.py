import streamlit as st
import pandas as pd
import io
from streamlit_extras.colored_header import colored_header

#function to extract table from inventory and disply in page

def extract_data(filename, sheet_name, item_name, columns, column_names):
    df = pd.read_excel(filename, sheet_name=sheet_name, header=None)
    line = df[df[1] == item_name].index

    line = line[0]

    line_amount = df[df[1] == "amount"].index
    line_amount = line_amount[line_amount > line][0]
    line_data = line_amount + 2
    table = []
    while True:
        try:
            value = df.iloc[line_data, 1]
            if pd.isnull(value):
                break
            pd.to_numeric(value)
        except (ValueError, TypeError):
            break

        values = [df.iloc[line_data, i] for i in columns]
        table.append(values)
        line_data += 1

    df_final = pd.DataFrame(table, columns=column_names)

    # Convert all columns to scientific notation
    pd.set_option('display.float_format', lambda x: '%.2e' % x)

    # Alternatively, if you only want to convert specific columns:
    for column in column_names:
        df_final[column] = df_final[column].apply(lambda x: format(x, '.2e') if isinstance(x, (int, float)) else x)

    return df_final

#Page content
st.set_page_config(layout="wide")
st.markdown("# Life Cycle Inventory - LCI")
colored_header(
    label="Foreground activities",
    description="",
    color_name="blue-70",
)


st.write('''The Life Cycle Assessment of hydrogen production is comprised of activities in the 
Foreground and Background. The Foreground corresponds to a list of materials and energy that 
make up the equipment and infrastructure necessary to produce hydrogen. Bellow these elements 
are detailed regarding corresponding activity name, amount, unit, and reference location of the inventory.''')

#Inventory downoad button
df_xlsx = pd.read_excel('electrolyzers_LCI.xlsx')

# Convert DataFrame to bytes-like object
excel_data = io.BytesIO()
df_xlsx.to_excel(excel_data, index=False)
excel_data.seek(0)

st.download_button(label='📥 Download inventory',
                   data=excel_data,
                   file_name='electrolyzers_LCI.xlsx',
                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#reference
#st.link_button(label='Inventory reference', url='https://doi.org/10.1016/j.est.2021.102759', help=None, type="secondary", disabled=False, use_container_width=False)
st.markdown("[Inventory reference](https://doi.org/10.1016/j.est.2021.102759)")

st.markdown("---")

st.markdown("**Proton Exchange Membrane - PEM**")

st.write('''PEM electrolyser systems were developed to overcome some of the operational drawbacks 
of alkaline electrolysers. They use pure water as an
electrolyte solution, and so avoid the recovery and recycling of the potassium hydroxide
electrolyte solution that is necessary with alkaline electrolysers. They are smaller than 
alkaline electrolysers and produce highly compressed hydrogen for decentralised production and storage at
refuelling stations (30–60 bar without an additional compressor and up to 100–200 bar in some
systems, compared to 1–30 bar for alkaline electrolysers). Their operating range can
go from zero load to 160% of design capacity (so it is possible to overload the electrolyser for
some time, if the plant and power electronics have been designed accordingly). Against this,
however, they need expensive electrode catalysts (platinum, iridium) and membrane materials,
and their lifetime is currently shorter than that of alkaline electrolysers. Their overall costs are
currently higher than those of alkaline electrolysers, and currently they are less widely deployed.''')

expander = st.expander("PEM electrolyzer")
#inserting table from excel
item_name = "electrolyzer production, 1MWe, PEM, Stack"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("Balance of Plant for PEM")
item_name = "electrolyzer production, 1MWe, PEM, Balance of Plant"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("iridium production")
item_name = "iridium production"
column_names = ["Name", "Amount", "Unit", "Category", "Type"]
columns = [0, 1, 3, 4, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("treatment of fuel cell stack PEM")
item_name = "treatment of fuel cell stack, 1MWe, PEM"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("treatment of balance of plant for PEM")
item_name = "treatment of fuel cell balance of plant, 1MWe, PEM"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)


st.markdown("---")

st.markdown("**Alkaline Electrolysis Cell - AEC**")

st.write('''Alkaline electrolysis is a mature and commercial technology. The operating
range of alkaline electrolysers goes from a minimum load of 10% to full design capacity. Several
alkaline electrolysers with a capacity of up to 165 megawatts electrical (MWe) were built in the
last century in countries with large hydropower resources (Canada, Egypt, India, Norway and
Zimbabwe), although almost all of them were decommissioned when natural gas and steam
methane reforming for hydrogen production took off in the 1970s. Alkaline electrolysis is
characterised by relatively low capital costs compared to other electrolyser technologies due to
the avoidance of precious materials.''')


expander = st.expander("AEC electrolyzer")
item_name = "electrolyzer production, 1MWe, AEC, Stack"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("Balance of Plant for AEC")
item_name = "electrolyzer production, 1MWe, AEC, Balance of Plant"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("treatment of fuel cell stack AEC")
item_name = "treatment of fuel cell stack, 1MWe, AEC"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)

expander = st.expander("treatment of balance of plant for AEC")
item_name = "treatment of fuel cell balance of plant, 1MWe, AEC"
column_names = ["Name", "Amount", "Location", "Unit", "Type"]
columns = [0, 1, 2, 3, 5]
df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
expander.table(df)



