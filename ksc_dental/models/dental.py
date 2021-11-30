# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
# from mock import DEFAULT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import hashlib
import time



class Partner(models.Model):
    _inherit = "res.partner"
    
    
    def get_user_name(self):
        return self.name

class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = "product.product"
                
    action_perform = fields.Selection([('action', 'Action'), ('missing', 'Missing'), ('composite', 'Composite')], 'Action perform',default='action')
    is_medicament = fields.Boolean('Medicament', help="Check if the product is a medicament")
    is_insurance_plan = fields.Boolean('Insurance Plan', help='Check if the product is an insurance plan')
    is_treatment = fields.Boolean('Treatment', help="Check if the product is a Treatment")
    is_planned_visit = fields.Boolean('Planned Visit')
    duration = fields.Selection([('three_months', 'Three Months'), ('six_months', 'Six Months'), ('one_year', 'One Year')], 'Duration')
    
    insurance_company_id = fields.Many2many('res.partner','treatment_insurance_company_relation','insurance_company_id','treatment_id','Insurance Company')
    
    
    def get_treatment_charge(self):
        print("remon")
        return self.lst_price
    

class TeethCode(models.Model):
    _description = "teeth code"
    _name = "teeth.code"
    
    name =  fields.Char ('Name', size=128, required=True)
    code =  fields.Char ('Code', size=128, required=True)
    palmer_name = fields.Char('palmer_name', size=128, required=True)
    palmer_internal_id = fields.Integer('Palmar Internam ID')
    iso = fields.Char('iso', size=128, required=True)
    internal_id = fields.Integer('Internal IDS')
    child = fields.Boolean()
    
    
    def write(self, vals):
        for rec in self:
            if 'palmer_name' in vals:
                lst = self.search([('palmer_internal_id', '=', rec.palmer_internal_id)])
                super(TeethCode, lst).write({'palmer_name': vals['palmer_name']})
        return super(TeethCode, self).write(vals)
    
    @api.model
    def name_get(self):
        res = []
        teeth_type = self.env.user.company_id.chart_type
        for each in self:
            name = each.name
            if teeth_type == 'palmer':
                name = str(each.palmer_internal_id)
                if each.internal_id <= 8:
                    name += '-1x'
                elif each.internal_id <= 16:
                    name += '-2x'
                elif each.internal_id <= 24:
                    name += '-3x'
                else:
                    name += '-4x'
            elif teeth_type == 'iso':
                name = each.iso
            res.append((each.id, name))
        return res
    
    
    def get_teeth_code(self):
        l1 = []
        d1 = {}
        teeth_ids = self.env['teeth.code'].search([('child','=',False)])
        teeth_type = self.env.user.company_id.chart_type
        for teeth in teeth_ids:
            if teeth_type == 'palmer': 
                d1[int(teeth.internal_id)] = teeth.palmer_name
            elif teeth_type == 'iso':
                d1[int(teeth.internal_id)] = teeth.iso
            else:
                d1[int(teeth.internal_id)] = teeth.name
        x = d1.keys()
        x =sorted(x)
        for i in x:
            l1.append(d1[i])
        return l1

    
    def get_child_teeth_code(self):
        l1 = []
        d1 = {}
        teeth_ids = self.env['teeth.code'].search([('child','=',True)])
        teeth_type = self.env.user.company_id.chart_type
        for teeth in teeth_ids:
            if teeth_type == 'palmer': 
                d1[int(teeth.internal_id)] = teeth.palmer_name
            elif teeth_type == 'iso':
                d1[int(teeth.internal_id)] = teeth.iso or ''
            else:
                d1[int(teeth.internal_id)] = teeth.name
        x = d1.keys()
        x =sorted(x)
        for i in x:
            l1.append(d1[i])
        return l1

