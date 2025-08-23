import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
import networkx as nx


class TopologyRenderer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.assets_dir = Path(__file__).parent.parent / "assets"
        if not self.assets_dir.exists():
            self.logger.warning(f"Assets folder not found: {self.assets_dir}")

        # Map device type → icon file name
        self.icon_map = {
            "router": "wifi-router.png",
            "pc": "monitor.png",
            "laptop": "laptop.png",
            "switch": "hub.png",
        }

    def render_interactive_topology(self, G: nx.Graph, output_file: Path):
        """
        Render network topology as interactive HTML with device icons & tooltips.
        """
        try:
            from pyvis.network import Network
        except ImportError:
            self.logger.error("pyvis is not installed. Run: pip install pyvis")
            raise

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Create PyVis network
        net = Network(
            height="100%",
            width="100%",
            bgcolor="#ffffff",
            font_color="#111827",
            directed=False,
            cdn_resources="in_line",   # keep everything in one HTML file
        )

        # Barnes-Hut physics layout
        net.barnes_hut(
            gravity=-2000,
            central_gravity=0.3,
            spring_length=160,
            spring_strength=0.02,
            damping=0.85,
            overlap=0.1
        )

        # Interaction + physics settings
        net.set_options("""
        {
          "interaction": { "hover": true, "tooltipDelay": 100, "navigationButtons": true },
          "physics": { "enabled": true, "stabilization": { "iterations": 800 } }
        }
        """)

        # Add nodes with icons
        for nid, data in G.nodes(data=True):
            label = data.get("label", str(nid))
            title = data.get("title", f"Device: {label}")
            device_type = (data.get("device_type") or "").lower()

            icon_key = data.get("device_icon", device_type if device_type in self.icon_map else "router")
            image_path = self._resolve_icon(icon_key, output_file.parent)

            if image_path:
                # Device with icon
                net.add_node(
                    nid,
                    label=label,
                    title=title,     # tooltip text
                    shape="image",
                    image=image_path,
                    size=self._get_node_size(device_type)
                )
            else:
                # Fallback: dot node
                net.add_node(
                    nid,
                    label=label,
                    title=title,
                    shape="dot",
                    size=18
                )

        # Add edges
        for u, v, ed in G.edges(data=True):
            title = ed.get("title", f"{u} ↔ {v}")
            bandwidth = ed.get("bandwidth_mbps", ed.get("bandwidth", 0))

            net.add_edge(
                u,
                v,
                title=title,
                width=1.0 if not bandwidth else max(1.0, min(10.0, (1.5 + (float(bandwidth) ** 0.35))))
            )

        # Generate clean HTML (only graph)
        net.show(str(output_file))
        self.logger.info(f"Interactive topology saved to {output_file}")

    # ---------- Helpers ----------

    def _resolve_icon(self, icon_key: str, out_dir: Path) -> Optional[str]:
        """Return relative path for icon if available."""
        filename = self.icon_map.get(icon_key)
        if not filename:
            return None
        icon_path = self.assets_dir / filename
        if icon_path.is_file():
            try:
                return os.path.relpath(icon_path.resolve(), out_dir.resolve())
            except Exception:
                return str(icon_path.resolve())
        return None

    def _get_node_size(self, device_type: str) -> int:
        """Different sizes for different device types (for clarity)."""
        size_map = {
            "router": 45,
            "switch": 40,
            "pc": 30,
            "laptop": 30
        }
        return size_map.get(device_type, 35)
