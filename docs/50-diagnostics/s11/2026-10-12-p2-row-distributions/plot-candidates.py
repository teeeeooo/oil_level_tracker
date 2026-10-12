"""Plot distinct preferred source Y values beside unchanged reviewed queries.

A diagnostic coordinate plot, not a level trajectory or newly labeled truth.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
records = json.loads((HERE / 'candidates-readout.json').read_text())
frames = [r['frame'] for r in records['frames']]
fig, ax = plt.subplots(figsize=(11, 5.8), layout='constrained')
fig.patch.set_facecolor('#f7f9fc')
ax.set_facecolor('#ffffff')
ax.axvspan(2.65, 3.35, color='#f3eddb', zorder=0)
for x, frame in enumerate(records['frames']):
    ys = frame['distinct_interface_source_y']
    ax.scatter([x] * len(ys), ys, color='#18846c', s=55, zorder=3)
    known = [r for r in records['results'] if r['query']['frame'] == frame['frame']
             and r['query']['label'] == 'confirmed_target']
    for record in known:
        y = record['query']['source_xy'][1]
        ax.scatter([x], [y], facecolors='none', edgecolors='#b45309', marker='D',
                   linewidths=2.1, s=165, zorder=4)
        ax.annotate(str(int(y)), (x, y), xytext=(-28, -2), textcoords='offset points',
                    fontsize=10, color='#92400e')
ax.set_xticks(range(len(frames)), [f'f{frame}' for frame in frames])
ax.set_ylabel('Saved candidate source Y (downward in the image)')
ax.set_ylim(894, 824)
ax.set_xlim(-.55, 6.55)
ax.grid(axis='y', color='#e2e8f0')
ax.spines[['top', 'right']].set_visible(False)
ax.set_title('Reference similarity also accepts separate lower proposals', loc='left',
             fontsize=15, fontweight='bold', pad=18)
ax.text(3, 892.5, 'Initialization', ha='center', va='bottom', fontsize=9, color='#6b5d37')
ax.legend(handles=[
    Line2D([], [], linestyle='None', marker='o', color='#18846c', label='Interface preference (distinct Y)'),
    Line2D([], [], linestyle='None', marker='D', markerfacecolor='none',
           markeredgecolor='#b45309', markeredgewidth=2, color='none', label='Previously reviewed Oil candidate')],
    loc='center left', bbox_to_anchor=(0.01, .50), frameon=True, fontsize=10)
fig.supxlabel('Seven existing frames; no interpolation. Other proposals retain unreviewed physical identity.',
              fontsize=10, color='#475569')
fig.savefig(HERE / 'candidate-competition.png', dpi=150)
