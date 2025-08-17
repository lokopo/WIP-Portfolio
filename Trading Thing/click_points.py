#!/usr/bin/env python3

import os
import json
from typing import Any, Dict, List, Optional

try:
	import pyautogui
except Exception:
	pyautogui = None

# Default scripts directory; can be overridden via set_scripts_dir()
SCRIPTS_DIR: Optional[str] = None


class ClickPointError(Exception):
	pass


def set_scripts_dir(path: str) -> None:
	global SCRIPTS_DIR
	SCRIPTS_DIR = path


def get_scripts_dir() -> str:
	if SCRIPTS_DIR:
		return SCRIPTS_DIR
	# Fallback: assume sibling project "Pyautogui Suped Up/scripts"
	base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Pyautogui Suped Up", "scripts"))
	return base_dir


def scripts_dir_exists() -> bool:
	return os.path.isdir(get_scripts_dir())


def script_exists(script_name: str) -> bool:
	path = os.path.join(get_scripts_dir(), f"{script_name}.json")
	return os.path.isfile(path)


def _load_script_data(script_name: str) -> Dict[str, Any]:
	path = os.path.join(get_scripts_dir(), f"{script_name}.json")
	if not os.path.isfile(path):
		raise ClickPointError(f"Script not found: {path}")
	with open(path, "r") as f:
		return json.load(f)


def _is_click_command(cmd: Dict[str, Any]) -> bool:
	# Enhanced PyAutoGUI saves type as numeric enum value; CLICK is 1.
	# Support string fallback if schema changes.
	cmd_type = cmd.get("type")
	return cmd_type == 1 or cmd_type == "CLICK"


def get_click_positions(script_name: str) -> List[Dict[str, int]]:
	"""Return list of click command positions with applied offsets."""
	data = _load_script_data(script_name)
	commands = data.get("commands", [])
	clicks: List[Dict[str, int]] = []
	for cmd in commands:
		if _is_click_command(cmd):
			x = int(cmd.get("x", 0))
			y = int(cmd.get("y", 0))
			offset_x = int(cmd.get("offset_x", 0) or 0)
			offset_y = int(cmd.get("offset_y", 0) or 0)
			clicks.append({"x": x + offset_x, "y": y + offset_y})
	return clicks


def click_index(script_name: str, index: int, extra_offset_x: int = 0, extra_offset_y: int = 0) -> bool:
	"""
	Click the Nth click command from a saved script.
	- Returns True if a click was performed, False otherwise.
	"""
	if pyautogui is None:
		return False
	try:
		clicks = get_click_positions(script_name)
		if index < 0 or index >= len(clicks):
			return False
		pos = clicks[index]
		x = pos["x"] + int(extra_offset_x)
		y = pos["y"] + int(extra_offset_y)
		pyautogui.click(x, y)
		return True
	except Exception:
		return False


def click_first(script_name: str, extra_offset_x: int = 0, extra_offset_y: int = 0) -> bool:
	return click_index(script_name, 0, extra_offset_x, extra_offset_y)