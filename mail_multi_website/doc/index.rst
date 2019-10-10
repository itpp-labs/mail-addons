=====================
 Multi-Brand Mailing
=====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============


Access to websites
------------------

* Go to menu ``[[ Settings ]] >> Users & Companies >> Users``
* Select a user
* Grant access ``[x] Multi Websites for Backend``
* Configure **Allowed Websites**

User's email per website
------------------------

* Refresh page if you just granted your user access to websites
* Use top right-hand corner button with current website name to switch between websites
* Use top right-hand corner button with user name and avatar to open
  Preference popup. When you edit **Email** field, it will be saved as a value
  for current website.

Email template per website
--------------------------

* Refresh page if you just granted your user access to websites
* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Use top right-hand corner button with current website name to switch between websites
* Go to menu ``[[ Settings ]] >> Technical >> Email >> Templates``
* When you edit template, following fields will be saved as a value for current website:

  * **Body**
  * **Outgoing Mail Server**
  * **Optional report to print and attach**

* Additional variable ``website`` is available to configure rest fields (**Subject**, **From**, etc.)

Note. If related record (e.g. ``sale.order``) has field ``company_id`` or ``website_id`` those values will be used instead of currently selected in Website / Company Switchers

Alias domain per website
------------------------

Configure ``mail.catchall.domain`` per website. See Documentation of the module `Context-dependent values in System Parameters <https://apps.odoo.com/apps/modules/10.0/ir_config_parameter_multi_company>`__.

Outgoing mails servers per website
--------------------------

If each domain has different Outgoing Mail Server you need following adjustments 

* Got to menu ``[[ Website ]] >> Configuration >> Websites``
* In each Website specify field **Outgoing Mails**

Properties
----------

To review properties by website use menu ``[[ Settings ]] >> Technical >> Parameters >> Company Properties``. See **How it works** in Documentation of module `Website Switcher in Backend <https://apps.odoo.com/apps/modules/10.0/web_website>`__.

Usage
=====

When you work from backend, Email for current website is used.

When a user do something on website (e.g. purchase products) and some mail is sent, then email address for that website will be used (mostly Administrator's email address).

When email is sent, template's value like body, subject, etc. for current values are used.
