#  err-dnsutils: Run common DNS utils: host, dig, nslookup
#  Copyright (C) 2012 Nick 'zoni' Groenen <zoni@zoni.nl>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from errbot.botplugin import BotPlugin
from errbot import botcmd
import logging
from subprocess import Popen, PIPE, STDOUT

logger = logging.getLogger('errbot.botplugin.DnsUtils')

# Version of the message that's triggered after installing the plugin
# Incrementing this ensures the message is re-triggered, even if it had
# already been triggered in the past.
INSTALL_MESSAGE_VERSION = 1
# Message text to send to bot admins upon installing/updating plugin
INSTALL_MESSAGE_TEXT = """Thank you for installing err-dnsutils.

Please note that this plugin calls dig/nslookup/host and passes arguments on to them directly without any form of checking.
Although this should be safe (commands are called directly, not via shell which could be tricked into redirecting output or executing arbitrary commands), this might still give users more direct access than desired. If you're really paranoid (like me!) you may want to uninstall this plugin.

For more information about this plugin, or to reports bugs and feature requests, please visit the GitHub page at https://github.com/zoni/err-dnsutils"""

class DnsUtils(BotPlugin):
	"""Run common DNS utils: host, dig, nslookup"""

	def activate(self):
		super(DnsUtils, self).activate()
		if not 'INSTALL_MESSAGE_VERSION' in self.shelf.keys() or self.shelf['INSTALL_MESSAGE_VERSION'] < INSTALL_MESSAGE_VERSION:
			self.warn_admins(INSTALL_MESSAGE_TEXT)
			self.shelf['INSTALL_MESSAGE_VERSION'] = INSTALL_MESSAGE_VERSION
			self.shelf.sync() # Not strictly needed, but I like being safe

		# A little sanity checking
		for cmd in (['dig'], ['nslookup', 'localhost'], ['host']):
			try:
				Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()[0]
			except Exception as e:
				self.warn_admins("Warning! This plugin uses {0}, but it failed to execute: {1}".format(cmd[0], e))

	def execute(self, cmd, args):
		"""Execute a command and return it's result

		Args:
			cmd: A string pointing to the executable to run
			args: A list of arguments to pass to the executable
		Returns: String containing output
		"""
		try:
			return Popen([cmd] + args, stdout=PIPE, stderr=STDOUT).communicate()[0]
		except OSError as e:
			logger.exception(e)
			return "Failed to run {0}: {1}".format(cmd, e)

	@botcmd
	def dig(self, mess, args):
		"""Call 'dig'"""
		return self.execute('dig', args.split())

	@botcmd
	def nslookup(self, mess, args):
		"""Call 'nslookup'"""
		args = args.split()
		if len(args) < 1 or args[0] in ('-', '-interactive'):
			# Passing no arguments, or with first argument beginning with - or -interactive
			# to nslookup causes it to hang due to dropping into interactive mode. There's
			# probably a nicer way to deal with this though
			return "Your call to nslookup would have caused it to go into interactive mode and hang so I aborted it, sorry"
		else:
			return self.execute('nslookup', args)

	@botcmd
	def host(self, mess, args):
		"""Call 'host'"""
		return self.execute('host', args.split())

