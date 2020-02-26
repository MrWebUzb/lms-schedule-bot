import csv


def get_user_id(login):
    csv_file = csv.reader(open("infos/stud_id.csv", "rt", encoding='utf-8'), delimiter=",")

    user_list = [line for line in csv_file]

    for i, e in enumerate(user_list):
        try:
            if e[1].lower() == login.lower():
                return e[0]
        except ValueError as ke:
            return False

    return False


