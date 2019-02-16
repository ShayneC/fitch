"""
MIT License

Copyright (c) 2018 williamfzc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import unittest
import os
import time

from fitch.screen import FDevice
from fitch import detector
from fitch.logger import logger


class FPic(object):
    def __init__(self, pic_path):
        # /path/to/pic/pic1.png
        self.path = pic_path
        assert self.is_existed(), '{} not existed'.format(pic_path)
        # pic1.png
        self.file_name = pic_path.split(os.sep)[-1]
        # pic1
        self.name = self.file_name.split('.')[0]

    def is_existed(self):
        return bool(os.path.isfile(self.path))


class FPicStore(object):
    """ load pictures from dir, and store them here """

    def __init__(self, pic_dir_path):
        assert os.path.isdir(pic_dir_path), '{} not a dir'.format(pic_dir_path)
        self.pic_dir_path = pic_dir_path
        self.fpic_dict = dict()

        for each_pic_path in [os.path.join(pic_dir_path, i) for i in os.listdir(self.pic_dir_path)]:
            each_fpic = FPic(each_pic_path)
            each_pic_name = each_fpic.name
            self.fpic_dict[each_pic_name] = each_fpic
            logger.info('LOAD PICTURE [{}] FROM {}'.format(each_pic_name, each_pic_path))

    def __getattr__(self, item):
        if item in self.fpic_dict:
            return self.fpic_dict[item].path
        raise FileNotFoundError('picture {} not found in {}'.format(item, self.pic_dir_path))


class FTestCase(unittest.TestCase):
    """
    FTestCase, based on unittest.TestCase.
    Can be easily used by other modules, which support unittest.
    """
    f_device_id = None
    f_device = None

    @classmethod
    def setUpClass(cls):
        if not cls.f_device:
            cls.f_init_device(cls.f_device_id)
        cls.f_device_id = cls.f_device.device_id

    @classmethod
    def tearDownClass(cls):
        if cls.f_device:
            cls.f_stop_device()
            cls.f_device = None
        cls.f_device_id = None

    @classmethod
    def f_init_store(cls, pic_dir_path):
        """
        init pic store, and you can access them directly.

        eg:
        self.f_init_store('/path/to/your/pic_dir')
        self.f_pic_store.YOUR_PIC_NAME
        """
        cls.f_pic_store = FPicStore(pic_dir_path)

    @classmethod
    def f_init_device(cls, device_id):
        """ init device, and return it """
        assert cls.f_device_id, 'should set your device id first, likes `cls.f_device_id="1234F"`'
        assert not cls.f_device, 'device {} already existed, should not be re-init'.format(device_id)
        cls.f_device = FDevice(device_id)
        logger.info('DEVICE {} INIT FINISHED'.format(device_id))
        return cls.f_device

    @classmethod
    def f_find_target(cls, target_pic_path):
        """ find target, and get its position """
        assert cls.f_device, 'device not found, init it first, likes `cls.f_device_id="1234F"`'
        pic_path = cls.f_device.screen_shot()
        result = detector.detect(target_pic_path, pic_path)
        os.remove(pic_path)

        try:
            target_point = detector.cal_location(result)
        except AssertionError:
            # if not found, return None
            return None

        return target_point

    @classmethod
    def f_find_and_tap_target(cls, target_pic_path):
        """ find target, get its position, and tap it """
        target_point = cls.f_find_target(target_pic_path)
        assert target_point is not None, '{} not found'.format(target_pic_path)
        cls.f_device.player.tap(target_point)

    @classmethod
    def f_stop_device(cls):
        """ stop device after usage """
        cls.f_device and cls.f_device.stop()
        logger.info('DEVICE {} STOPPED'.format(cls.f_device_id))

    @classmethod
    def f_reset(cls):
        """ back to home page, and clean up backstage """
        cls.f_device.toolkit.input_key_event(3)
        time.sleep(1)
        cls.f_device.toolkit.clean_backstage()