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

Roadmap
=======

* ``body_html`` becomes untranslatable after module installation

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
      at `odoo apps store <https://apps.odoo.com/apps/modules/13.0/mail_multi_website/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/mail-addons/13.0

HTML Description: https://apps.odoo.com/apps/modules/13.0/mail_multi_website/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/mail-addons/commits/13.0/mail_multi_website.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/mail-addons/commits/13.0/mail_multi_website.atom>`_

Tested on Odoo 13.0 ca67c83e8d36ececaf97a7579c3ff2529b3e227c
