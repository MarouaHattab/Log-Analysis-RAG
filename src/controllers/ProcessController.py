from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from typing import List
from dataclasses import dataclass
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        if file_ext == ProcessingEnum.LOG.value:
            return TextLoader(file_path, encoding="utf-8")

        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()

        return None

    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20,
                            chunking_method: str="simple"):

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        # Route to appropriate chunking method
        if chunking_method == "log_error_block":
            chunks = self.process_log_error_block_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size
            )
        elif chunking_method == "log_time_window":
            chunks = self.process_log_time_window_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size
            )
        elif chunking_method == "log_component_based":
            chunks = self.process_log_component_based_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size
            )
        elif chunking_method == "log_status_code":
            chunks = self.process_log_status_code_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size
            )
        # elif chunking_method == "log_url_pattern":
        #     chunks = self.process_log_url_pattern_splitter(
        #         texts=file_content_texts,
        #         metadatas=file_content_metadata,
        #         chunk_size=chunk_size
        #     )
        # elif chunking_method == "log_bot_human":
        #     chunks = self.process_log_bot_human_splitter(
        #         texts=file_content_texts,
        #         metadatas=file_content_metadata,
        #         chunk_size=chunk_size
        #     )
        elif chunking_method == "log_semantic_sliding":
            chunks = self.process_log_semantic_sliding_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )
        # elif chunking_method == "log_http_method":
        #     chunks = self.process_log_http_method_splitter(
        #         texts=file_content_texts,
        #         metadatas=file_content_metadata,
        #         chunk_size=chunk_size
        #     )
        # elif chunking_method == "simpler_splitter":
        #     chunks = self.process_simpler_splitter(
        #         texts=file_content_texts,
        #         metadatas=file_content_metadata,
        #         chunk_size=chunk_size
        #     )
        else:  # Default to log_time_window (best for general log analysis)
            chunks = self.process_log_time_window_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size
            )

        return chunks

    def get_available_chunking_methods(self) -> List[str]:
        """
        Returns list of available chunking methods for log analysis.
        
        Methods:
        - log_error_block: Groups logs keeping errors together with their context
        - log_time_window: Groups logs by time windows (hourly)
        - log_component_based: Groups logs by IP address/client
        - log_status_code: Groups logs by HTTP status code category (2xx, 3xx, 4xx, 5xx)
        - log_url_pattern: Groups logs by URL patterns (images, API, static, filters)
        - log_bot_human: Separates bot traffic from human traffic
        - log_semantic_sliding: Sliding window with overlap for context preservation
        - log_http_method: Groups logs by HTTP method (GET, POST, etc.)
        - simpler_splitter: Simple size-based chunking
        """
        return [
            "log_error_block",
            "log_time_window",
            "log_component_based",
            "log_status_code",
            "log_url_pattern",
            "log_bot_human",
            "log_semantic_sliding",
            "log_http_method",
            "simpler_splitter"
        ]

    # def get_recommended_settings(self, chunking_method: str = None) -> dict:
    #     """
    #     Returns recommended chunk_size and overlap_size for log analysis RAG systems.
        
    #     Recommendations are optimized for:
    #     - Embedding model performance (optimal 500-3000 chars)
    #     - Log entry context preservation (~8-15 entries per chunk)
    #     - AI assistant response quality
        
    #     Args:
    #         chunking_method: Optional specific method to get settings for.
    #                        If None, returns settings for all methods.
        
    #     Returns:
    #         Dictionary with recommended settings.
    #     """
    #     settings = {
    #         # Best for RAG AI Assistant - maintains context with overlap
    #         "log_semantic_sliding": {
    #             "chunk_size": 2500,
    #             "overlap_size": 20,
    #             "description": "BEST FOR RAG - Sliding window with 20% overlap preserves context across chunks",
    #             "use_case": "AI assistant queries, semantic search, context-aware analysis"
    #         },
    #         # Time-based grouping for temporal analysis
    #         "log_time_window": {
    #             "chunk_size": 3000,
    #             "overlap_size": 0,
    #             "description": "Groups logs by hourly time windows",
    #             "use_case": "Time-based analysis, traffic patterns, peak hours"
    #         },
    #         # Error-focused for debugging
    #         "log_error_block": {
    #             "chunk_size": 2500,
    #             "overlap_size": 0,
    #             "description": "Keeps error logs with surrounding context together",
    #             "use_case": "Error debugging, security analysis, incident investigation"
    #         },
    #         # Status code grouping
    #         "log_status_code": {
    #             "chunk_size": 2500,
    #             "overlap_size": 0,
    #             "description": "Groups by HTTP status categories (2xx, 3xx, 4xx, 5xx)",
    #             "use_case": "Performance monitoring, error rate analysis"
    #         },
    #         # URL pattern analysis
    #         "log_url_pattern": {
    #             "chunk_size": 2500,
    #             "overlap_size": 0,
    #             "description": "Groups by resource type (images, API, static, filters)",
    #             "use_case": "Resource usage analysis, endpoint performance"
    #         },
    #         # Bot vs Human separation
    #         "log_bot_human": {
    #             "chunk_size": 3000,
    #             "overlap_size": 0,
    #             "description": "Separates bot traffic from human users",
    #             "use_case": "SEO analysis, bot behavior, genuine user patterns"
    #         },
    #         # IP/Client based
    #         "log_component_based": {
    #             "chunk_size": 2500,
    #             "overlap_size": 0,
    #             "description": "Groups logs by client IP address",
    #             "use_case": "Client behavior analysis, suspicious activity detection"
    #         },
    #         # HTTP method grouping
    #         "log_http_method": {
    #             "chunk_size": 2500,
    #             "overlap_size": 0,
    #             "description": "Groups by HTTP method (GET, POST, PUT, DELETE)",
    #             "use_case": "API operation analysis, write vs read patterns"
    #         },
    #         # Simple baseline
    #         "simpler_splitter": {
    #             "chunk_size": 2000,
    #             "overlap_size": 0,
    #             "description": "Basic size-based chunking without semantic awareness",
    #             "use_case": "Simple processing, baseline comparison"
    #         }
    #     }
        
    #     if chunking_method:
    #         return settings.get(chunking_method, settings["log_semantic_sliding"])
    #     return settings

    # def get_best_method_for_rag(self) -> dict:
    #     """
    #     Returns the best chunking configuration for RAG AI assistant responses.
        
    #     For optimal RAG performance with log data:
    #     - Method: log_semantic_sliding
    #     - Chunk size: 2500 characters (~8-15 log entries)
    #     - Overlap: 20% (maintains context between chunks)
        
    #     Returns:
    #         Dictionary with optimal settings for RAG.
    #     """
    #     return {
    #         "method": "log_semantic_sliding",
    #         "chunk_size": 2500,
    #         "overlap_size": 20,
    #         "reason": "Sliding window with overlap provides the best context preservation for AI responses",
    #         "tips": [
    #             "Use chunk_size=2500 for ~8-15 log entries per chunk",
    #             "20% overlap ensures no context is lost at boundaries",
    #             "Works best with embedding models (500-3000 char optimal range)",
    #             "For specific error analysis, combine with log_error_block",
    #             "For time-based queries, use log_time_window instead"
    #         ]
    #     }

    def process_log_error_block_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific error block splitter method.
        Groups log entries by error patterns and status codes to keep related errors together.
        Best for analyzing error patterns and their context.
        """
        logger.info(f"🔄 [LOG_ERROR_BLOCK] Starting chunking - grouping errors together...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_ERROR_BLOCK] Found {len(lines)} log entries to process")
        
        # Error status codes
        error_statuses = ['400', '401', '403', '404', '405', '500', '501', '502', '503', '504']
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        
        for idx, line in enumerate(lines):
            is_error = any(f" {status} " in line for status in error_statuses)
            line_size = len(line) + 1
            
            # Add line to current chunk
            current_chunk.append(line)
            current_chunk_size += line_size
            
            # Check if we should create a chunk
            # Chunk on: size threshold OR if we have errors and hit a non-error line
            should_chunk = (
                current_chunk_size >= chunk_size or 
                (any(any(f" {status} " in l for status in error_statuses) for l in current_chunk) and 
                 not is_error and len(current_chunk) > 1)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_error_block",
                        "error_lines": sum(1 for l in current_chunk if any(f" {status} " in l for status in error_statuses)),
                        "total_lines": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_ERROR_BLOCK] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_error_block",
                    "error_lines": sum(1 for l in current_chunk if any(f" {status} " in l for status in error_statuses)),
                    "total_lines": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_ERROR_BLOCK] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_time_window_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific time window splitter method.
        Groups log entries by time windows (minute/hour boundaries).
        Best for analyzing logs by time period.
        Detects timestamp patterns like [23/Jan/2019:03:56:14 +0330]
        """
        logger.info(f"🔄 [LOG_TIME_WINDOW] Starting chunking - grouping by time windows...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_TIME_WINDOW] Found {len(lines)} log entries to process")
        
        # Pattern to extract timestamps like [23/Jan/2019:03:56:14 +0330]
        timestamp_pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})'
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_time_window = None
        
        for idx, line in enumerate(lines):
            # Extract timestamp from log line
            match = re.search(timestamp_pattern, line)
            time_window = None
            
            if match:
                day, month, year, hour, minute, second = match.groups()
                # Time window key (hour-based grouping)
                time_window = f"{year}-{month}-{day}_{hour}:00"
            
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            # Check if we should create a chunk
            # Chunk on: size threshold OR time window change
            should_chunk = (
                current_chunk_size >= chunk_size or 
                (current_time_window and time_window and current_time_window != time_window)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_time_window",
                        "time_window": current_time_window,
                        "entries": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            if time_window:
                current_time_window = time_window
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_TIME_WINDOW] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_time_window",
                    "time_window": current_time_window,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_TIME_WINDOW] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_component_based_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific component-based splitter method.
        Groups log entries by component/source (IP addresses, user agents, endpoints).
        Best for analyzing logs by component or client.
        """
        logger.info(f"🔄 [LOG_COMPONENT_BASED] Starting chunking - grouping by components...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_COMPONENT_BASED] Found {len(lines)} log entries to process")
        
        # Extract IP address pattern (at start of most log lines)
        ip_pattern = r'^(\d+\.\d+\.\d+\.\d+)'
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_component = None
        
        for idx, line in enumerate(lines):
            # Extract IP/component from log line
            match = re.search(ip_pattern, line)
            component = match.group(1) if match else "UNKNOWN"
            
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            # Check if we should create a chunk
            # Chunk on: size threshold OR component change with multiple lines
            should_chunk = (
                current_chunk_size >= chunk_size or 
                (current_component and current_component != component and len(current_chunk) > 1)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_component_based",
                        "component": current_component,
                        "entries": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            current_component = component
            
            if (idx + 1) % 100 == 0:
                logger.info(f" [LOG_COMPONENT_BASED] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_component_based",
                    "component": current_component,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_COMPONENT_BASED] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_status_code_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific status code splitter method.
        Groups log entries by HTTP status code categories:
        - 2xx (Success), 3xx (Redirect), 4xx (Client Error), 5xx (Server Error)
        Best for analyzing logs by response status type.
        """
        logger.info(f"🔄 [LOG_STATUS_CODE] Starting chunking - grouping by status codes...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_STATUS_CODE] Found {len(lines)} log entries to process")
        
        # Status code pattern: extract 3-digit code
        status_pattern = r'" (\d{3}) '
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_status_category = None
        
        def get_status_category(status_code):
            if status_code:
                first_digit = status_code[0]
                if first_digit == '2':
                    return '2xx_success'
                elif first_digit == '3':
                    return '3xx_redirect'
                elif first_digit == '4':
                    return '4xx_client_error'
                elif first_digit == '5':
                    return '5xx_server_error'
            return 'unknown'
        
        for idx, line in enumerate(lines):
            # Extract status code from log line
            match = re.search(status_pattern, line)
            status_code = match.group(1) if match else None
            status_category = get_status_category(status_code)
            
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            # Check if we should create a chunk
            # Chunk on: size threshold OR status category change
            should_chunk = (
                current_chunk_size >= chunk_size or 
                (current_status_category and current_status_category != status_category)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_status_code",
                        "status_category": current_status_category,
                        "entries": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            current_status_category = status_category
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_STATUS_CODE] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_status_code",
                    "status_category": current_status_category,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_STATUS_CODE] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_url_pattern_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific URL pattern splitter method.
        Groups log entries by URL patterns:
        - /image/* (image requests)
        - /static/* (static files: CSS, JS, fonts)
        - /filter/* or /ajaxFilter/* (filter/search operations)
        - /m/* (mobile endpoints)
        - /api/* or /settings/* (API calls)
        - /product/* (product pages)
        - other (miscellaneous)
        Best for analyzing traffic by resource type.
        """
        logger.info(f"🔄 [LOG_URL_PATTERN] Starting chunking - grouping by URL patterns...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_URL_PATTERN] Found {len(lines)} log entries to process")
        
        # URL patterns with priorities
        url_patterns = {
            'image': r'GET /image/',
            'static': r'GET /static/',
            'filter': r'(GET|POST) /(ajax)?[fF]ilter',
            'mobile': r'GET /m/',
            'api': r'GET /(settings|site|order)/',
            'product': r'GET /product/',
            'browse': r'GET /browse/',
        }
        
        def get_url_category(line):
            for category, pattern in url_patterns.items():
                if re.search(pattern, line):
                    return category
            return 'other'
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_category = None
        
        for idx, line in enumerate(lines):
            category = get_url_category(line)
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            should_chunk = (
                current_chunk_size >= chunk_size or
                (current_category and current_category != category and len(current_chunk) > 1)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_url_pattern",
                        "url_category": current_category,
                        "entries": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            current_category = category
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_URL_PATTERN] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_url_pattern",
                    "url_category": current_category,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_URL_PATTERN] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_bot_human_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific bot vs human traffic splitter method.
        Separates log entries by traffic source:
        - Bot traffic (Googlebot, bingbot, AhrefsBot, etc.)
        - Human traffic (regular browsers)
        Best for analyzing bot behavior vs user behavior separately.
        """
        logger.info(f"🔄 [LOG_BOT_HUMAN] Starting chunking - separating bot and human traffic...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_BOT_HUMAN] Found {len(lines)} log entries to process")
        
        # Bot patterns in User-Agent
        bot_patterns = [
            r'[Gg]ooglebot', r'[Bb]ingbot', r'[Yy]ahoo', r'[Bb]aidu',
            r'[Ss]lurp', r'[Dd]uckDuck', r'[Ff]acebot', r'[Ii]A_[Aa]rchiver',
            r'AhrefsBot', r'MJ12bot', r'SemrushBot', r'DotBot',
            r'crawler', r'spider', r'bot\.html', r'[Rr]obot'
        ]
        bot_regex = '|'.join(bot_patterns)
        
        def is_bot(line):
            return bool(re.search(bot_regex, line, re.IGNORECASE))
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_is_bot = None
        
        for idx, line in enumerate(lines):
            line_is_bot = is_bot(line)
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            should_chunk = (
                current_chunk_size >= chunk_size or
                (current_is_bot is not None and current_is_bot != line_is_bot and len(current_chunk) > 1)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_bot_human",
                        "traffic_type": "bot" if current_is_bot else "human",
                        "entries": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            current_is_bot = line_is_bot
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_BOT_HUMAN] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_bot_human",
                    "traffic_type": "bot" if current_is_bot else "human",
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_BOT_HUMAN] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_semantic_sliding_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, overlap_size: int = 20):
        """
        Log-specific semantic sliding window splitter with overlap.
        Creates chunks with overlapping log entries to preserve context.
        Best for RAG applications where context between chunks matters.
        """
        logger.info(f"🔄 [LOG_SEMANTIC_SLIDING] Starting chunking with overlap_size={overlap_size}...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_SEMANTIC_SLIDING] Found {len(lines)} log entries to process")
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        overlap_buffer = []  # Store lines for overlap
        
        for idx, line in enumerate(lines):
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            if current_chunk_size >= chunk_size:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_semantic_sliding",
                        "chunk_index": len(chunks),
                        "entries": len(current_chunk),
                        "has_overlap": len(overlap_buffer) > 0
                    }
                ))
                
                # Calculate overlap lines (based on percentage of chunk)
                overlap_count = max(1, len(current_chunk) * overlap_size // 100)
                overlap_buffer = current_chunk[-overlap_count:]
                
                # Start new chunk with overlap
                current_chunk = overlap_buffer.copy()
                current_chunk_size = sum(len(l) + 1 for l in current_chunk)
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_SEMANTIC_SLIDING] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_semantic_sliding",
                    "chunk_index": len(chunks),
                    "entries": len(current_chunk),
                    "has_overlap": len(overlap_buffer) > 0
                }
            ))
        
        logger.info(f"✨ [LOG_SEMANTIC_SLIDING] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_http_method_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific HTTP method splitter.
        Groups log entries by HTTP method (GET, POST, PUT, DELETE, etc.).
        Best for analyzing different types of operations separately.
        """
        logger.info(f"🔄 [LOG_HTTP_METHOD] Starting chunking - grouping by HTTP methods...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"📋 [LOG_HTTP_METHOD] Found {len(lines)} log entries to process")
        
        # HTTP method pattern
        method_pattern = r'"(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE) '
        
        def get_http_method(line):
            match = re.search(method_pattern, line)
            return match.group(1) if match else 'UNKNOWN'
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_method = None
        
        for idx, line in enumerate(lines):
            method = get_http_method(line)
            line_size = len(line) + 1
            current_chunk.append(line)
            current_chunk_size += line_size
            
            should_chunk = (
                current_chunk_size >= chunk_size or
                (current_method and current_method != method and len(current_chunk) > 1)
            )
            
            if should_chunk and current_chunk:
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "log_http_method",
                        "http_method": current_method,
                        "entries": len(current_chunk)
                    }
                ))
                current_chunk = []
                current_chunk_size = 0
            
            current_method = method
            
            if (idx + 1) % 100 == 0:
                logger.info(f"✅ [LOG_HTTP_METHOD] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_http_method",
                    "http_method": current_method,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"✨ [LOG_HTTP_METHOD] Chunking complete! Total chunks: {len(chunks)}")
        return chunks


    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks
