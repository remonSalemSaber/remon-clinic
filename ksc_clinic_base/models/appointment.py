# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.osv import expression
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    appointment_id = fields.Many2one('ksc.appointment',  string='Appointment', readonly=True, states={'draft': [('readonly', False)]})


class KscRoom(models.Model):
    _name = 'ksc.room'
    _description = 'Ksc Room'
    
    name = fields.Char(required=True)


class KSCServiceLine(models.Model):
    _name = "ksc.service.line"
    _description = "List of Services"

    name = fields.Char(string='Name',default=lambda self: self.product_id.name)
    product_id = fields.Many2one('product.product', ondelete="restrict", string='Service')
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', help='Amount of medication (eg, 250 mg) per dose')
    qty = fields.Float(string='Quantity', default=1.0)
    move_id = fields.Many2one('stock.move', string='Stock Move')
    date = fields.Date("Date", default=fields.Date.context_today)

    appointment_id = fields.Many2one('ksc.appointment', ondelete="cascade", string='Appointment')

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id


class KscAppointment(models.Model):
    _name = 'ksc.appointment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'ksc.mixin']
    _description = 'Ksc Appointment'

    @api.model
    def _get_service_id(self):
        return False
    
    @api.model
    def _get_room_domain(self):
        res = []
        return res

    @api.model
    def _get_physician_domain(self):
        res = []
        return res

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Appointment Id', readonly=True, copy=False, tracking=True, states=READONLY_STATES)
    patient_id = fields.Many2one('res.partner', domain="[('is_patient','=',True)]", ondelete='restrict',
        required=True, index=True,help='Patient Name', states=READONLY_STATES, tracking=True)
    physician_id = fields.Many2one('res.partner', domain=lambda self: self._get_physician_domain(), ondelete='restrict', string='Physician', 
        index=True, help='Physician\'s Name', states=READONLY_STATES, tracking=True)
    image_128 = fields.Binary(related='patient_id.image_128',string='Image', readonly=True)
    notes = fields.Text(string='Notes', states=READONLY_STATES)
    invoice_id = fields.Many2one('account.move', string='Invoice', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting', 'Waiting'),
        ('in_consultation', 'In consultation'),
        ('pause', 'Pause'),
        ('to_invoice', 'To Invoice'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='State',default='draft', required=True, copy=False, tracking=True)
    start_date = fields.Datetime(string='Start Date', states=READONLY_STATES, copy=False)
    end_date = fields.Datetime(string='End Date', states=READONLY_STATES, copy=False)
    room_id = fields.Many2one('ksc.room', domain=lambda self: self._get_room_domain(), ondelete='cascade', 
        string='Room', help="Appointment Room", states=READONLY_STATES, copy=False)
    cancel_reason = fields.Text(string="Cancel Reason", states=READONLY_STATES, copy=False)
    
    product_id = fields.Many2one('product.product', ondelete='restrict', 
        string='Consultation Service', help="Consultation Services", required=True, 
        default=lambda self:self._get_service_id(), states=READONLY_STATES)
    diseases_ids = fields.Many2many('ksc.diseases', related='patient_id.diseases_ids', readonly=False, states=READONLY_STATES)

    differencial_diagnosis = fields.Text(string='Differential Diagnosis', states=READONLY_STATES, help="The process of weighing the probability of one disease versus that of other diseases possibly accounting for a patient's illness.")
    medical_advice = fields.Text(string='Medical Advice', states=READONLY_STATES, help="The provision of a formal professional opinion regarding what a specific individual should or should not do to restore or preserve health.")
    
    follow_up = fields.Boolean()
    
    service_line_ids = fields.One2many('ksc.service.line', 'appointment_id',string='Service Line', states=READONLY_STATES, copy=False)
    

    def action_create_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_clinic_base.action_ksc_patient_evaluation_popup")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id}
        return action

    def unlink(self):
        for data in self:
            if data.state != 'draft':
                raise UserError(_('You can not delete record not in draft state'))
        return super(KscAppointment, self).unlink()
    
    def appointment_confirm(self):
        if self.invoice_id:
            raise UserError(_('Invoice is not created yet'))
        self.state = 'confirm'

    def appointment_waiting(self):
        self.state = 'waiting'

    def appointment_consultation(self):
        self.state = 'in_consultation'

    def action_pause(self):
        self.state = 'pause'

    def action_start_paused(self):
        self.state = 'in_consultation'

    def consultation_done(self):
        self.state = 'to_invoice'

    def appointment_done(self):
        self.state = 'done'

    def appointment_cancel(self):
        self.state = 'cancel'

    def appointment_draft(self):
        self.state = 'draft'

    def create_invoice(self):
        product_id = self.product_id
        if not product_id:
            raise UserError(_("Please Set Consultation Service first."))
        product_data = [{'product_id': product_id}]
        for service in self.service_line_ids:
            product_data.append({
                'product_id': service.product_id,
                'quantity': service.qty,
            })
        inv_data = {
            'physician_id': self.physician_id and self.physician_id.id or False,
            'appointment_id': self.id,
        }

        invoice = self.ksc_create_invoice(partner=self.patient_id,product_data=product_data, inv_data=inv_data)
        self.invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.appointment_done()

    def view_invoice(self):
        appointment_invoices = self.env['account.move'].search([('appointment_id','=',self.id)])
        invoices = self.mapped('invoice_id') + appointment_invoices

        action = self.ksc_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.patient_id.id,
        })
        return action

    def action_open_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Follow Up'),
            'res_model': 'ksc.wizard.appointment.followup',
            'view_mode': 'form',
            'context': {'model':self._name,'rec_id':self.id},
            'target': 'new',
        }


class KSCDiseases(models.Model):
    _name = 'ksc.diseases'
    _description = "Diseases"

    name = fields.Char(string='Name', required=True, translate=True,  help='Disease name', index=True)