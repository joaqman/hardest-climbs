sport_grade_map = {
    "9c": "5.15d",
    "9b/c": "5.15c/d",
    "9b+": "5.15c",
    "9b/+": "5.15b/c",
    "9b": "5.15b",
    "9a+": "5.15a",
}

boulder_grade_map = {
    "9A": "V17",
    "8C+": "V16",
    "8C": "V15",
}


def map_grades(grade, style="sport"):
    if style == "sport":
        return sport_grade_map.get(grade)
    else:
        return boulder_grade_map.get(grade)


def create_video_list(x):
    links = []
    for name, link in x.items():
        links.append(f'<a href="{link}" class="link-warning">{name}</a>')

    return ", ".join(links)


def create_repeat_list(x):
    return ", ".join(x)


def create_title(title):
    return f'<h4>{title}</h4>'


def create_html_from_json_element(x: dict):
    title = x.get("name")
    grade = x.get("grade")
    fa = x.get("fa")
    repeats = x.get("repeat")
    videos = x.get("videos")

    return f'\
        <div class="col-6">\
            <div class="p-3 bg-secondary text-white rounded">\
                {create_title(title)}\
                Grade: {grade} / {map_grades(grade)}<br>\
                First Ascent: {fa}<br>\
                Repeated by: {create_repeat_list(repeats)}<br>\
                Videos: {create_video_list(videos)}\
            </div>\
        </div>'


def create_html_columns(x: list):
    columns = []

    for climb in x:
        html = create_html_from_json_element(climb)
        columns.append(html)

    return "".join(columns)

