=========
 Mailgun
=========

Usage
=====

* register or log in http://mailgun.com
* On https://mailgun.com/app/domains click on you domain, e.g. sandbox123...mailgun.org domain. Here you can see all information needed to configure odoo outgoing mail feature

  * if you in sandbox domain, add Authorized Recepient
  * Copy API Key value into odoo
  
    * Open menu ``Settings / Parameters / System Parameters``
    * Create new parameter
  
      * key: ``mailgun.apikey``
      * Value: API Key from mailgun (``key-...``)
      * click Save
  
  * Copy smtp credentials into odoo

    * open ``Settings / Technical / Email / Outgoing Mail Servers``

      * delete localhost
      * create new server

        * Description: ``mailgun``
        * SMTP Server: ``smtp.mailgun.org``
        * Connection Security: ``SSL/TLS``
        * Username: e.g. ``postmaster@sandbox123....mailgun.org``
        * Password: ``...`` (copy ``Default Password`` from mailgun)

  * From odoo menu ``Settings / General Settings`` edit Alias Domain
  
    * Put your mailgun domain here. E.g. sandbox123...mailgun.org
    * Click 'Apply' button

* From https://mailgun.com/cp/routes create new route

  * Priority: ``0``
  * Filter expression: ``catch_all()``
  * Actions: ``store(notify="http://<your odoo domain>/mailgun/notify")``

* Set admin's email alias. Open menu ``Settings / Users / Users``

  * choose your user and click ``[Edit]``
  * On Preference tab put alias into Messaging Alias field and click ``[Save]``. E.g. ``admin@sandbox...mailgun.org``

* Via your favorite mail client (e.g. gmail.com) send email to ``admin@sandox...mailgun.org``
* Open ``Discuss`` in odoo
* See your message there
* Reply to the message and check it in your mail client (e.g. gmail.com)


=========
 Mailgun
=========

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Mailgun-side
------------

* register or log in http://mailgun.com
* Open menu ``[[ Domains ]]`` and click on you domain, e.g. sandbox123...mailgun.org domain. Here you can see all information needed to configure odoo outgoing mail feature
* Please note that state of your domain should be ``Active`` before you can use it. If it is ``Unverified`` - verify it first using Mailgun FAQ ``How do I verify my domain``
* if you are using your sandbox domain, add Authorized Recepient first (Sandbox domains are restricted to authorized recipients only)
* create new Route

  * Open menu ``[[ Routes ]]``
  * Click ``[Create Route]`` button

    * **Expression Type** - ``Custom``
    * **Raw Expression** - ``match_recipient('.*@<your mail domain>')``
    * **Actions** - ``Store and notify``, ``http://<your odoo domain>/mailgun/notify``

Odoo-side
---------

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Configure Outgoung mail server

  * Open menu ``[[ Settings ]] >> Technical >> Email >> Outgoing Mail Servers``
  * Edit ``localhost`` record as following
  * **Description** - ``Mailgun``
  * **SMTP Server** - take from Mailgun **SMTP Hostname** (usually it is ``smtp.mailgun.org``)
  * **Connection Security** - ``SSL/TLS``
  * **Username** - take from Mailgun **Default SMTP Login**
  * **Password** - take from Mailgun **Default Password**
  * Click ``[Test Connection]`` button and then ``[Save]``

* Configure Incoming mail feature

  * Configure catchall domain

    * Open menu ``Settings / General Settings``, check **External Email Servers** and edit **Alias Domain** - set it from Mailgun **Domain Name**
    * Click ``[Save]`` button

  * Set Mailgun API credentials

    * Open menu ``[[ Settings ]] >> Parameters >> System Parameters``
    * Create new parameter

      * key: ``mailgun.apikey``
      * Value: API Key from mailgun (``key-...``)
      * Click ``[Save]`` button

  * Configure mail aliases and emails for users

    * Open menu ``[[ Settings ]] >> Users >> Users``
    * Select the ``Administrator`` user (this is for example, you should configure all your users the same way but using different aliases) and click ``[Edit]``
    * On Preference tab edit **Alias** field - create new mail alias, e.g. ``admin@<you mail domain>``
    * On Mail alias form pay attention to the required **Aliased Model** field (The model (Odoo Document Kind) to which this alias corresponds. Any incoming email that does not reply to an existing record will cause the creation of a new record of this model (e.g. a Project Task)). You can select ``Test Mail Model`` here but just for testing the feature
    * Open user's **Related Partner** and edit **Email** field - usually should be the same as mail alias name (``admin@<you mailgun domain`` for ``Administrator``) - this would be an address for replying user's messages

Usage
=====

Outgoing
--------

* Open menu ``[[ Settings ]]>> Email >> Emails`` to create a message
* Click ``[Send Now]`` button
* RESULT: receive the message in you mail client (e.g. on gmail.com)

Incoming
--------

* Reply the message in you mail client (e.g. on gmail.com)
* Open ``[[ Discuss ]]`` in odoo
* RESULT: See your reply message there

* Create new message from you mail client to e.g. ``admin@<you mailgun domain>``
* RESULT: in Odoo open menu ``[[ Settings ]] >> Technical >> Email >> Messages`` and see the message there
