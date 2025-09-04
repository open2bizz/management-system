# Copyright (C) 2025 Open2bizz BV www.open2bizz.nl / Based on: Risk Model Canvas
# © 2023 by Gilbert van Zeijl and Vincent van Dijk is licensed under CC BY-SA 4.0
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MDocumentPageTheme(models.Model):
    """ Themes for manuals NEN7510 """
    _name = "document.page.theme"
    _description = "Theme for manuals NEN7510"

    active = fields.Boolean("Active", default=True)
    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    sequence = fields.Integer(string="Sequence")

