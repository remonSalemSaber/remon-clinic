odoo.define('ksc_clinic_base.web_calendar_config', function (require) {
"use strict";

var CalendarModel = require('web.CalendarModel');
var CalendarView = require('web.CalendarView');


CalendarModel.include({
    toHHMMSS: function (sec_num) {
        var hours   = Math.floor(sec_num / 3600);
        var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
        var seconds = sec_num - (hours * 3600) - (minutes * 60);

        if (hours   < 10) {hours   = "0"+hours;}
        if (minutes < 10) {minutes = "0"+minutes;}
        if (seconds < 10) {seconds = "0"+seconds;}
        return hours+':'+minutes+':'+seconds;
    },

    _getFullCalendarOptions: function () {
        const clinic_model_list = [
            'dental',
            'dermatology',
            'practitioner',
            'medicine',
            'nose_and_ear',
            'nutrition',
            'obstetrics_and_gynecology',
            'ophthalmology',
            'orthopedic',
            'pediatric',
            'physiotherapy',
            'radiology',
            'urology',
        ]
        const key = clinic_model_list.find(model => this.modelName.includes(model))
        var result = this._super()
        if (!_.isEmpty(this.mapping.company_data)) {
            if (!!this.mapping.company_data[`${key}_calendar_weekends`])
                result['weekends'] = this.mapping.company_data[`${key}_calendar_weekends`];
            if (!!this.mapping.company_data[`${key}_calendar_weeknumber`])
                result['weekNumbers'] = this.mapping.company_data[`${key}_calendar_weeknumber`];
            if (!!this.mapping.company_data[`${key}_calendar_weekday`])
                result['firstDay'] = parseInt(this.mapping.company_data[`${key}_calendar_weekday`]);
            if (!!this.mapping.company_data[`${key}_calendar_allow_overlap`])
                result['slotEventOverlap'] = this.mapping.company_data[`${key}_calendar_allow_overlap`];
            if (!!this.mapping.company_data[`${key}_calendar_disable_dragging`])
                result['eventStartEditable'] = !this.mapping.company_data[`${key}_calendar_disable_dragging`];
            if (!!this.mapping.company_data[`${key}_calendar_disable_resizing`])
                result['eventDurationEditable'] = !this.mapping.company_data[`${key}_calendar_disable_resizing`];
            if (!!this.mapping.company_data[`${key}_calendar_snap_minutes`])
                result['snapDuration'] = this.toHHMMSS(parseInt(this.mapping.company_data[`${key}_calendar_snap_minutes`]) * 60);
            if (!!this.mapping.company_data[`${key}_calendar_slot_minutes`])
                result['slotDuration'] = this.toHHMMSS(parseInt(this.mapping.company_data[`${key}_calendar_slot_minutes`]) * 60);
            if (!!this.mapping.company_data[`${key}_calendar_min_time`])
                result['minTime'] = this.toHHMMSS(parseFloat(this.mapping.company_data[`${key}_calendar_min_time`]) * 3600.0);
            if (!!this.mapping.company_data[`${key}_calendar_max_time`])
                result['maxTime'] = this.toHHMMSS(parseFloat(this.mapping.company_data[`${key}_calendar_max_time`]) * 3600.0);
            if (!!this.mapping.company_data[`${key}_calendar_start_time`])
                result['scrollTime'] = this.toHHMMSS(parseFloat(this.mapping.company_data[`${key}_calendar_start_time`]) * 3600.0);
        }
        return result;
    },
});

CalendarView.include({
    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        var attrs = this.arch.attrs;
        if (attrs['company_data']){
            this.controllerParams.mapping['company_data'] = JSON.parse(attrs['company_data']);
            this.loadParams.mapping['company_data'] = JSON.parse(attrs['company_data']);
        }
    },
});

});
