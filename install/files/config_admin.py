#!/usr/bin/python3

from paramecio.citoplasma.i18n import I18n

modules_admin=[[I18n.lang('admin', 'users_admin', 'User\'s Admin'), 'paramecio.modules.admin.admin.ausers', 'ausers']]

modules_other=[I18n.lang('pastafari', 'pastafari', 'Pastafari'), [["Dashboard", 'modules.pastafari.dashboard', '/pastafari'], [I18n.lang('pastafari', 'os', 'Operating systems'), 'modules.pastafari.os', '/pastafari/os'], [I18n.lang('pastafari', 'servers_groups', 'Server Groups'), 'modules.pastafari.groups', '/pastafari/groups'], [I18n.lang('pastafari', 'servers', 'Servers'), 'modules.pastafari.servers', '/pastafari/servers'], ["", 'modules.pastafari.admin.tasks', 'pastafari/tasks'], ["", 'modules.pastafari.admin.updateservers', 'pastafari/updateservers']], 'pastafari']

modules_admin.append(modules_other)
