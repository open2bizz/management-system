# Copyright (C) 2026 Open2Bizz (<http://www.open2bizz.tech>).
# Special addon for mgmntsystem OCA Modules special: NEN7510 NL Open2bizz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class MgmtsystemNonconformity(models.Model):
    _inherit = "mgmtsystem.nonconformity"


    # Open2Bizz june 2026. Add fields for Root Cause Analysis
    root_cause_analysis = fields.Boolean(
        string="Root Cause Analysis Needed?"
    )

    root_cause_analysis_id = fields.Many2one(
        "mgmtsystem.root_cause_analysis",
        string="Root Cause Analysis",
        tracking=True
    )

    def action_create_root_cause_analysis(self):
        self.ensure_one()
        if self.root_cause_analysis_id:
            raise ValidationError(_("A Root Cause Analysis already exists for this action."))
        action_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        rca = self.env['mgmtsystem.root_cause_analysis'].create({
            'name': self.name,
            'res_model_id': action_model.id,
            'res_id': self.id,
            'user_id': self.user_id.id or False,
        })
        self.root_cause_analysis_id = rca.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mgmtsystem.root_cause_analysis',
            'res_id': rca.id,
            'view_mode': 'form',
            'target': 'current',
        }
