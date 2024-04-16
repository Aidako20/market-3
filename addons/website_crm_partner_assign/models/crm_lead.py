#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importrandom

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportAccessDenied,AccessError,UserError
fromflectra.toolsimporthtml_escape



classCrmLead(models.Model):
    _inherit="crm.lead"

    partner_latitude=fields.Float('GeoLatitude',digits=(16,5))
    partner_longitude=fields.Float('GeoLongitude',digits=(16,5))
    partner_assigned_id=fields.Many2one('res.partner','AssignedPartner',tracking=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]",help="Partnerthiscasehasbeenforwarded/assignedto.",index=True)
    partner_declined_ids=fields.Many2many(
        'res.partner',
        'crm_lead_declined_partner',
        'lead_id',
        'partner_id',
        string='Partnernotinterested')
    date_partner_assign=fields.Date(
        'PartnerAssignmentDate',compute='_compute_date_partner_assign',
        copy=True,readonly=False,store=True,
        help="Lastdatethiscasewasforwarded/assignedtoapartner")

    def_merge_data(self,fields):
        fields+=['partner_latitude','partner_longitude','partner_assigned_id','date_partner_assign']
        returnsuper(CrmLead,self)._merge_data(fields)

    @api.depends("partner_assigned_id")
    def_compute_date_partner_assign(self):
        forleadinself:
            ifnotlead.partner_assigned_id:
                lead.date_partner_assign=False
            else:
                lead.date_partner_assign=fields.Date.context_today(lead)

    defassign_salesman_of_assigned_partner(self):
        salesmans_leads={}
        forleadinself:
            iflead.activeandlead.probability<100:
                iflead.partner_assigned_idandlead.partner_assigned_id.user_id!=lead.user_id:
                    salesmans_leads.setdefault(lead.partner_assigned_id.user_id.id,[]).append(lead.id)

        forsalesman_id,leads_idsinsalesmans_leads.items():
            leads=self.browse(leads_ids)
            leads.write({'user_id':salesman_id})

    defaction_assign_partner(self):
        returnself.assign_partner(partner_id=False)

    defassign_partner(self,partner_id=False):
        partner_dict={}
        res=False
        ifnotpartner_id:
            partner_dict=self.search_geo_partner()
        forleadinself:
            ifnotpartner_id:
                partner_id=partner_dict.get(lead.id,False)
            ifnotpartner_id:
                tag_to_add=self.env.ref('website_crm_partner_assign.tag_portal_lead_partner_unavailable',False)
                iftag_to_add:
                    lead.write({'tag_ids':[(4,tag_to_add.id,False)]})
                continue
            lead.assign_geo_localize(lead.partner_latitude,lead.partner_longitude)
            partner=self.env['res.partner'].browse(partner_id)
            ifpartner.user_id:
                lead.handle_salesmen_assignment(partner.user_id.ids,team_id=partner.team_id.id)
            lead.write({'partner_assigned_id':partner_id})
        returnres

    defassign_geo_localize(self,latitude=False,longitude=False):
        iflatitudeandlongitude:
            self.write({
                'partner_latitude':latitude,
                'partner_longitude':longitude
            })
            returnTrue
        #Don'tpasscontexttobrowse()!Weneedcountrynameinenglishbelow
        forleadinself:
            iflead.partner_latitudeandlead.partner_longitude:
                continue
            iflead.country_id:
                result=self.env['res.partner']._geo_localize(
                    lead.street,lead.zip,lead.city,
                    lead.state_id.name,lead.country_id.name
                )
                ifresult:
                    lead.write({
                        'partner_latitude':result[0],
                        'partner_longitude':result[1]
                    })
        returnTrue

    defsearch_geo_partner(self):
        Partner=self.env['res.partner']
        res_partner_ids={}
        self.assign_geo_localize()
        forleadinself:
            partner_ids=[]
            ifnotlead.country_id:
                continue
            latitude=lead.partner_latitude
            longitude=lead.partner_longitude
            iflatitudeandlongitude:
                #1.firstway:inthesamecountry,smallarea
                partner_ids=Partner.search([
                    ('partner_weight','>',0),
                    ('partner_latitude','>',latitude-2),('partner_latitude','<',latitude+2),
                    ('partner_longitude','>',longitude-1.5),('partner_longitude','<',longitude+1.5),
                    ('country_id','=',lead.country_id.id),
                    ('id','notin',lead.partner_declined_ids.mapped('id')),
                ])

                #2.secondway:inthesamecountry,bigarea
                ifnotpartner_ids:
                    partner_ids=Partner.search([
                        ('partner_weight','>',0),
                        ('partner_latitude','>',latitude-4),('partner_latitude','<',latitude+4),
                        ('partner_longitude','>',longitude-3),('partner_longitude','<',longitude+3),
                        ('country_id','=',lead.country_id.id),
                        ('id','notin',lead.partner_declined_ids.mapped('id')),
                    ])

                #3.thirdway:inthesamecountry,extralargearea
                ifnotpartner_ids:
                    partner_ids=Partner.search([
                        ('partner_weight','>',0),
                        ('partner_latitude','>',latitude-8),('partner_latitude','<',latitude+8),
                        ('partner_longitude','>',longitude-8),('partner_longitude','<',longitude+8),
                        ('country_id','=',lead.country_id.id),
                        ('id','notin',lead.partner_declined_ids.mapped('id')),
                    ])

                #5.fifthway:anywhereinsamecountry
                ifnotpartner_ids:
                    #stillhaven'tfoundany,let'stakeallpartnersinthecountry!
                    partner_ids=Partner.search([
                        ('partner_weight','>',0),
                        ('country_id','=',lead.country_id.id),
                        ('id','notin',lead.partner_declined_ids.mapped('id')),
                    ])

                #6.sixthway:closestpartnerwhatsoever,justtohaveatleastoneresult
                ifnotpartner_ids:
                    #warning:point()typetakes(longitude,latitude)asparametersinthisorder!
                    self._cr.execute("""SELECTid,distance
                                  FROM (selectid,(point(partner_longitude,partner_latitude)<->point(%s,%s))ASdistanceFROMres_partner
                                  WHEREactive
                                        ANDpartner_longitudeisnotnull
                                        ANDpartner_latitudeisnotnull
                                        ANDpartner_weight>0
                                        ANDidnotin(selectpartner_idfromcrm_lead_declined_partnerwherelead_id=%s)
                                        )ASd
                                  ORDERBYdistanceLIMIT1""",(longitude,latitude,lead.id))
                    res=self._cr.dictfetchone()
                    ifres:
                        partner_ids=Partner.browse([res['id']])

                total_weight=0
                toassign=[]
                forpartnerinpartner_ids:
                    total_weight+=partner.partner_weight
                    toassign.append((partner.id,total_weight))

                random.shuffle(toassign) #avoidalwaysgivingtheleadstothefirstonesindbnaturalorder!
                nearest_weight=random.randint(0,total_weight)
                forpartner_id,weightintoassign:
                    ifnearest_weight<=weight:
                        res_partner_ids[lead.id]=partner_id
                        break
        returnres_partner_ids

    defpartner_interested(self,comment=False):
        message=_('<p>Iaminterestedbythislead.</p>')
        ifcomment:
            message+='<p>%s</p>'%html_escape(comment)
        forleadinself:
            lead.message_post(body=message)
            lead.sudo().convert_opportunity(lead.partner_id.id) #sudorequiredtoconvertpartnerdata

    defpartner_desinterested(self,comment=False,contacted=False,spam=False):
        ifcontacted:
            message='<p>%s</p>'%_('Iamnotinterestedbythislead.Icontactedthelead.')
        else:
            message='<p>%s</p>'%_('Iamnotinterestedbythislead.Ihavenotcontactedthelead.')
        partner_ids=self.env['res.partner'].search(
            [('id','child_of',self.env.user.partner_id.commercial_partner_id.id)])
        self.message_unsubscribe(partner_ids=partner_ids.ids)
        ifcomment:
            message+='<p>%s</p>'%html_escape(comment)
        self.message_post(body=message)
        values={
            'partner_assigned_id':False,
        }

        ifspam:
            tag_spam=self.env.ref('website_crm_partner_assign.tag_portal_lead_is_spam',False)
            iftag_spamandtag_spamnotinself.tag_ids:
                values['tag_ids']=[(4,tag_spam.id,False)]
        ifpartner_ids:
            values['partner_declined_ids']=[(4,p,0)forpinpartner_ids.ids]
        self.sudo().write(values)

    defupdate_lead_portal(self,values):
        self.check_access_rights('write')
        forleadinself:
            lead_values={
                'expected_revenue':values['expected_revenue'],
                'probability':values['probability']orFalse,
                'priority':values['priority'],
                'date_deadline':values['date_deadline']orFalse,
            }
            #Asactivitiesmaybelongtoseveralusers,onlythecurrentportaluseractivity
            #willbemodifiedbytheportalform.Ifnoactivityexistwecreateanewoneinstead
            #thatweassigntotheportaluser.

            user_activity=lead.sudo().activity_ids.filtered(lambdaactivity:activity.user_id==self.env.user)[:1]
            ifvalues['activity_date_deadline']:
                ifuser_activity:
                    user_activity.sudo().write({
                        'activity_type_id':values['activity_type_id'],
                        'summary':values['activity_summary'],
                        'date_deadline':values['activity_date_deadline'],
                    })
                else:
                    self.env['mail.activity'].sudo().create({
                        'res_model_id':self.env.ref('crm.model_crm_lead').id,
                        'res_id':lead.id,
                        'user_id':self.env.user.id,
                        'activity_type_id':values['activity_type_id'],
                        'summary':values['activity_summary'],
                        'date_deadline':values['activity_date_deadline'],
                    })
            lead.write(lead_values)

    defupdate_contact_details_from_portal(self,values):
        self.check_access_rights('write')
        fields=['partner_name','phone','mobile','email_from','street','street2',
            'city','zip','state_id','country_id']
        ifany([keynotinfieldsforkeyinvalues]):
            raiseUserError(_("Notallowedtoupdatethefollowingfield(s):%s.")%",".join([keyforkeyinvaluesifnotkeyinfields]))
        returnself.sudo().write(values)

    @api.model
    defcreate_opp_portal(self,values):
        ifnot(self.env.user.partner_id.grade_idorself.env.user.commercial_partner_id.grade_id):
            raiseAccessDenied()
        user=self.env.user
        self=self.sudo()
        ifnot(values['contact_name']andvalues['description']andvalues['title']):
            return{
                'errors':_('Allfieldsarerequired!')
            }
        tag_own=self.env.ref('website_crm_partner_assign.tag_portal_lead_own_opp',False)
        values={
            'contact_name':values['contact_name'],
            'name':values['title'],
            'description':values['description'],
            'priority':'2',
            'partner_assigned_id':user.commercial_partner_id.id,
        }
        iftag_own:
            values['tag_ids']=[(4,tag_own.id,False)]

        lead=self.create(values)
        lead.assign_salesman_of_assigned_partner()
        lead.convert_opportunity(lead.partner_id.id)
        return{
            'id':lead.id
        }

    #
    #  DONOTFORWARDPORTINMASTER
    #  instead,crm.leadshouldimplementportal.mixin
    #
    defget_access_action(self,access_uid=None):
        """Insteadoftheclassicformview,redirecttotheonlinedocumentfor
        portalusersorifforce_website=Trueinthecontext."""
        self.ensure_one()

        user,record=self.env.user,self
        ifaccess_uid:
            try:
                record.check_access_rights('read')
                record.check_access_rule("read")
            exceptAccessError:
                returnsuper(CrmLead,self).get_access_action(access_uid)
            user=self.env['res.users'].sudo().browse(access_uid)
            record=self.with_user(user)
        ifuser.shareorself.env.context.get('force_website'):
            try:
                record.check_access_rights('read')
                record.check_access_rule('read')
            exceptAccessError:
                pass
            else:
                return{
                    'type':'ir.actions.act_url',
                    'url':'/my/opportunity/%s'%record.id,
                }
        returnsuper(CrmLead,self).get_access_action(access_uid)
