# Copyright 2026 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, models


class MgmtsystemRootCauseAnalysis(models.Model):
    _inherit = 'mgmtsystem.root_cause_analysis'

    default_incident_description = fields.Many2one(
        comodel_name='default.data',
        string='Default Incident Description',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_description')]"
    )

    @api.onchange('default_incident_description')
    def onchange_default_incident_description(self):
        if self.default_incident_description:
            update_data = self.default_incident_description.get_update_default_data(self.incident_description)
            if update_data['update']:
                self.incident_description = update_data['data']

    default_incident_sym_con = fields.Many2one(
        comodel_name='default.data',
        string='Default Symptoms and Consequences',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_sym_con')]"
    )

    @api.onchange('default_incident_sym_con')
    def onchange_default_incident_sym_con(self):
        if self.default_incident_sym_con:
            update_data = self.default_incident_sym_con.get_update_default_data(self.incident_sym_con)
            if update_data['update']:
                self.incident_sym_con = update_data['data']

    default_incident_root_cause = fields.Many2one(
        comodel_name='default.data',
        string='Default Root Cause',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_root_cause')]"
    )

    @api.onchange('default_incident_root_cause')
    def onchange_default_incident_root_cause(self):
        if self.default_incident_root_cause:
            update_data = self.default_incident_root_cause.get_update_default_data(self.incident_root_cause)
            if update_data['update']:
                self.incident_root_cause = update_data['data']

    default_incident_corr_actions = fields.Many2one(
        comodel_name='default.data',
        string='Default Corrective Actions',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_corr_actions')]"
    )

    @api.onchange('default_incident_corr_actions')
    def onchange_default_incident_corr_actions(self):
        if self.default_incident_corr_actions:
            update_data = self.default_incident_corr_actions.get_update_default_data(self.incident_corr_actions)
            if update_data['update']:
                self.incident_corr_actions = update_data['data']

    default_incident_prevent_actions = fields.Many2one(
        comodel_name='default.data',
        string='Default Preventive Actions',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_prevent_actions')]"
    )

    @api.onchange('default_incident_prevent_actions')
    def onchange_default_incident_prevent_actions(self):
        if self.default_incident_prevent_actions:
            update_data = self.default_incident_prevent_actions.get_update_default_data(self.incident_prevent_actions)
            if update_data['update']:
                self.incident_prevent_actions = update_data['data']

    default_incident_lessons_learned = fields.Many2one(
        comodel_name='default.data',
        string='Default Lessons Learned',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_lessons_learned')]"
    )

    @api.onchange('default_incident_lessons_learned')
    def onchange_default_incident_lessons_learned(self):
        if self.default_incident_lessons_learned:
            update_data = self.default_incident_lessons_learned.get_update_default_data(self.incident_lessons_learned)
            if update_data['update']:
                self.incident_lessons_learned = update_data['data']

    default_incident_identification_primary = fields.Many2one(
        comodel_name='default.data',
        string='Default Primary Cause(s)',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_identification_primary')]"
    )

    @api.onchange('default_incident_identification_primary')
    def onchange_default_incident_identification_primary(self):
        if self.default_incident_identification_primary:
            update_data = self.default_incident_identification_primary.get_update_default_data(self.incident_identification_primary)
            if update_data['update']:
                self.incident_identification_primary = update_data['data']

    default_incident_identification_secondary = fields.Many2one(
        comodel_name='default.data',
        string='Default Secondary Cause(s)',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_identification_secondary')]"
    )

    @api.onchange('default_incident_identification_secondary')
    def onchange_default_incident_identification_secondary(self):
        if self.default_incident_identification_secondary:
            update_data = self.default_incident_identification_secondary.get_update_default_data(self.incident_identification_secondary)
            if update_data['update']:
                self.incident_identification_secondary = update_data['data']

    default_incident_identification_factors = fields.Many2one(
        comodel_name='default.data',
        string='Default Contributing Factors',
        domain="[('model', '=', 'mgmtsystem.root_cause_analysis'), ('field', '=', 'incident_identification_factors')]"
    )

    @api.onchange('default_incident_identification_factors')
    def onchange_default_incident_identification_factors(self):
        if self.default_incident_identification_factors:
            update_data = self.default_incident_identification_factors.get_update_default_data(self.incident_identification_factors)
            if update_data['update']:
                self.incident_identification_factors = update_data['data']
