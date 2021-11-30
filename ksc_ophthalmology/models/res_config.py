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
            'ophthalmology_calendar_weekends',
            'ophthalmology_calendar_weeknumber',
            'ophthalmology_calendar_weekday',
            'ophthalmology_calendar_allow_overlap',
            'ophthalmology_calendar_disable_dragging',
            'ophthalmology_calendar_disable_resizing',
            'ophthalmology_calendar_snap_minutes',
            'ophthalmology_calendar_slot_minutes',
            'ophthalmology_calendar_min_time',
            'ophthalmology_calendar_max_time',
            'ophthalmology_calendar_start_time',
            'ophthalmology_room_ids'
        ]


class ResCompany(models.Model):
    _inherit = "res.company"

    ophthalmology_physician_ids = fields.Many2many('res.partner','company_ophthalmology_physician', domain="[('is_physician','=',True)]")
    ophthalmology_consultation_product_id = fields.Many2one('product.product')
    ophthalmology_room_ids = fields.Many2many('ksc.room', 'company_ophthalmology_room')
    ophthalmology_journal_ids = fields.Many2many('account.journal','company_ophthalmology_journal')

    ophthalmology_calendar_weekends = fields.Boolean(string='Show weekends?', default=True)
    ophthalmology_calendar_weeknumber = fields.Boolean(string='Show week number?', default=True)
    ophthalmology_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, default='0')
    ophthalmology_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', default=True)
    ophthalmology_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', default=False)
    ophthalmology_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', default=False)
    ophthalmology_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',default=15)
    ophthalmology_calendar_slot_minutes = fields.Integer(string='Minutes per row', default=30)
    ophthalmology_calendar_min_time = fields.Float(string='Calendar time range from', default=0.0)
    ophthalmology_calendar_max_time = fields.Float(string='Calendar time range to', default=24.0)
    ophthalmology_calendar_start_time = fields.Float(string='Start time', default=6.0) 


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ophthalmology_consultation_product_id = fields.Many2one('product.product', related='company_id.ophthalmology_consultation_product_id', readonly=False)
    ophthalmology_physician_ids = fields.Many2many('res.partner', related='company_id.ophthalmology_physician_ids',
        domain="[('is_physician','=',True)]", readonly=False)
    ophthalmology_room_ids = fields.Many2many('ksc.room', related='company_id.ophthalmology_room_ids', readonly=False)
    ophthalmology_journal_ids = fields.Many2many('account.journal',related='company_id.ophthalmology_journal_ids', readonly=False)

    ophthalmology_calendar_weekends = fields.Boolean(string='Show weekends?', related='company_id.ophthalmology_calendar_weekends', readonly=False)
    ophthalmology_calendar_weeknumber = fields.Boolean(string='Show week number?', related='company_id.ophthalmology_calendar_weeknumber', readonly=False)
    ophthalmology_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, related='company_id.ophthalmology_calendar_weekday', readonly=False)
    ophthalmology_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', related='company_id.ophthalmology_calendar_allow_overlap', readonly=False)
    ophthalmology_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', related='company_id.ophthalmology_calendar_disable_dragging', readonly=False)
    ophthalmology_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', related='company_id.ophthalmology_calendar_disable_resizing', readonly=False)
    ophthalmology_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',related='company_id.ophthalmology_calendar_snap_minutes', readonly=False)
    ophthalmology_calendar_slot_minutes = fields.Integer(string='Minutes per row', related='company_id.ophthalmology_calendar_slot_minutes', readonly=False)
    ophthalmology_calendar_min_time = fields.Float(string='Calendar time range from', related='company_id.ophthalmology_calendar_min_time', readonly=False)
    ophthalmology_calendar_max_time = fields.Float(string='Calendar time range to', related='company_id.ophthalmology_calendar_max_time', readonly=False)
    ophthalmology_calendar_start_time = fields.Float(string='Start time', related='company_id.ophthalmology_calendar_start_time', readonly=False)     

