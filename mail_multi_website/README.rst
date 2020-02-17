.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

=====================
 Multi-Brand Mailing
=====================

Mail-related stuff for multi-website support

* Makes following field in ``res.users`` website-dependent:

  * ``email``
  * ``signature``

* Makes following fields in ``mail.template`` website-dependent:

  * ``body_html``
  * ``mail_server_id``
  * ``report_template``

* Overrides ``mail.template``'s ``render_template`` method to add ``website``
  variable. It may cause incompatibility with other modules that redefine that
  method too.

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `e-thos SSII <http://www.e-thos.fr/>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/12.0/mail_multi_website/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/mail-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/mail_multi_website/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/mail-addons/commits/12.0/mail_multi_website.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/mail-addons/commits/12.0/mail_multi_website.atom>`_

Tested on Odoo 12.0 80cef9e8c52ff7dc0715a7478a2288d3de7065df
