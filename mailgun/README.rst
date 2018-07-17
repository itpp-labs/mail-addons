.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

=========
 Mailgun
=========

The module allows to receive incoming messages or send them to clients who uses external mail services (e.g. gmail.com) by using Mailgun.
There is no IMAP or POP3 servers on mailgun that is to be used with odoo.
That is why we need this module. It fetches messages from mailgun using their API and stores them in odoo.

TODO
====

* If emails are sent when odoo is stopped then Mailgun will retry (other than for delivery notification) during 8 hours at the following intervals before stop trying: 10 minutes, 10 minutes, 15 minutes, 30 minutes, 1 hour, 2 hour and 4 hours. This could be fixed by fetching undelivered messages after odoo starts.

Credits
=======

Contributors
------------
* Ildar Nasyrov <Nasyrov@it-projects.info>
* Ivan Yelizariev <yelizariev@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/11.0/mailgun/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/mail-addons/11.0

HTML Description: https://apps.odoo.com/apps/modules/11.0/mailgun/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/mail-addons/commits/11.0/mailgun.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/mail-addons/commits/11.0/malgun.atom>`_

Tested on Odoo 11.0 dc61861f90d15797b19f8ebddfb0c8a66d0afa88
