import matplotlib.pyplot as plt
from matplotlib import patches
import plot_utils
import datetime
import matplotlib.dates as mdates


def is_covered_by_allocation(month, allocation):
    return (allocation['start_date'] <= month and allocation['end_date'] >=
            month)


def get_end_of_month_date(date):
    end_time = date
    while not plot_utils.is_last_day_of_month(end_time):
        end_time += datetime.timedelta(days=1)
    return end_time


def plot_percentage(axes, date, new_percentage, curr_percentage, y0, color,
                    hatch=None):
    end_of_month = get_end_of_month_date(date)
    width = end_of_month - date
    x0 = date
    start_height = y0 + curr_percentage / 100
    bar_height = new_percentage / 100
    axes.add_patch(patches.Rectangle([x0, start_height], width, bar_height,
                                     facecolor=color, hatch=hatch))
    return axes


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


def make_coverage_plot(personnel, allocations,
                       start_time=datetime.datetime.strptime('01-01-2024',
                                                             '%d-%m-%Y'),
                       end_time=None):
    alloc_start_time, alloc_end_time = plot_utils.determine_plot_timelines(allocations)
    if start_time is None:
        start_time = alloc_start_time
    if end_time is None:
        end_time = alloc_end_time
#    person_allocations = {}
    fig, axs = plt.subplots()
    fig.set_figheight(18)
    fig.set_figwidth(32)
    num_entries = len(personnel)
    colors = plot_utils.get_project_colors()
    ticks = []
    y0 = 0.5
    for person in personnel:
        person_start_date = start_time if person['start_date'] == "None" else person['start_date']
        person_end_date = end_time if person['end_date'] == "None" else person['end_date']
        curr_start_date = max(start_time, person_start_date)
        curr_end_date = min(end_time, person_end_date)
        for date in month_iterator(curr_start_date, curr_end_date):
            curr_percentage = 0
            for allocation in allocations:
                if allocation["name"] == person["name"]:
                    if is_covered_by_allocation(date, allocation):
                        currcolor = colors[allocation["project"]]
                        financing = allocation["financing"]
                        if financing == 'external':
                            hatch = None
                        else:
                            hatch = '//'
                        axs = plot_percentage(axs, date,
                                              allocation["percentage"],
                                              curr_percentage, y0, currcolor,
                                              hatch=hatch)
                        curr_percentage += allocation["percentage"]
                        if curr_percentage > 100:
                            print(curr_percentage)
                            print(date)
                            print(f"Warning! Higher than 100 percentage: {person['name']}")
            if curr_percentage < 100:
                axs = plot_percentage(axs, date, 100-curr_percentage,
                                      curr_percentage, y0, colors['Basis'],
                                      hatch=None)
        y0 += 1
    y0 = 0.5
    for person in personnel:
        ticks.append(person["name"])
        axs.hlines(y0, xmin=start_time, xmax=end_time, color='k', linewidth=4)
        for y in [0.20, 0.40, 0.60, 0.80]:
            axs.hlines(y0+y, xmin=start_time, xmax=end_time, color='grey')
        y0 += 1
    legend_elements = []
    for project, color in colors.items():
        legend_elements.append(patches.Patch(facecolor=color, label=project))
    axs.set_xlim(start_time, end_time)
    axs.set_ylim(0.5, num_entries + 0.5)
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
    axs.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1, 13, 6)))
    axs.set_xlabel('Date', size=25)
    axs.set_ylabel('Person', size=25)
    axs.set_yticks(range(1, len(ticks)+1))
    axs.set_yticklabels(ticks)
    axs.tick_params(axis='both', labelsize=20)
    axs.legend(handles=legend_elements, prop={'size': 20})
    return axs
