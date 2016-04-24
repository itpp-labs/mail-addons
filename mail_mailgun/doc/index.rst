==============
 Mail mailgun
==============

Usage
=====

* register on http://mailgun.com       
* On https://mailgun.com/app/domains click on sandbox...mailgun.org domain. Here you can see all information needed to configure odoo outgoing mail feature
* Copy API Key value into odoo

  * Open menu Settings/Parameters/System Parameters
  * Edit mailgun.apikey parameter
  * Put API Key from mailgun into Value field and save

* From https://mailgun.com/cp/routes create new route

  * Priority: ``0``
  * Filter expression: ``catch_all()``
  * Actions: ``store(notify="http://<your odoo domain>/mailgun/notify")``

* In odoo remove 'localhost' Outgoing Mail Server and create 'mailgun'. Now you can send emails
* From odoo menu Settings/General Settings edit Alias Domain

  * Put your mailgun domain here. E.g. sandbox...mailgun.org
  * Click 'Apply' button

* Edit Messaging Alias for your user. Now you can receive emails that is sent to configured alias email address.

  * From menu Settings/Users/Users open you user and click 'Edit'
  * On Preference tab put alias into Messaging Alias field and click 'Save'. E.g. ``admin@sandbox...mailgun.org``

* Send email on ``admin@sandox...mailgun.org``
* Open ``Discuss`` from odoo
* See your message there
* Stop odoo and send several emails again. On odoo starting you see all your messages in ``Discuss``




