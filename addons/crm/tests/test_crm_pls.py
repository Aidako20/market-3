#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectraimportfields,tools
fromflectra.tests.commonimportTransactionCase


classTestCRMPLS(TransactionCase):

    def_get_lead_values(self,team_id,name_suffix,country_id,state_id,email_state,phone_state,source_id,stage_id):
        return{
            'name':'lead_'+name_suffix,
            'type':'opportunity',
            'state_id':state_id,
            'email_state':email_state,
            'phone_state':phone_state,
            'source_id':source_id,
            'stage_id':stage_id,
            'country_id':country_id,
            'team_id':team_id
        }

    defgenerate_leads_with_tags(self,tag_ids):
        Lead=self.env['crm.lead']
        team_id=self.env['crm.team'].create({
            'name':'blup',
        }).id

        leads_to_create=[]
        foriinrange(150):
            ifi<50: #tag1
                leads_to_create.append({
                    'name':'lead_tag_%s'%str(i),
                    'tag_ids':[(4,tag_ids[0])],
                    'team_id':team_id
                })
            elifi<100: #tag2
                leads_to_create.append({
                    'name':'lead_tag_%s'%str(i),
                    'tag_ids':[(4,tag_ids[1])],
                    'team_id':team_id
                })
            else: #tag1and2
                leads_to_create.append({
                    'name':'lead_tag_%s'%str(i),
                    'tag_ids':[(6,0,tag_ids)],
                    'team_id':team_id
                })

        leads_with_tags=Lead.create(leads_to_create)

        returnleads_with_tags

    deftest_predictive_lead_scoring(self):
        """WetestherecomputationofleadprobabilitybasedonPLSBayes.
                Wewilluse3differentvaluesforeachpossiblevariables:
                country_id:1,2,3
                state_id:1,2,3
                email_state:correct,incorrect,None
                phone_state:correct,incorrect,None
                source_id:1,2,3
                stage_id:1,2,3+thewonstage
                Andwewillcomputeallofthisfor2differentteam_id
            Note:Weassumeherethatoriginalbayescomputationiscorrect
            aswedon'tcomputemanuallytheprobabilities."""
        Lead=self.env['crm.lead']
        LeadScoringFrequency=self.env['crm.lead.scoring.frequency']
        state_values=['correct','incorrect',None]
        source_ids=self.env['utm.source'].search([],limit=3).ids
        state_ids=self.env['res.country.state'].search([],limit=3).ids
        country_ids=self.env['res.country'].search([],limit=3).ids
        stage_ids=self.env['crm.stage'].search([],limit=3).ids
        won_stage_id=self.env['crm.stage'].search([('is_won','=',True)],limit=1).id
        team_ids=self.env['crm.team'].create([{'name':'TeamTest1'},{'name':'TeamTest2'}]).ids
        #createbunchoflostandwoncrm_lead
        leads_to_create=[]
        #  forteam1
        foriinrange(3):
            leads_to_create.append(
                self._get_lead_values(team_ids[0],'team_1_%s'%str(i),country_ids[i],state_ids[i],state_values[i],state_values[i],source_ids[i],stage_ids[i]))
        leads_to_create.append(
            self._get_lead_values(team_ids[0],'team_1_%s'%str(3),country_ids[0],state_ids[1],state_values[2],state_values[0],source_ids[2],stage_ids[1]))
        leads_to_create.append(
            self._get_lead_values(team_ids[0],'team_1_%s'%str(4),country_ids[1],state_ids[1],state_values[1],state_values[0],source_ids[1],stage_ids[0]))
        #  forteam2
        leads_to_create.append(
            self._get_lead_values(team_ids[1],'team_2_%s'%str(5),country_ids[0],state_ids[1],state_values[2],state_values[0],source_ids[1],stage_ids[2]))
        leads_to_create.append(
            self._get_lead_values(team_ids[1],'team_2_%s'%str(6),country_ids[0],state_ids[1],state_values[0],state_values[1],source_ids[2],stage_ids[1]))
        leads_to_create.append(
            self._get_lead_values(team_ids[1],'team_2_%s'%str(7),country_ids[0],state_ids[2],state_values[0],state_values[1],source_ids[2],stage_ids[0]))
        leads_to_create.append(
            self._get_lead_values(team_ids[1],'team_2_%s'%str(8),country_ids[0],state_ids[1],state_values[2],state_values[0],source_ids[2],stage_ids[1]))
        leads_to_create.append(
            self._get_lead_values(team_ids[1],'team_2_%s'%str(9),country_ids[1],state_ids[0],state_values[1],state_values[0],source_ids[1],stage_ids[1]))

        leads=Lead.create(leads_to_create)

        #SetthePLSconfig
        self.env['ir.config_parameter'].sudo().set_param("crm.pls_start_date","2000-01-01")
        self.env['ir.config_parameter'].sudo().set_param("crm.pls_fields","country_id,state_id,email_state,phone_state,source_id")

        #setleadsaswonandlost
        #forTeam1
        leads[0].action_set_lost()
        leads[1].action_set_lost()
        leads[2].action_set_won()
        #forTeam2
        leads[5].action_set_lost()
        leads[6].action_set_lost()
        leads[7].action_set_won()

        #A.TestFullRebuild
        #rebuildfrequenciestableandrecomputeautomated_probabilityforallleads.
        Lead._cron_update_automated_probabilities()

        #AsthecroniscomputingandwritinginSQLqueries,weneedtoinvalidatethecache
        leads.invalidate_cache()

        self.assertEqual(tools.float_compare(leads[3].automated_probability,33.49,2),0)
        self.assertEqual(tools.float_compare(leads[8].automated_probability,7.74,2),0)

        #Testfrequencies
        lead_4_stage_0_freq=LeadScoringFrequency.search([('team_id','=',leads[4].team_id.id),('variable','=','stage_id'),('value','=',stage_ids[0])])
        lead_4_stage_won_freq=LeadScoringFrequency.search([('team_id','=',leads[4].team_id.id),('variable','=','stage_id'),('value','=',won_stage_id)])
        lead_4_country_freq=LeadScoringFrequency.search([('team_id','=',leads[4].team_id.id),('variable','=','country_id'),('value','=',leads[4].country_id.id)])
        lead_4_email_state_freq=LeadScoringFrequency.search([('team_id','=',leads[4].team_id.id),('variable','=','email_state'),('value','=',str(leads[4].email_state))])

        lead_9_stage_0_freq=LeadScoringFrequency.search([('team_id','=',leads[9].team_id.id),('variable','=','stage_id'),('value','=',stage_ids[0])])
        lead_9_stage_won_freq=LeadScoringFrequency.search([('team_id','=',leads[9].team_id.id),('variable','=','stage_id'),('value','=',won_stage_id)])
        lead_9_country_freq=LeadScoringFrequency.search([('team_id','=',leads[9].team_id.id),('variable','=','country_id'),('value','=',leads[9].country_id.id)])
        lead_9_email_state_freq=LeadScoringFrequency.search([('team_id','=',leads[9].team_id.id),('variable','=','email_state'),('value','=',str(leads[9].email_state))])

        self.assertEqual(lead_4_stage_0_freq.won_count,1.1)
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1)
        self.assertEqual(lead_4_country_freq.won_count,0.1)
        self.assertEqual(lead_4_email_state_freq.won_count,1.1)
        self.assertEqual(lead_4_stage_0_freq.lost_count,2.1)
        self.assertEqual(lead_4_stage_won_freq.lost_count,0.1)
        self.assertEqual(lead_4_country_freq.lost_count,1.1)
        self.assertEqual(lead_4_email_state_freq.lost_count,2.1)

        self.assertEqual(lead_9_stage_0_freq.won_count,1.1)
        self.assertEqual(lead_9_stage_won_freq.won_count,1.1)
        self.assertEqual(lead_9_country_freq.won_count,0.0) #frequencydoesnotexist
        self.assertEqual(lead_9_email_state_freq.won_count,1.1)
        self.assertEqual(lead_9_stage_0_freq.lost_count,2.1)
        self.assertEqual(lead_9_stage_won_freq.lost_count,0.1)
        self.assertEqual(lead_9_country_freq.lost_count,0.0) #frequencydoesnotexist
        self.assertEqual(lead_9_email_state_freq.lost_count,2.1)

        #B.TestLiveIncrement
        leads[4].action_set_lost()
        leads[9].action_set_won()

        #re-getfrequenciesthatdidnotexistsbefore
        lead_9_country_freq=LeadScoringFrequency.search([('team_id','=',leads[9].team_id.id),('variable','=','country_id'),('value','=',leads[9].country_id.id)])

        #B.1.Testfrequencies-team1shouldnotimpactteam2
        self.assertEqual(lead_4_stage_0_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.won_count,0.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_0_freq.lost_count,3.1) #+1
        self.assertEqual(lead_4_stage_won_freq.lost_count,0.1) #unchanged-considerstageswith<=sequencewhenlost
        self.assertEqual(lead_4_country_freq.lost_count,2.1) #+1
        self.assertEqual(lead_4_email_state_freq.lost_count,3.1) #+1

        self.assertEqual(lead_9_stage_0_freq.won_count,2.1) #+1
        self.assertEqual(lead_9_stage_won_freq.won_count,2.1) #+1-considereverystageswhenwon
        self.assertEqual(lead_9_country_freq.won_count,1.1) #+1
        self.assertEqual(lead_9_email_state_freq.won_count,2.1) #+1
        self.assertEqual(lead_9_stage_0_freq.lost_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_won_freq.lost_count,0.1) #unchanged
        self.assertEqual(lead_9_country_freq.lost_count,0.1) #unchanged(didnotexistsbefore)
        self.assertEqual(lead_9_email_state_freq.lost_count,2.1) #unchanged

        #Propabilitiesofotherleadsshouldnotbeimpactedasonlymodifiedleadarerecomputed.
        self.assertEqual(tools.float_compare(leads[3].automated_probability,33.49,2),0)
        self.assertEqual(tools.float_compare(leads[8].automated_probability,7.74,2),0)

        self.assertEqual(leads[3].is_automated_probability,True)
        self.assertEqual(leads[8].is_automated_probability,True)

        #Restore->Shoulddecreaselost
        leads[4].toggle_active()
        self.assertEqual(lead_4_stage_0_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.won_count,0.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_0_freq.lost_count,2.1) #-1
        self.assertEqual(lead_4_stage_won_freq.lost_count,0.1) #unchanged-considerstageswith<=sequencewhenlost
        self.assertEqual(lead_4_country_freq.lost_count,1.1) #-1
        self.assertEqual(lead_4_email_state_freq.lost_count,2.1) #-1

        self.assertEqual(lead_9_stage_0_freq.won_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_won_freq.won_count,2.1) #unchanged
        self.assertEqual(lead_9_country_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_9_email_state_freq.won_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_0_freq.lost_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_won_freq.lost_count,0.1) #unchanged
        self.assertEqual(lead_9_country_freq.lost_count,0.1) #unchanged
        self.assertEqual(lead_9_email_state_freq.lost_count,2.1) #unchanged

        #settowonstage->Shouldincreasewon
        leads[4].stage_id=won_stage_id
        self.assertEqual(lead_4_stage_0_freq.won_count,2.1) #+1
        self.assertEqual(lead_4_stage_won_freq.won_count,2.1) #+1
        self.assertEqual(lead_4_country_freq.won_count,1.1) #+1
        self.assertEqual(lead_4_email_state_freq.won_count,2.1) #+1
        self.assertEqual(lead_4_stage_0_freq.lost_count,2.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.lost_count,0.1) #unchanged
        self.assertEqual(lead_4_country_freq.lost_count,1.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.lost_count,2.1) #unchanged

        #Archive(waswon,nowlost)->Shoulddecreasewonandincreaselost
        leads[4].toggle_active()
        self.assertEqual(lead_4_stage_0_freq.won_count,1.1) #-1
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1) #-1
        self.assertEqual(lead_4_country_freq.won_count,0.1) #-1
        self.assertEqual(lead_4_email_state_freq.won_count,1.1) #-1
        self.assertEqual(lead_4_stage_0_freq.lost_count,3.1) #+1
        self.assertEqual(lead_4_stage_won_freq.lost_count,1.1) #considerstageswith<=sequencewhenlostandasstageiswon..evenwon_stagelost_countisincreasedby1
        self.assertEqual(lead_4_country_freq.lost_count,2.1) #+1
        self.assertEqual(lead_4_email_state_freq.lost_count,3.1) #+1

        #Movetooriginalstage->Shoulddonothing(asleadisstilllost)
        leads[4].stage_id=stage_ids[0]
        self.assertEqual(lead_4_stage_0_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.won_count,0.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_0_freq.lost_count,3.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.lost_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.lost_count,2.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.lost_count,3.1) #unchanged

        #Restore->Shoulddecreaselost-attheend,frequenciesshouldbelikefirstfrequencyestests(exceptfor0.0->0.1)
        leads[4].toggle_active()
        self.assertEqual(lead_4_stage_0_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.won_count,0.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_0_freq.lost_count,2.1) #-1
        self.assertEqual(lead_4_stage_won_freq.lost_count,1.1) #unchanged-considerstageswith<=sequencewhenlost
        self.assertEqual(lead_4_country_freq.lost_count,1.1) #-1
        self.assertEqual(lead_4_email_state_freq.lost_count,2.1) #-1

        #Probabilitiesshouldonlyberecomputedaftermodifyingtheleaditself.
        leads[3].stage_id=stage_ids[0] #probabilityshouldonlychangeabitasfrequenciesarealmostthesame(except0.0->0.1)
        leads[8].stage_id=stage_ids[0] #probabilityshouldchangequitealot

        #Testfrequencies(shouldnothavechanged)
        self.assertEqual(lead_4_stage_0_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.won_count,0.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_4_stage_0_freq.lost_count,2.1) #unchanged
        self.assertEqual(lead_4_stage_won_freq.lost_count,1.1) #unchanged
        self.assertEqual(lead_4_country_freq.lost_count,1.1) #unchanged
        self.assertEqual(lead_4_email_state_freq.lost_count,2.1) #unchanged

        self.assertEqual(lead_9_stage_0_freq.won_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_won_freq.won_count,2.1) #unchanged
        self.assertEqual(lead_9_country_freq.won_count,1.1) #unchanged
        self.assertEqual(lead_9_email_state_freq.won_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_0_freq.lost_count,2.1) #unchanged
        self.assertEqual(lead_9_stage_won_freq.lost_count,0.1) #unchanged
        self.assertEqual(lead_9_country_freq.lost_count,0.1) #unchanged
        self.assertEqual(lead_9_email_state_freq.lost_count,2.1) #unchanged

        #Continuetotestprobabilitycomputation
        leads[3].probability=40

        self.assertEqual(leads[3].is_automated_probability,False)
        self.assertEqual(leads[8].is_automated_probability,True)

        self.assertEqual(tools.float_compare(leads[3].automated_probability,20.87,2),0)
        self.assertEqual(tools.float_compare(leads[8].automated_probability,2.43,2),0)
        self.assertEqual(tools.float_compare(leads[3].probability,40,2),0)
        self.assertEqual(tools.float_compare(leads[8].probability,2.43,2),0)

        #Testmodifycountry_id
        leads[8].country_id=country_ids[1]
        self.assertEqual(tools.float_compare(leads[8].automated_probability,34.38,2),0)
        self.assertEqual(tools.float_compare(leads[8].probability,34.38,2),0)

        leads[8].country_id=country_ids[0]
        self.assertEqual(tools.float_compare(leads[8].automated_probability,2.43,2),0)
        self.assertEqual(tools.float_compare(leads[8].probability,2.43,2),0)

        #----------------------------------------------
        #Testtag_idfrequenciesandprobabilityimpact
        #----------------------------------------------

        tag_ids=self.env['crm.tag'].create([
            {'name':"Tag_test_1"},
            {'name':"Tag_test_2"},
        ]).ids
        #tag_ids=self.env['crm.tag'].search([],limit=2).ids
        leads_with_tags=self.generate_leads_with_tags(tag_ids)

        leads_with_tags[:30].action_set_lost() #60%lostontag1
        leads_with_tags[31:50].action_set_won()  #40%wonontag1
        leads_with_tags[50:90].action_set_lost() #80%lostontag2
        leads_with_tags[91:100].action_set_won()  #20%wonontag2
        leads_with_tags[100:135].action_set_lost() #70%lostontag1and2
        leads_with_tags[136:150].action_set_won()  #30%wonontag1and2
        #tag1:won=19+14 / lost=30+35
        #tag2:won=9+14 / lost=40+35

        tag_1_freq=LeadScoringFrequency.search([('variable','=','tag_id'),('value','=',tag_ids[0])])
        tag_2_freq=LeadScoringFrequency.search([('variable','=','tag_id'),('value','=',tag_ids[1])])
        self.assertEqual(tools.float_compare(tag_1_freq.won_count,33.1,1),0)
        self.assertEqual(tools.float_compare(tag_1_freq.lost_count,65.1,1),0)
        self.assertEqual(tools.float_compare(tag_2_freq.won_count,23.1,1),0)
        self.assertEqual(tools.float_compare(tag_2_freq.lost_count,75.1,1),0)

        #Forcerecompute-Apriori,noneedtodothisas,foreachwon/lost,weincrementtagfrequency.
        Lead._cron_update_automated_probabilities()
        leads_with_tags.invalidate_cache()

        lead_tag_1=leads_with_tags[30]
        lead_tag_2=leads_with_tags[90]
        lead_tag_1_2=leads_with_tags[135]

        self.assertEqual(tools.float_compare(lead_tag_1.automated_probability,33.69,2),0)
        self.assertEqual(tools.float_compare(lead_tag_2.automated_probability,23.51,2),0)
        self.assertEqual(tools.float_compare(lead_tag_1_2.automated_probability,28.05,2),0)

        lead_tag_1.tag_ids=[(5,0,0)] #removealltags
        lead_tag_1_2.tag_ids=[(3,tag_ids[1],0)] #removetag2

        self.assertEqual(tools.float_compare(lead_tag_1.automated_probability,28.6,2),0)
        self.assertEqual(tools.float_compare(lead_tag_2.automated_probability,23.51,2),0) #noimpact
        self.assertEqual(tools.float_compare(lead_tag_1_2.automated_probability,33.69,2),0)

        lead_tag_1.tag_ids=[(4,tag_ids[1])] #addtag2
        lead_tag_2.tag_ids=[(4,tag_ids[0])] #addtag1
        lead_tag_1_2.tag_ids=[(3,tag_ids[0]),(4,tag_ids[1])] #removetag1/addtag2

        self.assertEqual(tools.float_compare(lead_tag_1.automated_probability,23.51,2),0)
        self.assertEqual(tools.float_compare(lead_tag_2.automated_probability,28.05,2),0)
        self.assertEqual(tools.float_compare(lead_tag_1_2.automated_probability,23.51,2),0)

        #gobacktoinitialsituation
        lead_tag_1.tag_ids=[(3,tag_ids[1]),(4,tag_ids[0])] #removetag2/addtag1
        lead_tag_2.tag_ids=[(3,tag_ids[0])] #removetag1
        lead_tag_1_2.tag_ids=[(4,tag_ids[0])] #addtag1

        self.assertEqual(tools.float_compare(lead_tag_1.automated_probability,33.69,2),0)
        self.assertEqual(tools.float_compare(lead_tag_2.automated_probability,23.51,2),0)
        self.assertEqual(tools.float_compare(lead_tag_1_2.automated_probability,28.05,2),0)

        #setemail_stateforeachleadandupdateprobabilities
        leads.filtered(lambdalead:lead.id%2==0).email_state='correct'
        leads.filtered(lambdalead:lead.id%2==1).email_state='incorrect'
        Lead._cron_update_automated_probabilities()
        leads_with_tags.invalidate_cache()

        self.assertEqual(tools.float_compare(leads[3].automated_probability,4.21,2),0,
                        f'PLS:failedwith{leads[3].automated_probability},shouldbe4.21')
        self.assertEqual(tools.float_compare(leads[8].automated_probability,0.23,2),0)

        #removeallplsfields
        self.env['ir.config_parameter'].sudo().set_param("crm.pls_fields",False)
        Lead._cron_update_automated_probabilities()
        leads_with_tags.invalidate_cache()

        self.assertEqual(tools.float_compare(leads[3].automated_probability,34.38,2),0)
        self.assertEqual(tools.float_compare(leads[8].automated_probability,50.0,2),0)

        #checkiftheprobabilitiesarethesamewiththeoldparam
        self.env['ir.config_parameter'].sudo().set_param("crm.pls_fields","country_id,state_id,email_state,phone_state,source_id")
        Lead._cron_update_automated_probabilities()
        leads_with_tags.invalidate_cache()

        self.assertEqual(tools.float_compare(leads[3].automated_probability,4.21,2),0)
        self.assertEqual(tools.float_compare(leads[8].automated_probability,0.23,2),0)

    deftest_predictive_lead_scoring_always_won(self):
        """Thecomputationmayleadscorescloseto100%(or0%),wecheckthatpending
        leadsarealwaysinthe]0-100[range."""
        Lead=self.env['crm.lead']
        LeadScoringFrequency=self.env['crm.lead.scoring.frequency']
        country_id=self.env['res.country'].search([],limit=1).id
        stage_id=self.env['crm.stage'].search([],limit=1).id
        team_id=self.env['crm.team'].create({'name':'TeamTest1'}).id
        #createtwoleads
        leads=Lead.create([
            self._get_lead_values(team_id,'edgepending',country_id,False,False,False,False,stage_id),
            self._get_lead_values(team_id,'edgelost',country_id,False,False,False,False,stage_id),
            self._get_lead_values(team_id,'edgewon',country_id,False,False,False,False,stage_id),
        ])
        #setanewtag
        leads.tag_ids=self.env['crm.tag'].create({'name':'leadscoringedgecase'})

        #SetthePLSconfig
        self.env['ir.config_parameter'].sudo().set_param("crm.pls_start_date","2000-01-01")
        #tag_idscanbeusedinversionsnewerthanv14
        self.env['ir.config_parameter'].sudo().set_param("crm.pls_fields","country_id")

        #setleadsaswonandlost
        leads[1].action_set_lost()
        leads[2].action_set_won()

        #recompute
        Lead._cron_update_automated_probabilities()
        Lead.invalidate_cache()

        #adapttheprobabilityfrequencytohavehighvalues
        #thiswaywearenearlysureit'sgoingtobewon
        freq_stage=LeadScoringFrequency.search([('variable','=','stage_id'),('value','=',str(stage_id))])
        freq_tag=LeadScoringFrequency.search([('variable','=','tag_id'),('value','=',str(leads.tag_ids.id))])
        freqs=freq_stage+freq_tag

        #checkprobabilities:wonedgecase
        freqs.write({'won_count':10000000,'lost_count':1})
        leads._compute_probabilities()
        self.assertEqual(tools.float_compare(leads[2].probability,100,2),0)
        self.assertEqual(tools.float_compare(leads[1].probability,0,2),0)
        self.assertEqual(tools.float_compare(leads[0].probability,99.99,2),0)

        #checkprobabilities:lostedgecase
        freqs.write({'won_count':1,'lost_count':10000000})
        leads._compute_probabilities()
        self.assertEqual(tools.float_compare(leads[2].probability,100,2),0)
        self.assertEqual(tools.float_compare(leads[1].probability,0,2),0)
        self.assertEqual(tools.float_compare(leads[0].probability,0.01,2),0)

    deftest_settings_pls_start_date(self):
        #Wetestherethatsettingsnevercrashduetoill-configuredconfigparam'crm.pls_start_date'
        set_param=self.env['ir.config_parameter'].sudo().set_param
        str_date_8_days_ago=fields.Date.to_string(fields.Date.today()-timedelta(days=8))
        resConfig=self.env['res.config.settings']

        set_param("crm.pls_start_date","2021-10-10")
        res_config_new=resConfig.new()
        self.assertEqual(fields.Date.to_string(res_config_new.predictive_lead_scoring_start_date),
            "2021-10-10","Ifconfigparamisavaliddate,dateinsettingsshouldmatchwithconfigparam")

        set_param("crm.pls_start_date","")
        res_config_new=resConfig.new()
        self.assertEqual(fields.Date.to_string(res_config_new.predictive_lead_scoring_start_date),
            str_date_8_days_ago,"Ifconfigparamisempty,dateinsettingsshouldbesetto8daysbeforetoday")

        set_param("crm.pls_start_date","Onedoesnotsimplywalkintosystemparameterstocorruptthem")
        res_config_new=resConfig.new()
        self.assertEqual(fields.Date.to_string(res_config_new.predictive_lead_scoring_start_date),
            str_date_8_days_ago,"Ifconfigparamisnotavaliddate,dateinsettingsshouldbesetto8daysbeforetoday")

    deftest_pls_no_share_stage(self):
        """Wetestherethesituationwhereallstagesareteamspecific,asthereis
            acurrentlimitation(canbeseenin_pls_get_won_lost_total_count)regarding
            thefirststage(usedtoknowhowmanylostandwonthereis)thatrequires
            tohavenoteamassignedtoit."""
        Lead=self.env['crm.lead']
        team_id=self.env['crm.team'].create([{'name':'TeamTest'}]).id
        self.env['crm.stage'].search([('team_id','=',False)]).write({'team_id':team_id})
        lead=Lead.create({'name':'team','team_id':team_id,'probability':41.23})
        Lead._cron_update_automated_probabilities()
        self.assertEqual(tools.float_compare(lead.probability,41.23,2),0)
        self.assertEqual(tools.float_compare(lead.automated_probability,0,2),0)

