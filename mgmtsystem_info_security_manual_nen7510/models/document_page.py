#    Copyright (C) 2025 Open2bizz BV www.open2bizz.nl

from odoo import fields, models, api, _
from markupsafe import Markup
from odoo.tools import html_escape


class DocumentPage(models.Model):
    """
    Extend Document Page with info for Procedure NEN7510
    """

    _inherit = ["document.page"]

    nen_chapter = fields.Many2one("document.page.chapter", "NEN Chapter")
    nen_control = fields.Char("NEN Control")
    nen_mandatory = fields.Boolean("Mandatory", track_visibility=True)
    state_compliant = fields.Selection(
        [('compliant', 'Compliant'), ('implemented', 'Implemented'),
         ('non_compliant', 'None Compliant'), ('compliant_improvement', 'Compliant with points for improvement')],
        string="State Compliant", default='non_compliant', track_visibility=True
    )
    external_reference = fields.Html("External Reference(s)")
    internal_reference = fields.Html("Internal Reference(s)")

    mgmtsystem_action_ids = fields.Many2many("mgmtsystem.action", string="Management System Action")

    # Feature O2B 26778
    nen_sources = fields.Html("Sources", help="List of sources; person, document, log, other")
    nen_observations = fields.Html("Observations", help="Observation, evidence. (intent, existence and operation)")
    nen_judgement_assessor = fields.Float(
        string="Judgement Assessor (%)", track_visibility=True,
        help="Judgement Assessor / auditor in percentage completed. (0% = open, 100% = completed)"
    )
    nen_judgement_assessor_status = fields.Selection(
        [('open', 'Open'), ('progress', 'In progress'), ('completed', 'Completed')],
        compute="_compute_nen_judgement_assessor_status", default='open',
        string="Judgement Assessor Status", store=True, track_visibility=True
    )
    nen_judgement_assessor_notes = fields.Html("Notes Judgement Assessor", help="Notes from Judgement Assessor / auditor")
    nen_theme_id = fields.Many2one("document.page.themer", "NEN Theme")

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
        self.message_post(
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

    @api.depends('nen_judgement_assessor', 'state_compliant')
    def _compute_nen_judgement_assessor_status(self):
        for record in self:
            nen_judgement_assessor_status = 'open'
            if record.nen_judgement_assessor >= 1.0:
                nen_judgement_assessor_status = 'completed'
            elif record.nen_judgement_assessor > 0.0:
                nen_judgement_assessor_status = 'progress'
            record.nen_judgement_assessor_status = nen_judgement_assessor_status
