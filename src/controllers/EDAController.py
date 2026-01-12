from .BaseController import BaseController
from .ProjectController import ProjectController
import re
import os
import logging
from typing import Dict, Any

logger = logging.getLogger('uvicorn.error')

class EDAController(BaseController):
    def __init__(self, project_id: str, file_id: str):
        super().__init__()
        self.project_id = project_id
        self.file_id = file_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)
        self.file_path = os.path.join(self.project_path, file_id)

    def analyze_log(self) -> Dict[str, Any]:
        if not os.path.exists(self.file_path):
            return {"error": f"File not found: {self.file_path}"}

        # Parsing logic - optimized for zero-footprint memory usage
        log_pattern = re.compile(r'(?P<ip>\S+) - - \[(?P<timestamp>.*?)\] "(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+|-)')
        
        # Aggregators
        total_requests = 0
        unique_ips = set()
        total_size = 0
        error_count = 0
        status_counts = {}
        ip_counts = {}
        url_counts = {}
        hourly_traffic = {}

        try:
            line_count = 0
            # latin-1 is safer for logs as it never fails on weird bytes
            with open(self.file_path, 'r', encoding='latin-1', errors='ignore') as f:
                for line in f:
                    line_count += 1
                    if line_count % 100000 == 0:
                        logger.info(f"EDA Processed {line_count} lines...")

                    match = log_pattern.match(line)
                    if not match:
                        continue
                    
                    data = match.groupdict()
                    total_requests += 1
                    
                    # IP logic
                    ip = data['ip']
                    if len(unique_ips) < 10000 or ip in unique_ips:
                        unique_ips.add(ip)
                        ip_counts[ip] = ip_counts.get(ip, 0) + 1
                    
                    # Status logic
                    try:
                        status = int(data['status'])
                        status_counts[status] = status_counts.get(status, 0) + 1
                        if status >= 400:
                            error_count += 1
                    except:
                        pass
                    
                    # Size logic
                    try:
                        sz = data['size']
                        size_val = int(sz) if sz != '-' else 0
                        total_size += size_val
                    except:
                        pass
                    
                    # URL logic
                    url = data['url']
                    if len(url_counts) < 10000 or url in url_counts:
                         url_counts[url] = url_counts.get(url, 0) + 1
                    
                    # Time logic
                    try:
                        # Extract "10/Jan/2026:05" from "10/Jan/2026:05:14:22 +0000"
                        parts = data['timestamp'].split(':')
                        if len(parts) >= 2:
                            ts_hour = parts[0] + ":" + parts[1]
                            if len(hourly_traffic) < 5000: # ~7 months of hourly data
                                hourly_traffic[ts_hour] = hourly_traffic.get(ts_hour, 0) + 1
                    except Exception as e:
                        pass
            
            logger.info(f"EDA Finished reading {line_count} lines. Total valid: {total_requests}")
        except Exception as e:
             logger.error(f"Error reading file at line {line_count}: {str(e)}")
             return {"error": f"Error reading file: {str(e)}"}

        
        if total_requests == 0:
            return {"error": "No valid log lines found"}

        # Format and Sort Data for Charts
        
        # 1. Top IPs (Top 10)
        sorted_ips = dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 2. Top URLs (Top 10)
        sorted_urls = dict(sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 3. Traffic Over Time (Sorted by time)
        sorted_hours = sorted(hourly_traffic.keys())
        traffic_data = {
            "labels": sorted_hours,
            "values": [hourly_traffic[h] for h in sorted_hours]
        }

        metrics = {
            "total_requests": total_requests,
            "unique_visitors": len(unique_ips),
            "total_bandwidth_mb": round(total_size / (1024 * 1024), 2),
            "error_rate": round((error_count / total_requests * 100), 2) if total_requests > 0 else 0,
            "avg_response_size": round(total_size / total_requests, 2) if total_requests > 0 else 0
        }

        return {
            "metrics": metrics,
            "charts": {
                "status_counts": status_counts,
                "top_ips": sorted_ips,
                "top_urls": sorted_urls,
                "traffic_over_time": traffic_data
            }
        }


