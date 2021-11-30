# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'

    def get_journal_domain(self):
        domain = super(AccountPayment,self).get_journal_domain()
        if self._context.get('ophthalmology'):
            ids = self.env.company.ophthalmology_journal_ids.ids
            domain.append(('id','in',ids))
        return domain


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'
    
    avalibel_in_ophthalmology = fields.Boolean()

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'
    
    avalibel_in_ophthalmology = fields.Boolean()


class KSCServiceLine(models.Model):
    _inherit = "ksc.service.line"
    _description = "List of Services"

    ophthalmology_appt_id = fields.Many2one('ksc.ophthalmology.appointment', ondelete="cascade", string='Appointment')


class KscophthalmologyAppointment(models.Model):
    _name = 'ksc.ophthalmology.appointment'
    _inherit = 'ksc.appointment'
    _description = 'Ksc ophthalmology Appointment'
    

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}
    service_line_ids = fields.One2many('ksc.service.line', 'ophthalmology_appt_id',string='Service Line', states=READONLY_STATES, copy=False)

    @api.model
    def create(self, values):
        if values.get('name', 'New Appointment') == 'New Appointment':
            values['name'] = self.env['ir.sequence'].next_by_code('ksc.ophthalmology.appointment') or 'New Appointment'
        return super(KscophthalmologyAppointment, self).create(values)

    @api.model
    def _get_room_domain(self):
        return [('id','in',self.env.company.ophthalmology_room_ids.ids)]
    
    @api.model
    def _get_physician_domain(self):
        return [('id','in',self.env.company.ophthalmology_physician_ids.ids)]
    
    @api.model
    def _get_service_id(self):
        consultation = False
        if self.env.user.company_id.ophthalmology_consultation_product_id:
            consultation = self.env.user.company_id.ophthalmology_consultation_product_id.id
        return consultation