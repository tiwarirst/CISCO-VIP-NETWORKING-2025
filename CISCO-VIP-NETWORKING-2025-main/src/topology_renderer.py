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

        # Enhanced icon mapping - keeping original plus adding more
        self.icon_map = {
            "router": "wifi-router.png",
            "pc": "monitor.png",
            "laptop": "laptop.png",
            "switch": "hub.png",
            "server": "server.png",  # Added
            "firewall": "firewall.png",  # Added
            "access_point": "wifi.png",  # Added
        }
        
        # Enhanced device colors for better visual distinction
        self.device_colors = {
            "router": "#c92a2a",
            "switch": "#1971c2", 
            "pc": "#37b24d",
            "laptop": "#fab005",
            "server": "#7048e8",  # Added
            "firewall": "#d6336c",  # Added
            "access_point": "#12b886",  # Added
            "unknown": "#666666"
        }
        
        # Device symbols as fallback when icons not found
        self.device_symbols = {
            "router": "🔀",
            "pc": "🖥️", 
            "laptop": "💻",
            "switch": "🔗",
            "server": "🖥️",
            "firewall": "🛡️",
            "access_point": "📡",
            "unknown": "⚫"
        }
        
        self.priority_colors = {
            "critical": "#8B0000",
            "high": "#FF6347",
            "medium": "#4682B4",
            "low": "#32CD32",
            "unknown": "#808080",
        }

    def render_interactive_topology(self, G: nx.Graph, output_file: Path):
        try:
            from pyvis.network import Network
        except ImportError:
            self.logger.error("pyvis is not installed. Run: pip install pyvis")
            raise

        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Enhanced network settings for better topology visualization
        net = Network(
            height="100vh",  # Full viewport height
            width="100vw",   # Full viewport width
            bgcolor="#f8f9fa",
            font_color="#212529",
            directed=False,
            cdn_resources="local",
        )

        # Enhanced physics for better node positioning
        net.barnes_hut(
            gravity=-3000,
            central_gravity=0.1,
            spring_length=200,
            spring_strength=0.015,
            damping=0.95,
            overlap=0.1
        )

        # Enhanced visualization options
        net.set_options("""
        {
          "interaction": { 
            "hover": true, 
            "tooltipDelay": 200, 
            "multiselect": true, 
            "navigationButtons": true 
          },
          "physics": {
            "enabled": true,
            "stabilization": { 
              "enabled": true, 
              "fit": true, 
              "iterations": 1000, 
              "updateInterval": 50 
            }
          },
          "nodes": { 
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.2)",
              "size": 8
            },
            "font": { "size": 14, "face": "Arial, sans-serif" },
            "borderWidth": 3,
            "size": 25
          },
          "edges": { 
            "smooth": { "type": "continuous", "roundness": 0.3 }, 
            "shadow": false,
            "font": { "size": 12 }
          }
        }
        """)

        # Enhanced node creation
        for nid, data in G.nodes(data=True):
            label = data.get("label", nid)
            title = data.get("title", label)
            device_type = (data.get("device_type") or "").lower()
            icon_key = data.get("device_icon", device_type if device_type in self.icon_map else "router")
            image_path = self._resolve_icon(icon_key, output_file.parent)

            # Enhanced tooltip
            tooltip_parts = [f"<b>{label}</b>"]
            if data.get('device_type'):
                tooltip_parts.append(f"Type: {data['device_type']}")
            if data.get('ip_address'):
                tooltip_parts.append(f"IP: {data['ip_address']}")
            enhanced_title = "<br>".join(tooltip_parts)

            if image_path:
                net.add_node(
                    nid, 
                    label=label, 
                    title=enhanced_title, 
                    shape="image", 
                    image=image_path,
                    size=40,  # Larger size
                    borderWidth=3, 
                    color={"border": self._device_border_color(device_type)}
                )
            else:
                # Fallback with device symbols and colors
                symbol = self.device_symbols.get(device_type, self.device_symbols["unknown"])
                color = self.device_colors.get(device_type, self.device_colors["unknown"])
                
                net.add_node(
                    nid, 
                    label=f"{symbol}\n{label}", 
                    title=enhanced_title, 
                    shape="dot", 
                    size=30,  # Larger size
                    color={
                        "background": color + "40",  # Add transparency
                        "border": color,
                        "highlight": {"background": color + "60", "border": color}
                    },
                    font={"size": 12}
                )

        # Enhanced edge creation
        for u, v, ed in G.edges(data=True):
            title = ed.get("title", f"{u} ↔ {v}")
            bandwidth = ed.get("bandwidth_mbps", ed.get("bandwidth", 0))
            priority = ed.get("priority", "unknown")
            style = self._edge_style(ed.get("link_type", "subnet"), float(bandwidth), priority)
            style["title"] = self._edge_title(title, ed)

            # Enhanced bandwidth-based width calculation
            bw = float(bandwidth or 0)
            if bw >= 10000:
                style["width"] = 8
            elif bw >= 1000:
                style["width"] = 6
            elif bw >= 100:
                style["width"] = 4
            elif bw > 0:
                style["width"] = 2
            else:
                style["width"] = 1

            net.add_edge(u, v, **style)

        # Generate HTML with full-page styling
        try:
            pyvis_html = net.generate_html()
        except AttributeError:
            tmp = output_file.with_suffix(".tmp.html")
            net.write_html(str(tmp))
            pyvis_html = tmp.read_text(encoding="utf-8")
            tmp.unlink(missing_ok=True)

        # Apply full-page styling
        full_page_style = """
<style>
body, html {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    background: #f8f9fa !important;
}
#mynetworkid {
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}
</style>
"""
        
        # Insert full-page style
        head_idx = pyvis_html.lower().find("</head>")
        if head_idx != -1:
            pyvis_html = pyvis_html[:head_idx] + full_page_style + pyvis_html[head_idx:]

        # Add enhanced controls and legend
        final_html = self._inject_before_body_end(pyvis_html, self._controls_and_legend_html())
        output_file.write_text(final_html, encoding="utf-8")
        self.logger.info(f"Enhanced interactive topology saved to {output_file}")

    # ---------- Helpers (keeping all original methods) ----------

    def _resolve_icon(self, icon_key: str, out_dir: Path) -> Optional[str]:
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

    def _device_border_color(self, device_type: str) -> str:
        # Enhanced with more device types
        colors = {
            "router": "#c92a2a",
            "switch": "#1971c2",
            "pc": "#37b24d",
            "laptop": "#fab005",
            "server": "#7048e8",
            "firewall": "#d6336c", 
            "access_point": "#12b886",
        }
        return colors.get(device_type, "#666666")

    def _edge_style(
        self, link_type: str, bandwidth_mbps: float, priority: str
    ) -> Dict[str, Any]:
        base = {
            "subnet": {"width": 4, "dashes": False},  # Thicker default
            "ospf": {"width": 3, "dashes": [8, 4]},
            "bgp": {"width": 3, "dashes": [12, 6]},
            "description": {"width": 2, "dashes": [4, 4]},
        }.get(link_type, {"width": 3, "dashes": False})

        # Enhanced bandwidth scaling
        if bandwidth_mbps >= 10000:
            base["width"] = max(base["width"], 8)
        elif bandwidth_mbps >= 1000:
            base["width"] = max(base["width"], 6)
        elif bandwidth_mbps < 100:
            base["width"] = max(base["width"] - 1, 1)

        # Enhanced priority colors
        priority_colors = {
            "critical": {"color": "#dc3545", "highlight": "#c82333"},
            "high": {"color": "#fd7e14", "highlight": "#e8690b"}, 
            "medium": {"color": "#0d6efd", "highlight": "#0b5ed7"},
            "low": {"color": "#198754", "highlight": "#146c43"},
        }
        
        if priority.lower() in priority_colors:
            base["color"] = priority_colors[priority.lower()]
        else:
            base["color"] = self.priority_colors.get(priority, "#808080")

        if link_type == "bgp":
            base["arrows"] = {"to": {"enabled": True, "scaleFactor": 0.5}}

        return base

    def _edge_title(self, title: str, ed: Dict[str, Any]) -> str:
        bw = ed.get("bandwidth_mbps")
        util = ed.get("utilization_percent")
        prio = ed.get("priority")
        link_type = ed.get("link_type")

        parts = [f"<b>{title}</b>"]  # Enhanced with bold
        if link_type:
            parts.append(f"Type: {link_type.upper()}")
        if bw is not None:
            try:
                parts.append(f"Bandwidth: {float(bw):.0f} Mbps")
            except Exception:
                parts.append(f"Bandwidth: {bw}")
        if util is not None:
            try:
                parts.append(f"Utilization: {float(util):.1f}%")
            except Exception:
                parts.append(f"Utilization: {util}%")
        if prio:
            parts.append(f"Priority: {prio}")
        return "<br>".join(parts)  # Enhanced with HTML breaks

    def _inject_before_body_end(self, base_html: str, injection: str) -> str:
        idx = base_html.lower().rfind("</body>")
        if idx == -1:
            return base_html + injection
        return base_html[:idx] + injection + base_html[idx:]

    def _controls_and_legend_html(self) -> str:
        return """
<!-- Enhanced Floating Controls and Legend -->
<style>
  .floating-panel {
    position: fixed; top: 20px; right: 20px; z-index: 9999;
    background: rgba(248, 249, 250, 0.95); 
    backdrop-filter: blur(10px);
    border: 1px solid #dee2e6; 
    padding: 15px; 
    border-radius: 10px; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
    font-size: 13px;
    min-width: 200px;
  }
  .floating-panel h4 { 
    margin: 0 0 10px 0; font-size: 16px; font-weight: 600; color: #212529;
  }
  .floating-panel .row { 
    margin: 8px 0; display: flex; gap: 8px; flex-wrap: wrap;
  }
  .floating-panel button { 
    background: #0d6efd; color: white; border: none;
    padding: 6px 12px; border-radius: 5px; cursor: pointer;
    font-size: 12px; transition: all 0.2s;
  }
  .floating-panel button:hover {
    background: #0b5ed7; transform: translateY(-1px);
  }
  .legend-section {
    margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;
  }
  .legend-item {
    display: flex; align-items: center; margin: 6px 0; font-size: 12px;
  }
  .legend-line { 
    width: 20px; height: 3px; margin-right: 8px;
  }
  .legend-dashed {
    background: repeating-linear-gradient(to right, #000 0px, #000 8px, transparent 8px, transparent 12px);
  }
</style>
<div class="floating-panel">
  <h4>🔧 Topology Controls</h4>
  <div class="row">
    <button id="fitBtn">📍 Fit View</button>
    <button id="togglePhysicsBtn">⚡ Physics</button>
  </div>
  <div class="row">
    <button id="zoomInBtn">🔍 Zoom In</button>
    <button id="zoomOutBtn">🔍 Zoom Out</button>
  </div>
  
  <div class="legend-section">
    <h4>📋 Legend</h4>
    <div class="legend-item">
      <div class="legend-line" style="background: #495057;"></div>
      <span>Subnet Links</span>
    </div>
    <div class="legend-item">
      <div class="legend-line legend-dashed" style="background-color: #1971c2;"></div>
      <span>OSPF Links</span>
    </div>
    <div class="legend-item">
      <div class="legend-line legend-dashed" style="background-color: #c92a2a;"></div>
      <span>BGP Links</span>
    </div>
    <div style="margin-top: 10px; font-size: 11px; color: #6c757d;">
      💡 Hover for details • 🖱️ Drag to move • 🔄 Scroll to zoom
    </div>
  </div>
</div>

<script>
(function() {
  function wireUp() {
    try {
      if (typeof network === "undefined") {
        return setTimeout(wireUp, 100);
      }
      var physicsEnabled = true;

      // Fit button
      var fitBtn = document.getElementById("fitBtn");
      if (fitBtn) {
        fitBtn.addEventListener("click", function() {
          try { network.fit({animation: {duration: 1000}}); } 
          catch (e) { console.warn("fit() failed:", e); }
        });
      }

      // Physics toggle
      var toggleBtn = document.getElementById("togglePhysicsBtn");
      if (toggleBtn) {
        toggleBtn.addEventListener("click", function() {
          physicsEnabled = !physicsEnabled;
          try { 
            network.setOptions({ physics: { enabled: physicsEnabled } });
            toggleBtn.textContent = physicsEnabled ? "⚡ Physics" : "⏸️ Physics";
          } catch (e) { console.warn("toggle physics failed:", e); }
        });
      }

      // Zoom controls
      var zoomInBtn = document.getElementById("zoomInBtn");
      var zoomOutBtn = document.getElementById("zoomOutBtn");
      
      if (zoomInBtn) {
        zoomInBtn.addEventListener("click", function() {
          try {
            var scale = network.getScale() * 1.2;
            network.moveTo({scale: scale, animation: {duration: 300}});
          } catch (e) { console.warn("Zoom in failed:", e); }
        });
      }
      
      if (zoomOutBtn) {
        zoomOutBtn.addEventListener("click", function() {
          try {
            var scale = network.getScale() / 1.2;
            network.moveTo({scale: scale, animation: {duration: 300}});
          } catch (e) { console.warn("Zoom out failed:", e); }
        });
      }

      // Auto-fit after stabilization
      network.on("stabilizationIterationsDone", function () {
        setTimeout(function() {
          try { network.fit({animation: {duration: 1000}}); }
          catch (e) { console.warn("Initial fit failed:", e); }
        }, 500);
      });
      
    } catch (e) {
      console.warn("Control wiring error:", e);
      setTimeout(wireUp, 100);
    }
  }
  
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wireUp);
  } else {
    wireUp();
  }
})();
</script>
"""