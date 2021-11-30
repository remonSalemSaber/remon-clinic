# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    request_id = fields.Many2one('ksc.laboratory.request', string='Lab Request', copy=False, ondelete='restrict')


class Physician(models.Model):
    _inherit = "res.partner"

    def _rec_count(self):
        rec = super(Physician, self)._rec_count()
        Labrequest = self.env['ksc.laboratory.request']
        Labresult = self.env['patient.laboratory.test']
        for record in self.with_context(active_test=False):
            record.lab_request_count = Labrequest.search_count([('physician_id', '=', record.id)])
            record.lab_result_count = Labresult.search_count([('physician_id', '=', record.id)])

    lab_request_count = fields.Integer(compute='_rec_count', string='# Lab Request')
    lab_result_count = fields.Integer(compute='_rec_count', string='# Lab Result')

    def action_lab_request(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_laboratory.hms_action_lab_test_request")
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action

    def action_lab_result(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_laboratory.action_lab_result")
        action['domain'] = [('physician_id','=',self.id)]
        action['context'] = {'default_physician_id': self.id}
        return action


class kscPatient(models.Model):
    _inherit = "res.partner"

    def _rec_count(self):
        rec = super(kscPatient, self)._rec_count()
        for rec in self:
            rec.request_count = len(rec.request_ids)
            rec.test_count = len(rec.test_ids)

    def _ksc_get_attachemnts(self):
        attachments = super(kscPatient, self)._ksc_get_attachemnts()
        attachments += self.test_ids.mapped('attachment_ids')
        return attachments

    request_ids = fields.One2many('ksc.laboratory.request', 'patient_id', string='Lab Requests')
    test_ids = fields.One2many('patient.laboratory.test', 'patient_id', string='Tests')
    request_count = fields.Integer(compute='_rec_count', string='# Lab Requests')
    test_count = fields.Integer(compute='_rec_count', string='# Lab Tests')

    def action_lab_requests(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_laboratory.hms_action_lab_test_request")
        action['domain'] = [('id','in',self.request_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action

    def action_view_test_results(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ksc_laboratory.action_lab_result")
        action['domain'] = [('id','in',self.test_ids.ids)]
        action['context'] = {'default_patient_id': self.id}
        return action

