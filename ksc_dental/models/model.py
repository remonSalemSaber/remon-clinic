from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'

    def get_journal_domain(self):
        domain = super(AccountPayment,self).get_journal_domain()
        if self._context.get('dental'):
            ids = self.env.company.dental_journal_ids.ids
            domain.append(('id','in',ids))
        return domain

class KscPatientDiagnosis(models.Model):
    _name = 'ksc.patient.diagnosis'
    _description = 'Patient Diagnosis Notes'
    _rec_name = 'note'

    note = fields.Text()
    patient_id = fields.Many2one('res.partner')


class KscTreatmentPlanDetails(models.Model):
    _name = 'ksc.treatment.plan.details'
    _description = 'Treatment Plan Details'
    _rec_name = 'note'

    note = fields.Text()
    patient_id = fields.Many2one('res.partner')


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner','ksc.mixin']

    teeth_treatment_ids = fields.One2many(
        'medical.teeth.treatment', 'patient_id', 'Operations', readonly=True, tracking=True)
    planned_operation_ids = fields.One2many(
        'medical.teeth.treatment', 'patient_id', compute='_compute_planned_operation_ids', tracking=True)
    in_progress_operation_ids = fields.One2many(
        'medical.teeth.treatment', 'patient_id', compute='_compute_in_progress_operation_ids', tracking=True)
    completed_operation_ids = fields.One2many(
        'medical.teeth.treatment', 'patient_id', compute='_compute_completed_operation_ids', tracking=True)
    diagnosis_ids = fields.One2many(
        'ksc.patient.diagnosis', 'patient_id', tracking=True)
    treatment_plan_details_ids = fields.One2many(
        'ksc.treatment.plan.details', 'patient_id', tracking=True)
    
    planned_total = fields.Float(compute='_compute_planned_total', string='Total')
    ortho_plan_ids = fields.One2many('ksc.ortho.plan', 'patient_id', 'Orthodontic Plan', tracking=True)
    
    @api.depends('planned_operation_ids')
    def _compute_planned_total(self):
        for rec in self:
            rec.planned_total = sum(self.planned_operation_ids.mapped('total'))

    discount_planned_total = fields.Float(compute='_compute_discount_planned_total', string='Discount Total')
    
    @api.depends('planned_operation_ids')
    def _compute_discount_planned_total(self):
        for rec in self:
            rec.discount_planned_total = sum(self.planned_operation_ids.mapped('dicount_amount'))
    
    amount_planned_total = fields.Float(compute='_compute_amount_planned_total', string='Amount Total')
    
    @api.depends('planned_operation_ids')
    def _compute_amount_planned_total(self):
        for rec in self:
            rec.amount_planned_total = sum(self.planned_operation_ids.mapped('amount'))
    
    @api.depends('teeth_treatment_ids')
    def _compute_planned_operation_ids(self):
        for rec in self:
            rec.planned_operation_ids = rec.teeth_treatment_ids.search(
                [('patient_id', '=', rec.id), ('state', '=', 'planned')])

    
    @api.depends('teeth_treatment_ids')
    def _compute_in_progress_operation_ids(self):
        for rec in self:
            rec.in_progress_operation_ids = rec.teeth_treatment_ids.search(
                [('patient_id', '=', rec.id), ('state', '=', 'in_progress')])

    
    @api.depends('teeth_treatment_ids')
    def _compute_completed_operation_ids(self):
        for rec in self:
            rec.completed_operation_ids = rec.teeth_treatment_ids.search(
                [('patient_id', '=', rec.id), ('state', '=', 'completed')])

    
    def open_chart(self):
        for rec in self:
            teeth_type = self.env.user.company_id.chart_type
            return {
                'type': 'ir.actions.client',
                'name': 'Dental Chart',
                'tag': 'dental_chart',
                'params': {
                    'patient_id':  rec.id or False,
                    'model':  'res.partner',
                    'type': teeth_type
                },
            }
    
    def open_child_chart(self):
        for rec in self:
            teeth_type = self.env.user.company_id.chart_type
            return {
                'type': 'ir.actions.client',
                'name': 'Dental Chart',
                'tag': 'child_dental_chart',
                'params': {
                    'patient_id':  rec.id or False,
                    'model':  'res.partner',
                    'type': teeth_type
                },
            }
    
    
    def get_patient_history(self, appt_id,child=False):
        return_list = []
        extra_history = 0
        total_operation = []
        return_list.append([])
        if appt_id:
            appt_id_brw = self.env['ksc.dental.appointment'].browse(appt_id)
            total_operation = appt_id_brw.teeth_treatment_ids.filtered(lambda self:self.child == child)
            extra_history = len(total_operation)
            for each_patient_operation in self.teeth_treatment_ids.filtered(lambda self:self.child == child):
                if each_patient_operation.description.action_perform == "missing" and each_patient_operation.appt_id.id < appt_id:
                    total_operation += each_patient_operation
        else:
            total_operation = self.teeth_treatment_ids.filtered(lambda self:self.child == child)
            extra_history = len(total_operation)
        history_count = 0
        for each_operation in total_operation:
            history_count += 1
            current_tooth_id = each_operation.teeth_id.internal_id
            if each_operation.description:
                desc_brw = self.env['product.product'].browse(
                    each_operation.description.id)
                if desc_brw.action_perform == 'missing':
                    return_list[0].append(current_tooth_id)
                self._cr.execute('select teeth from teeth_code_medical_teeth_treatment_rel where operation = %s' % (
                    each_operation.id,))
                multiple_teeth = self._cr.fetchall()
                multiple_teeth_list = [multiple_teeth_each[0]
                                       for multiple_teeth_each in multiple_teeth]
                total_multiple_teeth_list = []
                for each_multiple_teeth_list in multiple_teeth_list:
                    each_multiple_teeth_list_brw = self.env['teeth.code'].browse(
                        each_multiple_teeth_list)
                    total_multiple_teeth_list.append(
                        each_multiple_teeth_list_brw.internal_id)
                    multiple_teeth_list = total_multiple_teeth_list
                other_history = 0
                if history_count > extra_history:
                    other_history = 1
                return_list.append(
                    {   
                        'other_history': other_history,
                        'created_date': each_operation.create_date,
                        'status': each_operation.state,
                        'discount': each_operation.discount,
                        'id': each_operation.id,
                        'multiple_teeth': multiple_teeth_list,
                        'tooth_id': current_tooth_id,
                        'surface': each_operation.detail_description,
                        'desc': {
                            'name': each_operation.description.name,
                            'id': each_operation.description.id,
                            'action': each_operation.description.action_perform
                        }
                    })
        return return_list

    def get_teeth_id(self,line):
        if line['teeth_id'] not in ['all','-']:
            return int(line['teeth_id']) + 32 if line['child'] else int(line['teeth_id'])
        return False   
    
    def get_teeth_treatment_fields(self, lines, appt_id):
        vals = []
        for line in lines:
            surface = line['values'][0]['values']
            vals.append({
                'state': line['status_name'],
                'teeth_id': self.get_teeth_id(line),
                'description': int(line['values'][0]['categ_id']),
                'detail_description': " ".join(surface),
                'discount': line['discount'],
                'appt_id': appt_id and int(appt_id),
                'patient_id':self.id,
                'id': int(line['id']) if line['id'] not in ['undefined',''] else False,
                'child':line['child'],
            })
        return vals
    
    def create_teeth_treatment(self,vals):
        self.env['medical.teeth.treatment'].create(vals)

    def delete_teeth_treatment(self, ids):
        self.env['medical.teeth.treatment'].browse(ids).unlink()

    def update_teeth_treatment(self, vals):
        treatment_obj = self.env['medical.teeth.treatment']
        for val in vals:
            treatment_obj.browse(val['id']).write(val)

    def get_invoice_line_account(self, type, product):
        accounts = product.product_tmpl_id.get_product_accounts()
        if type in ('out_invoice', 'out_refund'):
            return accounts['income']
        return accounts['expense']


    # def try_create_invoice(self):
    #     lines = self.env['medical.teeth.treatment'].search(
    #         [('patient_id', '=', self.id), ('state', '=', 'in_progress'), ('invoice_id','=',None)])
    #     if lines:
    #         inv_obj = self.env['account.move']
    #         InvLine = self.env['account.move.line']
    #         invoice = inv_obj.create({
    #             # 'account_id': self.property_account_receivable_id.id,
    #             'partner_id': self.id,
    #             'move_type': 'out_invoice',
    #             'physician_id': self.env.user.partner_id.id if self.env.user.partner_id else None,
    #         })
    #         for line in lines:
    #             InvLine.create({
    #                 'product_id': line.description.id,
    #                 'account_id': self.get_invoice_line_account(invoice.move_type,line.description).id,
    #                 'move_id': invoice.id,
    #                 'product_uom_id': line.description.uom_id.id,
    #                 'name': line.description.name,
    #                 'discount': line.discount,
    #                 'price_unit': line.amount,
    #             })
    #             line.write({'invoice_id':invoice.id})
    #     return True
    
    def try_create_invoice(self):
        lines = self.env['medical.teeth.treatment'].search(
            [('patient_id', '=', self.id), ('state', '=', 'in_progress'), ('invoice_id','=',None)])
        products_data = []
        for line in lines:
            products_data.append({
                'product_id': line.description,
                'quantity': 1,
                'discount': line.discount,
                'price_unit': line.amount,
            })

        inv_data = {
            'physician_id': self.env.user.partner_id.id if self.env.user.partner_id else None,
            'appointment_id': self.id,
        }

        invoice = self.ksc_create_invoice(partner=self,product_data=products_data, inv_data=inv_data)
        lines.write({'invoice_id':invoice.id})

    def create_lines(self, treatment_lines, patient_id, appt_id,child=False):
        vals = self.get_teeth_treatment_fields(treatment_lines,appt_id)
        new_lines = list(filter(lambda dic: dic['id'] == False, vals))
        old_lines = list(filter(lambda dic: dic['id'] != False, vals))
        old_ids = [x['id'] for x in old_lines]
        teeth_treatment_ids = self.teeth_treatment_ids.filtered(lambda self:self.child == child)
        del_lines = list(filter(lambda id: id not in old_ids,teeth_treatment_ids.ids))
        if new_lines:
            self.create_teeth_treatment(new_lines)
        if old_lines:
            self.update_teeth_treatment(old_lines)
        if del_lines:
            self.delete_teeth_treatment(del_lines)
        self.try_create_invoice()
        return True
