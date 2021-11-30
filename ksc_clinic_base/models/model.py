# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.osv.expression import get_unaccent_wrapper
import re

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'

    def _rec_count(self):
        for rec in self:
            rec.evaluation_count = len(rec.evaluation_ids)
    
    is_patient = fields.Boolean()
    is_physician = fields.Boolean()

    arabic_name = fields.Char()
    code = fields.Char(string='Identification Code', default='/',
        help='Identifier provided by the Health Center.', copy=False, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'), 
        ('female', 'Female')], string='Gender', default='male', tracking=True)
    birthday = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_get_age')
    blood_group = fields.Selection([ ('A+', 'A+'),('A-', 'A-'), ('B+', 'B+'),('B-', 'B-'),
        ('AB+', 'AB+'),('AB-', 'AB-'), ('O+', 'O+'),('O-', 'O-')], string='Blood Group')
    marital_status = fields.Selection([
        ('single', 'Single'), 
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
        ('live_in_relationship', 'Live In Relationship'),
    ], string='Marital Status', default="single")
    nationality = fields.Char()
    civil = fields.Char()
    diseases_ids = fields.Many2many('ksc.diseases')
    
    evaluation_count = fields.Integer(compute='_rec_count', string='# Evaluations')
    evaluation_ids = fields.One2many('ksc.patient.evaluation', 'patient_id', 'Evaluations')

    last_evaluation_id = fields.Many2one("ksc.patient.evaluation", string="Last Appointment", compute='_get_last_evaluation', readonly=True)
    weight = fields.Float(related="last_evaluation_id.weight", string='Weight', help="Weight in KG", readonly=True)
    height = fields.Float(related="last_evaluation_id.height", string='Height', help="Height in cm", readonly=True)
    temp = fields.Float(related="last_evaluation_id.temp", string='Temp', readonly=True)
    hr = fields.Float(related="last_evaluation_id.hr", string='HR', help="Heart Rate", readonly=True)
    rr = fields.Float(related="last_evaluation_id.rr", string='RR', readonly=True, help='Respiratory Rate')
    systolic_bp = fields.Float(related="last_evaluation_id.systolic_bp", string="Systolic BP")
    diastolic_bp = fields.Float(related="last_evaluation_id.diastolic_bp", string="Diastolic BP")
    spo2 = fields.Float(related="last_evaluation_id.spo2", string='SpO2', readonly=True, 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    bmi = fields.Float(related="last_evaluation_id.bmi", string='Body Mass Index', readonly=True)
    bmi_state = fields.Selection(related="last_evaluation_id.bmi_state", string='BMI State', readonly=True)

    def _get_last_evaluation(self):
        for rec in self:
            evaluation_ids = rec.evaluation_ids.filtered(lambda x: x.state=='done')
                   
            if evaluation_ids:
                rec.last_evaluation_id = evaluation_ids[0].id if evaluation_ids else False
            else:
                rec.last_evaluation_id = False

    def action_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_clinic_base.action_ksc_patient_evaluation")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id}
        return action

    @api.depends('birthday')
    def _get_age(self):
        for rec in self:
            rec.age = 0
            if rec.birthday:
                end_data = fields.Datetime.now()
                delta = relativedelta(end_data, rec.birthday)
                rec.age = delta.years
    
    @api.model
    def create(self, values):
        if values.get('code','/') == '/':
            if values.get('is_patient'):
                values['code'] = self.env['ir.sequence'].next_by_code('patient') or ''
            elif values.get('is_physician'):
                values['code'] = self.env['ir.sequence'].next_by_code('physician') or ''
        return super(ResPartner, self).create(values)
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        self = self.with_user(name_get_uid or self.env.uid)
        # as the implementation is in SQL, we force the recompute of fields if necessary
        self.recompute(['display_name'])
        self.flush()
        if args is None:
            args = []
        order_by_rank = self.env.context.get('res_partner_search_mode') 
        if (name or order_by_rank) and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            self.check_access_rights('read')
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            from_str = from_clause if from_clause else 'res_partner'
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            fields = self._get_name_search_order_by_fields()

            query = """SELECT res_partner.id
                         FROM {from_str}
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}

                           OR {arabic_name} {operator} {percent}
                           OR {code} {operator} {percent}
                           OR {civil} {operator} {percent}
                           OR {phone} {operator} {percent}
                           OR {mobile} {operator} {percent}

                           OR {reference} {operator} {percent}
                           OR {vat} {operator} {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY {fields} {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(from_str=from_str,
                               fields=fields,
                               where=where_str,
                               operator=operator,
                               email=unaccent('res_partner.email'),
                               display_name=unaccent('res_partner.display_name'),
                               reference=unaccent('res_partner.ref'),

                               arabic_name=unaccent('res_partner.arabic_name'),
                               code=unaccent('res_partner.code'),
                               civil=unaccent('res_partner.civil'),
                               phone=unaccent('res_partner.phone'),
                               mobile=unaccent('res_partner.mobile'),

                               percent=unaccent('%s'),
                               vat=unaccent('res_partner.vat'),)

            where_clause_params += [search_name]*8  # for email / display_name, reference
            where_clause_params += [re.sub('[^a-zA-Z0-9\-\.]+', '', search_name) or None]  # for vat
            where_clause_params += [search_name]  # for order by
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            return [row[0] for row in self.env.cr.fetchall()]

        return super(ResPartner, self)._name_search(name, args, operator=operator, limit=limit, name_get_uid=name_get_uid)
