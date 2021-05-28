import matplotlib.pyplot as plt
import pandas as pd

Hour_trend = pd.read_csv('hourly_trend.csv', header = None)
Hour_trend.columns = ['hour', 'num_psn', 'num_opn', 'num_vst']
fig, ax = plt.subplots(figsize=(8, 4.5))

for idx in list(range(1, 4)):
    x = Hour_trend['hour']
    y1 = Hour_trend.iloc[:, idx]
    y2 = 0 if idx == 1 else Hour_trend.iloc[:, idx-1]
    ax.plot(x ,y1 ,'-o',label=Hour_trend.columns[idx])
    ax.fill_between(x, y1, y2, alpha=0.5)
plt.ylim(ymin = 0, ymax = ax.get_ylim()[1])

ax.set_title('Hourly Trend Of The Day Before The Current Date')
handles, labels = ax.get_legend_handles_labels()
ax.legend(
    reversed(handles),
    reversed(labels),
    bbox_to_anchor = (1, 0.5),
    loc = 'center left',
)
ax.set_xticks(Hour_trend['hour'])

plt.xlabel('hour')
plt.grid(axis = 'y', alpha = 0.3)
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)
plt.show()