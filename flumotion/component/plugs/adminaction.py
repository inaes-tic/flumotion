# -*- Mode: Python; test-case-name: flumotion.test.test_http -*-
# vi:si:et:sw=4:sts=4:ts=4
#
# Flumotion - a streaming media server
# Copyright (C) 2006 Fluendo, S.L. (www.fluendo.com).
# All rights reserved.

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE.GPL" in the source distribution for more information.

# Licensees having purchased or holding a valid Flumotion Advanced
# Streaming Server license may use this file in accordance with the
# Flumotion Advanced Streaming Server Commercial License Agreement.
# See "LICENSE.Flumotion" in the source distribution for more information.

# Headers in this file shall remain intact.

import time

from twisted.python import reflect

from flumotion.common import errors, log, common
from flumotion.component.plugs import base


class AdminAction(base.ManagerPlug):
    """
    Base class for plugs that can react to actions by an admin. For
    example, some plugs might want to check that the admin in question
    has the right permissions, and some others might want to log the
    action to a database. Defines the admin action API methods.
    """
    def action(self, avatar, method, args, kwargs):
        raise NotImplementedError('subclasses have to override me')


class AdminActionFileLogger(AdminAction):
    filename = None
    file = None

    def start(self, vishnu):
        self.filename = self.args['properties']['logfile']
        try:
            self.file = open(self.filename, 'a')
        except IOError, data:
            raise errors.PropertiesError('could not open log file %s '
                                         'for writing (%s)'
                                         % (self.filename, data[1]))

    def stop(self, vishnu):
        self.file.close()
        self.file = None

    def action(self, avatar, method, args, kwargs):
        # gaaaaah
        peer = avatar.mind.broker.transport.getPeer()
        s = ('[%04d-%02d-%02d %02d:%02d:%02d] %s@%s: %s: %r %r\n'
             % (time.gmtime()[:6] +
                (getattr(avatar.keycard, 'username', None),
                 common.addressGetHost(peer),
                 method, args, kwargs)))
        self.file.write(s)
        self.file.flush()
