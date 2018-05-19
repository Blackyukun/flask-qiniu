import os
import re
import sys
from datetime import datetime

import qiniu


class QiniuUpload(object):
    """
    Integrated qiniu storage Flask plugin
    """

    def __init__(self, app=None):
        self.app = app
        if app: self.init_app(app)

    def init_qiniu(self):
        self._qiniuer = qiniu.Auth(self.app.config.get('QN_ACCESS_KEY', ''),
                                  self.app.config.get('QN_SECRET_KEY', ''))
        self._bucket_manager = qiniu.BucketManager(self._qiniuer)
        self._bucket = self.app.config.get('QN_PIC_BUCKET', '')
        self._domain = 'http://' + self.app.config.get('QN_PIC_DOMAIN', '') + '/'

    def init_app(self, app):
        """
        Initializes your qiniu settings from the application settings.
        :param app: Flask application instance
        """
        self.app = app
        self.init_qiniu()

    def _get_publish_time(self, timestamp):
        if timestamp:
            t = float(timestamp/10000000)
            return datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M')
        return None

    def _get_file_size(self, size):
        if size:
            return float('%.2f' % (size / 1024))
        return 0

    def _get_file_link(self, filename):
        return self._domain + '/' + filename

    def get_token(self, policy=None):
        """Generate uploaded token"""
        return self._qiniuer.upload_token(self._bucket, policy=policy)

    def _legal_file_name(self, filename):
        """
        Parse the legal file name
        :param filename: file name
        :return: file name
        """
        return re.sub(r'[\/\\\:\*\?"<>|]', r'_', filename)

    def upload_file(self, filename, path=None, data=None):
        """
        :param filename: File name
        :param data: File stream
        :param path: File path before upload
        :return: True or False
        """
        token = self.get_token()
        key = self._legal_file_name(filename)
        try:
            if data:
                ret, info = qiniu.put_data(token, key, data)
            else:
                ret, info = qiniu.put_file(token, key, path)
            return True if info.status_code == 200 else False
        except Exception:
            return False

    def upload_call(self):
        pass

    def delete_file(self, key):
        """
        Delete file
        :param key: file name
        :return: True or False
        """
        ret, info = self._bucket_manager.delete(self._bucket, key)

        return True if ret == {} else False

    def rename_file(self, key, key_to):
        """
        Rename file
        :param key: file name
        :param key_to: new file name
        :return: True or False
        """
        key, key_to = self._legal_file_name(key), self._legal_file_name(key_to)
        ret, info = self._bucket_manager.rename(self._bucket, key, key_to)

        return True if ret == {} else False

    def upload_status(self, key):
        ret, info = self._bucket_manager.stat(self._bucket, key)

        return True if info.status_code == 200 else False

    def get_all_file(self, prefix=None, limit=None, delimiter=None, marker=None, mime_type=()):
        """
        :param prefix: file prefix
        :param limit: list items
        :param delimiter: list all files except '/' and all prefixes separated by '/'
        :param marker: mark
        :param mime_type: file mimeType -> tuple
        :return: [{'
            name':'file name', 
            'url': 'file url',
            'time': 'last update time',
            'size': 'file size',
            }, ]
        """
        if not mime_type: mime_type = ''

        files = []
        ret, eof, info = self._bucket_manager.list(self._bucket, prefix, marker, limit, delimiter)
        if ret.get('items', []):
            for i in ret.get('items'):
                if i.get('mimeType', '').startswith(mime_type):
                    files.append({
                        'name': i.get('key', ''),
                        'url': self._domain + i.get('key', ''),
                        'time': self._get_publish_time(i.get('putTime', '')),
                        'size': self._get_file_size(i.get('fsize', 0))
                    })
        return files

    def crawl_resource_upload(self, url, filename):
        """
        Crawl web resource to Qiniu space
        :param url: web resource
        :param filename: file name
        :return: True or False
        """
        ret, info = self._bucket_manager.fetch(url, self._bucket, filename)
        return True if info.status_code == 200 else False

    def batch_rename(self, keys_dict):
        """
        Batch rename files
        :param keys_dict: 
                File name and new file name key value pair ->
                {
                    'filename1': 'new_filename1',
                    'filename2': 'new_filenamw2',
                }
        :return: True or False
        """
        for k in keys_dict.keys():
            keys_dict[k] = self._legal_file_name(keys_dict[k])
        ops = qiniu.build_batch_rename(self._bucket, keys_dict, force='true')
        ret, info = self._bucket_manager.batch(ops)
        return True if info.status_code == 200 else False

    def batch_delete(self, keys):
        """
        Batch delete files
        :param keys: file names list -> []
        :return: True or False
        """
        ops = qiniu.build_batch_delete(self._bucket, keys)
        ret, info = self._bucket_manager.batch(ops)
        return True if info.status_code == 200 else False

    def _method_result(self, method, *args):
        pass

