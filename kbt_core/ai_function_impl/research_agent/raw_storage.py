import hashlib
from pathlib import Path

def write_document(raw_base_dir: str, topic_keyword: str, site_context_url: str, version: str,  content_id: str, content: str) -> str:
    """Write a document content to a special raw storage: to a file raw/{topic_keyword}/{version}/{content_md5_hash}.md
    Returns document path
    """
    raw_dir = Path(f"{raw_base_dir}/{topic_keyword}/{site_context_url}/{version}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    file_path = raw_dir / f"{content_id}.md"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)
