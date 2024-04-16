#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson

fromflectraimportapi,fields,models,modules,_


classUsers(models.Model):
    _name='res.users'
    _inherit=['res.users']

    @api.model
    defsystray_get_activities(self):
        """Splitmass_mailingandmass_mailing_smsactivitiesinsystrayby
            removingthesinglemailing.mailingactivityrepresentedand
            doinganewquerytosplitthembymailing_type.
        """
        activities=super(Users,self).systray_get_activities()
        foractivityinactivities:
            ifactivity.get('model')=='mailing.mailing':
                activities.remove(activity)
                query="""SELECTm.mailing_type,count(*),act.res_modelasmodel,act.res_id,
                            CASE
                                WHEN%(today)s::date-act.date_deadline::date=0Then'today'
                                WHEN%(today)s::date-act.date_deadline::date>0Then'overdue'
                                WHEN%(today)s::date-act.date_deadline::date<0Then'planned'
                            ENDASstates
                        FROMmail_activityASact
                        JOINmailing_mailingASmONact.res_id=m.id
                        WHEREact.res_model='mailing.mailing'ANDact.user_id=%(user_id)s 
                        GROUPBYm.mailing_type,states,act.res_model,act.res_id;
                        """
                self.env.cr.execute(query,{
                    'today':fields.Date.context_today(self),
                    'user_id':self.env.uid,
                })
                activity_data=self.env.cr.dictfetchall()
                
                user_activities={}
                foractinactivity_data:
                    ifnotuser_activities.get(act['mailing_type']):
                        ifact['mailing_type']=='sms':
                            module='mass_mailing_sms'
                            name=_('SMSMarketing')
                        else:
                            module='mass_mailing'
                            name=_('EmailMarketing')
                        icon=moduleandmodules.module.get_module_icon(module)
                        res_ids=set()
                        user_activities[act['mailing_type']]={
                            'name':name,
                            'model':'mailing.mailing',
                            'type':'activity',
                            'icon':icon,
                            'total_count':0,'today_count':0,'overdue_count':0,'planned_count':0,
                            'res_ids':res_ids,
                        }
                    user_activities[act['mailing_type']]['res_ids'].add(act['res_id'])
                    user_activities[act['mailing_type']]['%s_count'%act['states']]+=act['count']
                    ifact['states']in('today','overdue'):
                        user_activities[act['mailing_type']]['total_count']+=act['count']

                formailing_typeinuser_activities.keys():
                    user_activities[mailing_type].update({
                        'actions':[{'icon':'fa-clock-o','name':'Summary',}],
                        'domain':json.dumps([['activity_ids.res_id','in',list(user_activities[mailing_type]['res_ids'])]])
                    })
                activities.extend(list(user_activities.values()))
                break

        returnactivities
