#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classAlarm(models.Model):
    _name='calendar.alarm'
    _description='EventAlarm'

    @api.depends('interval','duration')
    def_compute_duration_minutes(self):
        foralarminself:
            ifalarm.interval=="minutes":
                alarm.duration_minutes=alarm.duration
            elifalarm.interval=="hours":
                alarm.duration_minutes=alarm.duration*60
            elifalarm.interval=="days":
                alarm.duration_minutes=alarm.duration*60*24
            else:
                alarm.duration_minutes=0

    _interval_selection={'minutes':'Minutes','hours':'Hours','days':'Days'}

    name=fields.Char('Name',translate=True,required=True)
    alarm_type=fields.Selection(
        [('notification','Notification'),('email','Email')],
        string='Type',required=True,default='email')
    duration=fields.Integer('RemindBefore',required=True,default=1)
    interval=fields.Selection(
        list(_interval_selection.items()),'Unit',required=True,default='hours')
    duration_minutes=fields.Integer(
        'Durationinminutes',store=True,
        search='_search_duration_minutes',compute='_compute_duration_minutes',
        help="Durationinminutes")

    def_search_duration_minutes(self,operator,value):
        return[
            '|','|',
            '&',('interval','=','minutes'),('duration',operator,value),
            '&',('interval','=','hours'),('duration',operator,value/60),
            '&',('interval','=','days'),('duration',operator,value/60/24),
        ]

    @api.onchange('duration','interval','alarm_type')
    def_onchange_duration_interval(self):
        display_interval=self._interval_selection.get(self.interval,'')
        display_alarm_type={
            key:valueforkey,valueinself._fields['alarm_type']._description_selection(self.env)
        }[self.alarm_type]
        self.name="%s-%s%s"%(display_alarm_type,self.duration,display_interval)

    def_update_cron(self):
        try:
            cron=self.env['ir.model.data'].sudo().get_object('calendar','ir_cron_scheduler_alarm')
        exceptValueError:
            returnFalse
        returncron.toggle(model=self._name,domain=[('alarm_type','=','email')])

    @api.model
    defcreate(self,values):
        result=super(Alarm,self).create(values)
        self._update_cron()
        returnresult

    defwrite(self,values):
        result=super(Alarm,self).write(values)
        self._update_cron()
        returnresult

    defunlink(self):
        result=super(Alarm,self).unlink()
        self._update_cron()
        returnresult
