# Copyright (C) 2025 Open2bizz BV www.open2bizz.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MgmtsystemRootCauseAnalysis(models.Model):
    _name = "mgmtsystem.root_cause_analysis"
    _description = "Root Cause Analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", tracking=True)

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed')
        ],
        string="State",
        default='draft',
        tracking=True
    )

    user_id = fields.Many2one("res.users", string="User", tracking=True)

    # Source of the incident. Can be a task, ticket, etc.
    res_model_id = fields.Many2one(
        "ir.model", string="Model", tracking=True,
        domain=[("model", "!=", "mgmtsystem.root_cause_analysis")]
    )
    res_id = fields.Integer(string="Record ID")
    record_ref = fields.Reference(
        selection="_selection_target_model",
        string="Target Record",
        help="Reference to the target record. Only change this field if you want to replace it under another record.",
    )

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([('model', '!=', 'ow.mail.attach.record')])
        return [(model.model, model.name) for model in models]

    @api.onchange('record_ref')
    def _onchange_record_ref(self):
        if self.record_ref:
            self.res_model_id = self.env['ir.model'].search([('model', '=', self.record_ref._name)], limit=1)
            self.res_id = self.record_ref.id

    incident_description = fields.Html(string="Incident Description", tracking=True)

    incident_sym_con = fields.Html(string="Incident Symptoms and Consequences", tracking=True)

    incident_root_cause = fields.Html(string="Incident Root Cause", help="Root cause of the incident. Use 5x Why?", tracking=True)

    # Fields for incident identification
    incident_identification_primary = fields.Text(string="Primary Cause(s)", tracking=True)
    incident_identification_secondary = fields.Text(string="Secondary Cause(s)", tracking=True)
    incident_identification_factors = fields.Text(
        string="Secondary Cause(s)", tracking=True,
        help="Contributing factors (human, process, technical, etc.)"
    )
    incident_category_ids = fields.Many2many(
        "mgmtsystem.incident_categories",
        relation="mgmtsystem_rca_incident_cat_rel",
        column1="rca_id",
        column2="category_id",
        string="Categories",
        help="Categories of the incident",
        tracking=True
    )

    incident_corr_actions = fields.Html(
        string="Corrective Actions", tracking=True,
        help="Actions defined to remedy the primary and secondary causes"
    )
    incident_prevent_actions = fields.Html(
        string="Preventive Actions", tracking=True,
        help="Long-term measures to prevent recurrence."
    )
    incident_lessons_learned = fields.Html(
        string="Lessons Learned", tracking=True,
        help="What have we learned? What could be improved? Best practices identified? Share with other teams?"
    )


class MgmtsystemIncidentCategories(models.Model):
    _name = "mgmtsystem.incident_categories"
    _description = "Incident Categories"

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
