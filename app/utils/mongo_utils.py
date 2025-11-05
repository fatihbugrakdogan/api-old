import time


def convert_object_id_to_number(user_id):
    return str(int(time.mktime(user_id.generation_time.timetuple())))
