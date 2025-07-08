#    Copyright (C) 2025 Open2bizz BV www.open2bizz.nl

from odoo import fields, models, _
from markupsafe import Markup

class DocumentPage(models.Model):
    """
    Extend Document Page with info for Procedure NEN7510
    """

    _inherit = ["document.page"]

    nen_chapter = fields.Many2one("document.page.chapter", "NEN Chapter")
    nen_control = fields.Char("NEN Control")
    nen_mandatory = fields.Boolean("Mandatory")
    state_compliant = fields.Selection(
        [('compliant', 'Compliant'), ('implemented', 'Implemented'), ('non_compliant', 'None Compliant')],
        string="State Compliant"
    )
    external_reference = fields.Html("External Reference(s)")
    internal_reference = fields.Html("Internal Reference(s)")

    mgmtsystem_action_ids = fields.Many2many("mgmtsystem.action", string="Management System Action")

    # Feature O2B 26778
    nen_sources = fields.Html("Sources", help="List of sources; person, document, log, other")
    nen_observations = fields.Html("Observations", help="Observation, evidence. (intent, existence and operation)")
    nen_judgement_assessor = fields.Float(
        string="Judgement Assessor (%)",
        help="Judgement Assessor / auditor in percentage completed. (0% = open, 100% = completed)"
    )
    nen_judgement_assessor_status = fields.Selection(
        [('open', 'Open'), ('progress', 'In progress'), ('completed', 'Completed')],
        compute="_compute_nen_judgement_assessor_status", default='open',
        string="Judgement Assessor Status"
    )
    nen_judgement_assessor_notes = fields.Html("Notes Judgement Assessor", help="Notes from Judgement Assessor / auditor")

    def action_open_childs(self):
        for record in self:
            return {
                "type": "ir.actions.act_window",
                "name": "Child Documents",
                "res_model": "document.page",
                "domain": [('parent_id', '=', record.id)],
                "view_mode": "tree,form",
                "target": "current",
            }

    def action_create_mgmt_action(self):
        self.ensure_one()
        add_value = "<p><br/></p><hr/><p>Document Page value:</p><br/>"
        if self.content:
            new_value = Markup(add_value) + Markup(self.content)
        else:
            new_value = add_value
        vals = {
            'name': self.name,
            'type_action': 'improvement',
            'description': Markup(new_value),
            'user_id': self.env.user.id,
            'linked_procedure_ids': [(4,self.id)]
        }
        action = self.env['mgmtsystem.action'].create(vals)
        return {
            'name': _('Management System Action'),
            'type': 'ir.actions.act_window',
            'res_model': 'mgmtsystem.action',
            'res_id': action.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def _compute_nen_judgement_assessor_status(self):
        for record in self:
            if record.nen_judgement_assessor:
                if record.nen_judgement_assessor == 0.0:
                    record.nen_judgement_assessor_status = 'open'
                if record.nen_judgement_assessor >= 1.0:
                    record.nen_judgement_assessor_status = 'completed'
                else:
                    record.nen_judgement_assessor_status = 'progress'
