import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from database.airtable_manager import AirtableManager
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TableConfig:
    COLUMNS = [
        'status', 'data_envio', 'titulo', 'de_preconew',
        'para_preco', 'cupom', 'parcelas', 'imagem', 'id'
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
        "data_envio": st.column_config.TextColumn(
            "Data Sent",
            help="Record data sending time",
            width="small",
        ),        
        "titulo": st.column_config.TextColumn(
            "Title",
            help="Record title",
            width="medium",
        ),
        "de_preconew": st.column_config.NumberColumn(
            "Original Price",
            help="Original price",
            format="R$ %.2f",
            width="small",
        ),
        "para_preco": st.column_config.NumberColumn(
            "Final Price",
            help="Final price",
            format="R$ %.2f",
            width="small",
        ),
        "cupom": st.column_config.NumberColumn(
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
                self.airtable.update_record(record_id, {
                    "status": "ativo"
                })
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

    def check_duplicate_link(self, link: str, df: pd.DataFrame) -> bool:
        return (
            (df['link_produto'] == link).any() or
            (df['link_outrosafiliados'] == link).any() or
            (df['link_curtoml'] == link).any()
        )

    def create_link_record(self, link: str, link_type: str, cupom: str) -> None:
        #current_time = datetime.now().strftime("%d/%m/%Y, %H:%M")
        record_data = {
            "status": "pendente",
            #"data_envio": current_time,
            "cupom": cupom
        }
        
        if link_type == "Link de Outros Afialidos/Meu Link":
            record_data["link_outrosafiliados"] = link
        elif link_type == "Link Curto MercadoLivre":
            record_data["link_curtoml"] = link
        else:
            record_data["link_produto"] = link
            
        self.create_record(record_data)

    def convert_to_brasilia_time(timestamp):
        if timestamp.tzinfo is None:
            return timestamp.tz_localize('UTC').tz_convert('America/Sao_Paulo')
        else:
            return timestamp.tz_convert('America/Sao_Paulo')

class DataFrameManager:
    @staticmethod
    def create_dataframe_links(records: List[Dict[str, Any]]) -> tuple[pd.DataFrame, List[str]]:
        df = pd.DataFrame(records)
        record_ids = df['id'].tolist()
        df_new = pd.json_normalize(df['fields'])
        df_new['id'] = df['id']
        df_new['data_envio'] = pd.to_datetime(df_new["data_envio"], errors='coerce').apply(RecordManager.convert_to_brasilia_time)
        df_new['data_envio'] = df_new['data_envio'].dt.strftime("%d/%m/%Y, %H:%M")
        df_new['CreatedTime'] = pd.to_datetime(df_new["CreatedTime"], errors='coerce').apply(RecordManager.convert_to_brasilia_time)
        df_new['CreatedTime'] = df_new['CreatedTime'].dt.strftime("%d/%m/%Y, %H:%M")
        return df_new, record_ids

    @staticmethod
    def create_dataframe(records: List[Dict[str, Any]]) -> tuple[pd.DataFrame, List[str]]:
        df = pd.DataFrame(records)
        record_ids = df['id'].tolist()
        df_new = pd.json_normalize(df['fields'])
        df_new['id'] = df['id']
        df_new['data_envio'] = pd.to_datetime(df_new["data_envio"], errors='coerce').apply(RecordManager.convert_to_brasilia_time)
        df_new['data_envio'] = df_new['data_envio'].dt.strftime("%d/%m/%Y, %H:%M")

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
            df['data_envio'].str.contains(search_term, case=False, na=False)
        )
        return df[mask]

def create_record_form():
    with st.form("record_form"):
        genre = st.radio(
            "Qual tipo de Link",
            ["Link de Outros Afialidos/Meu Link", "Link Curto MercadoLivre", "Link do Produtos"]
        )
        links = st.text_input("Informe o link")
        cupom = st.text_input("Cupom")
        submitted = st.form_submit_button("Criar Registro")
        if submitted:
            record_data = {
                "links": links,
                "cupom": cupom,
                "tipo_link": genre
            }
            return record_data
    return None

def edit_record_form(record_data):
    with st.form("edit_form"):
        titulo = st.text_input("Título", value=record_data.get("titulo", ""))
        links = st.text_input("Link", value=record_data.get("links", ""))
        col1, col2 = st.columns(2)
        with col1:
            de_preco = st.number_input("Preço Original", value=float(record_data.get("de_preco", 0.0)))
            cupom = st.text_input("Desconto %", value=record_data.get("cupom", ""))
        with col2:
            para_preco = st.number_input("Preço Final", value=float(record_data.get("para_preco", 0.0)))
            parcelas = st.text_input("Parcelas", value=record_data.get("parcelas", ""))
        
        imagem = st.text_input("URL da Imagem", value=record_data.get("imagem", ""))
        status = st.selectbox("Status", ["pendente", "ativo", "inativo"], index=["pendente", "ativo", "inativo"].index(record_data.get("status", "pendente")))
        
        submitted = st.form_submit_button("Atualizar Registro")
        if submitted:
            updated_data = {
                "links": links,
                "titulo": titulo,
                "de_preco": de_preco,
                "para_preco": para_preco,
                "cupom": cupom,
                "parcelas": parcelas,
                "imagem": imagem,
                "status": status,
            }
            return updated_data
    return None

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
            selected_indices = selected_records['id']            
            with col1:
                if st.button("🗑️ Delete", type="secondary"):
                    record_manager.delete_records(selected_indices)

            with col2:
                if st.button("✏️ Altera Status", type="secondary"):
                    record_manager.update_status(selected_indices)

def show():
    try:
        UI.setup_page()
        airtable = AirtableManager()
        record_manager = RecordManager(airtable)
        airtable_links = AirtableManager(table_name="links")
        links_manager = RecordManager(airtable_links)

        tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "🖼️ Links", "➕ Novo", "✏️ Editar"])
        
        with tab1:
            records = airtable.read_records()
            records_links = airtable_links.read_records()
            df_links, record_ids_links = DataFrameManager.create_dataframe_links(records_links)

            if not records:
                st.info("🔍 No records found in the database.")
                return
                
            select_all, search = UI.create_top_controls()
            df, record_ids = DataFrameManager.create_dataframe(records)
            
            if select_all:
                df['select'] = True
            df = df.sort_values(by='data_envio', ascending=False, na_position='last').reset_index(drop=True)
            df = df[['select','status', 'data_envio','titulo','cupom', 'de_preconew', 'para_preco', 'imagem', 'id']]
            
            st.markdown(f"📊 **Total records: {len(df)}**")
            df = DataFrameManager.apply_search_filter(df, search)
            if search:
                st.markdown(f"🔍 **Showing {len(df)} filtered results**")
                
            with st.container():
                edited_df = UI.display_table(df)
                UI.handle_selected_records(edited_df, record_ids, record_manager)

        with tab2:
            df_links['data_envio'] = pd.to_datetime(df_links["data_envio"],format='%d/%m/%Y, %H:%M')
            df_links['CreatedTime'] = pd.to_datetime(df_links["data_envio"],format='%d/%m/%Y, %H:%M')
            df_links = df_links.sort_values(by='data_envio', ascending=False, na_position='last').reset_index(drop=True)
            df_links = df_links[['link_afiliado', 'status', 'cupom', 'data_envio','CreatedTime']]
            st.title("🔗 Links")
            st.dataframe(df_links)

        with tab3:
            new_record = create_record_form()
            if new_record:
                df_links, _ = DataFrameManager.create_dataframe_links(airtable_links.read_records())
                if links_manager.check_duplicate_link(new_record['links'], df_links):
                    st.error("Este link já existe na base de dados!")
                else:
                    links_manager.create_link_record(
                        new_record['links'],
                        new_record['tipo_link'],
                        new_record['cupom']
                    )
                    
        with tab4:
            record_id = st.selectbox("Selecione o registro para editar", 
                                   options=df['id'].tolist(),
                                   format_func=lambda x: df[df['id'] == x]['titulo'].iloc[0])
            if record_id:
                record_data = df[df['id'] == record_id].iloc[0].to_dict()
                updated_data = edit_record_form(record_data)
                if updated_data:
                    record_manager.airtable.update_record(record_id, updated_data)
                    st.success("Registro atualizado com sucesso!")
                    st.rerun()
                    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    show()