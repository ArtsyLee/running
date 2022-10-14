
import argparse
import os
import time
from config import TEMP_FOLDER

from stravalib.exc import RateLimitTimeout, ActivityUploadFailed, RateLimitExceeded
from gpxpy import parse as GPXParse

from utils import make_strava_client, get_strava_last_time, upload_gpx_to_strava


def get_files(last_time):
    """
    reuturn to values one dict for upload
    and one sorted list for next time upload
    """
    file_names = os.listdir(TEMP_FOLDER)
    temp_files = [
        (GPXParse(open(os.path.join(TEMP_FOLDER, i), "r", encoding = "UTF8")), os.path.join(TEMP_FOLDER, i))
        for i in file_names
        if i.endswith(".gpx")
    ]
    files_dict = {
        int(i[0].get_time_bounds().start_time.timestamp()): i[1]
        for i in temp_files
        if int(i[0].get_time_bounds().start_time.timestamp()) > last_time
    }

    return sorted(list(files_dict.keys())), files_dict


if __name__ == "__main__":
    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret")
    parser.add_argument("strava_refresh_token", help="strava refresh token")
    parser.add_argument(
        "--all",
        dest="all",
        action="store_true",
        help="if upload to strava all without check last time",
    )

    options = parser.parse_args()

    print("login")
    client = make_strava_client(
        options.client_id, options.client_secret, options.strava_refresh_token
    )

    print("login finish")
    
    last_time = 0
    # 是否只更新最新的
    if not options.all:
        last_time = get_strava_last_time(client, is_milliseconds = False)
    
    print("get file list finish")
    to_upload_time_list, to_upload_dict = get_files(last_time)
    index = 1
    for i in to_upload_time_list:
        temp_file = to_upload_dict.get(i)
        basename = os.path.basename(temp_file)

        # 咕咚
        name = None
        info = os.path.splitext(basename)[0].split("_")
        desc = "来源：咕咚 ({})\n时间：{}".format(info[2], info[0])
        # GPS Kit
        #desc = "来源：GPS Kit\n时间：{}".format(basename[:8])
        #info = os.path.splitext(basename)[0]
        #name = info[8:] if len(info[8:]) > 0 else None

        # 跑步
        type = "run"
        # 徒步
        #type = "hike"
        # 骑行
        #type = "ride"

        try:
            print(f"File: {basename}")
            upload_gpx_to_strava(client, temp_file, name = name, desc = desc, type = type)
        except RateLimitTimeout as e:
            timeout = e.timeout
            print(f"Strava API Rate Limit Timeout. Retry in {timeout} seconds")
            print()
            time.sleep(timeout)
            upload_gpx_to_strava(client, temp_file, name = name, desc = desc, type = type)
        except ActivityUploadFailed as e:
            print(f"Upload faild error {str(e)}")

        # spider rule
        time.sleep(1)

    time.sleep(10)

