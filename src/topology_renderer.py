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
            "server": "server.png",
            "firewall": "firewall.png",
            "access_point": "wifi.png",
        }
        
        # Cisco Packet Tracer style device representations (SVG-based)
        self.cisco_device_svgs = {
            "router": self._create_router_svg(),
            "switch": self._create_switch_svg(), 
            "pc": self._create_pc_svg(),
            "laptop": self._create_laptop_svg(),
            "server": self._create_server_svg(),
            "firewall": self._create_firewall_svg(),
            "access_point": self._create_ap_svg(),
            "unknown": self._create_generic_svg()
        }
        
        # Cisco-style device colors (realistic network equipment colors)
        self.device_colors = {
            "router": {"bg": "#4a5568", "border": "#2d3748", "accent": "#3182ce"},
            "switch": {"bg": "#2b6cb0", "border": "#1e40af", "accent": "#dbeafe"}, 
            "pc": {"bg": "#374151", "border": "#1f2937", "accent": "#60a5fa"},
            "laptop": {"bg": "#374151", "border": "#1f2937", "accent": "#a78bfa"},
            "server": {"bg": "#1f2937", "border": "#111827", "accent": "#fbbf24"},
            "firewall": {"bg": "#dc2626", "border": "#991b1b", "accent": "#fecaca"},
            "access_point": {"bg": "#059669", "border": "#047857", "accent": "#a7f3d0"},
            "unknown": {"bg": "#6b7280", "border": "#4b5563", "accent": "#d1d5db"}
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

        # Enhanced network settings for Cisco Packet Tracer style
        net = Network(
            height="100vh",
            width="100vw", 
            bgcolor="#ffffff",  # Clean white background like Packet Tracer
            font_color="#000000",
            directed=False,
            cdn_resources="local",
        )

        # Physics optimized for network topology layout
        net.barnes_hut(
            gravity=-5000,
            central_gravity=0.05,
            spring_length=300,  # More spacing between devices
            spring_strength=0.01,
            damping=0.98,
            overlap=0.05
        )

        # Cisco Packet Tracer style visualization options
        net.set_options("""
        {
          "interaction": { 
            "hover": true, 
            "tooltipDelay": 300,
            "multiselect": true, 
            "navigationButtons": true,
            "selectConnectedEdges": false
          },
          "physics": {
            "enabled": true,
            "stabilization": { 
              "enabled": true, 
              "fit": true, 
              "iterations": 2000, 
              "updateInterval": 25 
            }
          },
          "nodes": { 
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.15)",
              "size": 6,
              "x": 3,
              "y": 3
            },
            "font": { 
              "size": 12, 
              "face": "Arial, sans-serif",
              "color": "#000000"
            },
            "borderWidth": 2,
            "size": 35,
            "chosen": {
              "node": {
                "color": "#3182ce"
              }
            }
          },
          "edges": { 
            "smooth": { 
              "type": "straightCross",
              "forceDirection": "none"
            }, 
            "shadow": false,
            "font": { 
              "size": 10,
              "face": "Arial, sans-serif",
              "color": "#4a5568",
              "strokeWidth": 3,
              "strokeColor": "#ffffff"
            },
            "chosen": {
              "edge": {
                "color": "#3182ce"
              }
            }
          }
        }
        """)

        # Cisco Packet Tracer style node creation
        for nid, data in G.nodes(data=True):
            label = data.get("label", nid)
            device_type = (data.get("device_type") or "unknown").lower()
            icon_key = data.get("device_icon", device_type if device_type in self.icon_map else "router")
            
            # Create comprehensive device configuration tooltip
            enhanced_title = self._create_device_config_tooltip(label, device_type, data)

            # Try to use icon first, then fallback to SVG
            image_path = self._resolve_icon(icon_key, output_file.parent)
            
            if image_path:
                # Use existing icon files
                net.add_node(
                    nid, 
                    label=label, 
                    title=enhanced_title, 
                    shape="image", 
                    image=image_path,
                    size=50,  # Larger for Packet Tracer style
                    borderWidth=2,
                    color={"border": self.device_colors.get(device_type, self.device_colors["unknown"])["border"]},
                    font={"size": 12, "color": "#000000"}
                )
            else:
                # Use Cisco-style SVG representation
                svg_data = self.cisco_device_svgs.get(device_type, self.cisco_device_svgs["unknown"])
                colors = self.device_colors.get(device_type, self.device_colors["unknown"])
                
                net.add_node(
                    nid, 
                    label=label, 
                    title=enhanced_title, 
                    shape="image",
                    image=svg_data,
                    size=45,  # Cisco device size
                    borderWidth=2,
                    color={
                        "border": colors["border"]
                    },
                    font={"size": 12, "color": "#000000"}
                )

        # Cisco Packet Tracer style edge creation
        for u, v, ed in G.edges(data=True):
            title = ed.get("title", f"{u} ↔ {v}")
            bandwidth = ed.get("bandwidth_mbps", ed.get("bandwidth", 0))
            priority = ed.get("priority", "unknown")
            link_type = ed.get("link_type", "subnet")
            
            # Create Cisco-style edge tooltip
            tooltip_parts = [f"<div style='font-family: Arial; font-size: 11px;'>"]
            tooltip_parts.append(f"<b style='color: #2563eb;'>{u} ↔ {v}</b>")
            tooltip_parts.append(f"<br><span style='color: #64748b;'>Link Type:</span> <b>{link_type.upper()}</b>")
            
            if bandwidth:
                tooltip_parts.append(f"<br><span style='color: #64748b;'>Bandwidth:</span> <b>{bandwidth} Mbps</b>")
            if ed.get('utilization_percent'):
                util_color = "#22c55e" if float(ed['utilization_percent']) < 70 else "#ef4444"
                tooltip_parts.append(f"<br><span style='color: #64748b;'>Utilization:</span> <span style='color: {util_color}; font-weight: bold;'>{ed['utilization_percent']}%</span>")
            if priority and priority != "unknown":
                tooltip_parts.append(f"<br><span style='color: #64748b;'>Priority:</span> <b>{priority}</b>")
            
            tooltip_parts.append("</div>")
            cisco_tooltip = "".join(tooltip_parts)
            
            # Get Cisco-style edge styling
            style = self._get_cisco_edge_style(link_type, float(bandwidth or 0), priority)
            style["title"] = cisco_tooltip

            net.add_edge(u, v, **style)

        # Generate HTML with full-page styling
        try:
            pyvis_html = net.generate_html()
        except AttributeError:
            tmp = output_file.with_suffix(".tmp.html")
            net.write_html(str(tmp))
            pyvis_html = tmp.read_text(encoding="utf-8")
            tmp.unlink(missing_ok=True)

        # Apply Cisco Packet Tracer style full-page styling
        cisco_style = """
<style>
body, html {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    background: #ffffff !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}
#mynetworkid {
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
    background: #ffffff !important;
}
/* Cisco-style grid background */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: 
        linear-gradient(rgba(0,0,0,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.03) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none;
    z-index: -1;
}
</style>
"""
        
        # Insert Cisco-style styling
        head_idx = pyvis_html.lower().find("</head>")
        if head_idx != -1:
            pyvis_html = pyvis_html[:head_idx] + cisco_style + pyvis_html[head_idx:]

        # Add Cisco Packet Tracer style controls and legend
        final_html = self._inject_before_body_end(pyvis_html, self._cisco_controls_html())
        output_file.write_text(final_html, encoding="utf-8")
        self.logger.info(f"Enhanced interactive topology saved to {output_file}")

    # ---------- Cisco Packet Tracer Style SVG Creators ----------
    
    def _create_router_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <rect x="4" y="16" width="40" height="16" rx="2" fill="%234a5568" stroke="%232d3748" stroke-width="2"/>
            <circle cx="10" cy="24" r="2" fill="%233182ce"/>
            <circle cx="38" cy="24" r="2" fill="%2322c55e"/>
            <rect x="14" y="20" width="20" height="8" rx="1" fill="%232d3748"/>
            <text x="24" y="26" text-anchor="middle" font-family="Arial" font-size="8" fill="white">RTR</text>
            <rect x="6" y="10" width="4" height="6" fill="%236b7280"/>
            <rect x="38" y="10" width="4" height="6" fill="%236b7280"/>
        </svg>'''

    def _create_switch_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <rect x="4" y="18" width="40" height="12" rx="2" fill="%232b6cb0" stroke="%231e40af" stroke-width="2"/>
            <circle cx="8" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="13" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="18" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="23" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="28" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="33" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="38" cy="24" r="1.5" fill="%2322c55e"/>
            <text x="24" y="16" text-anchor="middle" font-family="Arial" font-size="7" fill="%23374151">SWITCH</text>
        </svg>'''

    def _create_pc_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <rect x="6" y="8" width="36" height="24" rx="2" fill="%23374151" stroke="%231f2937" stroke-width="2"/>
            <rect x="8" y="10" width="32" height="18" fill="%2360a5fa"/>
            <rect x="10" y="12" width="28" height="14" fill="%23dbeafe"/>
            <rect x="20" y="32" width="8" height="4" fill="%234b5563"/>
            <rect x="12" y="36" width="24" height="4" rx="2" fill="%236b7280"/>
            <text x="24" y="22" text-anchor="middle" font-family="Arial" font-size="8" fill="%23374151">PC</text>
        </svg>'''

    def _create_laptop_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <path d="M8 20 L40 20 L38 32 L10 32 Z" fill="%23374151" stroke="%231f2937" stroke-width="2"/>
            <rect x="10" y="22" width="28" height="8" fill="%23a78bfa"/>
            <rect x="12" y="24" width="24" height="4" fill="%23e0e7ff"/>
            <rect x="6" y="32" width="36" height="4" rx="2" fill="%236b7280"/>
            <text x="24" y="28" text-anchor="middle" font-family="Arial" font-size="7" fill="%23374151">LAPTOP</text>
        </svg>'''

    def _create_server_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <rect x="8" y="10" width="32" height="8" rx="2" fill="%231f2937" stroke="%23111827" stroke-width="2"/>
            <rect x="8" y="20" width="32" height="8" rx="2" fill="%231f2937" stroke="%23111827" stroke-width="2"/>
            <rect x="8" y="30" width="32" height="8" rx="2" fill="%231f2937" stroke="%23111827" stroke-width="2"/>
            <circle cx="12" cy="14" r="1.5" fill="%2322c55e"/>
            <circle cx="12" cy="24" r="1.5" fill="%2322c55e"/>
            <circle cx="12" cy="34" r="1.5" fill="%2322c55e"/>
            <rect x="16" y="12" width="20" height="4" rx="1" fill="%23fbbf24"/>
            <rect x="16" y="22" width="20" height="4" rx="1" fill="%23fbbf24"/>
            <rect x="16" y="32" width="20" height="4" rx="1" fill="%23fbbf24"/>
        </svg>'''

    def _create_firewall_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <rect x="8" y="14" width="32" height="20" rx="3" fill="%23dc2626" stroke="%23991b1b" stroke-width="2"/>
            <path d="M24 8 L30 14 L24 20 L18 14 Z" fill="%23fecaca" stroke="%23dc2626" stroke-width="2"/>
            <circle cx="16" cy="24" r="2" fill="%23fecaca"/>
            <circle cx="32" cy="24" r="2" fill="%23fecaca"/>
            <text x="24" y="28" text-anchor="middle" font-family="Arial" font-size="6" fill="white">FIREWALL</text>
            <rect x="20" y="34" width="8" height="6" fill="%236b7280"/>
        </svg>'''

    def _create_ap_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <circle cx="24" cy="24" r="16" fill="%23059669" stroke="%23047857" stroke-width="2"/>
            <path d="M24 12 C30 12 35 17 35 24 C35 31 30 36 24 36" stroke="%23a7f3d0" stroke-width="2" fill="none"/>
            <path d="M24 16 C27 16 30 19 30 24 C30 29 27 32 24 32" stroke="%23a7f3d0" stroke-width="2" fill="none"/>
            <circle cx="24" cy="24" r="3" fill="%23a7f3d0"/>
            <text x="24" y="42" text-anchor="middle" font-family="Arial" font-size="7" fill="%23047857">AP</text>
        </svg>'''

    def _create_generic_svg(self) -> str:
        return '''data:image/svg+xml;charset=utf-8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
            <circle cx="24" cy="24" r="18" fill="%236b7280" stroke="%234b5563" stroke-width="2"/>
            <circle cx="24" cy="24" r="12" fill="%23d1d5db"/>
            <text x="24" y="28" text-anchor="middle" font-family="Arial" font-size="10" fill="%23374151">?</text>
        </svg>'''

    def _get_cisco_edge_style(self, link_type: str, bandwidth_mbps: float, priority: str) -> Dict[str, Any]:
        """Get Cisco Packet Tracer style edge styling"""
        
        # Base Cisco network link styles
        cisco_styles = {
            "subnet": {
                "width": 3,
                "dashes": False,
                "color": {"color": "#374151", "highlight": "#1f2937"}
            },
            "serial": {
                "width": 2,
                "dashes": [4, 4],
                "color": {"color": "#dc2626", "highlight": "#991b1b"}
            },
            "ethernet": {
                "width": 4,
                "dashes": False,
                "color": {"color": "#2563eb", "highlight": "#1d4ed8"}
            },
            "ospf": {
                "width": 3,
                "dashes": [8, 4],
                "color": {"color": "#059669", "highlight": "#047857"}
            },
            "bgp": {
                "width": 3,
                "dashes": [12, 6],
                "color": {"color": "#7c3aed", "highlight": "#6d28d9"},
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}}
            },
            "trunk": {
                "width": 6,
                "dashes": False,
                "color": {"color": "#ea580c", "highlight": "#c2410c"}
            }
        }
        
        style = cisco_styles.get(link_type, cisco_styles["subnet"]).copy()
        
        # Cisco-style bandwidth scaling
        if bandwidth_mbps >= 10000:  # 10+ Gbps
            style["width"] = max(style["width"], 8)
            style["color"]["color"] = "#16a34a"  # Green for high speed
        elif bandwidth_mbps >= 1000:  # 1+ Gbps  
            style["width"] = max(style["width"], 6)
            style["color"]["color"] = "#2563eb"  # Blue for gigabit
        elif bandwidth_mbps >= 100:   # 100+ Mbps
            style["width"] = max(style["width"], 4)
            style["color"]["color"] = "#ea580c"  # Orange for fast ethernet
        elif bandwidth_mbps > 0:      # < 100 Mbps
            style["width"] = max(style["width"] - 1, 2)
            style["color"]["color"] = "#dc2626"  # Red for slow links
        
        # Priority-based visual cues
        if priority and priority.lower() in ["critical", "high"]:
            style["width"] = style["width"] + 1
            
        return style

    def _create_device_config_tooltip(self, label: str, device_type: str, data: Dict[str, Any]) -> str:
        """Create comprehensive device configuration tooltip with proper text formatting"""
        
        # Use plain text formatting for better readability
        tooltip_parts = []
        
        # Device Header - Clean text format
        tooltip_parts.append(f"🌐 {label} ({device_type.upper()})")
        tooltip_parts.append("=" * 40)
        
        # Status and Basic Info
        status = data.get('status', 'unknown').lower()
        status_icon = "🟢" if status == 'up' else "🔴" if status == 'down' else "🟡"
        
        tooltip_parts.append(f"Status: {status_icon} {status.upper()}")
        
        if data.get('uptime'):
            tooltip_parts.append(f"Uptime: {data['uptime']}")
            
        tooltip_parts.append("")  # Empty line for separation
        
        # Network Configuration - Clean format
        if any(key in data for key in ['ip_address', 'subnet_mask', 'gateway', 'vlan', 'management_ip']):
            tooltip_parts.append("📡 NETWORK CONFIGURATION")
            tooltip_parts.append("-" * 25)
            
            if data.get('ip_address'):
                tooltip_parts.append(f"• IP Address: {data['ip_address']}")
            
            if data.get('subnet_mask'):
                tooltip_parts.append(f"• Subnet Mask: {data['subnet_mask']}")
            
            if data.get('gateway'):
                tooltip_parts.append(f"• Gateway: {data['gateway']}")
                
            if data.get('vlan'):
                tooltip_parts.append(f"• VLAN: {data['vlan']}")
                
            if data.get('management_ip'):
                tooltip_parts.append(f"• Management IP: {data['management_ip']}")
            
            tooltip_parts.append("")  # Empty line
        
        # Device-Specific Configuration based on type
        if device_type.lower() == 'router':
            tooltip_parts.extend(self._router_config_section(data))
        elif device_type.lower() == 'switch':
            tooltip_parts.extend(self._switch_config_section(data))
        elif device_type.lower() in ['pc', 'laptop']:
            tooltip_parts.extend(self._host_config_section(data))
        elif device_type.lower() == 'server':
            tooltip_parts.extend(self._server_config_section(data))
        elif device_type.lower() == 'firewall':
            tooltip_parts.extend(self._firewall_config_section(data))
        elif device_type.lower() == 'access_point':
            tooltip_parts.extend(self._ap_config_section(data))
        
        # Hardware Information - Clean format
        if any(key in data for key in ['model', 'serial', 'os_version', 'memory', 'cpu']):
            tooltip_parts.append("🔧 HARDWARE INFORMATION")
            tooltip_parts.append("-" * 25)
            
            if data.get('model'):
                tooltip_parts.append(f"• Model: {data['model']}")
            
            if data.get('serial'):
                tooltip_parts.append(f"• Serial Number: {data['serial']}")
                
            if data.get('os_version'):
                tooltip_parts.append(f"• OS Version: {data['os_version']}")
                
            if data.get('memory'):
                tooltip_parts.append(f"• Memory: {data['memory']}")
                
            if data.get('cpu'):
                tooltip_parts.append(f"• CPU: {data['cpu']}")
            
            tooltip_parts.append("")  # Empty line
        
        # Performance Metrics - Clean format
        if any(key in data for key in ['cpu_usage', 'memory_usage', 'temperature', 'power_consumption']):
            tooltip_parts.append("📊 PERFORMANCE METRICS")
            tooltip_parts.append("-" * 25)
            
            if data.get('cpu_usage'):
                cpu_status = self._get_usage_status(data['cpu_usage'])
                tooltip_parts.append(f"• CPU Usage: {data['cpu_usage']} {cpu_status}")
            
            if data.get('memory_usage'):
                mem_status = self._get_usage_status(data['memory_usage'])
                tooltip_parts.append(f"• Memory Usage: {data['memory_usage']} {mem_status}")
                
            if data.get('temperature'):
                temp_status = self._get_temp_status(data['temperature'])
                tooltip_parts.append(f"• Temperature: {data['temperature']} {temp_status}")
                
            if data.get('power_consumption'):
                tooltip_parts.append(f"• Power Consumption: {data['power_consumption']}")
            
            tooltip_parts.append("")  # Empty line
        
        # Security Information - Clean format
        if any(key in data for key in ['security_level', 'access_list', 'encryption', 'authentication']):
            tooltip_parts.append("🔒 SECURITY CONFIGURATION")
            tooltip_parts.append("-" * 25)
            
            if data.get('security_level'):
                tooltip_parts.append(f"• Security Level: {data['security_level']}")
            
            if data.get('access_list'):
                tooltip_parts.append(f"• Access Lists: {data['access_list']}")
                
            if data.get('encryption'):
                tooltip_parts.append(f"• Encryption: {data['encryption']}")
                
            if data.get('authentication'):
                tooltip_parts.append(f"• Authentication: {data['authentication']}")
            
            tooltip_parts.append("")  # Empty line
        
        # Description/Notes - Clean format
        if data.get('description') or data.get('location') or data.get('contact'):
            tooltip_parts.append("📝 ADDITIONAL INFORMATION")
            tooltip_parts.append("-" * 25)
            
            if data.get('description'):
                # Clean up description - remove HTML tags if any
                description = str(data['description'])
                # Simple HTML tag removal
                import re
                description = re.sub(r'<[^>]+>', '', description)
                tooltip_parts.append(f"Description:")
                tooltip_parts.append(f"  {description}")
                
            if data.get('location'):
                tooltip_parts.append(f"• Location: {data['location']}")
                
            if data.get('contact'):
                tooltip_parts.append(f"• Contact: {data['contact']}")
            
            tooltip_parts.append("")  # Empty line
        
        # Footer with timestamp - Clean format
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tooltip_parts.append("-" * 40)
        tooltip_parts.append(f"Last Updated: {timestamp}")
        
        # Join all parts with newlines for clean text display
        return "\n".join(tooltip_parts)

    def _router_config_section(self, data: Dict[str, Any]) -> list:
        """Router-specific configuration section - Clean format"""
        section = []
        if any(key in data for key in ['routing_protocol', 'interfaces', 'routes', 'bgp_as']):
            section.append("🔀 ROUTING CONFIGURATION")
            section.append("-" * 25)
            
            if data.get('routing_protocol'):
                section.append(f"• Protocol: {data['routing_protocol']}")
            
            if data.get('bgp_as'):
                section.append(f"• BGP AS Number: {data['bgp_as']}")
            
            if data.get('interfaces'):
                section.append(f"• Interfaces: {data['interfaces']}")
                
            if data.get('routes'):
                section.append(f"• Static Routes: {data['routes']}")
            
            section.append("")  # Empty line
        return section

    def _switch_config_section(self, data: Dict[str, Any]) -> list:
        """Switch-specific configuration section - Clean format"""
        section = []
        if any(key in data for key in ['vlans', 'spanning_tree', 'port_count', 'trunk_ports']):
            section.append("🔌 SWITCH CONFIGURATION")
            section.append("-" * 25)
            
            if data.get('vlans'):
                section.append(f"• VLANs: {data['vlans']}")
            
            if data.get('spanning_tree'):
                section.append(f"• Spanning Tree: {data['spanning_tree']}")
            
            if data.get('port_count'):
                section.append(f"• Total Ports: {data['port_count']}")
                
            if data.get('trunk_ports'):
                section.append(f"• Trunk Ports: {data['trunk_ports']}")
            
            section.append("")  # Empty line
        return section

    def _host_config_section(self, data: Dict[str, Any]) -> list:
        """PC/Laptop configuration section - Clean format"""
        section = []
        if any(key in data for key in ['dns_servers', 'domain', 'mac_address', 'dhcp_enabled']):
            section.append("💻 HOST CONFIGURATION")
            section.append("-" * 25)
            
            if data.get('mac_address'):
                section.append(f"• MAC Address: {data['mac_address']}")
            
            if data.get('dns_servers'):
                section.append(f"• DNS Servers: {data['dns_servers']}")
            
            if data.get('domain'):
                section.append(f"• Domain: {data['domain']}")
                
            if data.get('dhcp_enabled'):
                dhcp_status = "Enabled" if data['dhcp_enabled'] else "Disabled"
                section.append(f"• DHCP: {dhcp_status}")
            
            section.append("")  # Empty line
        return section

    def _server_config_section(self, data: Dict[str, Any]) -> list:
        """Server-specific configuration section - Clean format"""
        section = []
        if any(key in data for key in ['services', 'databases', 'backup_status', 'cluster_role']):
            section.append("🖥️ SERVER CONFIGURATION")
            section.append("-" * 25)
            
            if data.get('services'):
                section.append(f"• Running Services: {data['services']}")
            
            if data.get('databases'):
                section.append(f"• Databases: {data['databases']}")
            
            if data.get('backup_status'):
                section.append(f"• Backup Status: {data['backup_status']}")
                
            if data.get('cluster_role'):
                section.append(f"• Cluster Role: {data['cluster_role']}")
            
            section.append("")  # Empty line
        return section

    def _firewall_config_section(self, data: Dict[str, Any]) -> list:
        """Firewall-specific configuration section - Clean format"""
        section = []
        if any(key in data for key in ['firewall_rules', 'vpn_tunnels', 'intrusion_detection', 'threat_level']):
            section.append("🛡️ FIREWALL CONFIGURATION")
            section.append("-" * 25)
            
            if data.get('firewall_rules'):
                section.append(f"• Active Rules: {data['firewall_rules']}")
            
            if data.get('vpn_tunnels'):
                section.append(f"• VPN Tunnels: {data['vpn_tunnels']}")
            
            if data.get('intrusion_detection'):
                section.append(f"• IDS/IPS: {data['intrusion_detection']}")
                
            if data.get('threat_level'):
                section.append(f"• Threat Level: {data['threat_level']}")
            
            section.append("")  # Empty line
        return section

    def _ap_config_section(self, data: Dict[str, Any]) -> list:
        """Access Point configuration section - Clean format"""
        section = []
        if any(key in data for key in ['ssid', 'channel', 'encryption_type', 'connected_clients']):
            section.append("📶 WIFI CONFIGURATION")
            section.append("-" * 25)
            
            if data.get('ssid'):
                section.append(f"• SSID: {data['ssid']}")
            
            if data.get('channel'):
                section.append(f"• Channel: {data['channel']}")
            
            if data.get('encryption_type'):
                section.append(f"• Encryption: {data['encryption_type']}")
                
            if data.get('connected_clients'):
                section.append(f"• Connected Clients: {data['connected_clients']}")
            
            section.append("")  # Empty line
        return section

    def _get_usage_status(self, usage_str: str) -> str:
        """Get usage status indicator"""
        try:
            usage = float(usage_str.rstrip('%'))
            if usage >= 90:
                return "⚠️ CRITICAL"
            elif usage >= 75:
                return "🟡 HIGH"
            elif usage >= 50:
                return "🔵 MEDIUM"
            else:
                return "✅ NORMAL"
        except:
            return ""

    def _get_temp_status(self, temp: str) -> str:
        """Get temperature status indicator"""
        try:
            temp_val = float(temp.rstrip('°C'))
            if temp_val >= 80:
                return "🔥 HOT"
            elif temp_val >= 60:
                return "🟡 WARM"
            else:
                return "❄️ NORMAL"
        except:
            return "" #cbd5e1;'>Domain:</span> <span style='color: #5eead4;'>{data['domain']}</span><br>")
                
            if data.get('dhcp_enabled'):
                dhcp_status = "Enabled" if data['dhcp_enabled'] else "Disabled"
                section.append(f"<span style='color: #cbd5e1;'>DHCP:</span> <span style='color: #5eead4;'>{dhcp_status}</span><br>")
            
            section.append("</div>")
        return section

    def _server_config_section(self, data: Dict[str, Any]) -> list:
        """Server-specific configuration section"""
        section = []
        if any(key in data for key in ['services', 'databases', 'backup_status', 'cluster_role']):
            section.append(
                "<div style='margin-bottom: 10px; border-left: 3px solid #f59e0b; padding-left: 8px;'>"
                "<span style='color: #fcd34d; font-weight: bold;'>🖥️ Server Config</span><br>"
            )
            
            if data.get('services'):
                section.append(f"<span style='color: #cbd5e1;'>Services:</span> <span style='color: #fcd34d;'>{data['services']}</span><br>")
            
            if data.get('databases'):
                section.append(f"<span style='color: #cbd5e1;'>Databases:</span> <span style='color: #fcd34d;'>{data['databases']}</span><br>")
            
            if data.get('backup_status'):
                backup_color = "#22c55e" if data['backup_status'].lower() == 'current' else "#f59e0b"
                section.append(f"<span style='color: #cbd5e1;'>Backup:</span> <span style='color: {backup_color};'>{data['backup_status']}</span><br>")
                
            if data.get('cluster_role'):
                section.append(f"<span style='color: #cbd5e1;'>Cluster Role:</span> <span style='color: #fcd34d;'>{data['cluster_role']}</span><br>")
            
            section.append("</div>")
        return section

    def _firewall_config_section(self, data: Dict[str, Any]) -> list:
        """Firewall-specific configuration section"""
        section = []
        if any(key in data for key in ['firewall_rules', 'vpn_tunnels', 'intrusion_detection', 'threat_level']):
            section.append(
                "<div style='margin-bottom: 10px; border-left: 3px solid #dc2626; padding-left: 8px;'>"
                "<span style='color: #fca5a5; font-weight: bold;'>🛡️ Firewall Config</span><br>"
            )
            
            if data.get('firewall_rules'):
                section.append(f"<span style='color: #cbd5e1;'>Active Rules:</span> <span style='color: #fca5a5;'>{data['firewall_rules']}</span><br>")
            
            if data.get('vpn_tunnels'):
                section.append(f"<span style='color: #cbd5e1;'>VPN Tunnels:</span> <span style='color: #fca5a5;'>{data['vpn_tunnels']}</span><br>")
            
            if data.get('intrusion_detection'):
                ids_status = data['intrusion_detection']
                ids_color = "#22c55e" if ids_status.lower() == 'active' else "#f59e0b"
                section.append(f"<span style='color: #cbd5e1;'>IDS/IPS:</span> <span style='color: {ids_color};'>{ids_status}</span><br>")
                
            if data.get('threat_level'):
                threat_color = self._get_threat_color(data['threat_level'])
                section.append(f"<span style='color: #cbd5e1;'>Threat Level:</span> <span style='color: {threat_color};'>{data['threat_level']}</span><br>")
            
            section.append("</div>")
        return section

    def _ap_config_section(self, data: Dict[str, Any]) -> list:
        """Access Point configuration section"""
        section = []
        if any(key in data for key in ['ssid', 'channel', 'encryption_type', 'connected_clients']):
            section.append(
                "<div style='margin-bottom: 10px; border-left: 3px solid #059669; padding-left: 8px;'>"
                "<span style='color: #a7f3d0; font-weight: bold;'>📶 WiFi Config</span><br>"
            )
            
            if data.get('ssid'):
                section.append(f"<span style='color: #cbd5e1;'>SSID:</span> <span style='color: #a7f3d0;'>{data['ssid']}</span><br>")
            
            if data.get('channel'):
                section.append(f"<span style='color: #cbd5e1;'>Channel:</span> <span style='color: #a7f3d0;'>{data['channel']}</span><br>")
            
            if data.get('encryption_type'):
                section.append(f"<span style='color: #cbd5e1;'>Encryption:</span> <span style='color: #a7f3d0;'>{data['encryption_type']}</span><br>")
                
            if data.get('connected_clients'):
                section.append(f"<span style='color: #cbd5e1;'>Clients:</span> <span style='color: #a7f3d0;'>{data['connected_clients']}</span><br>")
            
            section.append("</div>")
        return section

    def _get_usage_color(self, usage: float) -> str:
        """Get color based on usage percentage"""
        if usage >= 90:
            return "#ef4444"  # Red for critical
        elif usage >= 75:
            return "#f59e0b"  # Orange for high
        elif usage >= 50:
            return "#fbbf24"  # Yellow for medium
        else:
            return "#22c55e"  # Green for low

    def _get_temp_color(self, temp: str) -> str:
        """Get color based on temperature"""
        try:
            temp_val = float(temp.rstrip('°C'))
            if temp_val >= 80:
                return "#ef4444"  # Red for hot
            elif temp_val >= 60:
                return "#f59e0b"  # Orange for warm
            else:
                return "#22c55e"  # Green for normal
        except:
            return "#6b7280"  # Gray for unknown

    def _get_threat_color(self, threat_level: str) -> str:
        """Get color based on threat level"""
        threat_level = threat_level.lower()
        if threat_level in ['critical', 'high']:
            return "#ef4444"  # Red
        elif threat_level == 'medium':
            return "#f59e0b"  # Orange
        elif threat_level == 'low':
            return "#22c55e"  # Green
        else:
            return "#6b7280"  # Gray

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
        # Enhanced with more device types using new color scheme
        return self.device_colors.get(device_type, self.device_colors["unknown"])["border"]

    def _edge_style(
        self, link_type: str, bandwidth_mbps: float, priority: str
    ) -> Dict[str, Any]:
        # Use Cisco-style edge styling
        return self._get_cisco_edge_style(link_type, bandwidth_mbps, priority)

    def _edge_title(self, title: str, ed: Dict[str, Any]) -> str:
        # Enhanced edge tooltip with HTML formatting
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

    def _cisco_controls_html(self) -> str:
        return """
<!-- Cisco Packet Tracer Style Controls -->
<style>
  .cisco-toolbar {
    position: fixed; 
    top: 10px; 
    left: 10px; 
    right: 10px;
    z-index: 9999;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
    border: 1px solid #cbd5e1; 
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    font-size: 12px;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .cisco-toolbar h3 { 
    margin: 0; 
    font-size: 16px; 
    font-weight: 600; 
    color: #1e293b;
    display: flex;
    align-items: center;
  }
  .cisco-controls { 
    display: flex; 
    gap: 12px; 
    align-items: center;
  }
  .cisco-btn { 
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white; 
    border: none;
    padding: 6px 12px; 
    border-radius: 5px; 
    cursor: pointer;
    font-size: 11px; 
    font-weight: 500;
    transition: all 0.2s;
    border: 1px solid #2563eb;
  }
  .cisco-btn:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(59,130,246,0.3);
  }
  .cisco-legend {
    position: fixed; 
    bottom: 10px; 
    left: 10px; 
    z-index: 9999;
    background: rgba(248, 250, 252, 0.95); 
    backdrop-filter: blur(10px);
    border: 1px solid #cbd5e1; 
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    padding: 12px; 
    font-size: 11px;
    min-width: 200px;
    max-width: 300px;
  }
  .cisco-legend h4 { 
    margin: 0 0 10px 0; 
    font-size: 13px; 
    font-weight: 600; 
    color: #1e293b;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 5px;
  }
  .legend-item {
    display: flex; 
    align-items: center; 
    margin: 6px 0;
  }
  .legend-line { 
    width: 24px; 
    height: 3px; 
    margin-right: 8px;
    border-radius: 2px;
  }
  .legend-dashed {
    background: repeating-linear-gradient(to right, currentColor 0px, currentColor 6px, transparent 6px, transparent 12px);
  }
  .device-legend {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 10px;
  }
  .device-item {
    display: flex;
    align-items: center;
    font-size: 10px;
    color: #64748b;
  }
  .device-icon {
    width: 16px;
    height: 16px;
    margin-right: 6px;
    border-radius: 2px;
  }
</style>

<div class="cisco-toolbar">
  <h3>🌐 Network Topology Viewer</h3>
  <div class="cisco-controls">
    <button id="fitBtn" class="cisco-btn">📍 Fit View</button>
    <button id="togglePhysicsBtn" class="cisco-btn">⚡ Physics</button>
    <button id="zoomInBtn" class="cisco-btn">🔍 Zoom In</button>
    <button id="zoomOutBtn" class="cisco-btn">🔍 Zoom Out</button>
    <button id="fullscreenBtn" class="cisco-btn">⛶ Fullscreen</button>
  </div>
</div>

<div class="cisco-legend">
  <h4>📋 Network Legend</h4>
  
  <div style="margin-bottom: 12px;">
    <strong style="font-size: 11px; color: #374151;">Connection Types:</strong>
    <div class="legend-item">
      <div class="legend-line" style="background: #374151;"></div>
      <span>Subnet/Ethernet</span>
    </div>
    <div class="legend-item">
      <div class="legend-line legend-dashed" style="color: #dc2626;"></div>
      <span>Serial Links</span>
    </div>
    <div class="legend-item">
      <div class="legend-line legend-dashed" style="color: #059669;"></div>
      <span>OSPF Routes</span>
    </div>
    <div class="legend-item">
      <div class="legend-line legend-dashed" style="color: #7c3aed;"></div>
      <span>BGP Routes</span>
    </div>
    <div class="legend-item">
      <div class="legend-line" style="background: #ea580c; height: 5px;"></div>
      <span>Trunk Links</span>
    </div>
  </div>

  <div>
    <strong style="font-size: 11px; color: #374151;">Device Types:</strong>
    <div class="device-legend">
      <div class="device-item">
        <div class="device-icon" style="background: #4a5568;"></div>
        <span>Router</span>
      </div>
      <div class="device-item">
        <div class="device-icon" style="background: #2b6cb0;"></div>
        <span>Switch</span>
      </div>
      <div class="device-item">
        <div class="device-icon" style="background: #374151;"></div>
        <span>PC/Host</span>
      </div>
      <div class="device-item">
        <div class="device-icon" style="background: #dc2626;"></div>
        <span>Firewall</span>
      </div>
      <div class="device-item">
        <div class="device-icon" style="background: #059669;"></div>
        <span>Access Point</span>
      </div>
      <div class="device-item">
        <div class="device-icon" style="background: #1f2937;"></div>
        <span>Server</span>
      </div>
    </div>
  </div>
  
  <div style="margin-top: 12px; font-size: 10px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 8px;">
    💡 <strong>Tips:</strong><br>
    • Hover over devices for details<br>
    • Click and drag to move nodes<br>
    • Use mouse wheel to zoom<br>
    • Thicker lines = Higher bandwidth
  </div>
</div>

<script>
(function() {
  function initializeCiscoControls() {
    try {
      if (typeof network === "undefined") {
        return setTimeout(initializeCiscoControls, 100);
      }
      
      var physicsEnabled = true;

      // Fit to view
      document.getElementById("fitBtn").addEventListener("click", function() {
        try { 
          network.fit({animation: {duration: 1500, easingFunction: "easeOutCubic"}}); 
        } catch (e) { 
          console.warn("Fit failed:", e); 
        }
      });

      // Physics toggle
      document.getElementById("togglePhysicsBtn").addEventListener("click", function() {
        physicsEnabled = !physicsEnabled;
        try { 
          network.setOptions({ physics: { enabled: physicsEnabled } });
          this.textContent = physicsEnabled ? "⚡ Physics" : "⏸️ Physics";
          this.style.background = physicsEnabled ? 
            "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)" : 
            "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)";
        } catch (e) { 
          console.warn("Physics toggle failed:", e); 
        }
      });

      // Zoom controls with smooth animation
      document.getElementById("zoomInBtn").addEventListener("click", function() {
        try {
          var currentScale = network.getScale();
          network.moveTo({scale: currentScale * 1.3, animation: {duration: 500}});
        } catch (e) {
          console.warn("Zoom in failed:", e);
        }
      });
      
      document.getElementById("zoomOutBtn").addEventListener("click", function() {
        try {
          var currentScale = network.getScale();
          network.moveTo({scale: currentScale / 1.3, animation: {duration: 500}});
        } catch (e) {
          console.warn("Zoom out failed:", e);
        }
      });

      // Fullscreen toggle
      document.getElementById("fullscreenBtn").addEventListener("click", function() {
        try {
          if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            this.textContent = "🗗 Exit Fullscreen";
          } else {
            document.exitFullscreen();
            this.textContent = "⛶ Fullscreen";
          }
        } catch (e) {
          console.warn("Fullscreen failed:", e);
        }
      });

      // Auto-fit after network stabilizes
      network.on("stabilizationIterationsDone", function () {
        setTimeout(function() {
          try {
            network.fit({animation: {duration: 2000, easingFunction: "easeOutCubic"}});
          } catch (e) {
            console.warn("Auto-fit failed:", e);
          }
        }, 1000);
      });

      // Cisco-style node selection effects
      network.on("selectNode", function (params) {
        if (params.nodes.length > 0) {
          console.log("Selected device:", params.nodes[0]);
        }
      });
      
    } catch (e) {
      console.warn("Cisco control initialization error:", e);
      setTimeout(initializeCiscoControls, 200);
    }
  }
  
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeCiscoControls);
  } else {
    initializeCiscoControls();
  }
})();
</script>
"""