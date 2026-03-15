"""
File: ai_engine/visualizer.py
Purpose: Generate and save dashboard charts as PNG files
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
from utils.logger import setup_logger
from utils.file_utils import ensure_dir


CLUSTER_COLORS = {0: '#378ADD', 1: '#1D9E75', 2: '#D85A30', 3: '#7F77DD'}
CLUSTER_NAMES  = {0: 'Frequent low', 1: 'VIP', 2: 'At risk', 3: 'Middle tier'}


class Visualizer:

    def __init__(self, df: pd.DataFrame, output_dir: str = "outputs/charts"):
        self.df = df.copy()
        self.output_dir = output_dir
        self.logger = setup_logger("visualizer")
        ensure_dir(output_dir)
        sns.set_style("whitegrid")
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'axes.spines.top': False,
            'axes.spines.right': False,
        })

    def generate_all(self):
        """Generate and save all charts"""
        self.logger.info("Generating dashboard charts...")
        self.plot_cluster_distribution()
        self.plot_avg_spent_per_cluster()
        self.plot_spending_distribution()
        self.plot_scatter()
        self.plot_dashboard()
        self.logger.info(f"All charts saved to: {self.output_dir}/")

    def plot_cluster_distribution(self):
        """Donut chart — كام customer في كل cluster"""
        counts = self.df['cluster'].value_counts().sort_index()
        labels = [f"{CLUSTER_NAMES[i]} ({counts[i]})" for i in counts.index]
        colors = [CLUSTER_COLORS[i] for i in counts.index]

        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, _ = ax.pie(
            counts, labels=None, colors=colors,
            wedgeprops=dict(width=0.5), startangle=90
        )
        ax.legend(wedges, labels, loc='lower center',
                  bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=10, frameon=False)
        ax.set_title("Customer segments", fontsize=14, fontweight='bold', pad=16)

        self._save(fig, "01_cluster_distribution.png")

    def plot_avg_spent_per_cluster(self):
        """Bar chart — متوسط الإنفاق لكل cluster"""
        avg = self.df.groupby('cluster')['total_spent'].mean().reset_index()
        avg['name'] = avg['cluster'].map(CLUSTER_NAMES)
        avg['color'] = avg['cluster'].map(CLUSTER_COLORS)

        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(avg['name'], avg['total_spent'],
                      color=avg['color'], width=0.5, zorder=3)

        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 60,
                f"${bar.get_height():,.0f}",
                ha='center', va='bottom', fontsize=10
            )

        ax.set_ylabel("Avg total spent ($)", fontsize=11)
        ax.set_title("Average spending per segment", fontsize=14, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.set_ylim(0, self.df['total_spent'].max() * 1.2)

        self._save(fig, "02_avg_spent_per_cluster.png")

    def plot_spending_distribution(self):
        """Histogram — توزيع الإنفاق"""
        bins = [0, 1000, 2000, 3000, 4000, 6000]
        labels = ['$0-1k', '$1k-2k', '$2k-3k', '$3k-4k', '$4k+']

        self.df['spend_bin'] = pd.cut(
            self.df['total_spent'], bins=bins, labels=labels, right=False
        )
        counts = self.df['spend_bin'].value_counts().reindex(labels)

        fig, ax = plt.subplots(figsize=(7, 5))
        bars = ax.bar(labels, counts, color='#7F77DD', width=0.6, zorder=3)

        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.2,
                str(int(bar.get_height())),
                ha='center', va='bottom', fontsize=11
            )

        ax.set_ylabel("Number of customers", fontsize=11)
        ax.set_title("Spending distribution", fontsize=14, fontweight='bold')
        ax.set_ylim(0, counts.max() + 3)

        self._save(fig, "03_spending_distribution.png")

    def plot_scatter(self):
        """Scatter plot — purchases vs spent ملون بالـ cluster"""
        fig, ax = plt.subplots(figsize=(7, 5))

        for cluster_id, group in self.df.groupby('cluster'):
            ax.scatter(
                group['total_purchases'],
                group['total_spent'],
                c=CLUSTER_COLORS[cluster_id],
                label=CLUSTER_NAMES[cluster_id],
                s=80, alpha=0.85, zorder=3
            )

        ax.set_xlabel("Total purchases", fontsize=11)
        ax.set_ylabel("Total spent ($)", fontsize=11)
        ax.set_title("Purchases vs spent", fontsize=14, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.legend(frameon=False, fontsize=10)

        self._save(fig, "04_scatter.png")

    def plot_dashboard(self):
        """Dashboard كامل — الـ 4 charts في ملف واحد"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Customer Intelligence Dashboard", fontsize=18,
                     fontweight='bold', y=1.01)

        # Chart 1: Donut
        ax = axes[0, 0]
        counts = self.df['cluster'].value_counts().sort_index()
        colors = [CLUSTER_COLORS[i] for i in counts.index]
        wedges, _ = ax.pie(counts, colors=colors,
                           wedgeprops=dict(width=0.5), startangle=90)
        patches = [mpatches.Patch(color=CLUSTER_COLORS[i],
                   label=f"{CLUSTER_NAMES[i]} ({counts[i]})") for i in counts.index]
        ax.legend(handles=patches, loc='lower center',
                  bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=9, frameon=False)
        ax.set_title("Customer segments", fontsize=12, fontweight='bold')

        # Chart 2: Avg spent bar
        ax = axes[0, 1]
        avg = self.df.groupby('cluster')['total_spent'].mean()
        names = [CLUSTER_NAMES[i] for i in avg.index]
        clrs = [CLUSTER_COLORS[i] for i in avg.index]
        bars = ax.bar(names, avg.values, color=clrs, width=0.5, zorder=3)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                    f"${bar.get_height():,.0f}", ha='center', fontsize=9)
        ax.set_title("Avg spending per segment", fontsize=12, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.set_ylim(0, self.df['total_spent'].max() * 1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Chart 3: Histogram
        ax = axes[1, 0]
        bins = [0, 1000, 2000, 3000, 4000, 6000]
        labels = ['$0-1k', '$1k-2k', '$2k-3k', '$3k-4k', '$4k+']
        self.df['spend_bin'] = pd.cut(self.df['total_spent'],
                                      bins=bins, labels=labels, right=False)
        cnts = self.df['spend_bin'].value_counts().reindex(labels)
        bars = ax.bar(labels, cnts, color='#7F77DD', width=0.6, zorder=3)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(int(bar.get_height())), ha='center', fontsize=10)
        ax.set_title("Spending distribution", fontsize=12, fontweight='bold')
        ax.set_ylim(0, cnts.max() + 3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Chart 4: Scatter
        ax = axes[1, 1]
        for cluster_id, group in self.df.groupby('cluster'):
            ax.scatter(group['total_purchases'], group['total_spent'],
                       c=CLUSTER_COLORS[cluster_id],
                       label=CLUSTER_NAMES[cluster_id], s=60, alpha=0.85, zorder=3)
        ax.set_xlabel("Total purchases", fontsize=10)
        ax.set_ylabel("Total spent ($)", fontsize=10)
        ax.set_title("Purchases vs spent", fontsize=12, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
        ax.legend(frameon=False, fontsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        self._save(fig, "00_dashboard.png")

    def _save(self, fig, filename: str):
        path = f"{self.output_dir}/{filename}"
        fig.savefig(path, dpi=150, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        self.logger.info(f"Saved: {path}")