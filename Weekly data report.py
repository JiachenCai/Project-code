import pandas as pd
import pyodbc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import datetime
from sqlalchemy.engine import create_engine
import matplotlib.font_manager as font_manager

for _ in range(10):
    try:
        engine = create_engine('')
        #Just for displaying, ignore the parameters of the database
    except:
        pass
    else:
        break
else:
    assert 0

######## PART 1 ########

recent_dtrend = pd.read_sql(
    f'''
    SELECT 
        date
        ,num_new AS 'num_new'
        ,num_psn AS 'num_person'
        ,num_opn AS 'num_open'
    FROM daily_trend
    WHERE date >= '{DATE_START_DAILY}' AND date <= '{DATE_END}';''',
    engine,
)


recent_dtrend = recent_dtrend.astype({
    'num_new': int,
    'num_person': int,
    'num_open': int,
})

recent_dtrend = recent_dtrend.fillna(0)

# to csv
temp = recent_dtrend.copy()
temp.index = temp['date'].astype('str').str.slice(-5)
temp = temp.iloc[:, 1:]
temp = temp.loc[:, ::-1]



# draw plot
fig, ax = plt.subplots(figsize=(8,4.5))
for idx in range(1, 4):
    x = recent_dtrend['date']
    y1 = recent_dtrend.iloc[:, idx]
    y2 = 0 if idx == 1 else recent_dtrend.iloc[:, idx-1]
    ax.plot(x ,y1 ,'-o',label=recent_dtrend.columns[idx])
    ax.fill_between(x, y1, y2, alpha=0.5)

ax.set_ylim(bottom=0, top=ax.get_ylim()[1])

for current_date in recent_dtrend['date']:
    if current_date.weekday() >= 5:
        plt.bar(current_date, ax.get_ylim()[1]
                ,color='grey', alpha=0.3, width=1)

# Decorations
ax.set_title('Daily Trend for Recent 15 Days')

handles, labels = ax.get_legend_handles_labels()
ax.legend(
    reversed(handles),
    reversed(labels),
    bbox_to_anchor=(1, 0.5),
    loc='center left',
)

ax.set_xticks(recent_dtrend['date'])
fig.autofmt_xdate()

# plt.ylim(bottom=0)
plt.xlabel('date')
plt.grid(axis='y', alpha=0.3)
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)

plt.savefig(IMG_PATH[0], bbox_inches='tight', dpi=200)
#plt.show()

######## PART 2 ########
recent_mtrend = pd.read_sql(
    f'''
    SELECT 
        b.last_date_week
        ,SUM(num_new) AS 'num_new'
        ,SUM(num_psn) AS 'num_person'
        ,SUM(num_opn) AS 'num_open'
    FROM daily_trend a
    LEFT JOIN daily_user b ON a.date = b.date
    WHERE b.last_date_week >= '{DATE_START_WEEKLY}' AND b.last_date_week <= '{DATE_END}'
    GROUP BY b.last_date_week''',
    engine,
)

recent_mtrend = recent_mtrend.astype({
    'num_new': int,
    'num_person': int,
    'num_open': int,
})
recent_mtrend = recent_mtrend.fillna(0)

temp = recent_mtrend.copy()
temp.index = temp['last_date_week'].astype('str').str.slice(-5)
temp = temp.iloc[:, 1:]
temp = temp.loc[:, ::-1]


# draw plot
fig, ax = plt.subplots(figsize=(8,4.5))
for idx in range(1, 4):
    x = recent_mtrend['last_date_week']
    y1 = recent_mtrend.iloc[:, idx]
    y2 = 0 if idx == 1 else recent_mtrend.iloc[:, idx-1]
    ax.plot(x ,y1 ,'-o',label=recent_mtrend.columns[idx])
    ax.fill_between(x, y1, y2, alpha=0.5)

# Decorations
ax.set_title('Weekly Sum Trend for Recent 5 Weeks')

handles, labels = ax.get_legend_handles_labels()
ax.legend(
    reversed(handles),
    reversed(labels),
    bbox_to_anchor=(1, 0.5),
    loc='center left',
)

ax.set_xticks(recent_mtrend['last_date_week'])
fig.autofmt_xdate()

plt.xlabel('the last date of a week')
plt.ylim(bottom=0)
plt.grid(axis='y', alpha=0.3)
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)

plt.savefig(IMG_PATH[1], bbox_inches='tight', dpi=200)


######## PART 3 ########
page = pd.read_sql(
    f'''
    SELECT
        a.date
        ,name
        ,num_psn AS 'num_person'
        ,total_psn AS 'total_num_person'
        ,num_psn / total_psn AS 'percent_num_person'
    FROM
    (
        SELECT *
        FROM page
        WHERE
            (date >= '{DATE_START_DAILY}' AND date <= '{DATE_END}') AND 
            (name = '课表首页' OR 
            name = '单个院校评测详情' OR 
            name = '单个评测内容详情')
    ) a
    LEFT JOIN
    (
        SELECT date, SUM(num_psn) AS total_psn
        FROM page
        WHERE 
        (date >= '{DATE_START_DAILY}' AND date <= '{DATE_END}') AND 
        (name = '课表首页' OR 
        name = '单个院校评测详情' OR 
        name = '单个评测内容详情')
        GROUP BY date
    ) b ON a.date = b.date ''',
    engine,
)

#print(page)

page = page.astype({
    'num_person': int,
    'total_num_person': int,
    'percent_num_person': float,
})

