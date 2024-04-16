#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportmodels


classEventRegistration(models.Model):
    _inherit='event.registration'

    def_get_lead_grouping(self,rules,rule_to_new_regs):
        """Overridetosupportsale-orderbasedgroupingandupdate.

        Whencheckingforgroupsforrules,wesearchforexistingleadslinked
        tosamegroup(basedonsale_order_id)andrule.Eachrulecantherefore
        updateanexistingleadorcreateanewone,foreachsaleorderthat
        makesthegroup."""
        so_registrations=self.filtered(lambdareg:reg.sale_order_id)
        grouping_res=super(EventRegistration,self-so_registrations)._get_lead_grouping(rules,rule_to_new_regs)

        ifso_registrations:
            #findexistingleadsinbatchtoputthemincacheandavoidmultiplesearch/queries
            related_registrations=self.env['event.registration'].search([
                ('sale_order_id','in',so_registrations.sale_order_id.ids)
            ])
            related_leads=self.env['crm.lead'].search([
                ('event_lead_rule_id','in',rules.ids),
                ('registration_ids','in',related_registrations.ids)
            ])

            forruleinrules:
                rule_new_regs=rule_to_new_regs[rule]

                #foreachgroup(sale_order),finditslinkedregistrations
                so_to_regs=defaultdict(lambda:self.env['event.registration'])
                forregistrationinrule_new_regs&so_registrations:
                    so_to_regs[registration.sale_order_id]|=registration

                #foreachgroupedregistrations,prepareresultwithgroupandexistinglead
                so_res=[]
                forsale_order,registrationsinso_to_regs.items():
                    registrations=registrations.sorted('id') #asanORwasused,re-ensureorder
                    leads=related_leads.filtered(lambdalead:lead.event_lead_rule_id==ruleandlead.registration_ids.sale_order_id==sale_order)
                    so_res.append((leads,sale_order,registrations))
                ifso_res:
                    grouping_res[rule]=grouping_res.get(rule,list())+so_res

        returngrouping_res
