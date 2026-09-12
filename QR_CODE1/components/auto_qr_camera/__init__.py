import os
import streamlit.components.v1 as components

_COMPONENT_DIR = os.path.join(os.path.dirname(__file__))
_auto_qr_camera = components.declare_component(
    "auto_qr_camera",
    path=_COMPONENT_DIR,
)


def auto_qr_camera(key=None):
    """Open the device camera and automatically capture when a QR code is detected."""
    return _auto_qr_camera(key=key, default=None)
