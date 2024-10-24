import streamlit as st
from database.airtable_manager import AirtableManager
import pandas as pd
from datetime import datetime

def delete_records(airtable, record_ids):
    try:
        for record_id in record_ids:
            airtable.delete_record(record_id)
        st.success(f"Successfully deleted {len(record_ids)} record(s)")
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting records: {str(e)}")

def update_status(airtable, record_ids):
    try:
        for record_id in record_ids:
            airtable.update_record(record_id, {"status": "Ativo"})
        st.success(f"Successfully updated {len(record_ids)} record(s) to 'Ativo'")
        st.rerun()
    except Exception as e:
        st.error(f"Error updating records: {str(e)}")
def show():
    # Custom CSS with improved table and image styling
    st.markdown("""
        <style>
        .stCheckbox {
            margin-right: 10px;
        }
        .stButton button {
            width: 100%;
        }
        .stDataFrame {
            margin-top: 20px;
            margin-bottom: 20px;
        }
        /* Increase image size and improve display */
        .stDataFrame img {
            min-width: 150px !important;
            min-height: 150px !important;
            width: 150px !important;
            height: 150px !important;
            object-fit: contain !important;
            border-radius: 5px;
        }
        /* Remove yellow warning icon */
        .element-container:has(img) .stMarkdown {
            display: none;
        }
        /* Improve table styling */
        .stDataFrame table {
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            border-radius: 5px;
            overflow: hidden;
        }
        .stDataFrame thead tr {
            background-color: #009879;
            color: #ffffff;
            text-align: left;
        }
        .stDataFrame td {
            padding: 12px 15px;
        }
        .stDataFrame tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        .stDataFrame tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Main title
    st.markdown("# 📋 Records Management")
    
    try:
        # Initialize Airtable manager
        airtable = AirtableManager()
        
        # Fetch records
        records = airtable.read_records()
        
        if not records:
            st.info("🔍 No records found in the database.")
            return
        
        # Top layout with controls
        col1, col2, col3 = st.columns([2, 8, 2])
        
        with col1:
            select_all = st.checkbox("Select All")
        
        with col2:
            search = st.text_input("🔍 Search:", placeholder="Search records...")
        
        with col3:
            st.button("🔄 Refresh", type="primary")
        
        # Convert records to DataFrame
        df = pd.DataFrame(records)
        record_ids = df['id'].tolist()
        df_new = pd.json_normalize(df['fields'])
        # Keep createdTime as datetime object instead of converting to string
        df_new['createdTime'] = pd.to_datetime(df['createdTime'])
        df_new = df_new.sort_values(by='createdTime', ascending=False).reset_index(drop=True)
        
        # Configure table columns with custom formatting
        col_config = {
            "select": st.column_config.CheckboxColumn(
                "Select",
                default=False,
                help="Select records"
            ),
            "status": st.column_config.Column(
                "Status",
                help="Record status",
                width="small",
            ),
            "createdTime": st.column_config.DatetimeColumn(
                "Created At",
                help="Record creation time",
                format="DD/MM/YYYY HH:mm",
                width="small",
            ),
            "titulo": st.column_config.TextColumn(
                "Title",
                help="Record title",
                width="medium",
            ),
            "de_prieco": st.column_config.NumberColumn(
                "Original Price",
                help="Original price",
                format="R$ %.2f",
                width="small",
            ),
            "para_price": st.column_config.NumberColumn(
                "Final Price",
                help="Final price",
                format="R$ %.2f",
                width="small",
            ),
            "desconto": st.column_config.NumberColumn(
                "Discount",
                help="Discount percentage",
                format="%.0f%%",
                width="small",
            ),
            "parcelas": st.column_config.NumberColumn(
                "Installments",
                help="Number of installments",
                width="small",
            ),
            "imagem": st.column_config.ImageColumn(
                "Image",
                help="Product image",
                width="small"
            )
        }
        
        # Prepare DataFrame with selected columns and order
        df = df_new[['status', 'createdTime', 'titulo', 'de_prieco', 
                     'para_price', 'desconto', 'parcelas', 'imagem']]
        
        # Add selection column
        df.insert(0, 'select', False)
        
        # Handle "Select All"
        if select_all:
            df['select'] = True
        
        # Show total records
        st.markdown(f"📊 **Total records: {len(df)}**")
        
        # Apply search filter if search term exists
        if search:
            # Search in multiple columns
            mask = (
                    df['titulo'].str.contains(search, case=False, na=False) |
                    df['status'].str.contains(search, case=False, na=False) |
                    df['createdTime'].str.contains(search, case=False, na=False)
            )
            df = df[mask]
            st.markdown(f"🔍 **Showing {len(df)} filtered results**")
        
        # Display editable table with custom styling
        with st.container():
            edited_df = st.data_editor(
                df,
                column_config=col_config,
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                key="data_editor",
                disabled=["imagem"]  # Disable image column editing to prevent warnings
            )
        
        # Handle selected records
        selected_records = edited_df[edited_df['select'] == True]
        
        if not selected_records.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Delete", type="secondary"):
                    selected_indices = selected_records.index.tolist()
                    selected_ids = [record_ids[i] for i in selected_indices]
                    delete_records(airtable, selected_ids)
            
            with col2:
                if st.button("✏️ Edit", type="secondary"):
                    selected_indices = selected_records.index.tolist()
                    selected_ids = [record_ids[i] for i in selected_indices]
                    update_status(airtable, selected_ids)
                    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
