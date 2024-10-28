import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from database.airtable_manager import AirtableManager
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TableConfig:
    COLUMNS = [
        'status', 'createdTime', 'data_envio', 'titulo', 'de_prieco',
        'para_price', 'desconto', 'parcelas', 'imagem'
    ]
    
    COLUMN_CONFIG = {
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
        "data_envio": st.column_config.DatetimeColumn(
            "Data Sent",
            help="Record data sending time",
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

class RecordManager:
    def __init__(self, airtable: AirtableManager):
        self.airtable = airtable

    def delete_records(self, record_ids: List[str]) -> None:
        try:
            for record_id in record_ids:
                self.airtable.delete_record(record_id)
            st.success(f"Successfully deleted {len(record_ids)} record(s)")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting records: {str(e)}")

    def update_status(self, record_ids: List[str]) -> None:
        try:
            for record_id in record_ids:
                self.airtable.update_record(record_id, {"status": "Ativo"})
            st.success(f"Successfully updated {len(record_ids)} record(s) to 'Ativo'")
            st.rerun()
        except Exception as e:
            st.error(f"Error updating records: {str(e)}")

    def create_record(self, record_data: Dict[str, Any]) -> None:
        try:
            self.airtable.create_record(record_data)
            st.success("Successfully created new record")
            st.rerun()
        except Exception as e:
            st.error(f"Error creating record: {str(e)}")

    def get_records(self) -> List[Dict[str, Any]]:
        try:
            return self.airtable.read_records()
        except Exception as e:
            st.error(f"Error getting records: {str(e)}")

class DataFrameManager:
    @staticmethod
    def create_dataframe(records: List[Dict[str, Any]]) -> tuple[pd.DataFrame, List[str]]:
        df = pd.DataFrame(records)
        record_ids = df['id'].tolist()
        df_new = pd.json_normalize(df['fields'])
        df_new['createdTime'] = pd.to_datetime(df['createdTime'])
        df_new['data_envio'] = pd.to_datetime(df_new.get('data_envio', pd.NaT))

        df = df_new[TableConfig.COLUMNS]
        df.insert(0, 'select', False)
        
        return df, record_ids

    @staticmethod
    def apply_search_filter(df: pd.DataFrame, search_term: str) -> pd.DataFrame:
        if not search_term:
            return df
            
        mask = (
            df['titulo'].str.contains(search_term, case=False, na=False) |
            df['status'].str.contains(search_term, case=False, na=False) |
            df['createdTime'].astype(str).str.contains(search_term, case=False, na=False) |
            df['data_envio'].astype(str).str.contains(search_term, case=False, na=False)
        )
        return df[mask]

class UI:
    CUSTOM_CSS = """
        <style>
        .stCheckbox { margin-right: 10px; }
        .stButton button { width: 100%; }
        .stDataFrame { margin: 20px 0; }
        .stDataFrame img {
            min-width: 150px !important;
            min-height: 150px !important;
            width: 150px !important;
            height: 150px !important;
            object-fit: contain !important;
            border-radius: 5px;
        }
        .element-container:has(img) .stMarkdown { display: none; }
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
        .stDataFrame td { padding: 12px 15px; }
        .stDataFrame tbody tr { border-bottom: 1px solid #dddddd; }
        .stDataFrame tbody tr:nth-of-type(even) { background-color: #f3f3f3; }
        </style>
    """

    @staticmethod
    def setup_page():
        st.markdown(UI.CUSTOM_CSS, unsafe_allow_html=True)
        st.markdown("# 📋 Records Management")

    @staticmethod
    def create_top_controls() -> tuple[bool, str]:
        col1, col2, col3 = st.columns([2, 8, 2])
        
        with col1:
            select_all = st.checkbox("Select All")
        
        with col2:
            search = st.text_input("🔍 Search:", placeholder="Search records...")
        
        with col3:
            st.button("🔄 Refresh", type="primary")
            
        return select_all, search

    @staticmethod
    def display_table(df: pd.DataFrame) -> pd.DataFrame:
        return st.data_editor(
            df,
            column_config=TableConfig.COLUMN_CONFIG,
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor",
            disabled=["imagem"]
        )

    @staticmethod
    def handle_selected_records(edited_df: pd.DataFrame, record_ids: List[str], record_manager: RecordManager):
        selected_records = edited_df[edited_df['select'] == True]
        
        if not selected_records.empty:
            col1, col2, _ = st.columns(3)
            selected_indices = selected_records.index.tolist()
            selected_ids = [record_ids[i] for i in selected_indices]
            
            with col1:
                if st.button("🗑️ Delete", type="secondary"):
                    record_manager.delete_records(selected_ids)
            
            with col2:
                if st.button("✏️ Altera Status", type="secondary"):
                    record_manager.update_status(selected_ids)

def show():
    try:
        UI.setup_page()
        airtable = AirtableManager()
        record_manager = RecordManager(airtable)
        
        records = airtable.read_records()
        if not records:
            st.info("🔍 No records found in the database.")
            return
            
        select_all, search = UI.create_top_controls()
        df, record_ids = DataFrameManager.create_dataframe(records)
        
        if select_all:
            df['select'] = True

        # Sort DataFrame by 'data_envio' in descending order (most recent first)
        df = df.sort_values(by='data_envio', ascending=False, na_position='last').reset_index(drop=True)
        
        st.markdown(f"📊 **Total records: {len(df)}**")
        
        # Apply search filter
        df = DataFrameManager.apply_search_filter(df, search)
        if search:
            st.markdown(f"🔍 **Showing {len(df)} filtered results**")
            
        with st.container():
            edited_df = UI.display_table(df)
            UI.handle_selected_records(edited_df, record_ids, record_manager)
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

