# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'
    
    avalibel_in_dental = fields.Boolean()

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'
    
    avalibel_in_dental = fields.Boolean()


class KSCServiceLine(models.Model):
    _inherit = "ksc.service.line"
    _description = "List of Services"

    dental_appt_id = fields.Many2one('ksc.dental.appointment', ondelete="cascade", string='Appointment')


class KscDentalAppointment(models.Model):
    _name = 'ksc.dental.appointment'
    _inherit = 'ksc.appointment'
    _description = 'Ksc Dental Appointment'
    
    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    service_line_ids = fields.One2many('ksc.service.line', 'dental_appt_id',string='Service Line', states=READONLY_STATES, copy=False)
    teeth_treatment_ids = fields.One2many('medical.teeth.treatment', 'appt_id', 'Operations', readonly=True)

    @api.model
    def create(self, values):
        if values.get('name', 'New Appointment') == 'New Appointment':
            values['name'] = self.env['ir.sequence'].next_by_code('ksc.dental.appointment') or 'New Appointment'
        return super(KscDentalAppointment, self).create(values)

    @api.model
    def _get_room_domain(self):
        return [('id','in',self.env.company.dental_room_ids.ids)]
    
    @api.model
    def _get_physician_domain(self):
        return [('id','in',self.env.company.dental_physician_ids.ids)]
    
    @api.model
    def _get_service_id(self):
        consultation = False
        if self.env.user.company_id.dental_consultation_product_id:
            consultation = self.env.user.company_id.dental_consultation_product_id.id
        return consultation