pivot_page = page.pivot(
    index='date',
    columns='name',
    values='percent_num_person',
)
pivot_page = pivot_page[['课表首页', '单个院校评测详情', '单个评测内容详情']]
pivot_page.columns = ['timetable', 'school', 'course']
pivot_page = pivot_page.fillna(0)

temp = pivot_page.copy()
temp.index = temp.index.astype('str').str.slice(-5)
temp = (temp * 100).astype('int').astype('str') + '%'
temp = temp.loc[:, ::-1]
DataFrame_to_image(temp.T, './img/5.png')


#plot
fig, ax = plt.subplots(figsize=(8,4.5))
x = pivot_page.index
y2 = pd.Series(0, index=pivot_page.index)

ax.set_ylim(bottom=0, top=1)

for current_date in recent_dtrend['date']:
    if current_date.weekday() >= 5:
        plt.bar(current_date, 1
                ,color='grey', alpha=0.5, width=1)

for idx in range(0, 3):
    y1 = pivot_page.iloc[:, idx]
    plt.bar(
        x, y1,
        bottom=y2,
        edgecolor='white',
        label=y1.name,
    )
    y2 = y2 + y1


ax.set_title('Visitor Percentage of Business for Recent 15 Days')

handles, labels = ax.get_legend_handles_labels()
ax.legend(
    reversed(handles),
    reversed(labels),
    bbox_to_anchor=(1, 0.5),
    loc='center left',
)

ax.set_xticks(x)
fig.autofmt_xdate()

ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

plt.xlabel('date')
plt.grid(axis='y', alpha=0.3)
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)

plt.savefig(IMG_PATH[2], bbox_inches='tight', dpi=200)

## part 4

page_rank = pd.read_sql(

    f'''
    SELECT 
        p.name name,
        p.num_psn num_psn,
        p.num_clk num_clk
    FROM ucourse.page p
    WHERE p.date = '{DATE_END}'
    ORDER BY p.num_psn DESC
    LIMIT 5;''',

    engine,

)

page_rank.index = page_rank.index + 1

## plot

page_rank = pd.read_sql(
    f'''
    SELECT 
        p.name name,
        p.num_psn num_psn,
        p.num_clk num_clk
    FROM ucourse.page p
    WHERE p.date = '{DATE_END}'
    ORDER BY p.num_psn DESC
    LIMIT 10;''',
    engine,
)

x = range(0, 10, 1)
page_rank.plot(kind="bar", width=0.9)

# font_path = '/root/project/uFair/workflow/Noto-sans/NotoSans-Regular-2.ttf'
font_path = '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'
font_prop = font_manager.FontProperties(fname=font_path)

plt.xticks(x, page_rank['name'], rotation=60, fontproperties=font_prop)
plt.title("Top 10 Most Visited Pages of Previous Day")

plt.ylim(bottom=0)
plt.grid(axis='y', alpha=0.3)
plt.xlabel('The Name of Pages')
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)
plt.legend(
    bbox_to_anchor=(1, 0.5),
    loc='center left',
    )
plt.savefig('./img/8.png', bbox_inches='tight', pad_inches=0, dpi=200)

# part 5

getin_rank = pd.read_sql(
    f"""
    SELECT name, num_psn, num_opn 
    FROM getin 
    WHERE date = '{DATE_END}'
    ORDER BY num_psn DESC 
    LIMIT 5
    """,
    engine
)

getin_rank.index = getin_rank.index + 1

## plot

getin_rank = pd.read_sql(
    f"""
    SELECT name, num_psn, num_opn 
    FROM getin 
    WHERE date = '{DATE_END}'
    ORDER BY num_psn DESC 
    LIMIT 10
    """,
    engine
)

x = range(0, 10, 1)
getin_rank.plot(kind="bar", width=0.9)

# font_path = '/root/project/uFair/workflow/Noto-sans/NotoSans-Regular-2.ttf'
font_path = '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'
font_prop = font_manager.FontProperties(fname=font_path)

plt.xticks(x, getin_rank['name'], rotation=90, fontproperties=font_prop)
plt.title("Top 10 Most Getin Scenarios of Previous Day")

plt.ylim(bottom=0)
plt.grid(axis='y', alpha=0.3)
plt.xlabel('The Name of Pages')
plt.gca().spines["top"].set_alpha(0)
plt.gca().spines["bottom"].set_alpha(.3)
plt.gca().spines["right"].set_alpha(0)
plt.gca().spines["left"].set_alpha(.3)
plt.legend(
    bbox_to_anchor=(1, 0.5),
    loc='center left',
    )
plt.savefig('./img/9.png', bbox_inches='tight', pad_inches=0, dpi=200)


## Hourly Trend Of The Previous Day

Hour_trend = pd.read_sql(
    f"""
    SELECT hour, num_psn, num_opn, num_vst 
    FROM hourly_trend 
    WHERE date = '{DATE_END}'
    """,
    engine
)

Hour_trend.columns = ['hour', 'num_psn', 'num_opn', 'num_vst']


fig, ax = plt.subplots(figsize=(8, 4.5))

for idx in list(range(1, 4)):
    x = Hour_trend['hour']
    y1 = Hour_trend.iloc[:, idx]
    y2 = 0 if idx == 1 else Hour_trend.iloc[:, idx-1]
    ax.plot(x ,y1 ,'-o',label=Hour_trend.columns[idx])
    ax.fill_between(x, y1, y2, alpha=0.5)
plt.ylim(ymin = 0, ymax = ax.get_ylim()[1])

ax.set_title('Hourly Trend Of The Previous Day')
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
plt.savefig('./img/10.png', bbox_inches='tight', pad_inches=0, dpi=200)