class ProductCategory(models.Model):
    _inherit = "product.category"
    _description = "Product Category"
    
    treatment = fields.Boolean('Treatment')
    
    
    def get_treatment_categs(self):
        all_records = self.search([])
        treatment_list = []
        for each_rec in all_records:
            if each_rec.treatment == True:
                treatment_list.append({'treatment_categ_id': each_rec.id, 'name': each_rec.name, 'treatments': []})
        
        product_rec = self.env['product.product'].search([('is_treatment', '=', True)])
        for each_product in product_rec:
            each_template = each_product.product_tmpl_id
            for each_treatment in treatment_list:
                if each_template.categ_id.id == each_treatment['treatment_categ_id']:
                    each_treatment['treatments'].append({'treatment_id': each_product.id, 'treatment_name': each_template.name, 'action': each_product.action_perform})
                    break
         
        return treatment_list
    

class MedicalTeethTreatment(models.Model):
    _description = "Medical Teeth Treatment"
    _name = "medical.teeth.treatment"
    
    patient_id =  fields.Many2one('res.partner', 'Patient Details')
    teeth_id =  fields.Many2one('teeth.code', 'Tooth')
    description =  fields.Many2one('product.product', 'Description', domain=[('is_treatment', '=', True)])
    detail_description =  fields.Text('Surface')
    state = fields.Selection([('planned', 'Planned'), ('condition', 'Condition'), ('completed', 'Completed'), ('in_progress', 'In Progress'), ('invoiced', 'Invoiced')], 'Status',default='planned')
    total = fields.Float(compute='_compute_total')
    dentist = fields.Many2one('res.partner', 'Dentist')
    amount = fields.Float('Amount', related="description.lst_price")
    discount = fields.Float('Discount %')
    note = fields.Text()
    appt_id = fields.Many2one('ksc.dental.appointment', 'Appointment ID')
    teeth_code_rel = fields.Many2many('teeth.code','teeth_code_medical_teeth_treatment_rel','operation','teeth')
    invoice_id = fields.Many2one('account.move')
    completed = fields.Boolean()
    child = fields.Boolean()
    dicount_amount = fields.Float(compute='_compute_dicount_amount')
    
    @api.depends('amount','discount')
    def _compute_dicount_amount(self):
        for rec in self:
            rec.dicount_amount = (rec.amount * (rec.discount/100))

    
    def unlink(self):
        for rec in self:
            if rec.state in ('completed','in_progress') and not self.env.user.has_group('ksc_dental.group_allow_delete_teeth_treatment'):
                raise UserError(_('You cannot remove/deactivate an (In Progress , Completed) record'))
        return super(MedicalTeethTreatment, self).unlink()

    
    @api.depends('amount', 'discount')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.amount - (rec.amount * (rec.discount/100))



class OrthodonticPlan(models.Model):
    _description = "Orthodontic Plan"
    _name = "ksc.ortho.plan"
    _inherit = 'ksc.mixin'
    
    patient_id =  fields.Many2one('res.partner')
    physician_id = fields.Many2one('res.partner', required=True)
    product_id =  fields.Many2one('product.product',domain=[('is_treatment', '=', True)],required=True)
    amount = fields.Float('Amount', default=0.0, required=True)
    invoice_id = fields.Many2one('account.move')
    invoiced = fields.Boolean(compute='_compute_invoiced')
    state = fields.Selection([
        ('draft','Draft'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], 'Status',related="invoice_id.state")
    
    @api.depends('invoice_id')
    def _compute_invoiced(self):
        for rec in self:
            rec.invoiced = rec.invoice_id
    
    def _compute_physician_id(self):
        for rec in self:
            rec.physician_id = self.env.user.partner_id
    
    def unlink(self):
        for rec in self:
            if rec.invoice_id:
                raise UserError(_('You cannot remove/deactivate an invoiced record'))
        return super(OrthodonticPlan, self).unlink()

    def create_invoice(self):
        products_data = [{
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': self.amount,
        }]
        inv_data = {
            'physician_id':self.physician_id and self.physician_id.id,
            'partner_id': self.patient_id.id,
        }
        invoice = self.ksc_create_invoice(partner=self,product_data=products_data, inv_data=inv_data)
        self.invoice_id = invoice.id