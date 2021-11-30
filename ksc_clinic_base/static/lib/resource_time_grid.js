/*!
FullCalendar Resource Time Grid Plugin v4.4.0
Docs & License: https://fullcalendar.io/scheduler
(c) 2019 Adam Shaw
*/
!function(e, r) {
    "object" == typeof exports && "undefined" != typeof module ? r(exports, require("@fullcalendar/core"), require("@fullcalendar/resource-common"), require("@fullcalendar/timegrid"), require("@fullcalendar/resource-daygrid")) : "function" == typeof define && define.amd ? define(["exports", "@fullcalendar/core", "@fullcalendar/resource-common", "@fullcalendar/timegrid", "@fullcalendar/resource-daygrid"], r) : r((e = e || self).FullCalendarResourceTimeGrid = {}, e.FullCalendar, e.FullCalendarResourceCommon, e.FullCalendarTimeGrid, e.FullCalendarResourceDayGrid)
}(this, function(e, r, t, i, o) {
    "use strict";
    var s = "default"in t ? t.default : t
      , n = "default"in i ? i.default : i
      , a = function(e, r) {
        return (a = Object.setPrototypeOf || {
            __proto__: []
        }instanceof Array && function(e, r) {
            e.__proto__ = r
        }
        || function(e, r) {
            for (var t in r)
                r.hasOwnProperty(t) && (e[t] = r[t])
        }
        )(e, r)
    };
    function l(e, r) {
        function t() {
            this.constructor = e
        }
        a(e, r),
        e.prototype = null === r ? Object.create(r) : (t.prototype = r.prototype,
        new t)
    }
    var c = function() {
        return (c = Object.assign || function(e) {
            for (var r, t = 1, i = arguments.length; t < i; t++)
                for (var o in r = arguments[t])
                    Object.prototype.hasOwnProperty.call(r, o) && (e[o] = r[o]);
            return e
        }
        ).apply(this, arguments)
    }
      , d = function(e) {
        function o(o) {
            var s = e.call(this, o.el) || this;
            return s.buildDayRanges = r.memoize(i.buildDayRanges),
            s.splitter = new t.VResourceSplitter,
            s.slicers = {},
            s.joiner = new u,
            s.timeGrid = o,
            s
        }
        return l(o, e),
        o.prototype.firstContext = function(e) {
            e.calendar.registerInteractiveComponent(this, {
                el: this.timeGrid.el
            })
        }
        ,
        o.prototype.destroy = function() {
            this.context.calendar.unregisterInteractiveComponent(this)
        }
        ,
        o.prototype.render = function(e, t) {
            var o = this
              , s = this.timeGrid
              , n = t.dateEnv
              , a = e.dateProfile
              , l = e.resourceDayTable
              , d = this.dayRanges = this.buildDayRanges(l.dayTable, a, n)
              , u = this.splitter.splitProps(e);
            this.slicers = r.mapHash(u, function(e, r) {
                return o.slicers[r] || new i.TimeGridSlicer
            });
            var p = r.mapHash(this.slicers, function(e, r) {
                return e.sliceProps(u[r], a, null, t.calendar, s, d)
            });
            s.allowAcrossResources = 1 === d.length,
            s.receiveProps(c({}, this.joiner.joinProps(p, l), {
                dateProfile: a,
                cells: l.cells[0]
            }), t)
        }
        ,
        o.prototype.renderNowIndicator = function(e) {
            var r = this.timeGrid
              , t = this.props.resourceDayTable
              , i = this.slicers[""].sliceNowDate(e, r, this.dayRanges)
              , o = this.joiner.expandSegs(t, i);
            r.renderNowIndicator(o, e)
        }
        ,
        o.prototype.buildPositionCaches = function() {
            this.timeGrid.buildPositionCaches()
        }
        ,
        o.prototype.queryHit = function(e, r) {
            var t = this.timeGrid.positionToHit(e, r);
            if (t)
                return {
                    component: this.timeGrid,
                    dateSpan: {
                        range: t.dateSpan.range,
                        allDay: t.dateSpan.allDay,
                        resourceId: this.props.resourceDayTable.cells[0][t.col].resource.id
                    },
                    dayEl: t.dayEl,
                    rect: {
                        left: t.relativeRect.left,
                        right: t.relativeRect.right,
                        top: t.relativeRect.top,
                        bottom: t.relativeRect.bottom
                    },
                    layer: 0
                }
        }
        ,
        o
    }(r.DateComponent)
      , u = function(e) {
        function r() {
            return null !== e && e.apply(this, arguments) || this
        }
        return l(r, e),
        r.prototype.transformSeg = function(e, r, t) {
            return [c({}, e, {
                col: r.computeCol(e.col, t)
            })]
        }
        ,
        r
    }(t.VResourceJoiner)
      , p = function(e) {
        function i() {
            var i = null !== e && e.apply(this, arguments) || this;
            return i.processOptions = r.memoize(i._processOptions),
            i.flattenResources = r.memoize(t.flattenResources),
            i.buildResourceDayTable = r.memoize(f),
            i
        }
        return l(i, e),
        i.prototype._processOptions = function(e) {
            this.resourceOrderSpecs = r.parseFieldSpecs(e.resourceOrder)
        }
        ,
        i.prototype.render = function(r, t) {
            e.prototype.render.call(this, r, t);
            var i = t.options
              , o = t.nextDayThreshold;
            this.processOptions(i);
            var s = this.splitter.splitProps(r)
              , n = this.flattenResources(r.resourceStore, this.resourceOrderSpecs)
              , a = this.buildResourceDayTable(r.dateProfile, r.dateProfileGenerator, n, i.datesAboveResources);
            this.header && this.header.receiveProps({
                resources: n,
                dates: a.dayTable.headerDates,
                dateProfile: r.dateProfile,
                datesRepDistinctDays: !0,
                renderIntroHtml: this.renderHeadIntroHtml
            }, t),
            this.resourceTimeGrid.receiveProps(c({}, s.timed, {
                dateProfile: r.dateProfile,
                resourceDayTable: a
            }), t),
            this.resourceDayGrid && this.resourceDayGrid.receiveProps(c({}, s.allDay, {
                dateProfile: r.dateProfile,
                resourceDayTable: a,
                isRigid: !1,
                nextDayThreshold: o
            }), t),
            this.startNowIndicator(r.dateProfile, r.dateProfileGenerator)
        }
        ,
        i.prototype._renderSkeleton = function(r) {
            e.prototype._renderSkeleton.call(this, r),
            r.options.columnHeader && (this.header = new t.ResourceDayHeader(this.el.querySelector(".fc-head-container"))),
            this.resourceTimeGrid = new d(this.timeGrid),
            this.dayGrid && (this.resourceDayGrid = new o.ResourceDayGrid(this.dayGrid))
        }
        ,
        i.prototype._unrenderSkeleton = function() {
            e.prototype._unrenderSkeleton.call(this),
            this.header && this.header.destroy(),
            this.resourceTimeGrid.destroy(),
            this.resourceDayGrid && this.resourceDayGrid.destroy()
        }
        ,
        i.prototype.renderNowIndicator = function(e) {
            this.resourceTimeGrid.renderNowIndicator(e)
        }
        ,
        i.needsResourceData = !0,
        i
    }(i.AbstractTimeGridView);
    function f(e, r, o, s) {
        var n = i.buildDayTable(e, r);
        return s ? new t.DayResourceTable(n,o) : new t.ResourceDayTable(n,o)
    }
    var h = r.createPlugin({
        deps: [s, n],
        defaultView: "resourceTimeGridDay",
        views: {
            resourceTimeGrid: {
                class: p,
                allDaySlot: !0,
                slotDuration: "00:30:00",
                slotEventOverlap: !0
            },
            resourceTimeGridDay: {
                type: "resourceTimeGrid",
                duration: {
                    days: 1
                }
            },
            resourceTimeGridWeek: {
                type: "resourceTimeGrid",
                duration: {
                    weeks: 1
                }
            }
        }
    });
    e.ResourceTimeGrid = d,
    e.ResourceTimeGridView = p,
    e.default = h,
    Object.defineProperty(e, "__esModule", {
        value: !0
    })
});
