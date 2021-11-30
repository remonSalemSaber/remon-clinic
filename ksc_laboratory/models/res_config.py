# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _



WEEKDAYS = [('0', 'Sunday'), ('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'),('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday')]


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_fields(self):
        res = super(MailThread, self)._get_fields()
        return res + [
            'laboratory_calendar_weekends',
            'laboratory_calendar_weeknumber',
            'laboratory_calendar_weekday',
            'laboratory_calendar_allow_overlap',
            'laboratory_calendar_disable_dragging',
            'laboratory_calendar_disable_resizing',
            'laboratory_calendar_snap_minutes',
            'laboratory_calendar_slot_minutes',
            'laboratory_calendar_min_time',
            'laboratory_calendar_max_time',
            'laboratory_calendar_start_time',
        ]


class ResCompany(models.Model):
    _inherit = "res.company"

    laboratory_usage_location = fields.Many2one('stock.location', 
        string='Usage Location for Consumed Laboratory Test Material.')
    laboratory_stock_location = fields.Many2one('stock.location', 
        string='Stock Location for Consumed Laboratory Test Material')
    ksc_labresult_qrcode = fields.Boolean(string="Print Authetication QrCode on Laboratory Result", default=True)
    ksc_auto_create_lab_sample = fields.Boolean(string="Auto Create Lab Sample", default=True)

    laboratory_calendar_weekends = fields.Boolean(string='Show weekends?', default=True)
    laboratory_calendar_weeknumber = fields.Boolean(string='Show week number?', default=True)
    laboratory_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, default='0')
    laboratory_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', default=True)
    laboratory_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', default=False)
    laboratory_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', default=False)
    laboratory_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',default=15)
    laboratory_calendar_slot_minutes = fields.Integer(string='Minutes per row', default=30)
    laboratory_calendar_min_time = fields.Float(string='Calendar time range from', default=0.0)
    laboratory_calendar_max_time = fields.Float(string='Calendar time range to', default=24.0)
    laboratory_calendar_start_time = fields.Float(string='Start time', default=6.0)

    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    laboratory_usage_location = fields.Many2one('stock.location', 
        related='company_id.laboratory_usage_location',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Laboratory Test Material', readonly=False)
    laboratory_stock_location = fields.Many2one('stock.location', 
        related='company_id.laboratory_stock_location',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Laboratory Test Material', readonly=False)
    ksc_labresult_qrcode = fields.Boolean(related='company_id.ksc_labresult_qrcode', string="Print Authetication QrCode on Laboratory Result", readonly=False)
    ksc_auto_create_lab_sample = fields.Boolean(related='company_id.ksc_auto_create_lab_sample', string="Auto Create Laboratory Sample", readonly=False)

    laboratory_calendar_weekends = fields.Boolean(string='Show weekends?', related='company_id.laboratory_calendar_weekends', readonly=False)
    laboratory_calendar_weeknumber = fields.Boolean(string='Show week number?', related='company_id.laboratory_calendar_weeknumber', readonly=False)
    laboratory_calendar_weekday = fields.Selection(selection=WEEKDAYS, string='First day of week?',required=True, related='company_id.laboratory_calendar_weekday', readonly=False)
    laboratory_calendar_allow_overlap = fields.Boolean(string='Allow events overlap?', related='company_id.laboratory_calendar_allow_overlap', readonly=False)
    laboratory_calendar_disable_dragging = fields.Boolean(string='Disable drag and drop?', related='company_id.laboratory_calendar_disable_dragging', readonly=False)
    laboratory_calendar_disable_resizing = fields.Boolean(string='Disable resizing?', related='company_id.laboratory_calendar_disable_resizing', readonly=False)
    laboratory_calendar_snap_minutes = fields.Integer(string='Default minutes when creating and resizing',related='company_id.laboratory_calendar_snap_minutes', readonly=False)
    laboratory_calendar_slot_minutes = fields.Integer(string='Minutes per row', related='company_id.laboratory_calendar_slot_minutes', readonly=False)
    laboratory_calendar_min_time = fields.Float(string='Calendar time range from', related='company_id.laboratory_calendar_min_time', readonly=False)
    laboratory_calendar_max_time = fields.Float(string='Calendar time range to', related='company_id.laboratory_calendar_max_time', readonly=False)
    laboratory_calendar_start_time = fields.Float(string='Start time', related='company_id.laboratory_calendar_start_time', readonly=False)   
