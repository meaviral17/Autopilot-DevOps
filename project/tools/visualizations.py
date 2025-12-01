"""
Visualization tools for dependency graphs, heatmaps, and timelines.
"""
import os
import io
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns
import networkx as nx

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'


class Visualizations:
    """Visualization utilities for DevOps analysis."""
    
    @staticmethod
    def plot_dependency_graph(dependency_data: Dict, max_nodes: int = 50) -> Image.Image:
        """Create a visual dependency graph from dependency data.
        
        Args:
            dependency_data: Dict with 'nodes' and 'edges' from get_dependency_graph()
            max_nodes: Maximum nodes to display (for performance)
            
        Returns:
            PIL Image of the dependency graph
        """
        G = nx.DiGraph()
        
        nodes = dependency_data.get("nodes", [])[:max_nodes]
        edges = dependency_data.get("edges", [])
        
        # Add nodes
        for node in nodes:
            # Use just filename for cleaner display
            node_name = os.path.basename(node).replace('.py', '')
            G.add_node(node_name, full_path=node)
        
        # Add edges (only for nodes we're displaying)
        node_set = set(os.path.basename(n).replace('.py', '') for n in nodes)
        for edge in edges:
            from_node = os.path.basename(edge.get("from", "")).replace('.py', '')
            to_node = os.path.basename(edge.get("to", "")).replace('.py', '')
            
            if from_node in node_set and to_node in node_set:
                G.add_edge(from_node, to_node)
        
        # Create figure with dark mode background
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        # Handle empty graph
        if len(G.nodes()) == 0:
            ax.text(0.5, 0.5, 'No dependencies found.\n\nRun repository analysis to generate dependency graph.', 
                   horizontalalignment='center', verticalalignment='center', 
                   transform=ax.transAxes, color='#a0a0a0', fontsize=14, fontweight=500)
            ax.axis('off')
        else:
            # Layout
            try:
                if len(G.nodes()) > 1:
                    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
                else:
                    pos = {list(G.nodes())[0]: (0.5, 0.5)}
            except:
                pos = nx.circular_layout(G) if len(G.nodes()) > 1 else {list(G.nodes())[0]: (0.5, 0.5)}
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color='#3291ff', 
                                  node_size=1000, alpha=0.8, ax=ax)
            
            # Draw edges
            if len(G.edges()) > 0:
                nx.draw_networkx_edges(G, pos, edge_color='#666666', 
                                       arrows=True, arrowsize=20, 
                                       alpha=0.6, width=1.5, ax=ax)
            
            # Draw labels
            nx.draw_networkx_labels(G, pos, font_size=8, 
                                   font_weight='bold', font_color='#e5e5e5', ax=ax)
            
            ax.set_title("Dependency Graph", fontsize=14, fontweight='bold', pad=20, color='#e5e5e5')
            ax.axis('off')
        
        # Convert to PIL Image
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   facecolor='#1a1a1a', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return Image.open(buf)
    
    @staticmethod
    def plot_complexity_heatmap(complexity_data: List[Dict], max_files: int = 50) -> Image.Image:
        """Create a heatmap showing complexity across files.
        
        Args:
            complexity_data: List of dicts with 'file' and 'complexity' keys
            max_files: Maximum files to display
            
        Returns:
            PIL Image of the heatmap
        """
        if not complexity_data:
            # Return empty plot with dark mode
            fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1a1a1a')
            ax.set_facecolor('#1a1a1a')
            ax.text(0.5, 0.5, 'No complexity data available.\nRun complexity analysis on Python files first.', 
                   ha='center', va='center', fontsize=14, color='#a0a0a0', fontweight=500)
            ax.axis('off')
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none')
            buf.seek(0)
            plt.close()
            return Image.open(buf)
        
        # Prepare data - sort by complexity (descending) and take top files
        file_complexity_pairs = []
        for item in complexity_data:
            file_path = item.get("file", "unknown")
            comp = item.get("complexity", {})
            avg_complexity = comp.get("avg_complexity", 0)
            total_complexity = comp.get("complexity", 0)
            
            # Use average complexity as primary metric, fallback to total
            complexity_score = avg_complexity if avg_complexity > 0 else total_complexity
            
            # Use relative path, truncate if too long
            rel_path = file_path.replace('\\', '/')
            if len(rel_path) > 40:
                rel_path = '...' + rel_path[-37:]
            
            file_complexity_pairs.append((rel_path, complexity_score))
        
        # Sort by complexity (descending) and take top max_files
        file_complexity_pairs.sort(key=lambda x: x[1], reverse=True)
        file_complexity_pairs = file_complexity_pairs[:max_files]
        
        files = [pair[0] for pair in file_complexity_pairs]
        complexities = [pair[1] for pair in file_complexity_pairs]
        
        # Create heatmap data
        import numpy as np
        heatmap_data = np.array(complexities).reshape(-1, 1)
        
        # Create figure with dark mode
        fig, ax = plt.subplots(figsize=(10, max(6, len(files) * 0.35)), facecolor='#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        # Create heatmap with dark mode colors
        # Use a colormap that works well in dark mode (inverted YlOrRd)
        sns.heatmap(heatmap_data, 
                   yticklabels=files,
                   xticklabels=['Avg Complexity'],
                   annot=True, fmt='.1f', 
                   cmap='YlOrRd',  # Orange-red colormap
                   cbar_kws={'label': 'Complexity Score'},
                   ax=ax,
                   linewidths=0.5,
                   linecolor='#333333')
        
        # Dark mode styling
        ax.set_title("Code Complexity Heatmap", fontsize=14, fontweight='bold', 
                    pad=15, color='#e5e5e5')
        ax.set_ylabel("Files", fontsize=11, color='#a0a0a0')
        ax.set_xlabel("", fontsize=10, color='#a0a0a0')
        
        # Style ticks
        ax.tick_params(axis='y', colors='#e5e5e5', labelsize=9)
        ax.tick_params(axis='x', colors='#a0a0a0', labelsize=10)
        
        # Style colorbar
        cbar = ax.collections[0].colorbar
        cbar.ax.yaxis.label.set_color('#a0a0a0')
        cbar.ax.tick_params(colors='#a0a0a0')
        
        plt.tight_layout()
        
        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   facecolor='#1a1a1a', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return Image.open(buf)
    
    @staticmethod
    def plot_error_timeline(log_data: Dict, time_window_hours: int = 24) -> Image.Image:
        """Create a timeline plot of errors and warnings over time.
        
        Args:
            log_data: Output from parse_logs()
            time_window_hours: Time window to display
            
        Returns:
            PIL Image of the timeline
        """
        errors = log_data.get("errors", [])
        warnings = log_data.get("warnings", [])
        
        # Extract timestamps
        error_times = []
        warning_times = []
        
        for error in errors:
            ts_str = error.get("timestamp", "")
            if ts_str:
                try:
                    # Try multiple date formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', 
                               '%m/%d/%Y %H:%M:%S', '%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                        try:
                            # Handle microseconds if present
                            if '.' in ts_str:
                                dt = datetime.strptime(ts_str[:23], '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                dt = datetime.strptime(ts_str[:19], fmt)
                            error_times.append(dt)
                            break
                        except:
                            continue
                except:
                    pass
        
        for warning in warnings:
            ts_str = warning.get("timestamp", "")
            if ts_str:
                try:
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', 
                               '%m/%d/%Y %H:%M:%S', '%H:%M:%S']:
                        try:
                            dt = datetime.strptime(ts_str[:19], fmt)
                            warning_times.append(dt)
                            break
                        except:
                            continue
                except:
                    pass
        
        # Create figure with dark mode
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        
        if not error_times and not warning_times:
            # Show a proper timeline with 0 errors/warnings - create a 24-hour chart
            from datetime import datetime, timedelta
            now = datetime.now()
            hours = [now - timedelta(hours=i) for i in range(24, -1, -1)]
            zero_counts = [0] * len(hours)
            
            # Plot empty timeline with proper styling
            ax.plot(hours, zero_counts, marker='o', color='#4ade80', 
                   label='Errors (0)', linewidth=2, markersize=4, alpha=0.5)
            ax.plot(hours, zero_counts, marker='s', color='#fbbf24', 
                   label='Warnings (0)', linewidth=2, markersize=4, alpha=0.5)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#a0a0a0')
            
            # Dark mode styling
            ax.set_xlabel("Time (Last 24 Hours)", fontsize=11, color='#a0a0a0')
            ax.set_ylabel("Count", fontsize=11, color='#a0a0a0')
            ax.set_title("Error & Warning Timeline - No Errors Found", fontsize=14, fontweight='bold', pad=15, color='#e5e5e5')
            ax.legend(loc='upper right', facecolor='#2a2a2a', edgecolor='#333333', labelcolor='#e5e5e5')
            ax.grid(True, alpha=0.2, color='#555555')
            
            # Style ticks
            ax.tick_params(axis='x', colors='#a0a0a0', labelsize=10)
            ax.tick_params(axis='y', colors='#a0a0a0', labelsize=10)
            
            # Style spines
            for spine in ax.spines.values():
                spine.set_color('#555555')
                spine.set_linewidth(1)
            
            # Add success message
            ax.text(0.5, 0.95, '✓ No errors or warnings detected in the analyzed time period', 
                   ha='center', va='top', transform=ax.transAxes, 
                   fontsize=12, color='#4ade80', fontweight=500,
                   bbox=dict(boxstyle='round', facecolor='#1a3a1a', edgecolor='#4ade80', alpha=0.3))
            
            # Save and return the 0-error chart
            plt.tight_layout()
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none')
            buf.seek(0)
            plt.close()
            return Image.open(buf)
        else:
            # Group by hour
            error_counts = defaultdict(int)
            warning_counts = defaultdict(int)
            
            for dt in error_times:
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                error_counts[hour_key] += 1
            
            for dt in warning_times:
                hour_key = dt.replace(minute=0, second=0, microsecond=0)
                warning_counts[hour_key] += 1
            
            # Get time range
            all_times = list(error_counts.keys()) + list(warning_counts.keys())
            if all_times:
                min_time = min(all_times)
                max_time = max(all_times)
                
                # Plot
                if error_counts:
                    times = sorted(error_counts.keys())
                    counts = [error_counts[t] for t in times]
                    ax.plot(times, counts, marker='o', color='#ef4444', 
                           label='Errors', linewidth=2, markersize=6)
                    ax.fill_between(times, counts, alpha=0.3, color='#ef4444')
                
                if warning_counts:
                    times = sorted(warning_counts.keys())
                    counts = [warning_counts[t] for t in times]
                    ax.plot(times, counts, marker='s', color='#f59e0b', 
                           label='Warnings', linewidth=2, markersize=6)
                    ax.fill_between(times, counts, alpha=0.3, color='#f59e0b')
                
                # Format x-axis
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#a0a0a0')
                
                # Dark mode styling
                ax.set_xlabel("Time", fontsize=11, color='#a0a0a0')
                ax.set_ylabel("Count", fontsize=11, color='#a0a0a0')
                ax.set_title("Error & Warning Timeline", fontsize=14, fontweight='bold', pad=15, color='#e5e5e5')
                ax.legend(loc='upper right', facecolor='#2a2a2a', edgecolor='#333333', labelcolor='#e5e5e5')
                ax.grid(True, alpha=0.2, color='#555555')
                
                # Style ticks
                ax.tick_params(axis='x', colors='#a0a0a0', labelsize=10)
                ax.tick_params(axis='y', colors='#a0a0a0', labelsize=10)
                
                # Style spines
                for spine in ax.spines.values():
                    spine.set_color('#555555')
                    spine.set_linewidth(1)
        
        plt.tight_layout()
        
        # Convert to PIL Image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', 
                   facecolor='#1a1a1a', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return Image.open(buf)

