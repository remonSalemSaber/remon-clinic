# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError


class kscPhysiotherapyExercise(models.Model):
    _name = "physiotherapy.exercise"
    _description = "Exercise Of Physiotherapy"
    
    name = fields.Char('Exercise Name')
    exercise_group_id = fields.Many2one('physiotherapy.exercise.group','Exercise group')


class kscPhysiotherapyExerciseGroup(models.Model):
    _name = "physiotherapy.exercise.group"
    _description = "Exercise group Of Physiotherapy"

    name = fields.Char(string='Name', required=True, help="Exercise Group Name like Knee,Ankle...")
    description = fields.Text(string='Description')
    product_id = fields.Many2one('product.product',string='Service', required=True)
    exercise_ids = fields.One2many('physiotherapy.exercise','exercise_group_id',string='Exercise')
    duration = fields.Float()
    _sql_constraints = [('code_uniq', 'unique (name)', 'Physiotherapy Group Name must be unique')]


class kscPhysiotherapyExerciseGroupLines(models.Model):
    _name = "physiotherapy.exercise.group.lines"
    _description = "Physiotherapy Exercise Group Lines"
    
    group_id = fields.Many2one('physiotherapy.exercise.group','Exercise group')
    physiotherapy_id = fields.Many2one('ksc.physiotherapy','Physiotherapy')
    exercise_ids = fields.Many2many('physiotherapy.exercise','rel_exercise_group_exercise_line','exercise_id','exercise_group_id',string='Exercise')
    price = fields.Float(related='group_id.product_id.list_price', string='Price',store=True)

    @api.onchange('group_id')
    def onchange_group_id(self):
        self.exercise_ids = self.group_id.exercise_ids

#master Template data
class kscPhysiotherapyNoteTemplate(models.Model):
    _name = "ksc.physiotherapy.note.template"
    _description = "Physiotherapy Note"

    name = fields.Char("Name")
    right_val = fields.Char("Strength Right")
    left_val = fields.Char("Strength Left")
    sensory_val = fields.Char("Sensory")
    note_type = fields.Selection([('lower','Lower'),('upper','Upper'),('hand','Hand')],string="Note Type",required=True)


class kscPhysiotherapyNote(models.Model):
    _name = "ksc.physiotherapy.note"
    _description = "Physiotherapy Note"
    # _order = sequence

    # sequence = fields.Integer(string="Sequence",default=10)
    name = fields.Char("Name")
    right_val = fields.Char("Strength Right")
    left_val = fields.Char("Strength Left")
    sensory_val = fields.Char("Sensory")
    note_type = fields.Selection([('lower','Lower'),('upper','Upper'),('hand','Hand')],string="Note Type",required=True)
    hand_data_id = fields.Many2one('ksc.physiotherapy','Note')
    lower_data_id = fields.Many2one('ksc.physiotherapy','Lower Note')
    upper_data_id = fields.Many2one('ksc.physiotherapy','Upper Note')


#master Template data
class kscPhysiotherapySelectionNoteTemplate(models.Model):
    _name = "ksc.physiotherapy.selection.note.template"
    _description = "Physiotherapy Selection Note"
    # _order = sequence

    # sequence = fields.Integer(string="Sequence",default=10)
    name = fields.Char("Reflexes")
    right_val = fields.Selection([('normal', 'Normal'),('other', 'Other'),('positive', 'Positive'),('negative', 'Negative')],string="STRENGTH RIGHT",default='normal')
    left_val = fields.Selection([('normal', 'Normal'),('other', 'Other'),('positive', 'Positive'),('negative', 'Negative')],string="STRENGTH LEFT",default='normal')
    selnote_type = fields.Selection([('lower','Lower'),('upper','Upper'),('hand','Hand')],string="Note Type")


#master Template data
class kscPhysiotherapySelectionNote(models.Model):
    _name = "ksc.physiotherapy.selection.note"
    _description = "Physiotherapy Selection Note"
    # _order = sequence

    # sequence = fields.Integer(string="Sequence",default=10)
    name = fields.Char("Reflexes")
    right_val = fields.Selection([('normal', 'Normal'),('other', 'Other'),('positive', 'Positive'),('negative', 'Negative')],string="STRENGTH RIGHT",default='normal')
    left_val = fields.Selection([('normal', 'Normal'),('other', 'Other'),('positive', 'Positive'),('negative', 'Negative')],string="STRENGTH LEFT",default='normal')
    selnote_type = fields.Selection([('lower','Lower'),('upper','Upper'),('hand','Hand')],string="Note Type")
    lower_selectdata_id = fields.Many2one('ksc.physiotherapy','Lower SNote')
    upper_selectdata_id = fields.Many2one('ksc.physiotherapy','Upper SNote')


