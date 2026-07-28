# Copyright (C) 2025 Open2bizz BV www.open2bizz.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _
from odoo.exceptions import UserError


class MgmtsystemAction(models.Model):
    _inherit = "mgmtsystem.action"

    linked_procedure_ids = fields.Many2many(
        "document.page",
        string="Linked Procedures",
        tracking=True
    )

    origin_hazard_id = fields.Many2one(
        "mgmtsystem.hazard",
        string="Origin Hazard",
        tracking=True
    )

    origin_hazard_control_measure_id = fields.Many2one(
        "mgmtsystem.hazard.control_measure",
        string="Origin Hazard Control Measure",
        tracking=True
    )

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
            raise UserError(_("A Root Cause Analysis already exists for this action."))
        action_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        rca = self.env['mgmtsystem.root_cause_analysis'].create({
            'name': self.name,
            'res_model_id': action_model.id,
            'res_id': self.id,
        })
        self.root_cause_analysis_id = rca.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mgmtsystem.root_cause_analysis',
            'res_id': rca.id,
            'view_mode': 'form',
            'target': 'current',
        }
