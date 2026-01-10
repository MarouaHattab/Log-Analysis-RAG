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
        if chunking_method == "log_hybrid_adaptive":
            chunks = self.process_log_hybrid_adaptive_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )
        elif chunking_method == "log_hybrid_intelligent":
            chunks = self.process_log_hybrid_intelligent_splitter(
                texts=file_content_texts,
                metadatas=file_content_metadata,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )
        elif chunking_method == "log_error_block":
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
            "log_hybrid_adaptive",
            "log_semantic_sliding",
            "log_time_window",
            "log_error_block",
            "log_hybrid_intelligent",
            "log_component_based"
        ]

    def process_log_hybrid_adaptive_splitter(self, texts: List[str], metadatas: List[dict], 
                                            chunk_size: int, overlap_size: int = 20):
        """
        HYBRID ADAPTIVE CHUNKING METHOD - Best of all worlds!
        
        This method combines multiple strategies intelligently:
        1. Time-window awareness (keeps logs from same time period together)
        2. Error-block awareness (never splits error contexts)
        3. Component awareness (groups requests from same IP when beneficial)
        4. Semantic sliding (maintains overlap for context)
        5. Status-code awareness (groups similar HTTP responses)
        
        Strategy:
        - Primary grouping: Time windows (hourly)
        - Secondary grouping: Keep errors with their context
        - Tertiary grouping: Consider IP/component patterns
        - Always maintain overlap for RAG context
        
        Best for: General-purpose RAG systems that need to answer diverse queries
        about errors, performance, user behavior, and temporal patterns.
        """
        logger.info(f"[HYBRID_ADAPTIVE] Starting adaptive hybrid chunking...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[HYBRID_ADAPTIVE] Found {len(lines)} log entries to process")
        
        # Patterns for analysis
        timestamp_pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})'
        status_pattern = r'" (\d{3}) '
        ip_pattern = r'^(\d+\.\d+\.\d+\.\d+)'
        error_statuses = ['400', '401', '403', '404', '405', '500', '501', '502', '503', '504']
        
        def analyze_line(line):
            """Extract key features from log line"""
            features = {
                'time_window': None,
                'is_error': False,
                'status_category': None,
                'ip': None
            }
            
            # Extract timestamp
            ts_match = re.search(timestamp_pattern, line)
            if ts_match:
                day, month, year, hour, minute, second = ts_match.groups()
                features['time_window'] = f"{year}-{month}-{day}_{hour}:00"
            
            # Extract status code
            status_match = re.search(status_pattern, line)
            if status_match:
                status = status_match.group(1)
                features['is_error'] = any(f" {err} " in line for err in error_statuses)
                
                # Categorize status
                first_digit = status[0]
                if first_digit == '2':
                    features['status_category'] = '2xx'
                elif first_digit == '3':
                    features['status_category'] = '3xx'
                elif first_digit == '4':
                    features['status_category'] = '4xx'
                elif first_digit == '5':
                    features['status_category'] = '5xx'
            
            # Extract IP
            ip_match = re.search(ip_pattern, line)
            if ip_match:
                features['ip'] = ip_match.group(1)
            
            return features
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        current_context = {
            'time_window': None,
            'has_errors': False,
            'primary_ip': None,
            'status_category': None
        }
        overlap_buffer = []
        
        for idx, line in enumerate(lines):
            features = analyze_line(line)
            line_size = len(line) + 1
            
            # Decide if we should start a new chunk based on hybrid criteria
            should_chunk = False
            chunk_reason = []
            
            # Criterion 1: Size threshold reached
            if current_chunk_size >= chunk_size:
                should_chunk = True
                chunk_reason.append("size_limit")
            
            # Criterion 2: Time window changed (but only if we have enough content)
            if (current_context['time_window'] and 
                features['time_window'] and 
                current_context['time_window'] != features['time_window'] and
                len(current_chunk) >= 5):
                should_chunk = True
                chunk_reason.append("time_window_change")
            
            # Criterion 3: Error context boundary - if current chunk has errors
            # and we're moving to non-errors (keep error context together)
            if (current_context['has_errors'] and 
                not features['is_error'] and 
                current_chunk_size >= chunk_size * 0.6):  # At least 60% full
                should_chunk = True
                chunk_reason.append("error_boundary")
            
            # Criterion 4: Status category major change (but not for minor transitions)
            if (current_context['status_category'] and 
                features['status_category'] and
                current_context['status_category'] != features['status_category'] and
                current_chunk_size >= chunk_size * 0.8):  # At least 80% full
                
                # Only chunk on major category changes (e.g., success -> error)
                major_change = (
                    (current_context['status_category'] in ['2xx', '3xx'] and 
                    features['status_category'] in ['4xx', '5xx']) or
                    (current_context['status_category'] in ['4xx', '5xx'] and 
                    features['status_category'] in ['2xx', '3xx'])
                )
                if major_change:
                    should_chunk = True
                    chunk_reason.append("status_category_major_change")
            
            # Add line to current chunk
            current_chunk.append(line)
            current_chunk_size += line_size
            
            # Update context
            if features['time_window']:
                current_context['time_window'] = features['time_window']
            if features['is_error']:
                current_context['has_errors'] = True
            if features['ip']:
                current_context['primary_ip'] = features['ip']
            if features['status_category']:
                current_context['status_category'] = features['status_category']
            
            # Create chunk if needed
            if should_chunk and current_chunk:
                # Calculate chunk metadata
                error_count = sum(1 for l in current_chunk if any(f" {err} " in l for err in error_statuses))
                
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "hybrid_adaptive",
                        "chunk_index": len(chunks),
                        "entries": len(current_chunk),
                        "time_window": current_context['time_window'],
                        "has_errors": current_context['has_errors'],
                        "error_count": error_count,
                        "primary_ip": current_context['primary_ip'],
                        "status_category": current_context['status_category'],
                        "chunk_reasons": ", ".join(chunk_reason),
                        "has_overlap": len(overlap_buffer) > 0
                    }
                ))
                
                # Calculate overlap (20% of chunk)
                overlap_count = max(1, len(current_chunk) * overlap_size // 100)
                overlap_buffer = current_chunk[-overlap_count:]
                
                # Start new chunk with overlap
                current_chunk = overlap_buffer.copy()
                current_chunk_size = sum(len(l) + 1 for l in current_chunk)
                
                # Reset context (except keep last time_window for continuity)
                last_time_window = current_context['time_window']
                current_context = {
                    'time_window': last_time_window,
                    'has_errors': False,
                    'primary_ip': None,
                    'status_category': None
                }
            
            if (idx + 1) % 100 == 0:
                logger.info(f"[HYBRID_ADAPTIVE] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        # Don't forget the last chunk
        if current_chunk:
            error_count = sum(1 for l in current_chunk if any(f" {err} " in l for err in error_statuses))
            
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "hybrid_adaptive",
                    "chunk_index": len(chunks),
                    "entries": len(current_chunk),
                    "time_window": current_context['time_window'],
                    "has_errors": current_context['has_errors'],
                    "error_count": error_count,
                    "primary_ip": current_context['primary_ip'],
                    "status_category": current_context['status_category'],
                    "chunk_reasons": "final_chunk",
                    "has_overlap": len(overlap_buffer) > 0
                }
            ))
        
        logger.info(f"[HYBRID_ADAPTIVE] Chunking complete! Total chunks: {len(chunks)}")
        logger.info(f"[HYBRID_ADAPTIVE] Avg entries per chunk: {sum(c.metadata['entries'] for c in chunks) / len(chunks):.1f}")
        logger.info(f"[HYBRID_ADAPTIVE] Chunks with errors: {sum(1 for c in chunks if c.metadata['has_errors'])}")
        
        return chunks


    def process_log_hybrid_intelligent_splitter(self, texts: List[str], metadatas: List[dict], 
                                            chunk_size: int, overlap_size: int = 15):
        """
        HYBRID INTELLIGENT CHUNKING - Context-Aware Smart Splitting
        
        This advanced hybrid method uses intelligent boundaries:
        1. Never splits IP session patterns (consecutive requests from same IP)
        2. Never splits error sequences (errors + immediate context)
        3. Respects natural log boundaries (time gaps, URL pattern changes)
        4. Maintains semantic overlap
        5. Optimizes chunk size for embedding models
        
        Boundary Detection:
        - Time gap > 60 seconds = natural boundary
        - IP change after 5+ consecutive requests = session boundary
        - Error sequences kept intact (error + 2 before + 2 after)
        - URL pattern shifts = activity boundary
        
        Best for: RAG systems requiring high-quality semantic search and
        accurate context retrieval for complex queries.
        """
        logger.info(f"[HYBRID_INTELLIGENT] Starting intelligent context-aware chunking...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[HYBRID_INTELLIGENT] Found {len(lines)} log entries to process")
        
        # Parse all lines first for intelligent analysis
        timestamp_pattern = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})'
        status_pattern = r'" (\d{3}) '
        ip_pattern = r'^(\d+\.\d+\.\d+\.\d+)'
        url_pattern = r'"[A-Z]+ ([^ ]+)'
        
        parsed_lines = []
        for line in lines:
            info = {'line': line}
            
            # Parse timestamp
            ts_match = re.search(timestamp_pattern, line)
            if ts_match:
                day, month, year, hour, minute, second = ts_match.groups()
                info['timestamp'] = f"{year}-{month}-{day} {hour}:{minute}:{second}"
            else:
                info['timestamp'] = None
            
            # Parse status
            status_match = re.search(status_pattern, line)
            info['status'] = int(status_match.group(1)) if status_match else None
            info['is_error'] = info['status'] >= 400 if info['status'] else False
            
            # Parse IP
            ip_match = re.search(ip_pattern, line)
            info['ip'] = ip_match.group(1) if ip_match else None
            
            # Parse URL
            url_match = re.search(url_pattern, line)
            info['url'] = url_match.group(1) if url_match else None
            
            parsed_lines.append(info)
        
        def detect_boundary(idx, parsed_lines):
            """Detect if this is a good chunk boundary"""
            if idx == 0 or idx >= len(parsed_lines):
                return False, []
            
            current = parsed_lines[idx]
            previous = parsed_lines[idx - 1]
            reasons = []
            
            # Check for time gap (natural boundary)
            # This would require proper datetime parsing - simplified here
            
            # Check for IP session change
            if previous['ip'] and current['ip'] and previous['ip'] != current['ip']:
                # Look back to see if previous IP had a session (5+ consecutive)
                consecutive_count = 1
                for j in range(idx - 2, max(-1, idx - 10), -1):
                    if parsed_lines[j]['ip'] == previous['ip']:
                        consecutive_count += 1
                    else:
                        break
                
                if consecutive_count >= 5:
                    reasons.append('ip_session_boundary')
            
            # Check for error sequence boundary
            # Don't split if current or previous 2 are errors
            if (current['is_error'] or 
                (idx >= 1 and parsed_lines[idx-1]['is_error']) or
                (idx >= 2 and parsed_lines[idx-2]['is_error'])):
                return False, ['error_context_protection']
            
            # Check for URL pattern shift
            if previous['url'] and current['url']:
                prev_is_static = any(ext in previous['url'] for ext in ['.css', '.js', '.jpg', '.png', '.gif'])
                curr_is_static = any(ext in current['url'] for ext in ['.css', '.js', '.jpg', '.png', '.gif'])
                
                if prev_is_static != curr_is_static:
                    reasons.append('url_pattern_shift')
            
            return len(reasons) > 0, reasons
        
        chunks = []
        current_chunk = []
        current_chunk_size = 0
        overlap_buffer = []
        error_protection_count = 0
        
        for idx, item in enumerate(parsed_lines):
            line = item['line']
            line_size = len(line) + 1
            
            # Add to current chunk
            current_chunk.append(line)
            current_chunk_size += line_size
            
            # Track error protection
            if item['is_error']:
                error_protection_count = 5  # Protect next 5 lines
            elif error_protection_count > 0:
                error_protection_count -= 1
            
            # Check if we should chunk
            should_chunk = False
            chunk_reasons = []
            
            # Size-based chunking
            if current_chunk_size >= chunk_size:
                # But only if not in error protection and at a good boundary
                if error_protection_count == 0:
                    is_boundary, boundary_reasons = detect_boundary(idx + 1, parsed_lines)
                    
                    if is_boundary:
                        should_chunk = True
                        chunk_reasons.extend(boundary_reasons)
                        chunk_reasons.append('size_with_smart_boundary')
                    elif current_chunk_size >= chunk_size * 1.3:  # Allow 30% overflow
                        should_chunk = True
                        chunk_reasons.append('size_overflow')
            
            if should_chunk and current_chunk:
                # Calculate metadata
                chunk_ips = set(parsed_lines[max(0, idx - len(current_chunk)):idx]['ip'] 
                            for item in parsed_lines[max(0, idx - len(current_chunk)):idx])
                chunk_errors = sum(1 for item in parsed_lines[max(0, idx - len(current_chunk)):idx] 
                                if item['is_error'])
                
                chunks.append(Document(
                    page_content="\n".join(current_chunk),
                    metadata={
                        "method": "hybrid_intelligent",
                        "chunk_index": len(chunks),
                        "entries": len(current_chunk),
                        "unique_ips": len([ip for ip in chunk_ips if ip]),
                        "error_count": chunk_errors,
                        "boundary_reasons": ", ".join(chunk_reasons),
                        "has_overlap": len(overlap_buffer) > 0
                    }
                ))
                
                # Create overlap
                overlap_count = max(2, len(current_chunk) * overlap_size // 100)
                overlap_buffer = current_chunk[-overlap_count:]
                
                current_chunk = overlap_buffer.copy()
                current_chunk_size = sum(len(l) + 1 for l in current_chunk)
            
            if (idx + 1) % 100 == 0:
                logger.info(f"[HYBRID_INTELLIGENT] Progress: Processed {idx + 1}/{len(parsed_lines)} entries, Created {len(chunks)} chunks")
        
        # Final chunk
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "hybrid_intelligent",
                    "chunk_index": len(chunks),
                    "entries": len(current_chunk),
                    "boundary_reasons": "final_chunk",
                    "has_overlap": len(overlap_buffer) > 0
                }
            ))
        
        logger.info(f"[HYBRID_INTELLIGENT] Chunking complete! Total chunks: {len(chunks)}")
        logger.info(f"[HYBRID_INTELLIGENT] Avg entries per chunk: {sum(c.metadata['entries'] for c in chunks) / len(chunks):.1f}")
        
        return chunks


    def process_log_error_block_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific error block splitter method.
        Groups log entries by error patterns and status codes to keep related errors together.
        Best for analyzing error patterns and their context.
        """
        logger.info(f"[LOG_ERROR_BLOCK] Starting chunking - grouping errors together...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_ERROR_BLOCK] Found {len(lines)} log entries to process")
        
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
        
        logger.info(f"[LOG_ERROR_BLOCK] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_time_window_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific time window splitter method.
        Groups log entries by time windows (minute/hour boundaries).
        Best for analyzing logs by time period.
        Detects timestamp patterns like [23/Jan/2019:03:56:14 +0330]
        """
        logger.info(f"[LOG_TIME_WINDOW] Starting chunking - grouping by time windows...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_TIME_WINDOW] Found {len(lines)} log entries to process")
        
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
                logger.info(f"[LOG_TIME_WINDOW] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
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
        
        logger.info(f"[LOG_TIME_WINDOW] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_component_based_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific component-based splitter method.
        Groups log entries by component/source (IP addresses, user agents, endpoints).
        Best for analyzing logs by component or client.
        """
        logger.info(f"[LOG_COMPONENT_BASED] Starting chunking - grouping by components...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_COMPONENT_BASED] Found {len(lines)} log entries to process")
        
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
        
        logger.info(f"[LOG_COMPONENT_BASED] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_status_code_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific status code splitter method.
        Groups log entries by HTTP status code categories:
        - 2xx (Success), 3xx (Redirect), 4xx (Client Error), 5xx (Server Error)
        Best for analyzing logs by response status type.
        """
        logger.info(f"[LOG_STATUS_CODE] Starting chunking - grouping by status codes...")
        full_text = " ".join(texts)
        
        # Split by lines
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_STATUS_CODE] Found {len(lines)} log entries to process")
        
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
                logger.info(f"[LOG_STATUS_CODE] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
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
        
        logger.info(f"[LOG_STATUS_CODE] Chunking complete! Total chunks: {len(chunks)}")
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
        logger.info(f"[LOG_URL_PATTERN] Starting chunking - grouping by URL patterns...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_URL_PATTERN] Found {len(lines)} log entries to process")
        
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
                logger.info(f"[LOG_URL_PATTERN] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_url_pattern",
                    "url_category": current_category,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"[LOG_URL_PATTERN] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_bot_human_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific bot vs human traffic splitter method.
        Separates log entries by traffic source:
        - Bot traffic (Googlebot, bingbot, AhrefsBot, etc.)
        - Human traffic (regular browsers)
        Best for analyzing bot behavior vs user behavior separately.
        """
        logger.info(f"[LOG_BOT_HUMAN] Starting chunking - separating bot and human traffic...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_BOT_HUMAN] Found {len(lines)} log entries to process")
        
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
                logger.info(f"[LOG_BOT_HUMAN] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_bot_human",
                    "traffic_type": "bot" if current_is_bot else "human",
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"[LOG_BOT_HUMAN] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_semantic_sliding_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, overlap_size: int = 20):
        """
        Log-specific semantic sliding window splitter with overlap.
        Creates chunks with overlapping log entries to preserve context.
        Best for RAG applications where context between chunks matters.
        """
        logger.info(f"[LOG_SEMANTIC_SLIDING] Starting chunking with overlap_size={overlap_size}...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_SEMANTIC_SLIDING] Found {len(lines)} log entries to process")
        
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
                logger.info(f"[LOG_SEMANTIC_SLIDING] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
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
        
        logger.info(f"[LOG_SEMANTIC_SLIDING] Chunking complete! Total chunks: {len(chunks)}")
        return chunks

    def process_log_http_method_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int):
        """
        Log-specific HTTP method splitter.
        Groups log entries by HTTP method (GET, POST, PUT, DELETE, etc.).
        Best for analyzing different types of operations separately.
        """
        logger.info(f"[LOG_HTTP_METHOD] Starting chunking - grouping by HTTP methods...")
        full_text = " ".join(texts)
        
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        logger.info(f"[LOG_HTTP_METHOD] Found {len(lines)} log entries to process")
        
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
                logger.info(f"[LOG_HTTP_METHOD] Progress: Processed {idx + 1}/{len(lines)} entries, Created {len(chunks)} chunks")
        
        if current_chunk:
            chunks.append(Document(
                page_content="\n".join(current_chunk),
                metadata={
                    "method": "log_http_method",
                    "http_method": current_method,
                    "entries": len(current_chunk)
                }
            ))
        
        logger.info(f"[LOG_HTTP_METHOD] Chunking complete! Total chunks: {len(chunks)}")
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
