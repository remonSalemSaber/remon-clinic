odoo.define('ksc_clinic_base.CalendarView', function (require) {
    "use strict";

    const scalesInfo = {
        day: 'resourceTimeGridDay',
        week: 'resourceTimeGridWeek',
        month: 'dayGridMonth',
        year: 'dayGridYear',
    };
    
    var CalendarView = require('web.CalendarView');
    CalendarView.prototype.jsLibs.push(
        '/ksc_clinic_base/static/lib/resources_common.js',
        '/ksc_clinic_base/static/lib/resource_day_grid.js',
        '/ksc_clinic_base/static/lib/resource_time_grid.js'
        );
    CalendarView.include({
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
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
            let key = clinic_model_list.find(model => params.modelName.includes(model))
            if (!!key) {
                key = key.replace('.appointment', '');
                const column = 'room_id'
                var arch = this.arch;
                let scales;
                const allowedScales = Object.keys(scalesInfo);
                if (arch.attrs.scales) {
                    scales = arch.attrs.scales.split(',')
                        .filter(x => allowedScales.includes(x));
                } else {
                    scales = allowedScales;
                }
                this.controllerParams.scales = scales;
                this.rendererParams.scalesInfo = scalesInfo;
                this.loadParams.scalesInfo = scalesInfo;
                this.rendererParams.column = true;

                var fieldNames = this.loadParams.fieldNames;
                if (column) {
                    var fieldName = column;
                    fieldNames.push(fieldName);
                }
                this.loadParams.fieldColumn = column;
                this.loadParams.fieldNames = _.uniq(fieldNames);
            }
           
        },
    });
});
