from streamlit_extras.colored_header import colored_header
import lca_algebraic as agb
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import streamlit as st
from lib.settings import IMPACTS
from lib.utils import get_pv_prod_data, get_city_coordinates, init_once, display_params, compute_lca, \
    compute_intermediate, get_tooltip_html, get_js_code, get_css_code

def show():
  # Keep this import here
    st.set_page_config(layout="wide")

    init_once()

    st.markdown("# HySPI Calculator")

    colored_header(
        label="Foreground",
        description="Parameters extracted directly from your production plant",
        color_name="blue-70",
    )

    p = display_params()

    ir = compute_intermediate(p)

    # Add JavaScript and CSS to the page
    st.markdown(get_js_code(), unsafe_allow_html=True)
    st.markdown(get_css_code(), unsafe_allow_html=True)

    # Get tooltip HTML
    tooltip_html1, tooltip_html2 = get_tooltip_html()

    # Display tooltips
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'{tooltip_html1}', unsafe_allow_html=True)
        st.markdown(f'{tooltip_html2}', unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div style="padding: 5px; margin: 10px; border: 1px solid #cccccc; border-radius: 5px;"><b>Hydrogen production:</b> {ir.H2_year / 1000:.2f} t/year</div>',
            unsafe_allow_html=True)


    data = None  # Initialize data with a default value

    if p.renewable_coupling == "Yes":
        colored_header(
            label="Photovoltaic system",
            description="Select the location and PV capacity",
            color_name="blue-70",
        )

        st.session_state.setdefault("last_clicked", "")
        st.session_state.setdefault("latlon", "")
        st.session_state.setdefault("city_name", "")


        # Initialize OpenCage geocoder with your API key

        st.write("#### Enter a location or select one on the map")
        with st.container():
            col1, col2, col3= st.columns([1, 1, 1])


            with col1:
                city_name = st.text_input("Enter city name:", placeholder="Fos-sur-Mer")
                st.write("or")
                latlon = st.text_input("Enter latitude and longitude :",placeholder="e.g.: 43.4380, 4.9455", type="default")
                if latlon:
                    city_lat, city_lon = map(float, latlon.split(','))

            # Create a Folium map
            m = folium.Map(location=[46.903354, 2.088334], zoom_start=5)
            m.add_child(folium.LatLngPopup())

            if city_name:  # Check if city name is entered
                data = get_city_coordinates(city_name)
                if data:
                    folium.Marker(location=data).add_to(m)
                    #m.location=data in case we want to use for the rest of europe

            if latlon:  # Check if latitude and longitude are entered
                data = (city_lat, city_lon)
                folium.Marker(location=data).add_to(m)
                m.fit_bounds([data])

            with col2:
                # When the user interacts with the map
                map_data = st_folium(
                    m,
                    width = 270,
                    height=290,
                    key="folium_map"
                )

                if map_data.get("last_clicked"):
                    # Round the latitude and longitude to 4 decimal places
                    lat = round(map_data["last_clicked"]["lat"], 4)
                    lng = round(map_data["last_clicked"]["lng"], 4)

                    # Get the position using the rounded values
                    data = (lat, lng)

                    # Add the marker to the map
                    folium.Marker(location=data).add_to(m)

            col1.write("")
            col1.markdown(f'<div style="padding: 5px; margin: 10px; border: 1px solid #cccccc; border-radius: 5px;"><b>Location selected:</b> {data}</div>', unsafe_allow_html=True)

            col3.write("")
            pv_logo = "pv logo.png"
            col3.image(pv_logo, caption='', width= 200)
            col3.markdown("Solar radiation data was extracted from the PVGIS webapp. It consists of one value for every hour over a one year period. For more information consult:")
            col3.markdown("[PVGIS documentation](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/pvgis-user-manual_en)")

        if data is not None:

            col1, col2, col3 = st.columns([1, 1, 1])
            pv_cap_MW = col1.number_input("Select the PV farm capacity (MW):", value=5.0*p.electro_capacity_MW, min_value=0.1,
                                          max_value=1_000_000.0, step=0.1)
            pv_cap_kW=pv_cap_MW*1_000 #website requires pv capacity to be in kWp
            df = get_pv_prod_data(data[0], data[1], pv_cap_kW)


            # Sum of all elec_W figures
            TOTAL_elec_produced_Wh = df['elec_Wh'].sum()
            capped_values = df['elec_Wh'].clip(upper=ir.electro_capacity_W) #all values under electro_capacity_Wh
            hour_consumption_Wh = capped_values.sum()
            credit = TOTAL_elec_produced_Wh - hour_consumption_Wh #100% credit, all goes from PV to grid #change for surplus

            hours_year = 365 * 24
            necessary_elec_Wh = ir.electro_capacity_W * p.cf * hours_year  # here we add the capacity factor because this is related to electrolyzer's consumption
            grid = necessary_elec_Wh - hour_consumption_Wh #consumed from the grid
            pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh  #keeping this here as it helps to understand the situation in which all PV production is allocated to the impacts rather than the grig

            percentage_grid_hour = grid / necessary_elec_Wh
            percentage_pv_hour = 1 - percentage_grid_hour

            percentage_grid_hour = min(max(percentage_grid_hour, 0), 1)
            percentage_pv_hour= min(max(percentage_pv_hour, 0), 1)

            # monthly cap begins here:
            # Extract month and year part and create a new column
            df['YearMonth'] = df['DateTime'].dt.to_period('M')

            # Group by the month and sum the 'elec_Wh' values
            monthly_sums = df.groupby('YearMonth')['elec_Wh'].sum().reset_index()

            # Calculate the monthly maximum values based on the number of days in each month
            monthly_sums['days_in_month'] = monthly_sums['YearMonth'].dt.days_in_month
            monthly_sums['max_value'] = monthly_sums['days_in_month'] * 24 * ir.electro_capacity_W

            # Cap the monthly sums
            monthly_sums['Total_elec_Wh_month_capped'] = monthly_sums['elec_Wh'].clip(upper=monthly_sums['max_value'])

            # Calculate the difference
            monthly_sums['Difference'] = monthly_sums['elec_Wh'] - monthly_sums['Total_elec_Wh_month_capped']

            total_sum_hour_month_Wh = monthly_sums['Total_elec_Wh_month_capped'].sum()
            credit_minus_monthly_extra_Wh = monthly_sums['Difference'].sum()
            pv_credit_monthly_Wh = necessary_elec_Wh - total_sum_hour_month_Wh

            # daily cap begins here:
            # Extract date part and create a new column
            df['Date'] = df['DateTime'].dt.date

            # Group by the date and sum the 'elec_Wh' values
            daily_sums = df.groupby('Date')['elec_Wh'].sum().reset_index()
            daily_sums_24 = df.groupby('Date')['elec_Wh'].sum().reset_index() #here they are the same thing

            # Rename columns for clarity
            daily_sums.columns = ['Date', 'Total_elec_Wh_day']
            daily_sums_24.columns = ['Date', 'Total_elec_Wh_day_24'] #creating a new name for daily cap

            # Daily cap
            max_value = 24 * ir.electro_capacity_W

            daily_sums_24['Total_elec_Wh_day_24'] = daily_sums_24['Total_elec_Wh_day_24'].clip(upper=max_value) #capping value
            merged_df = pd.merge(daily_sums, daily_sums_24, on='Date')

            # Calculate the difference
            merged_df['Difference'] = merged_df['Total_elec_Wh_day'] - merged_df['Total_elec_Wh_day_24']

            # Created the new DataFrame with 'Date' and 'Difference'
            diff = merged_df[['Date', 'Difference']]

            diff.columns = ['Date', 'Total_elec_Wh_day_Difference']

            total_sum_hour_day_Wh = daily_sums_24['Total_elec_Wh_day_24'].sum()
            credit_minus_daily_extra_Wh = diff['Total_elec_Wh_day_Difference'].sum()
            pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh
            pv_credit_daily_Wh = necessary_elec_Wh - total_sum_hour_day_Wh


            battery_coupling = col2.selectbox("Battery coupled?", ["Yes", "No"], index=1)

            if battery_coupling == "No":
                gifb_path = 'H2b.gif'
                col3.image(gifb_path, use_column_width=True)

                col4, col2, col3 = st.columns([3, 1, 2])

                col4.write("##### Electricity per year:")
                col2.write("##### [KWh]")
                col3.write("##### Allocation options:")

                col4.write(f"Electrolyzer's total consumption: ")
                col2.write(f"{ir.Ec_MWh / p.BoP_LT_y:.2f}MWh")
                col4.write("PV production:")
                col2.markdown(f" {TOTAL_elec_produced_Wh / 1000000:.2f} MWh", unsafe_allow_html=True)
                col4.write("Electrolyzer's consumption from PV")
                col2.markdown(f" {hour_consumption_Wh / 1000000:.2f} MWh", unsafe_allow_html=True)

                if credit > 0:
                    col4.write("PV surplus production:")
                    col2.markdown(f" {credit / 1000000:.2f} MWh", unsafe_allow_html=True)
                    if credit - credit_minus_daily_extra_Wh > 0:
                        col4.write("PV surplus production (daily cap):")
                        col2.markdown(f"{(credit - credit_minus_daily_extra_Wh) / 1000000:.2f}MWh",
                                           unsafe_allow_html=True)
                    if credit - credit_minus_monthly_extra_Wh != 0:
                        col4.write("PV surplus production (monthly cap):")
                        col2.markdown(f"{(credit - credit_minus_monthly_extra_Wh) / 1000000:.2f}MWh",
                                      unsafe_allow_html=True)
            if battery_coupling == "Yes":
                gif_path = 'H2.gif'
                col3.image(gif_path, use_column_width=True)

                # Battery system
                battery_power_capacity_MW = col1.number_input("Battery power capacity (MW):", value=5.0, min_value=0.0,
                                                              step=0.1)
                battery_power_capacity_W = battery_power_capacity_MW * 1_000_000  # Convert to watts

                # Define storage capacity in Wh (20 MWh)
                battery_storage_capacity_MWh = col2.number_input("Battery storage capacity (MWh):", value=20.0,
                                                                 min_value=0.0, step=0.1)
                battery_storage_capacity_Wh = battery_storage_capacity_MWh * 1_000_000  # Convert to watt-hours

                eff_charge = 0.995
                eff_discharge = 0.995

                # Initialize battery state variables
                battery_stored_Wh = 0
                total_elec_sent_to_battery_Wh = 0
                total_elec_consumed_from_battery_Wh = 0
                send_to_grid = 0

                # Initialize DataFrame for adjusted daily sums
                df['Date'] = df['DateTime'].dt.date
                daily_sums = df.groupby('Date')['elec_Wh'].sum().reset_index()
                daily_sums['Adjusted_elec_Wh_day'] = daily_sums['elec_Wh']  # Initialize with the same value

                # Process each row to manage battery charging/discharging
                for index, row in df.iterrows():
                    date = row['Date']
                    surplus_Wh = row['elec_Wh'] - ir.electro_capacity_W
                    if surplus_Wh > 0:
                        # Charge the battery with surplus electricity
                        available_to_charge_Wh = min(surplus_Wh, battery_power_capacity_W,
                                                     battery_storage_capacity_Wh - battery_stored_Wh)
                        charged_Wh = available_to_charge_Wh * eff_charge
                        battery_stored_Wh += charged_Wh
                        total_elec_sent_to_battery_Wh += available_to_charge_Wh
                        daily_sums.loc[daily_sums['Date'] == date, 'Adjusted_elec_Wh_day'] += charged_Wh
                        send_to_grid = surplus_Wh - available_to_charge_Wh
                    else:
                        # Discharge the battery if there is no PV production
                        required_from_battery_Wh = min(-surplus_Wh, battery_power_capacity_W,
                                                       battery_stored_Wh)
                        discharged_Wh = required_from_battery_Wh * eff_discharge
                        battery_stored_Wh -= required_from_battery_Wh
                        total_elec_consumed_from_battery_Wh += discharged_Wh

                # Calculate efficiency losses
                efficiency_losses_Wh = total_elec_sent_to_battery_Wh - total_elec_consumed_from_battery_Wh

                col4, col2, col3 = st.columns([3, 1, 2])

                col4.write("##### Electricity per year:")
                col2.write("##### [MWh]")
                col3.write("##### Allocation options:")

                col4.write(f"Electrolyzer's total consumption: ")
                col2.write(f"{ir.Ec_MWh / p.BoP_LT_y:.2f}")
                col4.write("PV production:")
                col2.markdown(f" {TOTAL_elec_produced_Wh / 1000000:.2f}", unsafe_allow_html=True)
                col4.write("Electrolyzer's consumption from PV:")
                col2.markdown(f" {hour_consumption_Wh / 1000000:.2f}", unsafe_allow_html=True)
                col4.write("Electrolyzer's consumption from PV + battery:")
                col2.markdown(f" {(hour_consumption_Wh + total_elec_consumed_from_battery_Wh) / 1000000:.2f}",
                              unsafe_allow_html=True)
                # col4.write(f"Electricity sent to the battery:")
                # col2.write(f"{total_elec_sent_to_battery_Wh / 1000000:.2f}")
                col4.write(f"Electricity consumed from the battery:")
                col2.write(f"{total_elec_consumed_from_battery_Wh / eff_charge / 1_000_000: .2f}")
                # col4.write(f"Efficiency losses:")
                # col2.write(f"{efficiency_losses_Wh / 1_000_000: .2f}")

                # Updating percentages:
                grid = necessary_elec_Wh - (
                        hour_consumption_Wh + total_elec_consumed_from_battery_Wh)  # now the electricity used from PV gets an increment from battery

                percentage_grid_hour = grid / necessary_elec_Wh
                percentage_pv_hour = 1 - percentage_grid_hour

                percentage_grid_hour = min(max(percentage_grid_hour, 0), 1)
                percentage_pv_hour = min(max(percentage_pv_hour, 0), 1)

                # Adjust daily sums to include battery storage and apply daily cap
                daily_sums_24 = daily_sums.copy()
                daily_sums_24['Adjusted_elec_Wh_day'] = daily_sums_24['Adjusted_elec_Wh_day'].clip(upper=max_value)

                # Calculate the difference
                daily_sums['Difference'] = daily_sums['Adjusted_elec_Wh_day'] - daily_sums_24['Adjusted_elec_Wh_day']

                # Create the new DataFrame with 'Date' and 'Difference'
                diff = daily_sums[['Date', 'Difference']]

                # New column names
                diff.columns = ['Date', 'Total_elec_Wh_day_Difference']

                total_sum_hour_day_Wh = daily_sums_24['Adjusted_elec_Wh_day'].sum()
                credit_minus_daily_extra_Wh = diff['Total_elec_Wh_day_Difference'].sum()
                pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh
                pv_credit_daily_Wh = necessary_elec_Wh - total_sum_hour_day_Wh

                # Monthly cap begins here:
                df['YearMonth'] = df['DateTime'].dt.to_period('M')

                # Group by the month and sum the 'elec_Wh' values
                monthly_sums = df.groupby('YearMonth')['elec_Wh'].sum().reset_index()

                # Calculate the monthly maximum values based on the number of days in each month
                monthly_sums['days_in_month'] = monthly_sums['YearMonth'].dt.days_in_month
                monthly_sums['max_value'] = monthly_sums['days_in_month'] * 24 * ir.electro_capacity_W

                # Cap the monthly sums
                monthly_sums['Total_elec_Wh_month_capped'] = monthly_sums['elec_Wh'].clip(
                    upper=monthly_sums['max_value'])

                # Calculate the difference
                monthly_sums['Difference'] = monthly_sums['elec_Wh'] - monthly_sums['Total_elec_Wh_month_capped']

                total_sum_hour_month_Wh = monthly_sums['Total_elec_Wh_month_capped'].sum()
                credit_minus_monthly_extra_Wh = monthly_sums['Difference'].sum()
                pv_credit_monthly_Wh = necessary_elec_Wh - total_sum_hour_month_Wh

            with col3:
                col1, col2 = st.columns([3, 1])

                # Display text and calculated percentages
                with col1:
                    if TOTAL_elec_produced_Wh != hour_consumption_Wh:
                        st.write(":blue-background[Grid - yearly PV credit:]")
                        st.write(":blue-background[PV + yearly PV credit:]")
                    if credit - credit_minus_monthly_extra_Wh != 0:
                        st.write(":gray-background[Grid - monthly PV credit:]")
                        st.write(":gray-background[PV + monthly PV credit:]")
                    if credit - credit_minus_daily_extra_Wh != 0:
                        st.write(":blue-background[Grid - daily PV credit:]")
                        st.write(":blue-background[PV + daily PV credit:]")
                    st.write(":gray-background[Grid - hourly PV credit:]")
                    st.write(":gray-background[PV - hourly PV credit:]")

                with col2:
                    percentage_grid_year = pv_credit_Wh / necessary_elec_Wh
                    percentage_pv_year = 1 - percentage_grid_year

                    plot_percentage_grid_year = min(max(percentage_grid_year, 0), 1)
                    plot_percentage_pv_year = min(max(percentage_pv_year, 0), 1)

                    if TOTAL_elec_produced_Wh != hour_consumption_Wh:
                        st.write(f'{percentage_grid_year:.2%}', unsafe_allow_html=True)
                        st.write(f'{percentage_pv_year:.2%}', unsafe_allow_html=True)

                    percentage_grid_month = pv_credit_monthly_Wh / necessary_elec_Wh
                    percentage_pv_month = 1 - percentage_grid_month

                    plot_percentage_grid_month = min(max(percentage_grid_month, 0), 1)
                    plot_percentage_pv_month = min(max(percentage_pv_month, 0), 1)

                    if credit - credit_minus_monthly_extra_Wh != 0:
                        st.write(f'{percentage_grid_month:.2%}', unsafe_allow_html=True)
                        st.write(f'{percentage_pv_month:.2%}', unsafe_allow_html=True)

                    percentage_grid_day = pv_credit_daily_Wh / necessary_elec_Wh
                    percentage_pv_day = 1 - percentage_grid_day

                    percentage_grid_day = min(max(percentage_grid_day, 0), 1)
                    percentage_pv_day = min(max(percentage_pv_day, 0), 1)

                    if credit - credit_minus_daily_extra_Wh != 0:
                        st.write(f'{percentage_grid_day:.2%}', unsafe_allow_html=True)
                        st.write(f'{percentage_pv_day:.2%}', unsafe_allow_html=True)

                    st.write(f'{percentage_grid_hour:.2%}', unsafe_allow_html=True)
                    st.write(f'{percentage_pv_hour:.2%}', unsafe_allow_html=True)

            allocation = col3.selectbox("Electricity Allocation cap",
                                      ["Annual", "Monthly", "Daily", "Hourly"], index=2)
            if allocation == "Annual":
                percentage_grid = percentage_grid_year
                percentage_pv = percentage_pv_year
            if allocation == "Monthly":
                percentage_grid = percentage_grid_month
                percentage_pv = percentage_pv_month
            if allocation == "Daily":
                percentage_grid = percentage_grid_day
                percentage_pv = percentage_pv_day
            if allocation == "Hourly":
                percentage_grid = percentage_grid_hour
                percentage_pv = percentage_pv_hour

            # Prepare data for plotting
            data = {
                'Category': ['Year', 'Month', 'Day', 'Hour'],
                'Grid': [plot_percentage_grid_year, plot_percentage_grid_month, percentage_grid_day,
                         percentage_grid_hour],
                'PV': [plot_percentage_pv_year, plot_percentage_pv_month, percentage_pv_day, percentage_pv_hour]
            }

            df = pd.DataFrame(data)

            # Plot the data using matplotlib
            fig, ax = plt.subplots(figsize=(5,3))

            # Plot stacked bar graph
            bar_width = 0.35
            bar1 = ax.bar(df['Category'], df['Grid'], bar_width, label='Grid', color='#7E868E')
            bar2 = ax.bar(df['Category'], df['PV'], bar_width, bottom=df['Grid'], label='PV', color='#FFBE18')

            # Add labels and title
            ax.set_xlabel('Category')
            ax.set_ylabel('Percentage')
            ax.set_title('Grid and PV Percentages')
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.tight_layout()

            # Display the plot in Streamlit
            col4.pyplot(fig)

    #Indication for background before the data
    colored_header(
        label="Background",
        description="Electricity scenarios 2050",
        color_name="blue-70",
    )

    p.grid_market = st.radio("**Grid electricity market**",options=["FR2023", "DE2023", "ES2023"],key="grid electricity", horizontal=True)


    if data is not None and st.button("Compute result"):
        pass

    elif data is None and st.button("Compute result"):
        percentage_pv=0
        percentage_grid=1

    else:
        st.stop()

    #Results indication before code
    st.markdown("---")
    st.markdown("## Results")
    st.markdown("#### Hydrogen Environmental Impact")
    st.markdown("###### Functional unit: 1kg of Hydrogen produced")#verify the option to switch fu
    st.markdown("###### Method: EF v3.0 no LT")

    lca_result, system, production = compute_lca(p, ir, percentage_grid, percentage_pv)

    # Check if 'stored_results' exists in session state, if not, initialize it
    if 'stored_results' not in st.session_state:
        st.session_state.stored_results = pd.DataFrame()

    # Append the new results to the stored results
    st.session_state.stored_results = pd.concat([st.session_state.stored_results, lca_result], axis=0)

    st.session_state.counter += 1 #update result name order

    # Transpose the stored results for display
    transposed_table = st.session_state.stored_results.transpose()

    # Display the transposed DataFrame
    st.table(transposed_table)

    with st.container():
        paragraph = (
            f"The estimated electricity consumption throughout the plant's lifetime is {ir.Ec_GWh:.2f} GWh.\n\n"
            f"The total hydrogen production throughout the plant's lifetime is projected to be {ir.H2p_ton:.2f} tons.\n\n"
            f"The hydrogen production rate is approximately {ir.H2_per_hour:.2f} kg per hour.\n\n"
            f"Approximately {ir.E1:.2f} kWh of electricity is required to produce 1 kg of hydrogen.\n\n"
        )

        # Display the combined paragraph
        st.info(paragraph)

    st.markdown("---")


    st.table(agb.exploreImpacts(IMPACTS[0],
                       system,
                       ))
    st.table(agb.exploreImpacts(IMPACTS[0],
                                production,
                                ))

if __name__ == "__main__":
    show()
