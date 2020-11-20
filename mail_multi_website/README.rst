.. image:: https://itpp.dev/images/infinity-readme.png
   :alt: Tested and maintained by IT Projects Labs
   :target: https://itpp.dev

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

Questions?
==========

To get an assistance on this module contact us by email :arrow_right: help@itpp.dev

Contributors
============
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__


Further information
===================

Odoo Apps Store: https://apps.odoo.com/apps/modules/12.0/mail_multi_website/


Notifications on updates: `via Atom <https://github.com/it-projects-llc/mail-addons/commits/12.0/mail_multi_website.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/mail-addons/commits/12.0/mail_multi_website.atom>`_

Tested on `Odoo 12.0 <https://github.com/odoo/odoo/commit/80cef9e8c52ff7dc0715a7478a2288d3de7065df>`_
