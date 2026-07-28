#    Copyright (C) 2025 Open2bizz BV www.open2bizz.nl

from odoo import fields, models

from odoo.addons.html_editor.models.diff_utils import generate_comparison


class DocumentPageHistory(models.Model):
    _inherit = "document.page.history"

    # Snapshots of extra fields at the time of the history entry
    external_reference = fields.Html(sanitize=False)
    internal_reference = fields.Html(sanitize=False)
    nen_observations = fields.Html(sanitize=False)
    nen_judgement_assessor_notes = fields.Html(sanitize=False)

    # Diffs for extra fields vs. previous history entry for the same page
    external_reference_diff = fields.Html(
        compute="_compute_external_reference_diff", sanitize_tags=False
    )
    internal_reference_diff = fields.Html(
        compute="_compute_internal_reference_diff", sanitize_tags=False
    )
    nen_observations_diff = fields.Html(
        compute="_compute_nen_observations_diff", sanitize_tags=False
    )
    nen_judgement_assessor_notes_diff = fields.Html(
        compute="_compute_nen_judgement_assessor_notes_diff", sanitize_tags=False
    )

    def _get_prev_history(self, rec):
        return self.env["document.page.history"].search(
            [
                ("page_id", "=", rec.page_id.id),
                ("create_date", "<", rec.create_date),
            ],
            limit=1,
            order="create_date DESC",
        )

    def _compute_external_reference_diff(self):
        for rec in self:
            prev = self._get_prev_history(rec)
            text1 = prev.external_reference or ""
            text2 = rec.external_reference or ""
            rec.external_reference_diff = generate_comparison(text1, text2)

    def _compute_internal_reference_diff(self):
        for rec in self:
            prev = self._get_prev_history(rec)
            text1 = prev.internal_reference or ""
            text2 = rec.internal_reference or ""
            rec.internal_reference_diff = generate_comparison(text1, text2)

    def _compute_nen_observations_diff(self):
        for rec in self:
            prev = self._get_prev_history(rec)
            text1 = prev.nen_observations or ""
            text2 = rec.nen_observations or ""
            rec.nen_observations_diff = generate_comparison(text1, text2)

    def _compute_nen_judgement_assessor_notes_diff(self):
        for rec in self:
            prev = self._get_prev_history(rec)
            text1 = prev.nen_judgement_assessor_notes or ""
            text2 = rec.nen_judgement_assessor_notes or ""
            rec.nen_judgement_assessor_notes_diff = generate_comparison(text1, text2)
