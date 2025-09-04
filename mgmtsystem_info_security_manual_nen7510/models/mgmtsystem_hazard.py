# Copyright (C) 2025 Open2bizz BV www.open2bizz.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from markupsafe import Markup
from odoo.tools import html_escape


class MgmtsystemHazard(models.Model):
    _inherit = "mgmtsystem.hazard"

    code = fields.Char(
        string='Number',
        required=True,
        readonly=True,
        default='/',
        copy=False
    )

    canvas_name = fields.Char(string='Canvas Name')

    linked_procedure_ids = fields.Many2many(
        "document.page",
        string="Linked Procedures"
    )
    hazard_class = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], string="Class" , default="low", index=True
    )
    mgmtsystem_action_ids = fields.One2many("mgmtsystem.action", "origin_hazard_id", string="Management System Action")
    mgmtsystem_action_count = fields.Integer(compute="_compute_mgmtsystem_action_count")

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('mgmtsystem.hazard') or '/'
        return super(MgmtsystemHazard, self).create(vals)

    def _compute_mgmtsystem_action_count(self):
        for record in self:
            record.mgmtsystem_action_count = len(record.mgmtsystem_action_ids)

    def action_open_actions(self):
        for record in self:
            return {
                "type": "ir.actions.act_window",
                "name": "Child Documents",
                "res_model": "mgmtsystem.action",
                "domain": [('origin_hazard_id', '=', record.id)],
                "view_mode": "tree,form",
                "target": "current",
                "context": {
                    'default_origin_hazard_id': record.id,
                    'default_name': record.name,
                    'default_user_id': record.responsible_user_id.id or self.env.user.id,
                }
            }

class MgmtsystemHazardControlMeasure(models.Model):
    _inherit = "mgmtsystem.hazard.control_measure"

    mgmtsystem_action_ids = fields.One2many(
        "mgmtsystem.action", "origin_hazard_control_measure_id",
        string="Management System Action"
    )

    def action_create_mgmt_action(self):
        self.ensure_one()

        action_name = _(f"{self.hazard_id.name} - {self.name}")
        add_value = _("<p><br/></p><hr/><p>Control Measure of hazard comments:</p><br/>")
        if self.comment:
            new_value = Markup(add_value) + Markup(self.comment)
        else:
            new_value = add_value
        vals = {
            'name': action_name,
            'origin_hazard_control_measure_id': self.id,
            'origin_hazard_id': self.hazard_id.id,
            'type_action': 'improvement',
            'description': Markup(new_value),
            'user_id': self.responsible_user_id.id or self.env.user.id,
        }
        action = self.env['mgmtsystem.action'].create(vals)
        self.hazard_id.message_post(
            body=_(
                "A management action has been created. You can view it <a href='/web#id=%s&model=mgmtsystem.action' target='_blank'>here</a>.")
                 % html_escape(action.id),
            subtype_id=self.env.ref('mail.mt_note').id,
        )
        return {
            'name': _('Management System Action'),
            'type': 'ir.actions.act_window',
            'res_model': 'mgmtsystem.action',
            'res_id': action.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }



