import streamlit as st
import requests
import json
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Log Analysis RAG System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match HTML styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #9333ea;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #7e22ce;
    }
    .success-message {
        background-color: #f3e8ff;
        color: #7c3aed;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c4b5fd;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #fee2e2;
        color: #dc2626;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #fca5a5;
        margin: 1rem 0;
    }
    .info-message {
        background-color: #dbeafe;
        color: #2563eb;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #93c5fd;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'project_id' not in st.session_state:
    st.session_state.project_id = ""
if 'last_file_id' not in st.session_state:
    st.session_state.last_file_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_workflow_id' not in st.session_state:
    st.session_state.current_workflow_id = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

# API Configuration
API_BASE = os.getenv("API_BASE_URL", "http://4.232.170.195/")
WS_BASE = os.getenv("WS_BASE_URL", "ws://4.232.170.195/")

# Chunking method descriptions
CHUNKING_METHODS = {
    "log_hybrid_adaptive": "Hybrid Adaptive - Best for general analysis",
    "log_hybrid_intelligent": "Hybrid Intelligent - Context-aware splitting",
    "log_time_window": "Time Window - Group by time periods",
    "log_error_block": "Error Block - Group errors together",
    "log_component_based": "Component Based - Group by IP/source",
    "log_semantic_sliding": "Semantic Sliding - Context window with overlap"
}

def make_request(method, endpoint, **kwargs):
    """Helper function to make API requests"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        return response
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

# Header
st.markdown('<div class="main-header">📊 Log Analysis RAG System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent log file processing and retrieval-augmented generation</div>', unsafe_allow_html=True)

# Sidebar for Project Configuration
with st.sidebar:
    st.header("⚙️ Project Configuration")
    project_id = st.text_input(
        "Project ID",
        value=st.session_state.project_id,
        placeholder="e.g., logs_2024_01",
        help="Project identifier for log analysis workspace"
    )
    st.session_state.project_id = project_id
    
    st.markdown("---")
    st.markdown("### 📡 API Configuration")
    api_url = st.text_input("API Base URL", value=API_BASE)
    if api_url != API_BASE:
        API_BASE = api_url

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Upload & Process", "ℹ️ Index Info", "📊 Dashboard", "🔍 Search Logs", "🤖 AI Assistant"])

with tab1:
    st.header("Upload & Process Log Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Upload Log Files")
        uploaded_file = st.file_uploader(
            "Select log file (.txt, .log, .pdf)",
            type=['txt', 'log', 'pdf'],
            help="Upload your log file for analysis"
        )
        
        if uploaded_file is not None:
            st.info(f"Selected: {uploaded_file.name}")
        
        if st.button("Upload File", type="primary", disabled=not project_id or not uploaded_file):
            if not project_id:
                st.error("Please enter a Project ID first")
            elif not uploaded_file:
                st.error("Please select a file to upload")
            else:
                with st.spinner("Uploading file..."):
                    try:
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = make_request("POST", f"api/v1/data/upload/{project_id}", files=files)
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            st.session_state.last_file_id = data.get("file_id")
                            st.success(f"✅ File uploaded successfully! ID: {st.session_state.last_file_id}")
                        else:
                            error_msg = response.json().get("detail", "Upload failed") if response else "Connection error"
                            st.error(f"❌ Upload failed: {error_msg}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.subheader("2️⃣ Process & Index")
        
        chunking_method = st.selectbox(
            "Log Chunking Strategy",
            options=list(CHUNKING_METHODS.keys()),
            format_func=lambda x: CHUNKING_METHODS[x],
            index=0
        )
        
        col_chunk, col_overlap, col_reset = st.columns(3)
        with col_chunk:
            chunk_size = st.number_input("Chunk Size", min_value=1, value=100, step=10)
        with col_overlap:
            overlap_size = st.number_input("Overlap", min_value=0, value=20, step=5)
        with col_reset:
            do_reset = st.selectbox("Reset Index", options=["Yes", "No"], index=0)
        
        if st.button("Start Processing", type="primary", disabled=not project_id or not st.session_state.last_file_id or st.session_state.is_processing):
            if not project_id:
                st.error("Please enter a Project ID first")
            elif not st.session_state.last_file_id:
                st.error("Please upload a file first")
            else:
                st.session_state.is_processing = True
                with st.spinner("Starting processing..."):
                    try:
                        payload = {
                            "chunk_size": chunk_size,
                            "overlap_size": overlap_size,
                            "do_reset": 1 if do_reset == "Yes" else 0,
                            "file_id": st.session_state.last_file_id,
                            "chunking_method": chunking_method
                        }
                        response = make_request("POST", f"api/v1/data/process-and-push/{project_id}", json=payload)
                        
                        if response and response.status_code == 200:
                            data = response.json()
                            st.session_state.current_workflow_id = data.get("workflow_task_id")
                            st.success(f"✅ Processing started! Workflow ID: {st.session_state.current_workflow_id[:8]}...")
                            
                            # Show progress
                            progress_placeholder = st.empty()
                            status_placeholder = st.empty()
                            
                            while st.session_state.is_processing:
                                progress_response = make_request("GET", f"api/v1/data/workflow-progress/{st.session_state.current_workflow_id}")
                                if progress_response and progress_response.status_code == 200:
                                    progress_data = progress_response.json()
                                    status = progress_data.get("status", "PENDING")
                                    overall_progress = progress_data.get("overall_progress", 0)
                                    message = progress_data.get("message", "Processing...")
                                    
                                    progress_placeholder.progress(overall_progress / 100)
                                    status_placeholder.info(f"Status: {status} - {message} ({overall_progress}%)")
                                    
                                    if status in ["SUCCESS", "FAILURE"]:
                                        st.session_state.is_processing = False
                                        if status == "SUCCESS":
                                            st.success("✅ Processing complete! Your data is ready for querying.")
                                        else:
                                            st.error(f"❌ Processing failed: {progress_data.get('error_message', 'Unknown error')}")
                                        break
                                
                                time.sleep(2)
                        else:
                            error_msg = response.json().get("detail", "Processing failed") if response else "Connection error"
                            st.error(f"❌ Processing failed: {error_msg}")
                            st.session_state.is_processing = False
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.session_state.is_processing = False

with tab2:
    st.header("Index Information")
    
    if st.button("Refresh Index Information", type="primary", disabled=not project_id):
        if not project_id:
            st.error("Please enter a Project ID first")
        else:
            with st.spinner("Loading index information..."):
                response = make_request("GET", f"api/v1/nlp/index/info/{project_id}")
                
                if response and response.status_code == 200:
                    data = response.json()
                    collection_info = data.get("collection_info", {})
                    table_info = collection_info.get("table_info", {})
                    record_count = collection_info.get("record_count", 0)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Database Table", table_info.get("tablename", "N/A"))
                    with col2:
                        st.metric("Indexed Records", f"{record_count:,}")
                else:
                    error_msg = response.json().get("detail", "Collection not found") if response else "Connection error"
                    st.error(f"❌ {error_msg}")

with tab3:
    st.header("Dashboard")
    
    if st.button("Load Dashboard", type="primary", disabled=not project_id or not st.session_state.last_file_id):
        if not project_id:
            st.error("Please enter a Project ID first")
        elif not st.session_state.last_file_id:
            st.error("Please upload and process a file first")
        else:
            with st.spinner("Loading dashboard data..."):
                response = make_request("GET", f"api/v1/data/eda/{project_id}/{st.session_state.last_file_id}")
                
                if response and response.status_code == 200:
                    data = response.json()
                    
                    if "error" in data:
                        st.error(f"❌ {data['error']}")
                    else:
                        metrics = data.get("metrics", {})
                        charts = data.get("charts", {})
                        
                        # Metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Requests", f"{metrics.get('total_requests', 0):,}")
                        with col2:
                            st.metric("Unique Visitors", f"{metrics.get('unique_visitors', 0):,}")
                        with col3:
                            st.metric("Bandwidth", f"{metrics.get('total_bandwidth_mb', 0)} MB")
                        with col4:
                            st.metric("Error Rate", f"{metrics.get('error_rate', 0)}%")
                        
                        st.markdown("---")
                        
                        # Charts
                        col_chart1, col_chart2 = st.columns(2)
                        
                        with col_chart1:
                            # Traffic Over Time
                            if "traffic_over_time" in charts:
                                fig_traffic = go.Figure()
                                fig_traffic.add_trace(go.Scatter(
                                    x=charts["traffic_over_time"]["labels"],
                                    y=charts["traffic_over_time"]["values"],
                                    mode='lines+markers',
                                    name='Traffic',
                                    line=dict(color='#9333ea', width=2),
                                    fill='tonexty'
                                ))
                                fig_traffic.update_layout(
                                    title="Traffic Over Time",
                                    xaxis_title="Time",
                                    yaxis_title="Requests",
                                    height=400
                                )
                                st.plotly_chart(fig_traffic, use_container_width=True)
                            
                            # Status Codes
                            if "status_counts" in charts:
                                status_labels = list(charts["status_counts"].keys())
                                status_values = list(charts["status_counts"].values())
                                fig_status = go.Figure(data=[go.Pie(
                                    labels=status_labels,
                                    values=status_values,
                                    hole=0.4,
                                    marker_colors=['#9333ea', '#3b82f6', '#10b981', '#ef4444']
                                )])
                                fig_status.update_layout(
                                    title="Status Codes Distribution",
                                    height=400
                                )
                                st.plotly_chart(fig_status, use_container_width=True)
                        
                        with col_chart2:
                            # Top IPs
                            if "top_ips" in charts:
                                top_ips = charts["top_ips"]
                                fig_ips = go.Figure(data=[go.Bar(
                                    x=list(top_ips.keys()),
                                    y=list(top_ips.values()),
                                    marker_color='#9333ea'
                                )])
                                fig_ips.update_layout(
                                    title="Top IP Addresses",
                                    xaxis_title="IP Address",
                                    yaxis_title="Requests",
                                    height=400
                                )
                                st.plotly_chart(fig_ips, use_container_width=True)
                            
                            # Top URLs
                            if "top_urls" in charts:
                                top_urls = charts["top_urls"]
                                fig_urls = go.Figure(data=[go.Bar(
                                    x=list(top_urls.keys()),
                                    y=list(top_urls.values()),
                                    marker_color='#3b82f6'
                                )])
                                fig_urls.update_layout(
                                    title="Top URLs",
                                    xaxis_title="URL",
                                    yaxis_title="Requests",
                                    height=400
                                )
                                st.plotly_chart(fig_urls, use_container_width=True)
                else:
                    error_msg = response.json().get("error", "Failed to load dashboard") if response else "Connection error"
                    st.error(f"❌ {error_msg}")

with tab4:
    st.header("Search Logs")
    
    col_search, col_limit = st.columns([4, 1])
    with col_search:
        search_query = st.text_input(
            "Search logs",
            placeholder="e.g., 'error', 'timeout', 'status:500'..."
        )
    with col_limit:
        search_limit = st.number_input("Limit", min_value=1, max_value=20, value=5)
    
    if st.button("Search", type="primary", disabled=not project_id or not search_query):
        if not project_id:
            st.error("Please enter a Project ID first")
        elif not search_query:
            st.error("Please enter a search query")
        else:
            with st.spinner("Searching logs..."):
                try:
                    payload = {
                        "text": search_query,
                        "limit": search_limit
                    }
                    response = make_request("POST", f"api/v1/nlp/index/search/{project_id}", json=payload)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        
                        if not results:
                            st.info("No matching log entries found.")
                        else:
                            for idx, result in enumerate(results, 1):
                                with st.expander(f"Log Entry {idx} (Relevance: {result.get('score', 0)*100:.1f}%)"):
                                    st.code(result.get("text", ""), language="text")
                    else:
                        error_msg = response.json().get("detail", "Search failed") if response else "Connection error"
                        st.error(f"❌ {error_msg}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with tab5:
    st.header("🤖 AI Assistant")
    st.markdown("Ask questions about your logs using AI-powered RAG")
    
    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.info("""
            👋 Hello! I'm your intelligent log analysis assistant. I'm here to help you uncover insights from your data.
            
            **I can help you:**
            - ✅ Find specific errors or patterns
            - ✅ Analyze error frequencies and trends
            - ✅ Identify root causes of issues
            
            Upload and process your logs first to get started.
            """)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
    
    # Suggested questions
    st.markdown("**Suggested Questions:**")
    col_sug1, col_sug2, col_sug3, col_sug4 = st.columns(4)
    suggestions = [
        "What are the most frequent errors?",
        "Analyze the error trends over time",
        "Which IP addresses are causing issues?",
        "Summary of the last hour activity"
    ]
    
    for col, suggestion in zip([col_sug1, col_sug2, col_sug3, col_sug4], suggestions):
        with col:
            if st.button(suggestion[:30] + "...", key=f"sug_{suggestion}"):
                st.session_state.suggested_query = suggestion
    
    # Chat input
    user_query = st.chat_input("Ask about your logs... (e.g., 'What are the most common errors?')")
    
    if user_query or 'suggested_query' in st.session_state:
        query = user_query if user_query else st.session_state.get('suggested_query', '')
        if 'suggested_query' in st.session_state:
            del st.session_state.suggested_query
        
        if not project_id:
            st.error("Please enter a Project ID first")
        elif st.session_state.is_processing:
            st.warning("Please wait - processing is still in progress. You can ask questions once the processing is complete.")
        else:
            # Add user message to chat
            st.session_state.chat_history.append({"role": "user", "content": query})
            
            with st.spinner("Thinking..."):
                try:
                    payload = {
                        "text": query,
                        "limit": 6,
                        "chat_history": st.session_state.chat_history[:-1]  # Exclude current message
                    }
                    response = make_request("POST", f"api/v1/nlp/index/answer/{project_id}", json=payload)
                    
                    if response and response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "I apologize, but I couldn't generate an answer.")
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        st.session_state.chat_history = data.get("chat_history", st.session_state.chat_history)
                        st.rerun()
                    else:
                        error_msg = response.json().get("detail", "Failed to get answer") if response else "Connection error"
                        st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {error_msg}"})
                        st.rerun()
                except Exception as e:
                    st.session_state.chat_history.append({"role": "assistant", "content": f"Connection error: {str(e)}"})
                    st.rerun()
