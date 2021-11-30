from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime , timedelta , date
from dateutil.relativedelta import relativedelta

class TreatmentSuggestedPlan(models.Model):
    _name = 'treatment.suggested.plan'
    _description = 'Treatment Suggested Plan'
    
    plan_id = fields.Many2one('treatment.plan')
    duration = fields.Float(required=True)
    category_id = fields.Many2one('treatment.category', required=True)


class TreatmentPlan(models.Model):
    _name = 'treatment.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'ksc.mixin']
    _description = 'Treatment Plan'
    _rec_name = 'patient_id'

    @api.model
    def _get_physician_domain(self):
        return [('id','in',self.env.company.physiotherapy_physician_ids.ids)]

    name = fields.Char(string='Treatment Plan Id', readonly=True, copy=False, tracking=True)

    patient_id = fields.Many2one('res.partner', domain="[('is_patient','=',True)]", ondelete='restrict',
        required=True, index=True,help='Patient Name', tracking=True)
    image_128 = fields.Binary(related='patient_id.image_128',string='Image', readonly=True)
    physician_id = fields.Many2one('res.partner', domain=lambda self: self._get_physician_domain(), ondelete='restrict', string='Physician', 
        index=True, help='Physician\'s Name', tracking=True)

    line_ids = fields.One2many('treatment.plan.session', 'plan_id')
    suggested_line_ids = fields.One2many('treatment.suggested.plan', 'plan_id', required=True,)

    product_id = fields.Many2one('product.product', required=True)
    invoice_id = fields.Many2one('account.move')
    date_template_id = fields.Many2one('date.template')
    start_date = fields.Date()
    number_of_session = fields.Integer(default=3)

    state = fields.Selection([
        ('draft', 'Draft'), 
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], string='State', compute='_compute_state', readonly=True, default='draft')


    @api.depends('line_ids')
    def _compute_state(self):
        for rec in self:
            states = rec.line_ids.mapped('state')
            if not states:
                rec.state = 'draft'
            elif 'in_progress' in states:
                rec.state = 'in_progress'
            elif 'in_progress' not in states and 'draft' not in states:
                rec.state = 'done'
            else:
                rec.state = 'draft'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('treatment.plan') or _('New')
        return super(TreatmentPlan,self).create(values)

    def action_create_session_by_date_template(self):
        if self.start_date and self.number_of_session and self.date_template_id:
            if self.line_ids:
                self.line_ids.unlink()
            days = self.date_template_id.day_ids.mapped("day")
            date = self.start_date
            sessiones = []
            while len(sessiones) != self.number_of_session:
                if str(date.weekday()) in days:
                    sessiones.append({
                        'plan_id':self.id,
                        'date': date,
                    })
                date += relativedelta(days=1)
            if sessiones:
                self.env['treatment.plan.session'].create(sessiones)

    def action_create_plan_session(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Session'),
            'res_model': 'treatment.plan.session',
            'view_mode': 'form',
            'view_id': self.env.ref('ksc_physiotherapy.treatment_plan_session_view_form', False).id,
            'target': 'new',
            'context':{
                'default_plan_id': self.id,
            }
        }

    def action_view_plan_session(self):
        return {
            'type': 'ir.actions.act_window',
            'name': self.name or _("Plan Sessions"),
            'res_model': 'treatment.plan.session',
            'view_mode': 'tree,form',
            'domain':[('plan_id', '=', self.id)],
            'target': 'current',
            'context':{
                'default_plan_id': self.id,
            }
        }

    def create_invoice(self):
        product_id = self.product_id
        if not product_id:
            raise UserError(_("Please Set Product Service first."))
        product_data = [{'product_id': product_id}]
        inv_data = {
            'physician_id': self.physician_id and self.physician_id.id or False,
        }
        invoice = self.ksc_create_invoice(partner=self.patient_id,product_data=product_data, inv_data=inv_data)
        self.invoice_id = invoice.id
        return self.view_invoice()

    def view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.ksc_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.patient_id.id,
        })
        return action


class TreatmentPlanSession(models.Model):
    _name = 'treatment.plan.session'
    _description = 'Treatment Plan Session'
    _order = 'date asc'
    
    @api.model
    def _get_physiotherapist_domain(self):
        return [('id','in',self.env.company.physiotherapy_physiotherapist_ids.ids)]

    name = fields.Char(string='Session Id', readonly=True, copy=False, tracking=True)
    duration = fields.Float(compute='_compute_duration', store=True)
    line_ids = fields.One2many('treatment.plan.session.line', 'session_id')
    plan_id = fields.Many2one('treatment.plan')
    physiotherapist_id = fields.Many2one('res.partner', domain=lambda self: self._get_physiotherapist_domain(), ondelete='restrict', string='Physician', 
        index=True, help='Physiotherapist\'s Name', tracking=True)
    date = fields.Date()
    slot_time_id = fields.Many2one('slot.time')
    slot_time_ids = fields.Many2many('slot.time', compute='_compute_slot_time_ids')
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')], string='State', readonly=True, default='draft')


    @api.constrains('duration')
    def _validate_duration(self):
        for record in self:
            if record.duration > 1:
                raise ValidationError(_("A duration must be less than 01:00 "))

    def action_in_progress(self):
        self.state = 'in_progress'
    
    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    @api.depends('physiotherapist_id','date','slot_time_id')
    def _compute_slot_time_ids(self):
        for rec in self:
            rec.slot_time_ids = []
            physiotherapist_id = rec.physiotherapist_id and rec.physiotherapist_id.id or False
            date         = rec.date
            if physiotherapist_id and date:
                session_ids = self.search([('physiotherapist_id','=',physiotherapist_id),('date','=',date)])
                if session_ids:
                    slot_time_ids = session_ids.mapped('slot_time_id')
                    if slot_time_ids:
                        rec.slot_time_ids = slot_time_ids.ids

    @api.depends('line_ids')
    def _compute_duration(self):
        for rec in self:
            rec.duration = sum(rec.line_ids.mapped('treatment_ids.duration'))

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('treatment.plan.session') or _('New')
        return super(TreatmentPlanSession,self).create(values)


class TreatmentPlanSessionLine(models.Model):
    _name = 'treatment.plan.session.line'
    _description = 'Treatment Plan Session Line'
    _rec_name = 'category_id'

    session_id = fields.Many2one('treatment.plan.session')
    category_id = fields.Many2one('treatment.category', required=True)
    treatment_ids = fields.Many2many('treatment.treatment',  required=True) 

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.treatment_ids = None

class TreatmentTreatment(models.Model):
    _name = 'treatment.treatment'
    _description = 'Treatment Treatment'
    
    name = fields.Char(required=True)
    duration = fields.Float(required=True)
    category_id = fields.Many2one('treatment.category', required=True)


class TreatmentCategory(models.Model):
    _name = 'treatment.category'
    _description = 'Treatment Category'
    
    name = fields.Char(required=True)
    treatment_ids = fields.One2many('treatment.treatment', 'category_id')


class SlotTime(models.Model):
    _name = 'slot.time'
    _description = 'Slot Time'
    
    name = fields.Char(required=True)


class CustomWeekdays(models.Model):
    _name = 'custom.weekdays'

    def name_get(self):
        result = []
        for rec in self:
            name = dict(self._fields['day'].selection).get(rec.day)
            result.append((rec.id, name))
        return result

    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], required=True)


class DateTemplate(models.Model):
    _name = 'date.template'
    _description = 'Date Template'
    
    name = fields.Char(required=True)
    day_ids = fields.Many2many('custom.weekdays', string='Days', required=True)
    