## Contributing

Currently we focus on a pure port of Klarschiff (Java, PHP) to cleanship (Django) with all of the existing functionality.
For that reason, **we don't accept pull-requests yet**.  Feel free to discuss requests / bugs.
New features or breaking changes will be stalled till version 0.3! 

* 0.1 (Painbox) 01/2020 - prototyp focus on possibility
* 0.2 (Caladan) 12/2020 - full port of Klarschiff.HRO features
* 0.3 (IX) - new features and addons
* 1.0 (Guild) - extension for distributed services

## Code

For code format conventions, please see `.editorconfig`
We follow flake8 code conventions, [Django coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/) and pythonic best practises.

Please install `requirements\dev.txt` for the tools dependencies!

Feel free to use semantic inline comments as `TODO: refactoring` but plz. make sure, this task reflect also as a github issue!
Git commit messages follow [conventional commits](https://www.conventionalcommits.org), so headers e.g.
* `feat: Add abuse funtionality`
* `fix(admin): Broken category`
* `refactor(legacy)!: Extract importer as class` (! for breaking change)
Possible tags are also: build, docs, lang, refactor, style, test.
At the commit-body we give more details about what is (not) covered and which github tickets are focused.

Some reminders for first contact or before we push to github / pull-request:

* explore idea of new features / libs before in a separate small prototype
* feature-branches for parallel work -> rebase
* check tests
* check codecov
* check performance for realworld-data -> [DB optimization](https://docs.djangoproject.com/en/2.2/topics/db/optimization/)
* check flake8 codestyle
* check translations
* check docs
* check requirements, contributors, ...
* (CI checks again)


## Translating

* Update the current strings to .po templates:
   `django-admin makemessages -l de`
* Use e.g. poedit to add translation strings
* Update the binary translations: `django-admin compilemessages`

### Dictionary

To avoid any confusion about the wording and keeping the translations
consistent, we list dedicated

| en          | de            |
| ------------|:-------------:|
| issue       | Vorgang       |
| fieldteam   | Außendienst   |
| photo       | Photo         |
| category    | Kategorie     |
| eMail       | E-Mail        |
