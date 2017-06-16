from paramecio.citoplasma.i18n import I18n, load_lang
from settings.config_admin import modules_admin

modules_other=[I18n.lang('pastafari', 'pastafari', 'Pastafari'), [["Dashboard", 'modules.pastafari.dashboard', '/pastafari'], [I18n.lang('pastafari', 'os', 'Operating systems'), 'modules.pastafari.os', '/pastafari/os'], [I18n.lang('pastafari', 'servers_groups', 'Server Groups'), 'modules.pastafari.groups', '/pastafari/groups'], [I18n.lang('pastafari', 'servers', 'Servers'), 'modules.pastafari.servers', '/pastafari/servers']], 'pastafari']

modules_admin.append(modules_other)
