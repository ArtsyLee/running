
import os
import argparse
import asyncio
from io import BytesIO
from datetime import datetime, timedelta
from config import GARMIN_UPLOAD_FOLDER

from garmin_sync import Garmin
from gpxpy import parse as GPXParse


def get_files(last_time):
    """
    reuturn to values one dict for upload
    and one sorted list for next time upload
    """
    file_names = os.listdir(GARMIN_UPLOAD_FOLDER)
    temp_files = [
        (GPXParse(open(os.path.join(GARMIN_UPLOAD_FOLDER, i), "r", encoding = "UTF8")), os.path.join(GARMIN_UPLOAD_FOLDER, i))
        for i in file_names
        if i.endswith(".gpx")
    ]
    files_dict = {
        int(i[0].get_time_bounds().start_time.timestamp()): i[1]
        for i in temp_files
        if int(i[0].get_time_bounds().start_time.timestamp()) > last_time
    }

    return sorted(list(files_dict.keys())), files_dict


async def upload_activities(garmin_client):
    last_activity = await garmin_client.get_activities(0, 1)
    last_time = 0
    if last_activity:
        # is this startTimeGMT must have ?
        after_datetime_str = last_activity[0]["startTimeGMT"]
        after_datetime = datetime.strptime(after_datetime_str, "%Y-%m-%d %H:%M:%S")
        last_time = after_datetime.timestamp()

    to_upload_time_list, to_upload_dict = get_files(last_time)
    print("get file list finish")

    files_list = []
    for i in to_upload_time_list:
        temp_file = to_upload_dict.get(i)
        f = open(temp_file, encoding = "UTF8")
        file = BytesIO(bytes(f.read(), "utf8"))
        f.close()
        files_list.append((file, "running"))

    await garmin_client.upload_activities(files_list)
    return files_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("garmin_email", nargs="?", help="email of garmin")
    parser.add_argument("garmin_password", nargs="?", help="password of garmin")
    options = parser.parse_args()
    # 国际区
    print("login")
    garmin_auth_domain = ""
    garmin_client = Garmin(
        options.garmin_email, options.garmin_password, garmin_auth_domain
    )
    print("login finish")
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(upload_activities(garmin_client))
    loop.run_until_complete(future)

