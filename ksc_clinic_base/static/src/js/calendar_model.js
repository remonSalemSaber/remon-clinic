odoo.define('ksc_clinic_base.CalendarModel', function (require) {
    "use strict";

    var CalendarModel = require('web.CalendarModel');

    CalendarModel.include({
        load: function (params) {
            this.fieldColumn = params.fieldColumn;
            return this._super.apply(this, arguments);
        },
        _loadCalendar: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._compute_columns(self.data, self.data.data);
            });
        },
        _compute_columns: function (element, events) {
            let key = false
            let domain = []
            if (!_.isEmpty(this.mapping.company_data)) {
                const clinic_model_list = [
                    'dental.appointment',
                    'dermatology.appointment',
                    'practitioner.appointment',
                    'medicine.appointment',
                    'nose_and_ear.appointment',
                    'nutrition.appointment',
                    'obstetrics_and_gynecology.appointment',
                    'ophthalmology.appointment',
                    'orthopedic.appointment',
                    'pediatric.appointment',
                    'physiotherapy.appointment',
                    'radiology.appointment',
                    'urology.appointment',
                ]
                key = clinic_model_list.find(model => this.modelName.includes(model))
                if (!!key) {
                    key = key.replace('.appointment', '');
                    const room_ids = this.mapping.company_data[`${key}_room_ids`]
                    if (!_.isEmpty(room_ids))
                        domain = [['id', 'in', room_ids]]
                }
            }
            if (this.fieldColumn) {
                var self = this;
                var columField = this.fields[this.fieldColumn];
                if (columField) {
                    return this._rpc({
                        model: columField.relation,
                        method: 'search_read',
                        fields: ['name'],
                        domain: domain,
                    })
                    .then(function (records) {
                        if (records.length) {
                            records = _.each(records, function (r) {
                                return r.title = r.name;
                            });
                            self.data.resources = records;
                        } else {
                            self.data.resources = [{
                                id: false,
                                title: 'Unknown'
                            }];
                        }
                    });
                }
            } else {
                return Promise.resolve();
            }
        },
        _recordToCalendarEvent: function (evt) {
            var result = this._super.apply(this, arguments);
            if (this.fieldColumn) {
                var value = evt[this.fieldColumn];
                result.resourceId = _.isArray(value) ? value[0] : value;
            }
            return result;
        },
        _getFullCalendarOptions: function () {
            var result = this._super.apply(this, arguments);
            if (this.fieldColumn) {
                result.resources = [];
            }
            return result;
        },
        calendarEventToRecord: function (event) {
            var result = this._super.apply(this, arguments);
            if (event.resourceId) {
                result[this.fieldColumn] = event.resourceId;
            }
            return result;
        },
    });
});
