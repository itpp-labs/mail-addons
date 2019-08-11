Mail Base
=========

* makes built-in mail js features extendable.
* handles ``search_default_*`` parameters in context.
* fixes toggling left bar
* fixes Recipients field. Out-of-box this field could be empty.

One can say, that the module do this todo from `addons/mail/static/src/js/chat_manager.js <https://github.com/odoo/odoo/blob/10.0/addons/mail/static/src/js/chat_manager.js#L57>`__

    // to do: move this to mail.utils



Note. Due to odoo restrictions, module makes mail initialization again. That is browser loads emoji and other chat data twice. This is the only way to make Mail feature extendable.

Further information
===================

Demo: http://runbot.it-projects.info/demo/mail-addons/10.0

.. HTML Description: https://apps.odoo.com/apps/modules/10.0/mail_base/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Tested on Odoo 10.0 1be57f2825af4f3ade20a658c6f97f6cf93cc866
