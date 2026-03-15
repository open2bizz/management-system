# Copyright (C) 2025 Open2bizz BV www.open2bizz.nl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, exceptions, _
from odoo import SUPERUSER_ID  # Voeg deze import toe
import logging

_logger = logging.getLogger(__name__)

class MgmtsystemAction(models.Model):
    _inherit = "mgmtsystem.action"

    def _get_default_project(self):
    # PROBLEEM: Bij object creatie bestaat `self` nog niet, dus self.system_id zal altijd None zijn
    # Dit moet worden opgelost door de default waarde in een ander veld op te slaan
    # of door een andere benadering te gebruiken
        if hasattr(self, 'system_id') and self.system_id and self.system_id.project_id:
            return self.system_id.project_id.id
        else:
            return False

    project_id = fields.Many2one("project.project", string="Project", default=_get_default_project)
    task_id = fields.Many2one("project.task", string="Task")

    def _get_closing_phase(self):
        closing_phase = self.env['mgmtsystem.action.stage'].search([('is_ending', '=', True)], limit=1)
        if not closing_phase:
            closing_phase = self.env['mgmtsystem.action.stage'].search([('fold', '=', True)], limit=1)
        return closing_phase or False

    def _get_checking_phase(self):
        checking_phase = self.env['mgmtsystem.action.stage'].search([('to_check', '=', True)], limit=1)
        if not checking_phase:
            checking_phase =  False
        return checking_phase or False

    def action_create_task(self):
        """
        Create a project task based on the current management system action.

        This method creates a new project task associated with the current management system action.
        It sets up the task with details from the action, including project, name, description, tags,
        and deadline. It also updates the action's stage and links the newly created task to the action.

        The method performs several checks before creating the task:
        - Ensures that the project tag and ending stage are properly set up.
        - Verifies that a task doesn't already exist for this action.
        - Checks that a project is set for the action.

        After creating the task, it posts messages to both the action and the task to log the creation.

        :raises UserError: If the project tag or stage is not known, if a task already exists,
                           or if if no project is set.

        :return: None
        """
        self.ensure_one()
        ending_stage = self.env.ref('mgmtsystem_action_project.mgmtsystem_stage_task')
        all_tag_ids = []
        tag = self.env['ir.model.data'].sudo()._xmlid_to_res_id(
            'mgmtsystem_action_project.mgmtsystem_action_proj_tag'
        )
        if not tag or not ending_stage:
            raise exceptions.UserError(_("Project tag or stage not known. please update module"))
        else:
            all_tag_ids = [tag]
        # Also add tags from action to task. (if not created, create the tag)
        tag_others = self.tag_ids
        for tag_other in tag_others:
            tag_task = self.env['project.tags'].search([('name', '=', tag_other.name)], limit=1)
            if not tag_task:
                tag_task = self.env['project.tags'].create({'name': tag_other.name})
            all_tag_ids.append(tag_task.id)
        if self.task_id:
            raise exceptions.UserError(_("Task already exists"))
        elif not self.project_id:
            raise exceptions.UserError(_("Project not set"))
        else:
            vals = {
                'project_id': self.project_id.id,
                'name': self.name,
                'description': self.description,
                'tag_ids': [(6, 0, all_tag_ids)],  # (6, 0, list_of_ids) vervangt alle tags
                "mgmtsystem_action_id": self.id,
                'date_deadline': self.date_deadline or False,
            }
            # Open2Bizz special feature: Check if OCA module task_type is used, and set to internal task type
            # We do not want a dependeny for this, so we solved it this way
            if self.env['ir.module.module'].sudo().search(
                [('name', '=', 'project_type'), ('state', '=', 'installed')], limit=1):
                try:
                    type_id = self.env.ref('project_task_open2bizz.project_type_open2bizz_parent_004')
                    vals.update({'type_id': type_id.id})
                except Exception as e:  # Specificeer exception type
                    # Log de werkelijke fout voor debugging
                    _logger.error(f"Task type lookup failed: {e}")
                    raise exceptions.UserError(_("Task type internal cannot be found. "
                                                 "Update the module 'project_task_open2bizz'"))
            user = self.user_id
            if user:
                vals.update({'user_ids': [(4, self.user_id.id)]})
            task_id = self.env["project.task"].create(vals)
            self.write({
                'stage_id': ending_stage.id,
                'task_id': task_id.id
            })
            poster = self.env.user._is_internal() and self.env.user.id or SUPERUSER_ID
            title = _("Project task")
            self.with_user(poster).message_post(
                body=_("%s has been created", task_id._get_html_link(title=title)),
            )
            task_id.with_user(poster).message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': task_id, 'origin': self},
                subtype_xmlid='mail.mt_note',
            )

class MgmtsystemActionStage(models.Model):
    _inherit = "mgmtsystem.action.stage"

    to_check = fields.Boolean(string="To Check Stage")
