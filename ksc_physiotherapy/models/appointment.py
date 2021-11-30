# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _rec_count(self):
        rec = super(ResPartner, self)._rec_count()
        for rec in self:
            rec.physiotherapy_count = len(rec.physiotherapy_ids)
            rec.treatment_plan_count = len(rec.treatment_plan_ids)

    physiotherapy_ids = fields.One2many('ksc.physiotherapy', 'patient_id', string='Physiotherapy')
    physiotherapy_count = fields.Integer(compute='_rec_count', string='# Physiotherapy')


    treatment_plan_ids = fields.One2many('treatment.plan', 'patient_id')
    treatment_plan_count = fields.Integer(compute='_rec_count')
    

    def action_view_treatment_plan(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_physiotherapy.action_treatment_plan")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id
        }
        return action

    def action_create_treatment_plan(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Physiotherapy'),
            'res_model': 'treatment.plan',
            'view_mode': 'form',
            'context': {
                'default_patient_id':self.id,
            },
        }

    
    def action_view_physiotherapy(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_physiotherapy.ksc_action_form_physiotherapy")
        action['domain'] = [('patient_id', '=', self.id)]
        action['context'] = {
            'default_patient_id': self.id
        }
        return action

    def action_create_physiotherapy(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Physiotherapy'),
            'res_model': 'ksc.physiotherapy',
            'view_mode': 'calendar',
            'context': {
                'default_patient_id':self.id,
            },
        }


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'

    def get_journal_domain(self):
        domain = super(AccountPayment,self).get_journal_domain()
        if self._context.get('physiotherapy'):
            ids = self.env.company.physiotherapy_journal_ids.ids
            domain.append(('id','in',ids))
        return domain


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'
    
    avalibel_in_physiotherapy = fields.Boolean()
    avalibel_in_physiotherapy_treatment_plan = fields.Boolean()

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    _description = 'Account Journal'
    
    avalibel_in_physiotherapy = fields.Boolean()

class KSCServiceLine(models.Model):
    _inherit = "ksc.service.line"
    _description = "List of Services"

    physiotherapy_appt_id = fields.Many2one('ksc.physiotherapy.appointment', ondelete="cascade", string='Appointment')
    

class KscphysiotherapyAppointment(models.Model):
    _name = 'ksc.physiotherapy.appointment'
    _inherit = 'ksc.appointment'
    _description = 'Ksc physiotherapy Appointment'
    
    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}
    service_line_ids = fields.One2many('ksc.service.line', 'physiotherapy_appt_id',string='Service Line', states=READONLY_STATES, copy=False)

    @api.model
    def create(self, values):
        if values.get('name', 'New Appointment') == 'New Appointment':
            values['name'] = self.env['ir.sequence'].next_by_code('ksc.physiotherapy.appointment') or 'New Appointment'
        return super(KscphysiotherapyAppointment, self).create(values)

    @api.model
    def _get_room_domain(self):
        return [('id','in',self.env.company.physiotherapy_room_ids.ids)]
    
    @api.model
    def _get_physician_domain(self):
        return [('id','in',self.env.company.physiotherapy_physician_ids.ids)]
    
    @api.model
    def _get_service_id(self):
        consultation = False
        if self.env.user.company_id.physiotherapy_consultation_product_id:
            consultation = self.env.user.company_id.physiotherapy_consultation_product_id.id
        return consultation

    def action_create_physiotherapy(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Physiotherapy'),
            'res_model': 'ksc.physiotherapy',
            'view_mode': 'calendar',
            'context': {
                'default_patient_id':self.patient_id.id,
                'default_physician_id':self.physician_id.id,
                'default_physiotherapist_id':self.physician_id.id,
            },
        }