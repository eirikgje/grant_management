import datetime
import matplotlib.pyplot as plt
from matplotlib import patches
import matplotlib.dates as mdates
import plot_utils


def is_covered_by_allocation(month, allocation):
    return (allocation['start_date'] <= month and allocation['end_date'] >=
            month)


def month_iterator(start_time, end_time):
    curr_time = start_time
    delta = datetime.timedelta(days=31)
    new_time = curr_time
    yield new_time
    while new_time < end_time:
        new_time = curr_time + delta
        new_time = datetime.datetime.replace(new_time, day=1)
        curr_time = new_time
        if (curr_time.year == end_time.year and curr_time.month > end_time.month) or (curr_time.year > end_time.year):
            break
        yield new_time


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
                          start_time=None, end_time=None, hatch=None):
    if start_time is None or start_time < allocation['start_date']:
        start_time = allocation['start_date']
    if end_time is None or end_time > allocation['end_date']:
        end_time = allocation['end_date']
    width = end_time - start_time
    x0 = start_time
    rectangle = patches.Rectangle([x0, y0], width, bar_height, facecolor=color,
                                  alpha=0.6, hatch=hatch)
    axes.add_patch(rectangle)
    rx, ry = rectangle.get_xy()
    cx = rx + rectangle.get_width() / 2.0
    cy = ry + rectangle.get_height() / 2.0
    axes.annotate(f'{allocation["percentage"]}%', (cx, cy), color='k',
                  weight='bold', fontsize=15, ha='center', va='center')
    return axes


def fill_basis(personnel, allocations, start_time, end_time):
    for person in personnel:
        person_start_date = start_time if person['start_date'] == "None" else person['start_date']
        person_end_date = end_time if person['end_date'] == "None" else person['end_date']
        curr_basis_start = None
        curr_basis_percentage = None
        prev_date = None
        for curr_date in month_iterator(person_start_date, person_end_date):
            curr_percentage = 0
            for allocation in allocations:
                if allocation["name"] == person["name"]:
                    if is_covered_by_allocation(curr_date, allocation):
                        curr_percentage += allocation["percentage"]
            if curr_basis_start is None:
                if curr_percentage < 100:
                    curr_basis_start = curr_date
                    curr_basis_percentage = 100 - curr_percentage
            else:
                if not curr_basis_percentage == 100 - curr_percentage:
                    allocations.append({
                        "project": "Basis",
                        "financing": "external",
                        "name": person["name"],
                        "start_date": curr_basis_start,
                        "end_date": datetime.datetime.replace(prev_date, day=28),
                        "percentage": curr_basis_percentage})
                    if curr_percentage < 100:
                        curr_basis_start = curr_date
                        curr_basis_percentage = 100 - curr_percentage
                    else:
                        curr_basis_start = None
                        curr_basis_percentage = None
            prev_date = curr_date
        if curr_basis_start is not None:
            allocations.append({
                "project": "Basis",
                "financing": "external",
                "name": person["name"],
                "start_date": curr_basis_start,
                "end_date": datetime.datetime.replace(prev_date, day=28),
                "percentage": curr_basis_percentage})

    return allocations


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

    project_count = []
    allocations = fill_basis(personnel, allocations, start_time, end_time)

    fig, axs = plt.subplots()
    fig.set_figheight(18)
    fig.set_figwidth(32)
    num_entries = len(projects)
    for allocation in allocations:
        if allocation['financing'] == 'internal':
            if f'{allocation['project']}_{allocation['name']}_internal' not in project_count:
                project_count.append(f'{allocation['project']}_{allocation['name']}_internal')
                num_entries += 1
        elif allocation['financing'] == 'external':
            if f'{allocation['project']}_{allocation['name']}_external' not in project_count:
                project_count.append(f'{allocation['project']}_{allocation['name']}_external')
                num_entries += 1

    print(num_entries)
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
            for financing in ('external', 'internal'):
                was_found = False
                tick_inserted = False
                for allocation in allocations:
                    if (allocation['project'] == project['name'] and
                            allocation['name'] == person['name'] and
                            allocation['financing'] == financing):
                        was_found = True
                        if not tick_inserted:
                            axs.hlines(y0, xmin=start_time, xmax=end_time, color='k')
                            ticks.insert(0, allocation['name'])
                            tick_inserted = True
                        if financing == 'external':
                            hatch = None
                        else:
                            hatch = '//'
                        axs = gantt_plot_allocation(allocation, axs,
                                                    bar_height, y0,
                                                    color=curr_color,
                                                    start_time=start_time,
                                                    end_time=end_time,
                                                    hatch=hatch)
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
