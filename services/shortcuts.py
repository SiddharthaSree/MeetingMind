"""
Keyboard Shortcuts Service
Global hotkeys for power users
"""
import threading
from typing import Callable, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ShortcutAction(Enum):
    """Available shortcut actions"""
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"
    TOGGLE_RECORDING = "toggle_recording"
    ADD_BOOKMARK = "add_bookmark"
    MARK_ACTION_ITEM = "mark_action_item"
    MARK_DECISION = "mark_decision"
    OPEN_UI = "open_ui"
    MINIMIZE_TO_TRAY = "minimize_to_tray"


@dataclass
class Shortcut:
    """A keyboard shortcut"""
    action: ShortcutAction
    key_combo: str  # e.g., "ctrl+shift+r"
    description: str
    enabled: bool = True


# Default shortcuts
DEFAULT_SHORTCUTS = {
    ShortcutAction.TOGGLE_RECORDING: Shortcut(
        action=ShortcutAction.TOGGLE_RECORDING,
        key_combo="ctrl+shift+r",
        description="Start/Stop Recording"
    ),
    ShortcutAction.ADD_BOOKMARK: Shortcut(
        action=ShortcutAction.ADD_BOOKMARK,
        key_combo="ctrl+shift+b",
        description="Add Bookmark at Current Time"
    ),
    ShortcutAction.MARK_ACTION_ITEM: Shortcut(
        action=ShortcutAction.MARK_ACTION_ITEM,
        key_combo="ctrl+shift+a",
        description="Mark as Action Item"
    ),
    ShortcutAction.MARK_DECISION: Shortcut(
        action=ShortcutAction.MARK_DECISION,
        key_combo="ctrl+shift+d",
        description="Mark as Decision"
    ),
    ShortcutAction.OPEN_UI: Shortcut(
        action=ShortcutAction.OPEN_UI,
        key_combo="ctrl+shift+m",
        description="Open MeetingMind UI"
    ),
}


class KeyboardShortcuts:
    """
    Manages global keyboard shortcuts
    
    Uses pynput for cross-platform hotkey support
    """
    
    def __init__(self):
        self.shortcuts: Dict[ShortcutAction, Shortcut] = DEFAULT_SHORTCUTS.copy()
        self.callbacks: Dict[ShortcutAction, Callable] = {}
        self._listener = None
        self._running = False
        self._current_keys = set()
    
    def register(self, action: ShortcutAction, callback: Callable):
        """Register a callback for a shortcut action"""
        self.callbacks[action] = callback
    
    def set_shortcut(self, action: ShortcutAction, key_combo: str):
        """Change the key combination for an action"""
        if action in self.shortcuts:
            self.shortcuts[action].key_combo = key_combo
    
    def enable(self, action: ShortcutAction):
        """Enable a shortcut"""
        if action in self.shortcuts:
            self.shortcuts[action].enabled = True
    
    def disable(self, action: ShortcutAction):
        """Disable a shortcut"""
        if action in self.shortcuts:
            self.shortcuts[action].enabled = False
    
    def start(self):
        """Start listening for keyboard shortcuts"""
        if self._running:
            return
        
        try:
            from pynput import keyboard
            
            def on_press(key):
                try:
                    # Convert key to string
                    if hasattr(key, 'char') and key.char:
                        key_str = key.char.lower()
                    else:
                        key_str = str(key).replace('Key.', '').lower()
                    
                    self._current_keys.add(key_str)
                    self._check_shortcuts()
                except:
                    pass
            
            def on_release(key):
                try:
                    if hasattr(key, 'char') and key.char:
                        key_str = key.char.lower()
                    else:
                        key_str = str(key).replace('Key.', '').lower()
                    
                    self._current_keys.discard(key_str)
                except:
                    pass
            
            self._listener = keyboard.Listener(
                on_press=on_press,
                on_release=on_release
            )
            self._listener.start()
            self._running = True
            print("Keyboard shortcuts enabled")
            
        except ImportError:
            print("pynput not installed. Keyboard shortcuts disabled.")
            print("Install with: pip install pynput")
        except Exception as e:
            print(f"Could not start keyboard listener: {e}")
    
    def stop(self):
        """Stop listening for keyboard shortcuts"""
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._running = False
        self._current_keys.clear()
    
    def _check_shortcuts(self):
        """Check if current keys match any shortcut"""
        for shortcut in self.shortcuts.values():
            if not shortcut.enabled:
                continue
            
            # Parse key combo
            required_keys = set(shortcut.key_combo.lower().split('+'))
            
            # Normalize key names
            normalized_current = set()
            for key in self._current_keys:
                # Map common variations
                if key in ('ctrl_l', 'ctrl_r', 'control'):
                    normalized_current.add('ctrl')
                elif key in ('shift_l', 'shift_r'):
                    normalized_current.add('shift')
                elif key in ('alt_l', 'alt_r', 'alt_gr'):
                    normalized_current.add('alt')
                else:
                    normalized_current.add(key)
            
            # Check match
            if required_keys == normalized_current:
                self._trigger_action(shortcut.action)
    
    def _trigger_action(self, action: ShortcutAction):
        """Trigger the callback for an action"""
        callback = self.callbacks.get(action)
        if callback:
            # Run in separate thread to not block keyboard listener
            threading.Thread(target=callback, daemon=True).start()
    
    def get_shortcuts_help(self) -> str:
        """Get formatted help text for shortcuts"""
        lines = ["Keyboard Shortcuts:", "=" * 40]
        
        for shortcut in self.shortcuts.values():
            status = "✓" if shortcut.enabled else "✗"
            lines.append(f"{status} {shortcut.key_combo:20} - {shortcut.description}")
        
        return "\n".join(lines)
    
    def list_shortcuts(self) -> Dict[str, Dict]:
        """List all shortcuts as dict"""
        return {
            action.value: {
                'key_combo': shortcut.key_combo,
                'description': shortcut.description,
                'enabled': shortcut.enabled
            }
            for action, shortcut in self.shortcuts.items()
        }


# Global instance
_shortcuts: Optional[KeyboardShortcuts] = None


def get_shortcuts() -> KeyboardShortcuts:
    """Get the global keyboard shortcuts instance"""
    global _shortcuts
    if _shortcuts is None:
        _shortcuts = KeyboardShortcuts()
    return _shortcuts
