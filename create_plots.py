import coverage_plot
import gantt_plot
import project_finance_plot
import data_utils
import datetime

if __name__ == '__main__':
    projects, members, allocations, checkpoints = data_utils.load_data()
    start_date = datetime.datetime.strptime('01-01-2024', '%d-%m-%Y')
    end_date = datetime.datetime.strptime('01-07-2030', '%d-%m-%Y')
    coverage_axs = coverage_plot.make_coverage_plot(members, allocations,
                                                    end_time=end_date,
                                                    start_time=start_date)
    coverage_axs.figure.savefig("coverage_plot.png", bbox_inches='tight')
    gantt_axs = gantt_plot.make_gantt_plot(projects, allocations, members,
                                           start_time=start_date,
                                           end_time=end_date)
    gantt_axs.figure.savefig("gantt_plot.png", bbox_inches='tight')
    project_finance_fig = project_finance_plot.make_finance_plot(
            projects, checkpoints, end_time=end_date)
    project_finance_fig.savefig("project_finance_plot.png", bbox_inches='tight')
