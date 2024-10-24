import streamlit as st
import pandas as pd
from database.airtable_manager import AirtableManager
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def clean_discount(discount_str):
    """Extract numeric value from discount string"""
    try:
        return float(discount_str.split('%')[0])
    except:
        return 0

def show():
    # Custom CSS for better layout
    st.markdown("""
        <style>
        .stPlot {
            background-color: white;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main title
    st.markdown("# 📊 Analytics Dashboard")
    
    try:
        # Initialize Airtable manager and fetch data
        airtable = AirtableManager()
        records = airtable.read_records()
        
        if not records:
            st.info("🔍 No data available for analysis.")
            return
            
        # Convert records to DataFrame
        df = pd.DataFrame(records)
        df_new = pd.json_normalize(df['fields'])
        df_new['createdTime'] = pd.to_datetime(df['createdTime'])
        
        # Clean the discount field
        df_new['desconto'] = df_new['desconto'].apply(clean_discount)
        
        # Add date column - modified to show only day and month in descending order
        df_new['date'] = df_new['createdTime'].dt.strftime('%d/%m')
        
        # Calculate key metrics
        total_products = len(df_new)
        avg_discount = df_new['desconto'].mean()
        active_products = len(df_new[df_new['status'] == 'Ativo'])
        
        # Display metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <h3>Total Products</h3>
                    <h2>%d</h2>
                </div>
            """ % total_products, unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
                <div class="metric-card">
                    <h3>Average Discount</h3>
                    <h2>%.1f%%</h2>
                </div>
            """ % avg_discount, unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
                <div class="metric-card">
                    <h3>Active Products</h3>
                    <h2>%d</h2>
                </div>
            """ % active_products, unsafe_allow_html=True)
        
        st.markdown("### 📈 Daily Product Count")
        
        # Daily products chart - modified with sorting
        daily_counts = df_new.groupby('date').size().reset_index()
        daily_counts.columns = ['date', 'count']
        daily_counts = daily_counts.sort_values('date', ascending=False)  # Sort in descending order
        
        fig1 = px.line(daily_counts, 
                      x='date', 
                      y='count',
                      title='Products Added per Day',
                      labels={'count': 'Number of Products', 'date': 'Date'})
        fig1.update_traces(line_color='#009879')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Create two columns for secondary charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Price Distribution")
            
            # Price distribution chart
            fig2 = px.histogram(df_new, 
                              x='para_price',
                              nbins=20,
                              title='Price Distribution',
                              labels={'para_price': 'Price (R$)', 'count': 'Number of Products'})
            fig2.update_traces(marker_color='#009879')
            st.plotly_chart(fig2, use_container_width=True)
            
        with col2:
            st.markdown("### 📊 Status Distribution")
            
            # Status distribution pie chart
            status_counts = df_new['status'].value_counts()
            fig3 = px.pie(values=status_counts.values, 
                         names=status_counts.index,
                         title='Product Status Distribution')
            fig3.update_traces(marker=dict(colors=['#009879', '#34c3a8', '#75e1d0']))
            st.plotly_chart(fig3, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")
