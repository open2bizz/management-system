# Copyright 2026 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, exceptions, models, _


class MgmtsystemAction(models.Model):
    _inherit = 'mgmtsystem.action'

    default_description = fields.Many2one(
        comodel_name='default.data',
        string='Default Description',
        domain="[('model', '=', 'mgmtsystem.action'), ('field', '=', 'description')]"
    )

    @api.onchange('default_description')
    def onchange_default_description(self):
        if self.default_description:
            update_data = self.default_description.get_update_default_data(self.description)
            if update_data['update']:
                self.description = update_data['data']

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
        field_id = self.env['ir.model.fields'].search([('model', '=', 'project.task'), ('name', '=', field_name)])
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
