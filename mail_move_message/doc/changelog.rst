`10.0.1.0.6`
-------

- IMP: Select by default the same model destination as where the original message is posted
- FIX: If the related model is res.partner, use the field "id" for the domain restriction on the record
- FIX: Code cleaning (PEP8 + Pylint)

`1.0.5`
-------

- FIX: TypeError "Cannot read property 'constructor' of undefined" when change a model
- FIX: Issue related to 'Move to origin' option

`1.0.4`
-------

- FIX: don't allow to relocate message to itself as it cause infinitive loop
- ADD: 'Move Followers' option -- Add followers of current record to a new record.

`1.0.3`
-------

- FIX email_from parsing. There was an error with specific email_from value (e.g. '"name @ example" <name@example.com>')

`1.0.2`
-------

- big improvements in interface

`1.0.1`
-------

- fix bug "some messages are not shown in inbox after relocation"
- improve "Move back" tool
