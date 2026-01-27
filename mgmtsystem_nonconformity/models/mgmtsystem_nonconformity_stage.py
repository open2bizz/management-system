# Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

from odoo.tools.translate import _lt

class MgmtsystemNonconformityStage(models.Model):
    """This object is used to defined different state for non conformity."""

    _name = "mgmtsystem.nonconformity.stage"
    _description = "Nonconformity Stages"
    _order = "sequence"

    def _selection_state(self):
            return [
                ("draft", _("Draft")),
                ("analysis", _("Analysis")),
                ("pending", _("Action Plan")),
                ("open", _("In Progress")),
                ("done", _("Closed")),
                ("cancel", _("Cancelled")),
            ]
            
    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer(
        help="Used to order states. Lower is better.", default=100
    )
    state = fields.Selection(
        selection=_selection_state,
        default="draft",
        required=True,
    )
    is_starting = fields.Boolean(
        string="Is starting Stage",
        help="select stis checkbox if this is the default stage \n"
        "for new nonconformities",
    )
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view when there are \n"
        "no records in that stage to display.",
    )

    