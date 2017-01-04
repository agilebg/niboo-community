# -*- coding: utf-8 -*-
# © 2016 Jérôme Guerriat
# © 2016 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def create_task(self):
        self.ensure_one()
        user_id = self.user_id.id if self.user_id else self._uid
        return {
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('project.view_task_form2').id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'target': 'current',
            'context': {
                'default_project_id': self.project_id.id,
                'default_issue_ids': [(4, self.id, False)],
                'default_user_id': user_id,
                'default_description': self.description,
                'default_name': self.name,
            }
        }
