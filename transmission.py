# -*- coding: utf-8 -*-
# Created on 2016-9-17
# @author: Yefei
import requests
import base64


def is_hex_str(s):
    for c in s.lower():
        if c not in '0123456789abcdef':
            return False
    return True


class TransmissionRPCException(Exception):
    pass


class TransmissionRPC(object):
    def __init__(self, url='http://127.0.0.1:9091/transmission/', username='transmission', password='transmission'):
        self.url = url + 'rpc'
        self.upload_url = url + 'upload'
        self.session = requests.Session()
        self.session.auth = (username, password)
        self._get_transmission_session_id()
    
    def _get_transmission_session_id(self):
        r = self.session.head(self.url)
        s = r.headers.get('x-transmission-session-id')
        if not s:
            raise Exception('Unable to initialize transmission session id')
        self.session.headers['X-Transmission-Session-Id'] = s
    
    def process_response(self, r):
        if r.status_code != 200:
            r.raise_for_status()
        data = r.json()
        if data['result'] != 'success':
            raise TransmissionRPCException(data['result'])
        return data['arguments']
    
    def send(self, **params):
        r = self.session.post(self.url, json=params)
        return self.process_response(r)
    
    def loadDaemonPrefs(self):
        return self.send(method='session-get')
    
    def loadDaemonStats(self):
        return self.send(method='session-stats')
    
    def checkPort(self):
        return self.send(method='port-test')
    
    def renameTorrent(self, torrentIds, oldpath, newname):
        return self.send(method='torrent-rename-path', arguments={'ids': torrentIds, 'path': oldpath, 'name': newname})
    
    def getTorrents(self, fields, torrentIds=None):
        arguments = {'fields': fields}
        if torrentIds:
            arguments['ids'] = torrentIds
        return self.send(method='torrent-get', arguments=arguments)
    
    def getFreeSpace(self, path):
        r = self.send(method='free-space', arguments={'path': path})
        return r['size-bytes']
    
    def changeFileCommand(self, torrentId, fileIndices, command):
        return self.send(method='torrent-set', arguments={'ids': [torrentId], command: fileIndices})
    
    def sendTorrentSetRequests(self, method, torrent_ids, args={}):
        args['ids']  = torrent_ids
        return self.send(method=method, arguments=args)
    
    def sendTorrentActionRequests(self, method, torrent_ids):
        return self.sendTorrentSetRequests(method, torrent_ids)
    
    def startTorrents(self, torrent_ids, noqueue):
        return self.sendTorrentActionRequests('torrent-start-now' if noqueue else 'torrent-start', torrent_ids)
    
    def stopTorrents(self, torrent_ids):
        return self.sendTorrentActionRequests('torrent-stop', torrent_ids)
    
    def moveTorrents(self, torrent_ids, new_location):
        return self.sendTorrentSetRequests('torrent-set-location', torrent_ids, {"move": True, "location": new_location})
    
    def removeTorrents(self, torrent_ids):
        return self.sendTorrentActionRequests('torrent-remove', torrent_ids)
    
    def removeTorrentsAndData(self, torrent_ids=[]):
        return self.send(method='torrent-remove', arguments={'delete-local-data': True, 'ids': torrent_ids})
    
    def verifyTorrents(self, torrent_ids):
        return self.sendTorrentActionRequests('torrent-verify', torrent_ids)
    
    def reannounceTorrents(self, torrent_ids):
        return self.sendTorrentActionRequests('torrent-reannounce', torrent_ids)
    
    def addTorrentByUrl(self, url, download_dir=None, paused=False):
        if len(url) == 40 and is_hex_str(url):
            url = 'magnet:?xt=urn:btih:' + url
        arguments = {'paused':paused, 'filename':url}
        if download_dir:
            arguments['download-dir'] = download_dir
        return self.send(method='torrent-add', arguments=arguments)
    
    def addTorrentByFile(self, filedata, download_dir=None, paused=False):
        arguments = {'paused':paused, 'metainfo':base64.encodestring(filedata)}
        if download_dir:
            arguments['download-dir'] = download_dir
        return self.send(method='torrent-add', arguments=arguments)
    
    def savePrefs(self, **args):
        return self.send(method='session-set', arguments=args)
    
    def updateBlocklist(self):
        return self.send(method='blocklist-update')
    
    def moveTorrentsToTop(self, torrent_ids):
        return self.sendTorrentActionRequests('queue-move-top', torrent_ids)
    
    def moveTorrentsToBottom(self, torrent_ids):
        return self.sendTorrentActionRequests('queue-move-bottom', torrent_ids)
    
    def moveTorrentsUp(self, torrent_ids):
        return self.sendTorrentActionRequests('queue-move-up', torrent_ids)
    
    def moveTorrentsDown(self, torrent_ids):
        return self.sendTorrentActionRequests('queue-move-down', torrent_ids)


if __name__ == '__main__':
    t = TransmissionRPC()
    #print 'loadDaemonStats:', t.loadDaemonStats()
    #print 'loadDaemonPrefs', t.loadDaemonPrefs()
    print 'getFreeSpace:', t.getFreeSpace('/')
    print 'getTorrents:', t.getTorrents(['id'])
    # print t.addTorrentByFile(open('file.torrent').read())
    # print t.addTorrentByUrl('c453efbb52431c5a0a469d31cf2e0552552607c7')
