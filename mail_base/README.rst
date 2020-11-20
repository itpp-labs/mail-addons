.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

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

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* Pavel Romanchenko <apps@it-projects.info>

===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/11.0/mail_base/


Tested on `Odoo 11.0 <https://github.com/odoo/odoo/commit/ecbf7aa4714479229658d14cce28fa00376ed390>`_
