# -*- coding: utf-8 -*-
import os
import pwd
import subprocess
import random

from django.db import models
from django.utils.log import getLogger
from django.conf import settings
from syncmedia import managers

logger = getLogger("syncmedia.models")

SYNC_DIRS = getattr(settings, "SYNCHRO_DIRS", ['media/','hidden/'])
PROJECT_PATH = getattr(settings, "PROJECT_PATH", '/var/www/***REMOVED***')


class Host(models.Model):
    hostname = models.CharField(max_length=256, unique=True)
    url = models.CharField(max_length=256, unique=True)
    port = models.IntegerField(max_length=40, default=9922)
    username = models.CharField(max_length=256, blank=True, null=True)
    pubkey = models.CharField(max_length=512)

    objects = managers.HostManager()

    def __unicode__(self):
        return str(" ").join([self.hostname, self.url])

    def _kill(self, host=None):
        if host is None:
            command = COM_RELOAD
        else:
            command = [
                '/usr/bin/ssh',
                '%s' % host.url,
                '-l %s' % host.username,
                '-p %s' % host.port,
                '-c %s' % COMM_RELOAD,
            ]
        return subprocess.call(command)

    def push(self, sync_dirs=None, timeout=10, kill=False):
        ''' Rsync push to others hosts.

        Parameters
        ----------
        sync_dirs: list of directory to sync (path a relative to
            PROJECT_PATH).
        timeout: timeout in seconds for ssh connection.
        kill: if True call a remote command to restart the server.

        Returns
        -------
        a dictionary with host's urls keys and couples (dirname, bool)
            for each succeded or failed sync.

        '''
        if sync_dirs is None:
            sync_dirs = SYNC_DIRS
        hosts = Host.objects.all().exclude(url=self.url)
        ret = {}
        for host in hosts:
            ret[host.url] = []
            for sync_dir in sync_dirs:
                path = os.path.join(PROJECT_PATH, sync_dir)
                path_rsa = getattr(
                    settings,
                    "PATH_RSA",
                    os.path.join(pwd.getpwnam(self.username).pw_dir, ".ssh", "id_rsa"))
                rsync_call = [
                    '/usr/bin/rsync',
                    '-r',
                    '-e',
                    "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=%s -p %s -i %s" % \
                    (timeout, host.port, path_rsa),
                    path,
                    "%s@%s:%s" % (host.username, host.url, path),
                ]
                try:
                    out = subprocess.call(rsync_call)
                    logger.debug("%s\nexited with status: %s", " ".join(rsync_call), out)
                except Exception, e:
                    logger.error(e)
                    continue
                if out == 0:
                    logger.info("Syncrone, push of %s to %s SUCCEDED", sync_dir, host)
                    ret[host.url].append( (sync_dir, True) )
                else:
                    logger.info("Syncrone, push of %s to %s FAILED", sync_dir, host)
                    ret[host.url].append( (sync_dir, False) )
        return ret

    def pull(self, host=None, sync_dirs=None, timeout=10, kill=False):
        ''' Rsync pull to others hosts.

        Parameters
        ----------
        host: host to pull data from, if it's None a random one will
             be picked.
        sync_dirs: list of directory to sync (path a relative to
            PROJECT_PATH).
        timeout: timeout in seconds for ssh connection.
        kill: if True call a command to restart the local server.

        Returns
        -------
        A dictionaty with dirnames as keys and bools as values,
            indicating wether the rsync succeded or not.

        '''
        ret = {}
        if host is None:
            hosts = Host.objects.all().exclude(url=self.url)
            if hosts.exists():
                idx = random.randint(0, hosts.count() - 1)
                host = hosts[idx]
            else:
                logger.warning("No other hosts found... nothing to do.")
                return ret
        if sync_dirs is None:
            sync_dirs = SYNC_DIRS
        for sync_dir in sync_dirs:
            path = os.path.join(PROJECT_PATH, sync_dir)
            path_rsa = getattr(
                settings,
                "PATH_RSA",
                os.path.join(pwd.getpwnam(self.username).pw_dir, ".ssh", "id_rsa"))
            rsync_call = [
                '/usr/bin/rsync',
                '-r',
                '-e',
                "ssh -o StrictHostKeyChecking=no -o ConnectTimeout=%s -p %s -i %s" % \
                (timeout, host.port, path_rsa),
                "%s@%s:%s" % (host.username, host.url, path),
                path,
            ]
            try:
                out = subprocess.call(rsync_call)
                logger.debug("%s\nexited with status: %s", " ".join(rsync_call), out)
            except Exception, e:
                logger.error(e)
                continue
            if out == 0:
                logger.info("pull of %s from %s SUCCEDED", sync_dir, host)
                ret[sync_dir] = True
            else:
                logger.info("pull of %s from %s FAILED", sync_dir, host)
                ret[sync_dir] = False
        return ret