class kscPhysiotherapy(models.Model):
    _name = "ksc.physiotherapy"
    _description = "Physiotherapy"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'ksc.mixin']

    @api.model
    def _get_physician_domain(self):
        return [('id','in',self.env.company.physiotherapy_physician_ids.ids)]

    def _get_years_sex(self):
        for rec in self:
            age = ''
            if rec.patient_id.birthday:
                b_date = rec.patient_id.birthday
                delta = relativedelta(datetime.now(), b_date)
                age = _("%s year / %s") % (delta.years, 'Male' if rec.patient_id.gender=='male' else 'Female')
            rec.years_sex = age

    @api.depends('patient_id')
    def _get_physiotherapy_history(self):
        for rec in self:
            history = "<table style='border-bottom: 1px solid black' class='table table-condensed'>"
            for line in self.search([('patient_id', '=', rec.patient_id.id)],order='date desc', limit=10):
                history += _("<tr><td><b>Date:</b></td><td>%s</td></tr>")%(line.date)
                history += _("<tr><td><b>Exercise:</b></td>")
                history += _("<td><table class='table table-condensed'>")
                history += _("<strong><th>Group Name</th> <th>Price</th> <th>Exercise</th></strong>")
                for line in line.grp_exercise_ids:
                    history += _("<tr><td>%s</td><td>%s</td><td>%s</td></tr>")%(line.group_id.name, line.price, ','.join([ex.name for ex in line.exercise_ids]))
                history += _("</table></td></tr>")
            rec.physiotherapy_history = history


    @api.depends('patient_id')
    def _get_rec_total(self):
        for rec in self:
            rec.visit_count = self.search_count([('patient_id', '=', rec.patient_id.id)])

    STATES = {'done': [('readonly', True)], 'cancel': [('readonly', True)]}

    name = fields.Char('Name', readonly=True)
    patient_id = fields.Many2one('res.partner', domain="[('is_patient','=',True)]", ondelete='restrict',
        required=True, index=True,help='Patient Name', states=STATES, tracking=True)
    physician_id = fields.Many2one('res.partner', domain=lambda self: self._get_physician_domain(), ondelete='restrict', string='Physician', 
        index=True, help='Physician\'s Name', states=STATES, tracking=True)
    physiotherapist_id = fields.Many2one('res.partner', domain=lambda self: self._get_physician_domain(), ondelete='restrict',
        index=True, states=STATES, tracking=True)
    years_sex = fields.Char(compute="_get_years_sex", string='Age / Sex', states=STATES)
    code =  fields.Char(related='patient_id.code', string='Reg. No.', readonly=True)
    image_128 = fields.Binary(related='patient_id.image_128',string='Image', readonly=True)
    age =  fields.Integer(related='patient_id.age', string='Age', readonly=True)
    date = fields.Datetime(string='Physiotherapy Date', default=fields.Datetime.now, states=STATES) 
    end_date = fields.Datetime(string='End Date', default=fields.Datetime.now, states=STATES) 
    grp_exercise_ids = fields.One2many('physiotherapy.exercise.group.lines','physiotherapy_id',
        string='Exercise group', states=STATES)
    no_invoice =  fields.Boolean(string="Invoice Exempt", states=STATES)
    state = fields.Selection([('draft', 'Draft'), 
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('to_invoice', 'To Invoice'),], string='State', readonly=True, default='draft')
    invoice_id = fields.Many2one('account.move', string='Invoice'
        , states=STATES)
    visit_count = fields.Integer(compute="_get_rec_total", store=True, string='Past Visit', readonly=True)
    gender = fields.Selection(related="patient_id.gender", string="Gender", readonly=True)

    physiotherapy_history = fields.Html(compute='_get_physiotherapy_history', store=True, string='Physiotherapy History', readonly=True)

    # Physiotherapy Orientation note
    date_orientation = fields.Datetime(string='Orientation Date & Time', default=fields.Datetime.now, states=STATES)
    by_orientation = fields.Char(string="By", states=STATES)
    interested =  fields.Selection([('yes', 'Yes'),('no', 'No')],string="Interested",default='yes', states=STATES)
    interested_side = fields.Selection([('left', 'Lt'),('right', 'Rt'),('bilat','Bilat')],string="Side",default='right', states=STATES)
    joint_type = fields.Selection([('all_poly', 'All Poly')],string="Joint Type",default='all_poly', states=STATES)
    when_orientation = fields.Char(string="When", states=STATES)
    problem_areas = fields.Char(string="Problem Areas", states=STATES)
    diagnosed_first = fields.Selection([('yes', 'Yes'),('no', 'No')],string="Diagnosed First",default='yes', states=STATES)

    # Physiotherapy note
    date_lower_limb = fields.Datetime(string='Lower Limb Date & Time', default=fields.Datetime.now, states=STATES)
    date_upper_limb = fields.Datetime(string='Upper Limb Date & Time', default=fields.Datetime.now, states=STATES)
    date_hand = fields.Datetime(string='Hand Date & Time', default=fields.Datetime.now, states=STATES)
    
    hand_data_ids =  fields.One2many('ksc.physiotherapy.note','hand_data_id',string='Hand Note', states=STATES)
    lower_data_ids =  fields.One2many('ksc.physiotherapy.note','lower_data_id',string='Lower Note', states=STATES)
    upper_data_ids =  fields.One2many('ksc.physiotherapy.note','upper_data_id',string='Upper Note', states=STATES)
    lower_seldata_ids =  fields.One2many('ksc.physiotherapy.selection.note','lower_selectdata_id',string='Lower Selection Note', states=STATES)
    upper_seldata_ids =  fields.One2many('ksc.physiotherapy.selection.note','upper_selectdata_id',string='Upper Selection Note', states=STATES)

    appointment_id = fields.Many2one('ksc.physiotherapy.appointment', 'Appointment', states=STATES)
    notes = fields.Text(string="Notes", states=STATES)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Institution',default=lambda self: self.env.user.company_id.id)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, related invoice will be affected.")


    @api.onchange('grp_exercise_ids','date')
    def _onchange_grp_exercise_ids(self):
        duration = sum(self.grp_exercise_ids.mapped('group_id.duration'))
        self.end_date = self.date + timedelta(hours=duration)

    def action_accept(self):
        self.state = 'accepted'

    def action_cancel(self):
        self.state = 'cancel'

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_done(self):
        if self.no_invoice or self.invoice_id:
            self.state = 'done'
        else:
            self.state ='to_invoice'

    def create_invoice(self):
        product_data = []
        for line in self.grp_exercise_ids:
            product_data.append({
                'name': line.group_id.product_id.name,
                'price_unit': line.price or line.group_id.product_id.list_price,
                'product_id': line.group_id.product_id,
            })

        pricelist_context = {}
        if self.pricelist_id:
            pricelist_context = {'ksc_pricelist_id': self.pricelist_id.id}
        invoice = self.with_context(pricelist_context).ksc_create_invoice(partner=self.patient_id, product_data=product_data)
        self.invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.state = 'done'

    def view_invoice(self):
        invoices = self.mapped('invoice_id')
        action = self.ksc_action_view_invoice(invoices)
        return action

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('physiotherapy.code')
        return super(kscPhysiotherapy, self).create(values)
    
    def unlink(self):
        for data in self:
            if data.state != 'draft':
                raise UserError(_('You can not delete record not in draft state'))
        return super(kscPhysiotherapy, self).unlink()

    @api.model
    def default_get(self, fields):
        res = super(kscPhysiotherapy, self).default_get(fields)
        vals = []
        hand_templates = self.env['ksc.physiotherapy.note.template'].search([('note_type','=','hand')])
        for line in hand_templates:
            vals.append((0,0,{
                'name':line.name,
                'right_val': line.right_val,
                'left_val' : line.left_val,
                'note_type': line.note_type,
                'sensory_val': line.sensory_val
            }))
        res.update({'hand_data_ids': vals})

        vals = []
        lower_templates = self.env['ksc.physiotherapy.note.template'].search([('note_type','=','lower')])
        for line in lower_templates:
            vals.append((0,0,{
                'name':line.name,
                'right_val': line.right_val,
                'left_val' : line.left_val,
                'note_type' : line.note_type,
                'sensory_val': line.sensory_val
            }))
        res.update({'lower_data_ids': vals})
        vals = []

        upper_templates = self.env['ksc.physiotherapy.note.template'].search([('note_type','=','upper')])
        for line in upper_templates:
            vals.append((0,0,{
                'name':line.name,
                'right_val': line.right_val,
                'left_val' : line.left_val,
                'note_type' : line.note_type,
                'sensory_val': line.sensory_val
            }))
        res.update({'upper_data_ids': vals})

        vals = []
        lower_selection_templates = self.env['ksc.physiotherapy.selection.note.template'].search([('selnote_type','=','lower')])
        for line in lower_selection_templates:
            vals.append((0,0,{
                'name':line.name,
                'right_val': line.right_val,
                'left_val' : line.left_val,
                'selnote_type': line.selnote_type
            }))
        res.update({'lower_seldata_ids': vals})

        vals = []
        upper_selection_templates = self.env['ksc.physiotherapy.selection.note.template'].search([('selnote_type','=','upper')])
        for line in upper_selection_templates:
            vals.append((0,0,{
                'name':line.name,
                'right_val': line.right_val,
                'left_val' : line.left_val,
                'selnote_type': line.selnote_type
            }))
        res.update({'upper_seldata_ids': vals})

        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: