===========
 Mail Base
===========

* makes built-in mail js features extendable.
* handles ``search_default_*`` parameters in context.
* fixes toggling left bar
* fixes Recipients field. Out-of-box this field could be empty.

One can say, that the module do this todo from `addons/mail/static/src/js/chat_manager.js <https://github.com/odoo/odoo/blob/11.0/addons/mail/static/src/js/chat_manager.js#L57>`__

    // to do: move this to mail.utils

Note. Due to odoo restrictions, module makes mail initialization again. That is browser loads emoji and other chat data twice. This is the only way to make Mail feature extendable.

Credits
=======

Contributors
------------
* Pavel Romanchenko <apps@it-projects.info>

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support you are kindly requested to purchase the module at `odoo apps store <https://apps.odoo.com/apps/modules/11.0/mail_base/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/mail-addons/11.0

HTML Description: https://apps.odoo.com/apps/modules/11.0/mail_base/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 11.0 ecbf7aa4714479229658d14cce28fa00376ed390
