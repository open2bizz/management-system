# Copyright (C) 2025 Open2bizz BV www.open2bizz.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemAction(models.Model):
    _inherit = "mgmtsystem.action"

    linked_procedure_ids = fields.Many2many(
        "document.page",
        string="Linked Procedures"
    )

    origin_hazard_id = fields.Many2one(
        "mgmtsystem.hazard",
        string="Origin Hazard"
    )

    origin_hazard_control_measure_id = fields.Many2one(
        "mgmtsystem.hazard.control_measure",
        string="Origin Hazard Control Measure"
    )
