#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models,tools,_
fromflectra.addons.phone_validation.toolsimportphone_validation


classEventRegistration(models.Model):
    _inherit='event.registration'

    lead_ids=fields.Many2many(
        'crm.lead',string='Leads',copy=False,readonly=True,
        groups='sales_team.group_sale_salesman',
        help="Leadsgeneratedfromtheregistration.")
    lead_count=fields.Integer(
        '#Leads',compute='_compute_lead_count',groups='sales_team.group_sale_salesman',
        help="Counterfortheleadslinkedtothisregistration")

    @api.depends('lead_ids')
    def_compute_lead_count(self):
        forrecordinself:
            record.lead_count=len(record.lead_ids)

    @api.model_create_multi
    defcreate(self,vals_list):
        """Triggerrulesbasedonregistrationcreation,andcheckstatefor
        rulesbasedonconfirmed/doneattendees."""
        registrations=super(EventRegistration,self).create(vals_list)

        #handletriggersbasedoncreation,thenthosebasedonconfirmanddone
        #asregistrationscanbeautomaticallyconfirmed,orevencreateddirectly
        #withastategiveninvalues
        ifnotself.env.context.get('event_lead_rule_skip'):
            self.env['event.lead.rule'].search([('lead_creation_trigger','=','create')]).sudo()._run_on_registrations(registrations)
            open_registrations=registrations.filtered(lambdareg:reg.state=='open')
            ifopen_registrations:
                self.env['event.lead.rule'].search([('lead_creation_trigger','=','confirm')]).sudo()._run_on_registrations(open_registrations)
            done_registrations=registrations.filtered(lambdareg:reg.state=='done')
            ifdone_registrations:
                self.env['event.lead.rule'].search([('lead_creation_trigger','=','done')]).sudo()._run_on_registrations(done_registrations)

        returnregistrations

    defwrite(self,vals):
        """Updatetheleadvaluesdependingonfieldsupdatedinregistrations.
        Thereare2mainusecases

          *firstiswhenweupdatethepartner_idofmultipleregistrations.It
            happenswhenapublicuserfillitsinformationwhenheregisterto
            anevent;
          *secondiswhenweupdatespecificvaluesofoneregistrationlike
            updatingquestionanswersoracontactinformation(email,phone);

        Alsotriggerrulesbasedonconfirmedanddoneattendees(statewritten
        toopenanddone).
        """
        to_update,event_lead_rule_skip=False,self.env.context.get('event_lead_rule_skip')
        ifnotevent_lead_rule_skip:
            to_update=self.filtered(lambdareg:reg.lead_ids)
        ifto_update:
            lead_tracked_vals=to_update._get_lead_tracked_values()

        res=super(EventRegistration,self).write(vals)

        ifnotevent_lead_rule_skipandto_update:
            to_update.flush() #computenotablypartner-basedfieldsifnecessary
            to_update.sudo()._update_leads(vals,lead_tracked_vals)

        #handletriggersbasedonstate
        ifnotevent_lead_rule_skip:
            ifvals.get('state')=='open':
                self.env['event.lead.rule'].search([('lead_creation_trigger','=','confirm')]).sudo()._run_on_registrations(self)
            elifvals.get('state')=='done':
                self.env['event.lead.rule'].search([('lead_creation_trigger','=','done')]).sudo()._run_on_registrations(self)

        returnres

    def_load_records_create(self,values):
        """Inimportmode:donotrunrulesthoseareintendedtorunwhencustomers
        buytickets,notwhenbootstrappingadatabase."""
        returnsuper(EventRegistration,self.with_context(event_lead_rule_skip=True))._load_records_create(values)

    def_load_records_write(self,values):
        """Inimportmode:donotrunrulesthoseareintendedtorunwhencustomers
        buytickets,notwhenbootstrappingadatabase."""
        returnsuper(EventRegistration,self.with_context(event_lead_rule_skip=True))._load_records_write(values)

    def_update_leads(self,new_vals,lead_tracked_vals):
        """Updateleadslinkedtosomeregistrations.Updateisbaseddepending
        onupdatedfields,see``_get_lead_contact_fields()``and``_get_lead_
        description_fields()``.Mainheuristicis

          *checkattendee-basedleads,foreachregistrationrecomputecontact
            informationifnecessary(changingpartnertriggersthewholecontact
            computation);updatedescriptionifnecessary;
          *checkorder-basedleads,foreachexistinggroup-basedlead,only
            partnerchangetriggersacontactanddescriptionupdate.Weconsider
            thatgroup-basedruleworksmainlywiththemaincontactandless
            withfurtherdetailsofregistrations.Thosecanbefoundinstat
            buttonifnecessary.

        :paramnew_vals:valuesgiventowrite.Usedtodetermineupdatedfields;
        :paramlead_tracked_vals:dict(registration_id,registrationpreviousvalues)
          basedonnew_vals;
        """
        forregistrationinself:
            leads_attendee=registration.lead_ids.filtered(
                lambdalead:lead.event_lead_rule_id.lead_creation_basis=='attendee'
            )
            ifnotleads_attendee:
                continue

            old_vals=lead_tracked_vals[registration.id]
            #ifpartnerhasbeenupdated->updateregistrationcontactinformation
            #astheyarecomputed(andthereforenotgiventowritevalues)
            if'partner_id'innew_vals:
                new_vals.update(**dict(
                    (field,registration[field])
                    forfieldinself._get_lead_contact_fields()
                    iffield!='partner_id')
                )

            lead_values={}
            #updatecontactfields:validforallleadsofregistration
            upd_contact_fields=[fieldforfieldinself._get_lead_contact_fields()iffieldinnew_vals.keys()]
            ifany(new_vals[field]!=old_vals[field]forfieldinupd_contact_fields):
                lead_values=registration._get_lead_contact_values()

            #updatedescriptionfields:eachleadhastobeupdated,otherwise
            #updateinbatch
            upd_description_fields=[fieldforfieldinself._get_lead_description_fields()iffieldinnew_vals.keys()]
            ifany(new_vals[field]!=old_vals[field]forfieldinupd_description_fields):
                forleadinleads_attendee:
                    lead_values['description']="%s\n%s"%(
                        lead.description,
                        registration._get_lead_description(_("Updatedregistrations"),line_counter=True)
                    )
                    lead.write(lead_values)
            eliflead_values:
                leads_attendee.write(lead_values)

        leads_order=self.lead_ids.filtered(lambdalead:lead.event_lead_rule_id.lead_creation_basis=='order')
        forleadinleads_order:
            lead_values={}
            ifnew_vals.get('partner_id'):
                lead_values.update(lead.registration_ids._get_lead_contact_values())
                ifnotlead.partner_id:
                    lead_values['description']=lead.registration_ids._get_lead_description(_("Participants"),line_counter=True)
                elifnew_vals['partner_id']!=lead.partner_id.id:
                    lead_values['description']=lead.description+"\n"+lead.registration_ids._get_lead_description(_("Updatedregistrations"),line_counter=True,line_suffix=_("(updated)"))
            iflead_values:
                lead.write(lead_values)

    def_get_lead_values(self,rule):
        """Getleadvaluesfromregistrations.Selfcancontainmultiplerecords
        inwhichcasefirstfoundnonvoidvalueistaken.Notethatall
        registrationsshouldbelongtothesameevent.

        :returndictlead_values:valuesusedforcreate/writeonalead
        """
        lead_values={
            #fromrule
            'type':rule.lead_type,
            'user_id':rule.lead_user_id.id,
            'team_id':rule.lead_sales_team_id.id,
            'tag_ids':rule.lead_tag_ids.ids,
            'event_lead_rule_id':rule.id,
            #eventandregistration
            'event_id':self.event_id.id,
            'referred':self.event_id.name,
            'registration_ids':self.ids,
            'campaign_id':self._find_first_notnull('utm_campaign_id'),
            'source_id':self._find_first_notnull('utm_source_id'),
            'medium_id':self._find_first_notnull('utm_medium_id'),
        }
        lead_values.update(self._get_lead_contact_values())
        lead_values['description']=self._get_lead_description(_("Participants"),line_counter=True)
        returnlead_values

    def_get_lead_contact_values(self):
        """Specificmanagementofcontactvalues.Rulecreationbasishassome
        effectoncontactmanagement

          *inattendeemode:keepregistrationpartneronlyifpartnerphoneand
            emailmatch.Indeedleadaresynchronizedwiththeircontactandit
            wouldimplyrewritingonpartner,andthereforeonotherdocuments;
          *inbatchmode:ifacustomerisfounduseitasmaincontact.Registrations
            detailsareincludedinleaddescription;

        :returndict:valuesusedforcreate/writeonalead
        """
        valid_partner=next(
            (reg.partner_idforreginselfifreg.partner_id!=self.env.ref('base.public_partner')),
            self.env['res.partner']
        ) #CHECKME:broaderthanjustpublicpartner

        #monoregistrationmode:keeppartneronlyifemailandphonematches;
        #otherwiseregistration>partner.Notethatemailformatandphone
        #formattinghavetotakenintoaccountincomparison
        iflen(self)==1andvalid_partner:
            #compareemails:email_normalizedorraw
            ifself.emailandvalid_partner.email:
                ifvalid_partner.email_normalizedandtools.email_normalize(self.email)!=valid_partner.email_normalized:
                    valid_partner=self.env['res.partner']
                elifnotvalid_partner.email_normalizedandvalid_partner.email!=self.email:
                    valid_partner=self.env['res.partner']

            #comparephone,takingintoaccountformatting
            ifvalid_partnerandself.phoneandvalid_partner.phone:
                phone_formatted=phone_validation.phone_format(
                    self.phone,
                    valid_partner.country_id.codeorNone,
                    valid_partner.country_id.phone_codeorNone,
                    force_format='E164',
                    raise_exception=False
                )
                partner_phone_formatted=phone_validation.phone_format(
                    valid_partner.phone,
                    valid_partner.country_id.codeorNone,
                    valid_partner.country_id.phone_codeorNone,
                    force_format='E164',
                    raise_exception=False
                )
                ifphone_formattedandpartner_phone_formattedandphone_formatted!=partner_phone_formatted:
                    valid_partner=self.env['res.partner']
                if(notphone_formattedornotpartner_phone_formatted)andself.phone!=valid_partner.phone:
                    valid_partner=self.env['res.partner']

        ifvalid_partner:
            contact_vals=self.env['crm.lead']._prepare_values_from_partner(valid_partner)
            #forceemail_from/phoneonlyifnotsetonpartnerbecausethosefieldsarenowsynchronizedautomatically
            ifnotvalid_partner.email:
                contact_vals['email_from']=self._find_first_notnull('email')
            ifnotvalid_partner.phone:
                contact_vals['phone']=self._find_first_notnull('phone')
        else:
            #don'tforceemail_from+partner_idbecausethosefieldsarenowsynchronizedautomatically
            contact_vals={
                'contact_name':self._find_first_notnull('name'),
                'email_from':self._find_first_notnull('email'),
                'phone':self._find_first_notnull('phone'),
            }
        contact_vals.update({
            'name':"%s-%s"%(self.event_id.name,valid_partner.nameorself._find_first_notnull('name')orself._find_first_notnull('email')),
            'partner_id':valid_partner.id,
            'mobile':valid_partner.mobileorself._find_first_notnull('mobile'),
        })
        returncontact_vals

    def_get_lead_description(self,prefix='',line_counter=True,line_suffix=''):
        """Buildthedescriptionfortheleadusingaprefixforallgenerated
        lines.Forexampletoenumerateparticipantsorinformofanupdatein
        theinformationofaparticipant.

        :returnstringdescription:completedescriptionforaleadtakinginto
          accountallregistrationscontainedinself
        """
        reg_lines=[
            registration._get_lead_description_registration(
                prefix="%s."%(index+1)ifline_counterelse"",
                line_suffix=line_suffix
            )forindex,registrationinenumerate(self)
        ]
        return("%s\n"%prefixifprefixelse"")+("\n".join(reg_lines))

    def_get_lead_description_registration(self,prefix='',line_suffix=''):
        """Buildthedescriptionlinespecifictoagivenregistration."""
        self.ensure_one()
        return"%s%s(%s)%s"%(
            prefixor"",
            self.nameorself.partner_id.nameorself.email,
            "-".join(self[field]forfieldin('email','phone')ifself[field]),
            "%s"%line_suffixifline_suffixelse"",
        )

    def_get_lead_tracked_values(self):
        """Trackedvaluesarebasedontwosubsetoffieldstotrackinorder
        tofillorupdateleads.Twomainusecasesare

          *descriptionfields:registrationcontactfields:email,phone,...
            onregistration.Otherfieldsareaddedbyinheritancelike
            questionanswers;
          *contactfields:registrationcontactfields+partner_idfieldas
            contactofaleadismanagedspecifically.Indeedemailandphone
            synchronizationoflead/partner_idimpliespayingattentionto
            notrewritepartnervaluesfromregistrationvalues.

        Trackedvaluesarethereforetheunionofthosetwofieldsets."""
        tracked_fields=list(set(self._get_lead_contact_fields())orset(self._get_lead_description_fields()))
        returndict(
            (registration.id,
             dict((field,self._convert_value(registration[field],field))forfieldintracked_fields)
            )forregistrationinself
        )

    def_get_lead_grouping(self,rules,rule_to_new_regs):
        """Performgroupingofregistrationsinordertoenableorder-based
        leadcreationandupdateexistinggroupswithnewregistrations.

        Heuristicineventisthefollowing.Registrationscreatedinmulti-mode
        aregroupedbyevent.Customerusecase:website_eventflowcreates
        severalregistrationsinacreate-multi.

        Updateisnotsupportedasthereisnowaytodetermineifaregistration
        ispartofanexistingbatch.

        :paramrules:leadcreationrulestorunonregistrationsgivenbyself;
        :paramrule_to_new_regs:dict:foreachrule,subsetofselfmatching
          ruleconditions.Usedtospeedupbatchcomputation;

        :returndict:foreachrule,rule(keyofdict)givesalistofgroups.
          Eachgroupisatuple(
            existing_lead:existingleadtoupdate;
            group_record:recordusedtogroup;
            registrations:subrecordsetofself,containingregistrations
                           belongingtothesamegroup;
          )
        """
        event_to_reg_ids=defaultdict(lambda:self.env['event.registration'])
        forregistrationinself:
            event_to_reg_ids[registration.event_id]+=registration

        returndict(
            (rule,[(False,event,(registrations&rule_to_new_regs[rule]).sorted('id'))
                    forevent,registrationsinevent_to_reg_ids.items()])
            forruleinrules
        )

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    @api.model
    def_get_lead_contact_fields(self):
        """Getregistrationfieldslinkedtoleadcontact.Thoseareusednotably
        toseeifanupdateofleadisnecessaryortofillcontactvalues
        in``_get_lead_contact_values())``"""
        return['name','email','phone','mobile','partner_id']

    @api.model
    def_get_lead_description_fields(self):
        """Getregistrationfieldslinkedtoleaddescription.Thoseareused
        notablytoseeifanupdateofleadisnecessaryortofilldescription
        in``_get_lead_description())``"""
        return['name','email','phone']

    def_find_first_notnull(self,field_name):
        """Smalltooltoextractthefirstnotnullvalueofafield:itsvalue
        ortheidsifthisisarelationalfield."""
        value=next((reg[field_name]forreginselfifreg[field_name]),False)
        returnself._convert_value(value,field_name)

    def_convert_value(self,value,field_name):
        """Smalltoolbecauseconvert_to_writeistouchy"""
        ifisinstance(value,models.BaseModel)andself._fields[field_name].typein['many2many','one2many']:
            returnvalue.ids
        ifisinstance(value,models.BaseModel)andself._fields[field_name].type=='many2one':
            returnvalue.id
        returnvalue
