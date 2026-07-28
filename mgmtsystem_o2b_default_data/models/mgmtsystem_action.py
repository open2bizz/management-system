# Copyright 2026 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, models


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
