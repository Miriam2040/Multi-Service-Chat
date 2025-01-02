import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px


st.title("Cost Tracking Dashboard")

try:
    # Fetch cost data
    response = requests.get("http://localhost:8000/costs")
    costs = response.json()

    # Create dashboard layout
    main_metrics_col1, main_metrics_col2 = st.columns(2)

    # Main metrics
    with main_metrics_col1:
        total_cost = costs['total_cost']
        st.metric(
            "Total Cost",
            f"${total_cost:.2f}",
            help="Total cost of all content generation"
        )

    with main_metrics_col2:
        remaining = costs['remaining_budget']
        remaining_color = "normal" if remaining > 20 else "off"
        st.metric(
            "Remaining Budget",
            f"${remaining:.2f}",
            delta=None,
            delta_color=remaining_color,
            help="Remaining budget available"
        )

    # Budget usage progress bar
    st.subheader("Budget Usage")
    progress = (total_cost / (total_cost + remaining)) * 100
    st.progress(progress / 100, text=f"{progress:.1f}%")

    # Costs by type visualization
    st.subheader("Costs by Content Type")

    if costs['costs_by_type']:
        col1, col2 = st.columns(2)

        with col1:
            # Create pie chart
            df_costs = pd.DataFrame([
                {"Type": k, "Cost": v}
                for k, v in costs['costs_by_type'].items()
            ])

            fig = px.pie(
                df_costs,
                values='Cost',
                names='Type',
                title='Cost Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Create bar chart
            fig = px.bar(
                df_costs,
                x='Type',
                y='Cost',
                title='Costs by Type'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cost data available yet")

    # Recent transactions
    st.subheader("Recent Transactions")

    if costs['recent_costs']:
        # Convert to DataFrame for better display
        df_transactions = pd.DataFrame(costs['recent_costs'])

        # Format timestamp
        df_transactions['formatted_time'] = pd.to_datetime(
            df_transactions['timestamp']
        ).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Display as a styled table
        st.dataframe(
            df_transactions[['formatted_time', 'type', 'cost', 'prompt']],
            column_config={
                "formatted_time": st.column_config.TextColumn(
                    "Time",
                    width="medium"
                ),
                "type": st.column_config.TextColumn(
                    "Type",
                    width="small"
                ),
                "cost": st.column_config.NumberColumn(
                    "Cost",
                    format="$%.2f",
                    width="small"
                ),
                "prompt": st.column_config.TextColumn(
                    "Prompt",
                    width="large"
                ),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No transactions recorded yet")

except Exception as e:
    st.error(f"Error loading cost data: {str(e)}")

# Add some styling
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 18px;
    }
    .cost-table {
        font-size: 14px;
    }
    .stProgress > div > div > div > div {
        background-color: #00cc00;
    }
</style>
""", unsafe_allow_html=True)