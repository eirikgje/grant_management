import datetime


def get_project_colors():
#    colors = ['deeppink', 'blue', 'green', 'red', 'purple', 'brown']
    colors = {
            "CosmoglobeHD": "hotpink",
            "Cosmoglobe": "peru",
            "Origins": "cornflowerblue",
            "LiteBIRD Norway": "darkorchid",
            "Commander": "darkseagreen",
            "Basis": "darkgrey"}

    return colors


def determine_plot_timelines(entities):
    start_date = None
    end_date = None
    for entity in entities:
        if entity['start_date'] == "None":
            continue
        if start_date is None or entity['start_date'] < start_date:
            start_date = entity['start_date']
        if end_date is None or entity['end_date'] > end_date:
            end_date = entity['end_date']
    return start_date, end_date


def is_last_day_of_month(date):
    delta = datetime.timedelta(days=1)
    if date.month != (date + delta).month:
        return True
    return False
