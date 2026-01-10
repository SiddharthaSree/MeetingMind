"""
Integrations Service
Export to Slack, Teams, Notion, Email, etc.
"""
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class IntegrationType(Enum):
    """Available integrations"""
    SLACK = "slack"
    TEAMS = "teams"
    EMAIL = "email"
    NOTION = "notion"
    CLIPBOARD = "clipboard"


@dataclass
class IntegrationConfig:
    """Configuration for an integration"""
    type: IntegrationType
    enabled: bool
    webhook_url: Optional[str] = None
    api_key: Optional[str] = None
    channel: Optional[str] = None
    email: Optional[str] = None


class IntegrationsService:
    """
    Service for sharing meeting notes to external platforms
    
    Integrations:
    - Slack: Post to channel via webhook
    - Microsoft Teams: Post via webhook
    - Email: Generate mailto link
    - Notion: Export formatted for Notion
    - Clipboard: Copy formatted text
    """
    
    def __init__(self, config_path: str = None):
        from core.config import MEETINGS_DIR
        from pathlib import Path
        
        self.config_path = Path(config_path or MEETINGS_DIR) / "integrations.json"
        self._configs: Dict[str, IntegrationConfig] = {}
        self._load_configs()
    
    def _load_configs(self):
        """Load integration configurations"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    for name, config in data.items():
                        self._configs[name] = IntegrationConfig(
                            type=IntegrationType(config['type']),
                            enabled=config.get('enabled', False),
                            webhook_url=config.get('webhook_url'),
                            api_key=config.get('api_key'),
                            channel=config.get('channel'),
                            email=config.get('email')
                        )
            except Exception as e:
                print(f"Error loading integration configs: {e}")
    
    def _save_configs(self):
        """Save integration configurations"""
        data = {}
        for name, config in self._configs.items():
            data[name] = {
                'type': config.type.value,
                'enabled': config.enabled,
                'webhook_url': config.webhook_url,
                'api_key': config.api_key,
                'channel': config.channel,
                'email': config.email
            }
        
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def configure(
        self,
        name: str,
        integration_type: IntegrationType,
        **kwargs
    ):
        """Configure an integration"""
        self._configs[name] = IntegrationConfig(
            type=integration_type,
            enabled=True,
            **kwargs
        )
        self._save_configs()
    
    def get_config(self, name: str) -> Optional[IntegrationConfig]:
        """Get configuration for an integration"""
        return self._configs.get(name)
    
    def list_integrations(self) -> List[Dict[str, Any]]:
        """List all configured integrations"""
        return [
            {
                'name': name,
                'type': config.type.value,
                'enabled': config.enabled
            }
            for name, config in self._configs.items()
        ]
    
    # ==================== Slack ====================
    
    def share_to_slack(
        self,
        meeting_data: Dict[str, Any],
        webhook_url: str = None,
        channel: str = None
    ) -> bool:
        """
        Share meeting notes to Slack
        
        Args:
            meeting_data: Meeting data dict
            webhook_url: Slack webhook URL (or use configured)
            channel: Channel to post to
        
        Returns:
            True if successful
        """
        # Use configured webhook if not provided
        config = self._configs.get('slack')
        if not webhook_url and config:
            webhook_url = config.webhook_url
        
        if not webhook_url:
            print("No Slack webhook configured")
            return False
        
        # Format message for Slack
        message = self._format_for_slack(meeting_data)
        
        # Build payload
        payload = {
            "text": message['text'],
            "blocks": message['blocks']
        }
        if channel:
            payload["channel"] = channel
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
            return True
        except Exception as e:
            print(f"Error posting to Slack: {e}")
            return False
    
    def _format_for_slack(self, meeting_data: Dict) -> Dict:
        """Format meeting data for Slack"""
        summary = meeting_data.get('summary', {})
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 Meeting Notes"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Date:* {meeting_data.get('created_at', 'Unknown')[:10]}"
                }
            }
        ]
        
        # Add summary
        if isinstance(summary, dict) and summary.get('summary'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{summary['summary'][:2000]}"
                }
            })
        
        # Add action items
        action_items = summary.get('action_items', []) if isinstance(summary, dict) else []
        if action_items:
            items_text = "*Action Items:*\n"
            for item in action_items[:10]:
                if isinstance(item, dict):
                    items_text += f"• {item.get('description', item)}\n"
                else:
                    items_text += f"• {item}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": items_text
                }
            })
        
        return {
            "text": "Meeting notes shared",
            "blocks": blocks
        }
    
    # ==================== Microsoft Teams ====================
    
    def share_to_teams(
        self,
        meeting_data: Dict[str, Any],
        webhook_url: str = None
    ) -> bool:
        """
        Share meeting notes to Microsoft Teams
        
        Args:
            meeting_data: Meeting data dict
            webhook_url: Teams webhook URL
        
        Returns:
            True if successful
        """
        config = self._configs.get('teams')
        if not webhook_url and config:
            webhook_url = config.webhook_url
        
        if not webhook_url:
            print("No Teams webhook configured")
            return False
        
        # Format for Teams (Adaptive Card)
        card = self._format_for_teams(meeting_data)
        
        try:
            data = json.dumps(card).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req)
            return True
        except Exception as e:
            print(f"Error posting to Teams: {e}")
            return False
    
    def _format_for_teams(self, meeting_data: Dict) -> Dict:
        """Format meeting data for Teams Adaptive Card"""
        summary = meeting_data.get('summary', {})
        
        body = [
            {
                "type": "TextBlock",
                "text": "📋 Meeting Notes",
                "weight": "bolder",
                "size": "large"
            },
            {
                "type": "TextBlock",
                "text": f"Date: {meeting_data.get('created_at', 'Unknown')[:10]}",
                "isSubtle": True
            }
        ]
        
        # Add summary
        if isinstance(summary, dict) and summary.get('summary'):
            body.append({
                "type": "TextBlock",
                "text": "**Summary**",
                "weight": "bolder"
            })
            body.append({
                "type": "TextBlock",
                "text": summary['summary'][:2000],
                "wrap": True
            })
        
        # Add action items
        action_items = summary.get('action_items', []) if isinstance(summary, dict) else []
        if action_items:
            body.append({
                "type": "TextBlock",
                "text": "**Action Items**",
                "weight": "bolder"
            })
            for item in action_items[:10]:
                text = item.get('description', item) if isinstance(item, dict) else item
                body.append({
                    "type": "TextBlock",
                    "text": f"• {text}",
                    "wrap": True
                })
        
        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": body
                    }
                }
            ]
        }
    
    # ==================== Email ====================
    
    def generate_email_link(
        self,
        meeting_data: Dict[str, Any],
        to_email: str = None,
        subject: str = None
    ) -> str:
        """
        Generate a mailto link for sharing via email
        
        Args:
            meeting_data: Meeting data dict
            to_email: Recipient email
            subject: Email subject
        
        Returns:
            mailto: URL
        """
        summary = meeting_data.get('summary', {})
        
        if not subject:
            date = meeting_data.get('created_at', '')[:10]
            subject = f"Meeting Notes - {date}"
        
        # Build email body
        body = "Meeting Notes\n"
        body += "=" * 40 + "\n\n"
        
        if isinstance(summary, dict):
            body += "SUMMARY:\n"
            body += summary.get('summary', 'No summary') + "\n\n"
            
            body += "KEY POINTS:\n"
            body += summary.get('key_points', 'None') + "\n\n"
            
            action_items = summary.get('action_items', [])
            if action_items:
                body += "ACTION ITEMS:\n"
                for item in action_items:
                    text = item.get('description', item) if isinstance(item, dict) else item
                    body += f"- {text}\n"
        
        # URL encode
        params = {
            'subject': subject,
            'body': body
        }
        
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        
        if to_email:
            return f"mailto:{to_email}?{query}"
        return f"mailto:?{query}"
    
    # ==================== Clipboard ====================
    
    def copy_to_clipboard(
        self,
        meeting_data: Dict[str, Any],
        format: str = "markdown"
    ) -> bool:
        """
        Copy meeting notes to clipboard
        
        Args:
            meeting_data: Meeting data dict
            format: Output format (markdown, plain, html)
        
        Returns:
            True if successful
        """
        try:
            import pyperclip
        except ImportError:
            # Fallback for Windows
            import subprocess
            
            text = self._format_plain(meeting_data)
            
            try:
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE,
                    shell=True
                )
                process.communicate(text.encode('utf-8'))
                return True
            except:
                print("Could not copy to clipboard. Install pyperclip: pip install pyperclip")
                return False
        
        if format == "markdown":
            text = self._format_markdown(meeting_data)
        elif format == "html":
            text = self._format_html_simple(meeting_data)
        else:
            text = self._format_plain(meeting_data)
        
        pyperclip.copy(text)
        return True
    
    def _format_plain(self, meeting_data: Dict) -> str:
        """Format as plain text"""
        summary = meeting_data.get('summary', {})
        
        text = "MEETING NOTES\n"
        text += f"Date: {meeting_data.get('created_at', 'Unknown')[:10]}\n\n"
        
        if isinstance(summary, dict):
            text += "SUMMARY:\n"
            text += summary.get('summary', 'No summary') + "\n\n"
            
            action_items = summary.get('action_items', [])
            if action_items:
                text += "ACTION ITEMS:\n"
                for item in action_items:
                    t = item.get('description', item) if isinstance(item, dict) else item
                    text += f"- {t}\n"
        
        return text
    
    def _format_markdown(self, meeting_data: Dict) -> str:
        """Format as Markdown"""
        summary = meeting_data.get('summary', {})
        
        md = "# Meeting Notes\n\n"
        md += f"**Date:** {meeting_data.get('created_at', 'Unknown')[:10]}\n\n"
        
        if isinstance(summary, dict):
            md += "## Summary\n\n"
            md += summary.get('summary', 'No summary') + "\n\n"
            
            md += "## Key Points\n\n"
            md += summary.get('key_points', 'None') + "\n\n"
            
            action_items = summary.get('action_items', [])
            if action_items:
                md += "## Action Items\n\n"
                for item in action_items:
                    t = item.get('description', item) if isinstance(item, dict) else item
                    md += f"- [ ] {t}\n"
        
        return md
    
    def _format_html_simple(self, meeting_data: Dict) -> str:
        """Format as simple HTML"""
        summary = meeting_data.get('summary', {})
        
        html = "<h1>Meeting Notes</h1>\n"
        html += f"<p><strong>Date:</strong> {meeting_data.get('created_at', 'Unknown')[:10]}</p>\n"
        
        if isinstance(summary, dict):
            html += "<h2>Summary</h2>\n"
            html += f"<p>{summary.get('summary', 'No summary')}</p>\n"
            
            action_items = summary.get('action_items', [])
            if action_items:
                html += "<h2>Action Items</h2>\n<ul>\n"
                for item in action_items:
                    t = item.get('description', item) if isinstance(item, dict) else item
                    html += f"<li>{t}</li>\n"
                html += "</ul>\n"
        
        return html
