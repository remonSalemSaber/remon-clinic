# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round, float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError


WEEKDAYS = [('0', 'Sunday'), ('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'),('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday')]


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_fields(self):
        res = super(MailThread, self)._get_fields()
        return res + [
            'orthopedic_calendar_weekends',
            'orthopedic_calendar_weeknumber',
            'orthopedic_calendar_weekday',
            'orthopedic_calendar_allow_overlap',
            'orthopedic_calendar_disable_dragging',
            'orthopedic_calendar_disable_resizing',
            'orthopedic_calendar_snap_minutes',
            'orthopedic_calendar_slot_minutes',
            'orthopedic_calendar_min_time',
            'orthopedic_calendar_max_time',
            'orthopedic_calendar_start_time',
            'orthopedic_room_ids'
        ]



class ResCompany(models.Model):
    _inherit = "res.company"

    orthopedic_physician_ids = fields.Many2many('res.partner','company_orthopedic_physician', domain="[('is_physician','=',True)]")
    orthopedic_consultation_product_id = fields.Many2one('product.product')
    orthopedic_room_ids = fields.Many2many('ksc.room', 'company_orthopedic_room')
    orthopedic_journal_ids = fields.Many2many('account.journal','company_orthopedic_journal')

    orthopedic_calendar_weekends = fields.Boolean(string='Show weekends?', default=True)
    orthopedic_calendar_weeknumber = fields.Boolean(string='Show week number?', default=True)
    orthopedic_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, default='0')
    orthopedic_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', default=True)
    orthopedic_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', default=False)
    orthopedic_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', default=False)
    orthopedic_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',default=15)
    orthopedic_calendar_slot_minutes = fields.Integer(string='Minutes per row', default=30)
    orthopedic_calendar_min_time = fields.Float(string='Calendar time range from', default=0.0)
    orthopedic_calendar_max_time = fields.Float(string='Calendar time range to', default=24.0)
    orthopedic_calendar_start_time = fields.Float(string='Start time', default=6.0)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    orthopedic_consultation_product_id = fields.Many2one('product.product', related='company_id.orthopedic_consultation_product_id', readonly=False)
    orthopedic_physician_ids = fields.Many2many('res.partner', related='company_id.orthopedic_physician_ids',
        domain="[('is_physician','=',True)]", readonly=False)
    orthopedic_room_ids = fields.Many2many('ksc.room', related='company_id.orthopedic_room_ids', readonly=False)
    orthopedic_journal_ids = fields.Many2many('account.journal',related='company_id.orthopedic_journal_ids', readonly=False)

    orthopedic_calendar_weekends = fields.Boolean(string='Show weekends?', related='company_id.orthopedic_calendar_weekends', readonly=False)
    orthopedic_calendar_weeknumber = fields.Boolean(string='Show week number?', related='company_id.orthopedic_calendar_weeknumber', readonly=False)
    orthopedic_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, related='company_id.orthopedic_calendar_weekday', readonly=False)
    orthopedic_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', related='company_id.orthopedic_calendar_allow_overlap', readonly=False)
    orthopedic_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', related='company_id.orthopedic_calendar_disable_dragging', readonly=False)
    orthopedic_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', related='company_id.orthopedic_calendar_disable_resizing', readonly=False)
    orthopedic_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',related='company_id.orthopedic_calendar_snap_minutes', readonly=False)
    orthopedic_calendar_slot_minutes = fields.Integer(string='Minutes per row', related='company_id.orthopedic_calendar_slot_minutes', readonly=False)
    orthopedic_calendar_min_time = fields.Float(string='Calendar time range from', related='company_id.orthopedic_calendar_min_time', readonly=False)
    orthopedic_calendar_max_time = fields.Float(string='Calendar time range to', related='company_id.orthopedic_calendar_max_time', readonly=False)
    orthopedic_calendar_start_time = fields.Float(string='Start time', related='company_id.orthopedic_calendar_start_time', readonly=False)   

