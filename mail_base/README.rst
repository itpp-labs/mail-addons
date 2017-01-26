Mail Base
=========

* makes built-in mail js features extendable.
* handles ``search_default_*`` parameters in context.
* fixes toggling left bar
* fixes Recipients field. Out-of-box this field could be empty.

One can say, that the module do this todo from `addons/mail/static/src/js/chat_manager.js <https://github.com/odoo/odoo/blob/9.0/addons/mail/static/src/js/chat_manager.js#L57>`__

    // to do: move this to mail.utils



Note. Due to odoo restrictions, module makes mail initialization again. That is browser loads emoji and other chat data twice. This is the only way to make Mail feature extendable.

Further information
===================

Demo: http://runbot.it-projects.info/demo/mail-addons/9.0

.. HTML Description: https://apps.odoo.com/apps/modules/9.0/mail_base/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 9.0 c8cd67c5d98b410cabe0a6efb3347a8a4de731d8
