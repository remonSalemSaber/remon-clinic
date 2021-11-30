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
            'physiotherapy_calendar_weekends',
            'physiotherapy_calendar_weeknumber',
            'physiotherapy_calendar_weekday',
            'physiotherapy_calendar_allow_overlap',
            'physiotherapy_calendar_disable_dragging',
            'physiotherapy_calendar_disable_resizing',
            'physiotherapy_calendar_snap_minutes',
            'physiotherapy_calendar_slot_minutes',
            'physiotherapy_calendar_min_time',
            'physiotherapy_calendar_max_time',
            'physiotherapy_calendar_start_time',
            'physiotherapy_room_ids'
        ]

class ResCompany(models.Model):
    _inherit = "res.company"

    physiotherapy_physiotherapist_ids = fields.Many2many('res.partner','company_physiotherapy_physiotherapist', domain="[('is_physician','=',True)]")

    physiotherapy_physician_ids = fields.Many2many('res.partner','company_physiotherapy_physician', domain="[('is_physician','=',True)]")
    physiotherapy_consultation_product_id = fields.Many2one('product.product')
    physiotherapy_room_ids = fields.Many2many('ksc.room', 'company_physiotherapy_room')
    physiotherapy_journal_ids = fields.Many2many('account.journal','company_physiotherapy_journal')


    physiotherapy_calendar_weekends = fields.Boolean(string='Show weekends?', default=True)
    physiotherapy_calendar_weeknumber = fields.Boolean(string='Show week number?', default=True)
    physiotherapy_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, default='0')
    physiotherapy_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', default=True)
    physiotherapy_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', default=False)
    physiotherapy_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', default=False)
    physiotherapy_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',default=15)
    physiotherapy_calendar_slot_minutes = fields.Integer(string='Minutes per row', default=30)
    physiotherapy_calendar_min_time = fields.Float(string='Calendar time range from', default=0.0)
    physiotherapy_calendar_max_time = fields.Float(string='Calendar time range to', default=24.0)
    physiotherapy_calendar_start_time = fields.Float(string='Start time', default=6.0)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    physiotherapy_physiotherapist_ids = fields.Many2many('res.partner', related='company_id.physiotherapy_physiotherapist_ids',domain="[('is_physician','=',True)]", readonly=False)

    physiotherapy_consultation_product_id = fields.Many2one('product.product', related='company_id.physiotherapy_consultation_product_id', readonly=False)
    physiotherapy_physician_ids = fields.Many2many('res.partner', related='company_id.physiotherapy_physician_ids',domain="[('is_physician','=',True)]", readonly=False)
    physiotherapy_room_ids = fields.Many2many('ksc.room', related='company_id.physiotherapy_room_ids', readonly=False)
    physiotherapy_journal_ids = fields.Many2many('account.journal',related='company_id.physiotherapy_journal_ids', readonly=False)
    
    physiotherapy_calendar_weekends = fields.Boolean(string='Show weekends?', related='company_id.physiotherapy_calendar_weekends', readonly=False)
    physiotherapy_calendar_weeknumber = fields.Boolean(string='Show week number?', related='company_id.physiotherapy_calendar_weeknumber', readonly=False)
    physiotherapy_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, related='company_id.physiotherapy_calendar_weekday', readonly=False)
    physiotherapy_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', related='company_id.physiotherapy_calendar_allow_overlap', readonly=False)
    physiotherapy_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', related='company_id.physiotherapy_calendar_disable_dragging', readonly=False)
    physiotherapy_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', related='company_id.physiotherapy_calendar_disable_resizing', readonly=False)
    physiotherapy_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',related='company_id.physiotherapy_calendar_snap_minutes', readonly=False)
    physiotherapy_calendar_slot_minutes = fields.Integer(string='Minutes per row', related='company_id.physiotherapy_calendar_slot_minutes', readonly=False)
    physiotherapy_calendar_min_time = fields.Float(string='Calendar time range from', related='company_id.physiotherapy_calendar_min_time', readonly=False)
    physiotherapy_calendar_max_time = fields.Float(string='Calendar time range to', related='company_id.physiotherapy_calendar_max_time', readonly=False)
    physiotherapy_calendar_start_time = fields.Float(string='Start time', related='company_id.physiotherapy_calendar_start_time', readonly=False)