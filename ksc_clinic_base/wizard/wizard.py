from odoo import _, api, fields, models


class KscWizardAppointmentFollowup(models.TransientModel):
    _name = 'ksc.wizard.appointment.followup'
    _description = 'Ksc Wizard Appointment Followup'
    
    start_date = fields.Datetime(string='Start Date', copy=False)
    end_date = fields.Datetime(string='End Date', copy=False)

    def action_create_followup(self):
        model = self._context.get('model','ksc.appointment')
        rec_id = self._context.get('rec_id')
        appointment = self.env[model].browse(rec_id)
        copy_appointment = appointment.copy({
            'start_date':self.start_date,
            'end_date':self.end_date,
            'follow_up': True,
        })