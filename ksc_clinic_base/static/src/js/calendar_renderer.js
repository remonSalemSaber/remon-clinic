odoo.define('ksc_clinic_base.CalendarRenderer', function (require) {
    "use strict";

    var CalendarRenderer = require('web.CalendarRenderer');
    // var core = require('web.core');
    // var qweb = core.qweb;
    // var _t = core._t;
    CalendarRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.column = params.column;
        },
        _getFullCalendarOptions: function () {
            var self = this;
            var fcOptions = this._super.apply(this, arguments);
            if (this.column) {
                fcOptions.plugins.push('resourceTimeGrid');
                fcOptions.resources = (info, resourceCB) => {
                    resourceCB(self.state.resources);
                };
                fcOptions.eventDrop = function (eventDropInfo) {
                    var event = self._convertEventToFC3Event(eventDropInfo.event);
                    if (eventDropInfo.newResource && eventDropInfo.newResource.id) {
                        event.resourceId = eventDropInfo.newResource.id;
                    }
                    self.trigger_up('dropRecord', event);
                };
                fcOptions.select = function (selectionInfo) {
                    // Clicking on the view, dispose any visible popover. Otherwise create a new event.
                    if (self.$('.o_cw_popover').length) {
                        self._unselectEvent();
                    }
                    var data = {start: selectionInfo.start, end: selectionInfo.end, allDay: selectionInfo.allDay};
                    if (self.state.context.default_name) {
                        data.title = self.state.context.default_name;
                    }
                    if (selectionInfo.resource && selectionInfo.resource.id) {
                        data.resourceID = selectionInfo.resource.id;
                    }
                    self.trigger_up('openCreate', self._convertEventToFC3Event(data));
                    if (self.state.scale === 'year') {
                        self.calendar.view.unselect();
                    } else {
                        self.calendar.unselect();
                    }
                };
                fcOptions.refetchResourcesOnNavigate = true;
            }
            return fcOptions;
        },
        _convertEventToFC3Event: function (fc4Event) {
            var event = this._super.apply(this, arguments);
            if (fc4Event.resourceID) {
                event.resourceID = fc4Event.resourceID;
            }
            return event;
        }
    });
});
