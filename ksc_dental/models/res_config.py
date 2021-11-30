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
            'dental_calendar_weekends',
            'dental_calendar_weeknumber',
            'dental_calendar_weekday',
            'dental_calendar_allow_overlap',
            'dental_calendar_disable_dragging',
            'dental_calendar_disable_resizing',
            'dental_calendar_snap_minutes',
            'dental_calendar_slot_minutes',
            'dental_calendar_min_time',
            'dental_calendar_max_time',
            'dental_calendar_start_time',
            'dental_room_ids'
        ]



class ResCompany(models.Model):
    _inherit = "res.company"

    dental_physician_ids = fields.Many2many('res.partner','company_dental_physician', domain="[('is_physician','=',True)]")
    dental_consultation_product_id = fields.Many2one('product.product')
    dental_room_ids = fields.Many2many('ksc.room', 'company_dental_room')
    dental_journal_ids = fields.Many2many('account.journal','company_dental_journal')
    
    chart_type = fields.Selection([
        ('universal', 'Universal Numbering System'),
        ('palmer', 'Palmer Method'),
        ('iso', 'ISO FDI Numbering System')
    ], 'Select Chart Type', default='iso',required=True)

    dental_calendar_weekends = fields.Boolean(string='Show weekends?', default=True)
    dental_calendar_weeknumber = fields.Boolean(string='Show week number?', default=True)
    dental_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, default='0')
    dental_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', default=True)
    dental_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', default=False)
    dental_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', default=False)
    dental_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',default=15)
    dental_calendar_slot_minutes = fields.Integer(string='Minutes per row', default=30)
    dental_calendar_min_time = fields.Float(string='Calendar time range from', default=0.0)
    dental_calendar_max_time = fields.Float(string='Calendar time range to', default=24.0)
    dental_calendar_start_time = fields.Float(string='Start time', default=6.0)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dental_consultation_product_id = fields.Many2one('product.product', related='company_id.dental_consultation_product_id', readonly=False)
    dental_physician_ids = fields.Many2many('res.partner', related='company_id.dental_physician_ids',
        domain="[('is_physician','=',True)]", readonly=False)
    dental_room_ids = fields.Many2many('ksc.room', related='company_id.dental_room_ids', readonly=False)
    dental_journal_ids = fields.Many2many('account.journal',related='company_id.dental_journal_ids', readonly=False)

    dental_calendar_weekends = fields.Boolean(string='Show weekends?', related='company_id.dental_calendar_weekends', readonly=False)
    dental_calendar_weeknumber = fields.Boolean(string='Show week number?', related='company_id.dental_calendar_weeknumber', readonly=False)
    dental_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, related='company_id.dental_calendar_weekday', readonly=False)
    dental_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', related='company_id.dental_calendar_allow_overlap', readonly=False)
    dental_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', related='company_id.dental_calendar_disable_dragging', readonly=False)
    dental_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', related='company_id.dental_calendar_disable_resizing', readonly=False)
    dental_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',related='company_id.dental_calendar_snap_minutes', readonly=False)
    dental_calendar_slot_minutes = fields.Integer(string='Minutes per row', related='company_id.dental_calendar_slot_minutes', readonly=False)
    dental_calendar_min_time = fields.Float(string='Calendar time range from', related='company_id.dental_calendar_min_time', readonly=False)
    dental_calendar_max_time = fields.Float(string='Calendar time range to', related='company_id.dental_calendar_max_time', readonly=False)
    dental_calendar_start_time = fields.Float(string='Start time', related='company_id.dental_calendar_start_time', readonly=False)   