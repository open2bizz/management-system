#    Copyright (C) 2025 Open2bizz BV www.open2bizz.nl

from odoo import fields, models, api, _
from markupsafe import Markup
from odoo.tools import html_escape
import re


class DocumentPage(models.Model):
    """
    Extend Document Page with info for Procedure NEN7510
    """
    _inherit = ["document.page"]

    nen_chapter = fields.Many2one("document.page.chapter", "NEN Chapter")
    nen_control = fields.Char("NEN Control")
    nen_mandatory = fields.Boolean("Mandatory", tracking=True)
    state_compliant = fields.Selection([
        ('compliant', 'Compliant'),
        ('implemented', 'Implemented'),
        ('non_compliant', 'None Compliant'),
        ('compliant_improvement', 'Compliant with points for improvement'),
        ('not_applicable', 'Not applicable'),
        ],
        string="State Compliant", default='non_compliant', tracking=True
    )
    not_applicable_reason = fields.Html("Reason or comments why Not applicable")

    external_reference = fields.Html("External Reference(s)")
    internal_reference = fields.Html("Internal Reference(s)")

    mgmtsystem_action_ids = fields.Many2many("mgmtsystem.action", string="Management System Action")

    # Feature O2B 26778
    nen_sources = fields.Html("Sources", help="List of sources; person, document, log, other")
    nen_observations = fields.Html("Observations", help="Observation, evidence. (intent, existence and operation)")
    nen_judgement_assessor = fields.Float(
        string="Judgement Assessor (%)", tracking=True,
        help="Judgement Assessor / auditor in percentage completed. (0% = open, 100% = completed)"
    )
    nen_judgement_assessor_status = fields.Selection(
        [('open', 'Open'), ('progress', 'In progress'), ('completed', 'Completed')],
        compute="_compute_nen_judgement_assessor_status", default='open',
        string="Judgement Assessor Status", store=True, tracking=True
    )
    nen_judgement_assessor_notes = fields.Html("Notes Judgement Assessor", help="Notes from Judgement Assessor / auditor")
    nen_theme_id = fields.Many2one("document.page.theme", "NEN Theme")

    def action_open_childs(self):
        for record in self:
            return {
                "type": "ir.actions.act_window",
                "name": "Child Documents",
                "res_model": "document.page",
                "domain": [('parent_id', '=', record.id)],
                "view_mode": "list,form",
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
            body=Markup(
                _(
                    "Er is een managementactie aangemaakt. "
                    "Je kunt deze <a href=\"{url}\" target=\"_blank\">hier</a> bekijken."
                )
            ).format(
                url=f"/web#id={action.id}&model=mgmtsystem.action&view_type=form",
            ),
            body_is_html=True,
            subtype_xmlid="mail.mt_note",
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

    # --- Document history integration for extra HTML fields ---

    def _get_next_history_version(self):
        self.ensure_one()
        count = self.env['document.page.history'].search_count([('page_id', '=', self.id)])
        return count + 1

    def _format_changed_fields_label(self, fields_list):
        labels = {
            'content': 'Content',
            'external_reference': 'External Reference(s)',
            'internal_reference': 'Internal Reference(s)',
            'nen_observations': 'Observations',
            'nen_judgement_assessor_notes': 'Assessor Notes',
        }
        return ", ".join(labels.get(f, f) for f in fields_list)

    def _apply_version_and_summary(self, changed_field_keys):
        """Append version to draft_name and add changed fields note to draft_summary.
        This runs before creating a history entry so the history stores updated values.
        """
        self.ensure_one()
        version = self._get_next_history_version()

        # Name: strip trailing " v<number>" if already present, then append current
        base_name = self.draft_name or self.name or ""
        base_name = re.sub(r"\s+v\d+$", "", base_name).strip()
        new_name = (base_name + f" v{version}").strip()

        # Summary: remove existing trailing "Changed fields: ..." then append current list
        base_summary = self.draft_summary or ""
        base_summary = re.sub(r"\s*Changed fields:.*$", "", base_summary).rstrip()
        changed_note = ""
        if changed_field_keys:
            changed_note = (" " if base_summary else "") + "Changed fields: " + self._format_changed_fields_label(changed_field_keys)
        new_summary = (base_summary + changed_note) or False

        # Update without triggering extra history (these fields are not tracked here)
        self.with_context(prefetch_fields=False).write({
            'draft_name': new_name,
            'draft_summary': new_summary,
        })

    def _history_extra_fields_vals(self):
        self.ensure_one()
        return {
            'external_reference': self.external_reference,
            'internal_reference': self.internal_reference,
            'nen_observations': self.nen_observations,
            'nen_judgement_assessor_notes': self.nen_judgement_assessor_notes,
        }

    def _history_full_vals(self):
        self.ensure_one()
        vals = {
            'page_id': self.id,
            'name': self.draft_name,
            'summary': self.draft_summary,
            'content': self.content,
        }
        vals.update(self._history_extra_fields_vals())
        return vals

    def write(self, vals):
        tracked_fields = {
            'external_reference',
            'internal_reference',
            'nen_observations',
            'nen_judgement_assessor_notes',
        }
        need_history = any(f in vals for f in tracked_fields)
        content_changed = 'content' in vals  # handled by _inverse_content
        res = super().write(vals)
        if need_history and not content_changed:
            for rec in self:
                if rec.type == 'content':
                    changed_keys = [f for f in tracked_fields if f in vals]
                    rec._apply_version_and_summary(changed_keys)
                    rec._create_history(rec._history_full_vals())
        return res

    def _inverse_content(self):
        for rec in self:
            if rec.type == "content" and rec.content != rec.history_head.content:
                # Determine which HTML fields changed vs. previous history head
                changed_keys = ['content']
                prev = rec.history_head if rec.history_head else False
                for f in ['external_reference', 'internal_reference', 'nen_observations', 'nen_judgement_assessor_notes']:
                    prev_val = getattr(prev, f) if prev else False
                    new_val = getattr(rec, f)
                    if (new_val or "") != (prev_val or ""):
                        changed_keys.append(f)
                rec._apply_version_and_summary(changed_keys)
                rec._create_history(rec._history_full_vals())
