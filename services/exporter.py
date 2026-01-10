"""
Export Service
Handles exporting meeting notes to various formats and integrations
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import urllib.request
import urllib.error


class ExportFormat(Enum):
    """Supported export formats"""
    MARKDOWN = "markdown"
    JSON = "json"
    TXT = "txt"
    HTML = "html"


class ExportIntegration(Enum):
    """Supported external integrations"""
    NOTION = "notion"
    TODOIST = "todoist"
    # Future: JIRA, ASANA, EMAIL


@dataclass
class ExportResult:
    """Result of an export operation"""
    success: bool
    format: str
    path: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None


class ExportService:
    """
    Service for exporting meeting notes to files and external services
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize export service
        
        Args:
            output_dir: Default directory for file exports
        """
        from core.config import MEETINGS_DIR
        self.output_dir = Path(output_dir or MEETINGS_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Integration credentials (loaded from config)
        self._notion_token: Optional[str] = None
        self._todoist_token: Optional[str] = None
    
    def export(
        self,
        meeting_data: Dict[str, Any],
        format: ExportFormat = ExportFormat.MARKDOWN,
        filename: str = None
    ) -> ExportResult:
        """
        Export meeting notes to a file
        
        Args:
            meeting_data: Meeting data including summary, transcript, etc.
            format: Export format
            filename: Custom filename (auto-generated if not provided)
        
        Returns:
            ExportResult with path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meeting_{timestamp}"
        
        try:
            if format == ExportFormat.MARKDOWN:
                return self._export_markdown(meeting_data, filename)
            elif format == ExportFormat.JSON:
                return self._export_json(meeting_data, filename)
            elif format == ExportFormat.TXT:
                return self._export_txt(meeting_data, filename)
            elif format == ExportFormat.HTML:
                return self._export_html(meeting_data, filename)
            else:
                return ExportResult(
                    success=False,
                    format=format.value,
                    error=f"Unsupported format: {format}"
                )
        except Exception as e:
            return ExportResult(
                success=False,
                format=format.value,
                error=str(e)
            )
    
    def _export_markdown(self, data: Dict, filename: str) -> ExportResult:
        """Export to Markdown format"""
        summary = data.get('summary', {})
        transcript = data.get('transcript', {})
        metadata = data.get('metadata', {})
        
        lines = []
        
        # Header
        lines.append(f"# Meeting Notes")
        lines.append(f"**Date**: {metadata.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
        if metadata.get('participants'):
            lines.append(f"**Participants**: {', '.join(metadata['participants'])}")
        lines.append("")
        
        # Summary
        if summary.get('summary'):
            lines.append("## Summary")
            lines.append(summary['summary'])
            lines.append("")
        
        # Key Points
        if summary.get('key_points'):
            lines.append("## Key Points")
            lines.append(summary['key_points'])
            lines.append("")
        
        # Action Items
        if summary.get('action_items'):
            lines.append("## Action Items")
            for item in summary['action_items']:
                assignee = item.get('assignee', 'Unassigned')
                desc = item.get('description', str(item))
                due = f" (Due: {item['due_date']})" if item.get('due_date') else ""
                lines.append(f"- [ ] **{assignee}**: {desc}{due}")
            lines.append("")
        
        # Decisions
        if summary.get('decisions'):
            lines.append("## Decisions")
            for decision in summary['decisions']:
                lines.append(f"- {decision}")
            lines.append("")
        
        # Transcript (optional)
        if transcript.get('labeled_text'):
            lines.append("## Full Transcript")
            lines.append("```")
            lines.append(transcript['labeled_text'][:5000])  # Limit length
            if len(transcript['labeled_text']) > 5000:
                lines.append("... (truncated)")
            lines.append("```")
        
        content = '\n'.join(lines)
        
        filepath = self.output_dir / f"{filename}.md"
        filepath.write_text(content, encoding='utf-8')
        
        return ExportResult(
            success=True,
            format='markdown',
            path=str(filepath)
        )
    
    def _export_json(self, data: Dict, filename: str) -> ExportResult:
        """Export to JSON format"""
        # Add export metadata
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'version': '2.0',
            **data
        }
        
        filepath = self.output_dir / f"{filename}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return ExportResult(
            success=True,
            format='json',
            path=str(filepath)
        )
    
    def _export_txt(self, data: Dict, filename: str) -> ExportResult:
        """Export to plain text format"""
        summary = data.get('summary', {})
        
        lines = []
        lines.append("MEETING NOTES")
        lines.append("=" * 50)
        lines.append("")
        
        if summary.get('summary'):
            lines.append("SUMMARY")
            lines.append("-" * 30)
            lines.append(summary['summary'])
            lines.append("")
        
        if summary.get('key_points'):
            lines.append("KEY POINTS")
            lines.append("-" * 30)
            lines.append(summary['key_points'])
            lines.append("")
        
        if summary.get('action_items'):
            lines.append("ACTION ITEMS")
            lines.append("-" * 30)
            for item in summary['action_items']:
                assignee = item.get('assignee', 'Unassigned')
                desc = item.get('description', str(item))
                lines.append(f"  * [{assignee}] {desc}")
            lines.append("")
        
        content = '\n'.join(lines)
        
        filepath = self.output_dir / f"{filename}.txt"
        filepath.write_text(content, encoding='utf-8')
        
        return ExportResult(
            success=True,
            format='txt',
            path=str(filepath)
        )
    
    def _export_html(self, data: Dict, filename: str) -> ExportResult:
        """Export to HTML format"""
        summary = data.get('summary', {})
        metadata = data.get('metadata', {})
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Meeting Notes - {metadata.get('date', 'Meeting')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        .action-item {{ background: #f5f5f5; padding: 10px; margin: 5px 0; border-left: 3px solid #4CAF50; }}
        .decision {{ background: #e3f2fd; padding: 10px; margin: 5px 0; border-left: 3px solid #2196F3; }}
        ul {{ padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>📋 Meeting Notes</h1>
    <div class="meta">
        <strong>Date:</strong> {metadata.get('date', datetime.now().strftime('%Y-%m-%d'))}
    </div>
"""
        
        if summary.get('summary'):
            html += f"""
    <h2>📝 Summary</h2>
    <p>{summary['summary']}</p>
"""
        
        if summary.get('key_points'):
            html += f"""
    <h2>🎯 Key Points</h2>
    <p>{summary['key_points'].replace(chr(10), '<br>')}</p>
"""
        
        if summary.get('action_items'):
            html += """
    <h2>✅ Action Items</h2>
"""
            for item in summary['action_items']:
                assignee = item.get('assignee', 'Unassigned')
                desc = item.get('description', str(item))
                html += f'    <div class="action-item"><strong>{assignee}:</strong> {desc}</div>\n'
        
        if summary.get('decisions'):
            html += """
    <h2>🎯 Decisions</h2>
"""
            for decision in summary['decisions']:
                html += f'    <div class="decision">{decision}</div>\n'
        
        html += """
</body>
</html>"""
        
        filepath = self.output_dir / f"{filename}.html"
        filepath.write_text(html, encoding='utf-8')
        
        return ExportResult(
            success=True,
            format='html',
            path=str(filepath)
        )
    
    # ==================== External Integrations ====================
    
    def set_notion_token(self, token: str):
        """Set Notion API token"""
        self._notion_token = token
    
    def set_todoist_token(self, token: str):
        """Set Todoist API token"""
        self._todoist_token = token
    
    def export_to_notion(
        self,
        meeting_data: Dict[str, Any],
        database_id: str = None,
        page_id: str = None
    ) -> ExportResult:
        """
        Export meeting notes to Notion
        
        Args:
            meeting_data: Meeting data
            database_id: Notion database to add to
            page_id: Existing page to update
        
        Returns:
            ExportResult with Notion page URL
        """
        if not self._notion_token:
            return ExportResult(
                success=False,
                format='notion',
                error="Notion token not configured. Set it in Settings."
            )
        
        try:
            summary = meeting_data.get('summary', {})
            metadata = meeting_data.get('metadata', {})
            
            # Build Notion blocks
            blocks = self._build_notion_blocks(summary, metadata)
            
            # Create page via Notion API
            headers = {
                'Authorization': f'Bearer {self._notion_token}',
                'Content-Type': 'application/json',
                'Notion-Version': '2022-06-28'
            }
            
            if database_id:
                # Add to database
                payload = {
                    'parent': {'database_id': database_id},
                    'properties': {
                        'Name': {
                            'title': [{'text': {'content': f"Meeting Notes - {metadata.get('date', 'Today')}"}}]
                        }
                    },
                    'children': blocks
                }
            else:
                # Create standalone page
                payload = {
                    'parent': {'page_id': page_id or 'root'},
                    'properties': {
                        'title': [{'text': {'content': f"Meeting Notes - {metadata.get('date', 'Today')}"}}]
                    },
                    'children': blocks
                }
            
            req = urllib.request.Request(
                'https://api.notion.com/v1/pages',
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read())
                return ExportResult(
                    success=True,
                    format='notion',
                    url=result.get('url')
                )
                
        except urllib.error.HTTPError as e:
            return ExportResult(
                success=False,
                format='notion',
                error=f"Notion API error: {e.code} - {e.read().decode()}"
            )
        except Exception as e:
            return ExportResult(
                success=False,
                format='notion',
                error=str(e)
            )
    
    def _build_notion_blocks(self, summary: Dict, metadata: Dict) -> List[Dict]:
        """Build Notion block structure"""
        blocks = []
        
        # Summary heading
        if summary.get('summary'):
            blocks.append({
                'type': 'heading_2',
                'heading_2': {'rich_text': [{'text': {'content': 'Summary'}}]}
            })
            blocks.append({
                'type': 'paragraph',
                'paragraph': {'rich_text': [{'text': {'content': summary['summary'][:2000]}}]}
            })
        
        # Action items as to-do blocks
        if summary.get('action_items'):
            blocks.append({
                'type': 'heading_2',
                'heading_2': {'rich_text': [{'text': {'content': 'Action Items'}}]}
            })
            for item in summary['action_items']:
                desc = item.get('description', str(item))
                assignee = item.get('assignee', '')
                text = f"[{assignee}] {desc}" if assignee else desc
                blocks.append({
                    'type': 'to_do',
                    'to_do': {
                        'rich_text': [{'text': {'content': text[:2000]}}],
                        'checked': False
                    }
                })
        
        return blocks
    
    def export_action_items_to_todoist(
        self,
        meeting_data: Dict[str, Any],
        project_id: str = None
    ) -> ExportResult:
        """
        Export action items to Todoist
        
        Args:
            meeting_data: Meeting data
            project_id: Todoist project ID (uses Inbox if not specified)
        
        Returns:
            ExportResult
        """
        if not self._todoist_token:
            return ExportResult(
                success=False,
                format='todoist',
                error="Todoist token not configured. Set it in Settings."
            )
        
        try:
            summary = meeting_data.get('summary', {})
            action_items = summary.get('action_items', [])
            
            if not action_items:
                return ExportResult(
                    success=True,
                    format='todoist',
                    error="No action items to export"
                )
            
            headers = {
                'Authorization': f'Bearer {self._todoist_token}',
                'Content-Type': 'application/json'
            }
            
            created_tasks = []
            
            for item in action_items:
                desc = item.get('description', str(item))
                assignee = item.get('assignee', '')
                due = item.get('due_date')
                
                content = f"[Meeting] {desc}"
                if assignee:
                    content += f" (@{assignee})"
                
                payload = {
                    'content': content,
                    'description': f"From meeting notes"
                }
                
                if project_id:
                    payload['project_id'] = project_id
                
                if due:
                    payload['due_string'] = due
                
                req = urllib.request.Request(
                    'https://api.todoist.com/rest/v2/tasks',
                    data=json.dumps(payload).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read())
                    created_tasks.append(result.get('id'))
            
            return ExportResult(
                success=True,
                format='todoist',
                url=f"https://todoist.com/app/project/{project_id}" if project_id else "https://todoist.com/app/inbox"
            )
            
        except urllib.error.HTTPError as e:
            return ExportResult(
                success=False,
                format='todoist',
                error=f"Todoist API error: {e.code}"
            )
        except Exception as e:
            return ExportResult(
                success=False,
                format='todoist',
                error=str(e)
            )
    
    def get_available_exports(self) -> List[Dict[str, Any]]:
        """Get list of available export options"""
        exports = [
            {'id': 'markdown', 'name': 'Markdown (.md)', 'available': True},
            {'id': 'json', 'name': 'JSON (.json)', 'available': True},
            {'id': 'txt', 'name': 'Plain Text (.txt)', 'available': True},
            {'id': 'html', 'name': 'HTML (.html)', 'available': True},
            {'id': 'notion', 'name': 'Notion', 'available': bool(self._notion_token)},
            {'id': 'todoist', 'name': 'Todoist (Action Items)', 'available': bool(self._todoist_token)},
        ]
        return exports
