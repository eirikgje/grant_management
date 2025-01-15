import coverage_plot, gantt_plot, data_utils
import datetime

if __name__ == '__main__':
    projects, members, allocations = data_utils.load_data()
    end_date = datetime.datetime.strptime('01-07-2030', '%d-%m-%Y')
    coverage_axs = coverage_plot.make_coverage_plot(members, allocations,
                                                    end_time=end_date)
    coverage_axs.figure.savefig("coverage_plot.png", bbox_inches='tight')
    gantt_axs = gantt_plot.make_gantt_plot(projects, allocations, members,
                                           end_time=end_date)
    gantt_axs.figure.savefig("gantt_plot.png", bbox_inches='tight')
