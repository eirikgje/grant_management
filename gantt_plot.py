import datetime
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.dates as mdates
import plot_utils


def gantt_plot_project(project, axes, bar_height, y0, color,
                       default_start_time=None, default_end_time=None):
    if project['start_date'] == "None":
        width = default_end_time - default_start_time
        x0 = default_start_time
    else:
        width = project['end_date'] - project['start_date']
        x0 = project['start_date']
    rectangle = patches.Rectangle([x0, y0], width, bar_height, facecolor=color)
    axes.add_patch(rectangle)
    return axes


def gantt_plot_allocation(allocation, axes, bar_height, y0, color,
                          start_time=None, end_time=None):
    if start_time is None or start_time < allocation['start_date']:
        start_time = allocation['start_date']
    if end_time is None or end_time > allocation['end_date']:
        end_time = allocation['end_date']
    width = end_time - start_time
    x0 = start_time
    rectangle = patches.Rectangle([x0, y0], width, bar_height, facecolor=color,
                                  alpha=0.6)
    axes.add_patch(rectangle)
    rx, ry = rectangle.get_xy()
    cx = rx + rectangle.get_width() / 2.0
    cy = ry + rectangle.get_height() / 2.0
    axes.annotate(f'{allocation["percentage"]}%', (cx, cy), color='k',
                  weight='bold', fontsize=15, ha='center', va='center')
    return axes


def make_gantt_plot(projects, allocations, personnel,
                    start_time=datetime.datetime.strptime('01-01-2025',
                                                          '%d-%m-%Y'),
                    end_time=None):
    proj_start_time, proj_end_time = plot_utils.determine_plot_timelines(projects)
    if start_time is None:
        start_time = proj_start_time
    if end_time is None:
        end_time = proj_end_time
    if start_time.day != 1:
        start_time = datetime.datetime.replace(start_time, day=1)
    while not plot_utils.is_last_day_of_month(end_time):
        end_time = end_time + datetime.timedelta(days=1)

    proj_person_mapping = {}

    fig, axs = plt.subplots()
    fig.set_figheight(18)
    fig.set_figwidth(32)
    num_entries = len(projects)
    for allocation in allocations:
        if allocation['project'] not in proj_person_mapping.keys():
            proj_person_mapping[allocation['project']] = []
        if allocation['name'] in proj_person_mapping[allocation['project']]:
            continue
        proj_person_mapping[allocation['project']].append(allocation['name'])
        num_entries += 1

    plot_height = num_entries
    bar_height = 1

    y0 = plot_height - bar_height + 0.5
    ticks = []
    project_colors = plot_utils.get_project_colors()
    for project in projects:
        curr_color = project_colors[project['name']]
        axs.hlines(y0, xmin=start_time, xmax=end_time, color='k')
        axs = gantt_plot_project(project, axs, bar_height, y0,
                                 color=curr_color,
                                 default_start_time=start_time,
                                 default_end_time=end_time)
        ticks.insert(0, project['name'])
        y0 -= bar_height
        for person in personnel:
            tick_inserted = False
            was_found = False
            for allocation in allocations:
                if allocation['project'] == project['name'] and allocation['name'] == person['name']:
                    was_found = True
                    if not tick_inserted:
                        axs.hlines(y0, xmin=start_time, xmax=end_time, color='k')
                        ticks.insert(0, allocation['name'])
                        tick_inserted = True
                    axs = gantt_plot_allocation(allocation, axs, bar_height, y0,
                                                color=curr_color,
                                                start_time=start_time,
                                                end_time=end_time)
            if was_found:
                y0 -= bar_height
    axs.set_xlim(start_time, end_time)
    axs.set_ylim(0.5, num_entries+0.5)
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
    axs.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13, 6)))
    axs.set_xlabel('Date', size=25)
    axs.set_ylabel('Project/person', size=25)
    axs.set_yticks(range(1, len(ticks)+1))
    axs.set_yticklabels(ticks)
    axs.tick_params(axis='both', labelsize=20)
    return axs
