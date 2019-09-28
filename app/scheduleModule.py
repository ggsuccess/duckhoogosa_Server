import threading
import schedule
import os

import time
from aws_s3 import download, upload_file
from pixelate import make_img_pixel
from collections import deque
import pprint

imageScheduleQueue = deque()


def clear_image_qeuee():
    if len(imageScheduleQueue) != 0:
        print("Start trans")
        obj = imageScheduleQueue.popleft()
        download(obj['link'], obj['filename'])
        make_img_pixel(obj['filename'])
        path = os.getcwd() + "/download/" + obj['filename']

        data = obj['link'].split('/')
        root_index = obj['link'].split('/').index("duckhoogosa.s3.ap-northeast-2.amazonaws.com")
        full_path = ""
        for i, v in enumerate(obj['link'].split('/')):
            if i > root_index:
                full_path += "/" + v

        url = upload_file(path, full_path[1:])
        if os.path.isfile(path):
            os.remove(path)
            print("파일 지움", path)


def schedule_list():
    schedule.every(90).seconds.do(clear_image_qeuee)
    while True:
        schedule.run_pending()  # pending된 Job을 실행
        time.sleep(1)


alarm_thread = threading.Thread(target=schedule_list)
alarm_thread.start()
print('Thread Work Start (schedule)')

# threading을 사용하지 않으면 이 라인을 출력할 수 없다.


# obj = {link: args['representImg']}
# filename = getFileNameFromLink(args['representImg'])
# download(args['representImg'], filename)

# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every(5).to(10).minutes.do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":17").do(job)

