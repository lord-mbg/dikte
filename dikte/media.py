"""Pause and resume active media playback during dictation / speech."""

from __future__ import annotations

import shutil
import subprocess


def _find_qdbus() -> str | None:
    return shutil.which("qdbus6") or shutil.which("qdbus")


def pause_media() -> list[str]:
    """Pause any currently playing media player via MPRIS.

    Returns the list of service names that were playing and got paused.
    """
    qdbus = _find_qdbus()
    if not qdbus:
        return []
    paused: list[str] = []
    try:
        proc = subprocess.run(
            [qdbus],
            capture_output=True,
            text=True,
            timeout=1.0,
            check=False,
        )
        for line in proc.stdout.splitlines():
            svc = line.strip()
            if svc.startswith("org.mpris.MediaPlayer2."):
                try:
                    status_proc = subprocess.run(
                        [qdbus, svc, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.PlaybackStatus"],
                        capture_output=True,
                        text=True,
                        timeout=0.5,
                        check=False,
                    )
                    if status_proc.stdout.strip() == "Playing":
                        subprocess.run(
                            [qdbus, svc, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.Pause"],
                            capture_output=True,
                            timeout=0.5,
                            check=False,
                        )
                        paused.append(svc)
                except Exception:
                    pass
    except Exception:
        pass
    return paused


def resume_media(services: list[str]) -> None:
    """Resume playback for previously paused media players."""
    if not services:
        return
    qdbus = _find_qdbus()
    if not qdbus:
        return
    for svc in services:
        try:
            subprocess.run(
                [qdbus, svc, "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player.Play"],
                capture_output=True,
                timeout=0.5,
                check=False,
            )
        except Exception:
            pass
