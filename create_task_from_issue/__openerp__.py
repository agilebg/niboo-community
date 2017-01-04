# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Create Tasks from Issues',
    'category': 'Project',
    'summary': 'Create Tasks from Issues',
    'website': 'https://www.niboo.be/',
    'version': '9.0.1.0.0',
    'author': 'Niboo',
    'depends': [
        'project_issue',
    ],
    'data': [
        'views/project_issue.xml',
        'views/project_task.xml',
    ],
    'installable': True,
    'application': False,
}
