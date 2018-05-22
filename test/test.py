#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from flask import Flask
from flask_qiniu import QiniuUpload


class FlaskQiniuTestCase(unittest.TestCase):
    # flask 七牛配置
    CONFIG = dict(
        QN_ACCESS_KEY='七牛 Access Key',
        QN_SECRET_KEY='七牛 Secret Key',
        QN_PIC_BUCKET='七牛空间名称',
        QN_PIC_DOMAIN='七牛空间对应域名'
    )
    # 测试所需配置
    # TEST_CONFIG = dict(
    #     RENAME_FILE = '测试所需重命名文件',
    #     DELETE_FILE = '测试所需删除文件',
    #
    # )
    def setUp(self):
        self.app = self.create_app()
        self.qn = QiniuUpload(self.app)

    def create_app(self):
        app = Flask(__name__)
        app.config.update(self.CONFIG)
        return app

    def test_upload(self):
        f = open('./yinshi.jpg', 'rb')
        stream = f.read()
        f.close()
        filename = 'yinshi.jpg'
        path = './yinshi.jpg'
        ret = self.qn.upload_file(filename, path=None, data=stream)
        ret2 = self.qn.upload_file(filename, path=path)
        self.assertTrue(ret)
        self.assertTrue(ret2)

    def test_rename(self):
        filename = 'yinshi.jpg'
        filename_to = 'jinshi.jpg'
        ret = self.qn.rename_file(filename, filename_to)
        self.assertTrue(ret)

    def test_delete(self):
        filename = 'jinshi.jpg'
        ret = self.qn.delete_file(filename)
        self.assertTrue(ret)

    def test_crawl_upload(self):
        url = 'https://www.baidu.com/img/bd_logo1.png'
        filename = 'baidu_logo.png'
        ret = self.qn.crawl_resource_upload(url, filename)
        self.assertTrue(ret)

    def test_get(self):
        prefix = 'baidu'
        l = self.qn.get_file(prefix)
        self.assertGreater(len(l), 0)


if __name__ == '__main__':
    # unittest.main()
    def suite():
        tests = ['test_upload', 'test_rename', 'test_delete', 'test_crawl_upload', 'test_get']

        return unittest.TestSuite(map(FlaskQiniuTestCase, tests))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())