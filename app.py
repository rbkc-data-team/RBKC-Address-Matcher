import streamlit as st
import pandas as pd
import asyncio
import os
import io
import logging
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import httpx
from dotenv import load_dotenv


st.set_page_config(page_title="ThemeFinder Tool", layout="wide")

st.title("RBKC Address Matcher")
st.markdown(  
    "<p style='font-size:16px; color:black;'>"
    "This is a tool designed as...."
    "</p>",  
    unsafe_allow_html=True  
)  
  
# Initialize logs list in session state
if "logs" not in st.session_state:
    st.session_state["logs"] = []

# Custom logging handler to append logs to session state
class StreamlitLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        st.session_state["logs"].append(log_entry)

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Remove all handlers associated with the root logger object.
for handler in logger.handlers[:]:
    logger.removeHandler(handler)
streamlit_handler = StreamlitLogHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
streamlit_handler.setFormatter(formatter)
logger.addHandler(streamlit_handler)

# File uploader for .csv and .xlsx
st.markdown("""  
**Input Data Requirements:**  
  
- The columns must be named **``** and **``** .  
 
""")  
uploaded_file = st.file_uploader("Upload your data file (.csv or .xlsx)", type=["csv", "xlsx"],
                                 help=" add text",
                                 label_visibility='visible')

# Inputs


load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("DEPLOYMENT_NAME")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
model = os.getenv("AZURE_GPT_MODEL")
model_version = os.getenv("AZURE_MODEL_VERSION")
api_version = os.getenv("OPENAI_API_VERSION")

process_button = st.button("Match Addresses")
st.markdown(  
    "<p style='font-size:15px; color:gray;'>"  
    "This can take a few minutes depending on the size of the dataset. A table will appear below when the process is finished."    
    "</p>",  
    unsafe_allow_html=True  
)  

if "results_df" not in st.session_state:
    st.session_state["results_df"] = None


def export_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Themes')
    processed_data = output.getvalue()
    return processed_data

async def ADD_python_function(params):
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )
    llm = AzureChatOpenAI(
        model=model,
        azure_deployment=deployment,
        model_version=model_version,
        azure_endpoint=endpoint,
        temperature=0.1,
        azure_ad_token_provider=token_provider,
        api_version=api_version,
        http_client=httpx.Client(verify=False),
        http_async_client=httpx.AsyncClient(verify=False),
        openai_api_key=api_key,
    )


    logger.info("Starting theme finding process...")
    
    # add whatever python function below
    #result = await some_function(some params)
    logger.info("Theme finding process completed.")
    return result
  



if process_button:
    # Clear previous logs on new run
    st.session_state["logs"] = []
    if uploaded_file is None:
        st.error("Please upload a data file first.")
    # elif not question:
    #     st.error("Please enter a question.")
    # elif not system_prompt:
    #     st.error("Please enter a system prompt.")
    

if st.session_state["results_df"] is not None:
    st.download_button(
        label="Download results as CSV",
        data=export_df_to_csv(st.session_state["results_df"]),
        file_name="themefinder_results.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Download results as Excel",
        data=export_df_to_excel(st.session_state["results_df"]),
        file_name="themefinder_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



# Display logs in a multiline text area after processing completes
st.subheader("Process Logs")
if st.session_state["logs"]:
    logs_text = "\n".join(st.session_state["logs"])
    st.text_area("Logs", value=logs_text, height=300)
else:
    st.write("No logs available yet.")
