# Copyright (C) 2026 Open2bizz BV www.open2bizz.nl

from odoo import fields, models, exceptions, api, _
from markupsafe import Markup
from odoo.tools import html_escape
import re



class DocumentPage(models.Model):
    _inherit = ["document.page"]

    default_external_reference = fields.Many2one(
        comodel_name='default.data',
        string='Default External Reference',
        domain="[('model', '=', 'document.page'), ('field', '=', 'default_external_reference')]"
    )

    @api.onchange('default_external_reference')
    def onchange_default_external_reference(self):
        self.with_context(field_name='default_external_reference').onchange_default_data()

    default_internal_reference = fields.Many2one(
        comodel_name='default.data',
        string='Default Internal Reference',
        domain="[('model', '=', 'document.page'), ('field', '=', 'default_internal_reference')]"
    )

    @api.onchange('default_internal_reference')
    def onchange_default_internal_reference(self):
        self.with_context(field_name='default_internal_reference').onchange_default_data()

    default_nen_sources = fields.Many2many(
        comodel_name='default.data',
        relation='document_page_default_nen_sources_rel',
        column1='document_page_id',
        column2='default_data_id',
        string='Default NEN Sources',
        domain="[('model', '=', 'document.page'), ('field', '=', 'default_nen_sources')]"
    )

    @api.onchange('default_nen_sources')
    def onchange_default_nen_sources(self):
        self.with_context(field_name='default_nen_sources').onchange_default_data()

    default_nen_observations = fields.Many2many(
        comodel_name='default.data',
        relation='document_page_default_nen_observations_rel',
        column1='document_page_id',
        column2='default_data_id',
        string='Default NEN Observations',
        domain="[('model', '=', 'document.page'), ('field', '=', 'default_nen_observations')]"
    )

    @api.onchange('default_nen_observations')
    def onchange_default_nen_observations(self):
        self.with_context(field_name='default_nen_observations').onchange_default_data()

    def onchange_default_data(self):
        field_name = self.env.context.get('field_name', 'none')
        if field_name == "none":
            raise exceptions.ValidationError(_("Field name is required! Missing in context"))
        if self[field_name]:
            update_data = self.default_external_reference.get_update_default_data(field_name)
            if update_data['update']:
                self.write({
                    field_name: update_data['data']
                })

    def action_create_default_data(self):
        self.ensure_one()
        # Set context
        # Use this in the view:
        # context="{'field_name': 'description', 'default_data_field': 'default_description'}"
        field_name = self.env.context.get('field_name', 'none')
        default_data_field = self.env.context.get('default_data_field', 'none')

        if field_name == "none":
            raise exceptions.ValidationError(_("Field name is required! Missing in context"))
        if default_data_field == "none":
            raise exceptions.ValidationError(_("Default data field is required! Missing in context"))

        if self[default_data_field]:
            raise exceptions.ValidationError(_("There is already a default linked"))

        def_data_model = self.env['default.data']
        target_model = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        field_id = self.env['ir.model.fields'].search([('model', '=', self._name), ('name', '=', field_name)])
        value = self[field_name]

        default_data_value = def_data_model.action_create_default_data(target_model, field_id, value)
        self.write({default_data_field: default_data_value.id})

    def extend_default_data_field(self):
        self.ensure_one()
        # Set context
        # Use this in the view: context="{'field_name', 'destination_field_name'}"
        field_name = self.env.context.get('field_name', 'none')
        if field_name == "none":
            raise exceptions.ValidationError(_("Field name is required! Missing in context"))

        model_obj = self.env['ir.model'].search([('model', '=', self._name)], limit=1)
        field = self.env['ir.model.fields'].search([('model_id', '=', model_obj.id), ('name', '=', field_name)])

        view = self.env.ref('default_data.extend_default_data_form')
        context = {
            'default_model_id': model_obj.id,
            'default_field_id': field.id,
            'default_res_id': self.id,
            'default_position': 'before',
        }
        return {
            "name": "Add text",
            "type": "ir.actions.act_window",
            "res_model": "extend.default.data",
            "view_mode": "form",
            "views": [
                [view.id, "form"]
            ],
            "target": "new",
            "context": context
        }
