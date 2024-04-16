#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict
importitertools

fromflectraimportapi,fields,models


classFollowers(models.Model):
    """mail_followersholdsthedatarelatedtothefollowmechanisminside
    Flectra.Partnerscanchoosetofollowdocuments(records)ofanykind
    thatinheritsfrommail.thread.Followingdocumentsallowtoreceive
    notificationsfornewmessages.Asubscriptionischaracterizedby:

    :param:res_model:modelofthefollowedobjects
    :param:res_id:IDofresource(maybe0foreveryobjects)
    """
    _name='mail.followers'
    _rec_name='partner_id'
    _log_access=False
    _description='DocumentFollowers'

    #Note.Thereisnointegritycheckonmodelnamesforperformancereasons.
    #However,followersofunlinkedmodelsaredeletedbymodelsthemselves
    #(see'ir.model'inheritance).
    res_model=fields.Char(
        'RelatedDocumentModelName',required=True,index=True)
    res_id=fields.Many2oneReference(
        'RelatedDocumentID',index=True,help='Idofthefollowedresource',model_field='res_model')
    partner_id=fields.Many2one(
        'res.partner',string='RelatedPartner',ondelete='cascade',index=True,domain=[('type','!=','private')])
    channel_id=fields.Many2one(
        'mail.channel',string='Listener',ondelete='cascade',index=True)
    subtype_ids=fields.Many2many(
        'mail.message.subtype',string='Subtype',
        help="Messagesubtypesfollowed,meaningsubtypesthatwillbepushedontotheuser'sWall.")
    name=fields.Char('Name',compute='_compute_related_fields',
                       help="Nameoftherelatedpartner(ifexist)ortherelatedchannel")
    email=fields.Char('Email',compute='_compute_related_fields',
                        help="Emailoftherelatedpartner(ifexist)orFalse")
    is_active=fields.Boolean('IsActive',compute='_compute_related_fields',
                               help="Iftherelatedpartnerisactive(ifexist)orifrelatedchannelexist")

    def_invalidate_documents(self,vals_list=None):
        """Invalidatethecacheofthedocumentsfollowedby``self``.

        Modifyingfollowerschangeaccessrightstoindividualdocuments.Asthe
        cachemaycontainaccessible/inaccessibledata,onehastorefreshit.
        """
        to_invalidate=defaultdict(list)
        forrecordin(vals_listor[{'res_model':rec.res_model,'res_id':rec.res_id}forrecinself]):
            ifrecord.get('res_id'):
                to_invalidate[record.get('res_model')].append(record.get('res_id'))

    @api.model_create_multi
    defcreate(self,vals_list):
        res=super(Followers,self).create(vals_list)
        res._invalidate_documents(vals_list)
        returnres

    defwrite(self,vals):
        if'res_model'invalsor'res_id'invals:
            self._invalidate_documents()
        res=super(Followers,self).write(vals)
        ifany(xinvalsforxin['res_model','res_id','partner_id']):
            self._invalidate_documents()
        returnres

    defunlink(self):
        self._invalidate_documents()
        returnsuper(Followers,self).unlink()

    _sql_constraints=[
        ('mail_followers_res_partner_res_model_id_uniq','unique(res_model,res_id,partner_id)','Error,apartnercannotfollowtwicethesameobject.'),
        ('mail_followers_res_channel_res_model_id_uniq','unique(res_model,res_id,channel_id)','Error,achannelcannotfollowtwicethesameobject.'),
        ('partner_xor_channel','CHECK((partner_idISNULL)!=(channel_idISNULL))','Error:Afollowermustbeeitherapartnerorachannel(butnotboth).')
    ]

    #--------------------------------------------------
    #Privatetoolsmethodstofetchfollowersdata
    #--------------------------------------------------

    @api.depends('partner_id','channel_id')
    def_compute_related_fields(self):
        forfollowerinself:
            iffollower.partner_id:
                follower.name=follower.partner_id.name
                follower.email=follower.partner_id.email
                follower.is_active=follower.partner_id.active
            else:
                follower.name=follower.channel_id.name
                follower.is_active=bool(follower.channel_id)
                follower.email=False

    def_get_recipient_data(self,records,message_type,subtype_id,pids=None,cids=None):
        """Privatemethodallowingtofetchrecipientsdatabasedonasubtype.
        Purposeofthismethodistofetchalldatanecessarytonotifyrecipients
        inasinglequery.Itfetchesdatafrom

         *followers(partnersandchannels)ofrecordsthatfollowthegiven
           subtypeifrecordsandsubtypeareset;
         *partnersifpidsisgiven;
         *channelsifcidsisgiven;

        :paramrecords:fetchdatafromfollowersofrecordsthatfollowsubtype_id;
        :parammessage_type:mail.message.message_typeinordertoallowcustombehaviordependingonit(SMSforexample);
        :paramsubtype_id:mail.message.subtypetocheckagainstfollowers;
        :parampids:additionalsetofpartnerIDsfromwhichtofetchrecipientdata;
        :paramcids:additionalsetofchannelIDsfromwhichtofetchrecipientdata;

        :return:listofrecipientdatawhichisatuplecontaining
          partnerID(voidifchannelID),
          channelID(voidifpartnerID),
          activevalue(alwaysTrueforchannels),
          sharestatusofpartner(voidasirrelevantifchannelID),
          notificationstatusofpartnerorchannel(emailorinbox),
          usergroupsofpartner(voidasirrelevantifchannelID),
        """
        self.env['mail.followers'].flush(['partner_id','channel_id','subtype_ids'])
        self.env['mail.message.subtype'].flush(['internal'])
        self.env['res.users'].flush(['notification_type','active','partner_id','groups_id'])
        self.env['res.partner'].flush(['active','partner_share'])
        self.env['res.groups'].flush(['users'])
        self.env['mail.channel'].flush(['email_send','channel_type'])
        ifrecordsandsubtype_id:
            query="""
SELECTDISTINCTON(pid,cid)*FROM(
    WITHsub_followersAS(
        SELECTfol.id,fol.partner_id,fol.channel_id,subtype.internal
        FROMmail_followersfol
            RIGHTJOINmail_followers_mail_message_subtype_relsubrel
            ONsubrel.mail_followers_id=fol.id
            RIGHTJOINmail_message_subtypesubtype
            ONsubtype.id=subrel.mail_message_subtype_id
        WHEREsubrel.mail_message_subtype_id=%%sANDfol.res_model=%%sANDfol.res_idIN%%s
    )
    SELECTpartner.idaspid,NULL::intAScid,
            partner.activeasactive,partner.partner_shareaspshare,NULLasctype,
            users.notification_typeASnotif,array_agg(groups.id)ASgroups
        FROMres_partnerpartner
        LEFTJOINres_usersusersONusers.partner_id=partner.idANDusers.active
        LEFTJOINres_groups_users_relgroups_relONgroups_rel.uid=users.id
        LEFTJOINres_groupsgroupsONgroups.id=groups_rel.gid
        WHEREEXISTS(
            SELECTpartner_idFROMsub_followers
            WHEREsub_followers.channel_idISNULL
                ANDsub_followers.partner_id=partner.id
                AND(coalesce(sub_followers.internal,false)<>TRUEORcoalesce(partner.partner_share,false)<>TRUE)
        )%s
        GROUPBYpartner.id,users.notification_type
    UNION
    SELECTNULL::intASpid,channel.idAScid,
            TRUEasactive,NULLASpshare,channel.channel_typeASctype,
            CASEWHENchannel.email_send=TRUETHEN'email'ELSE'inbox'ENDASnotif,NULLASgroups
        FROMmail_channelchannel
        WHEREEXISTS(
            SELECTchannel_idFROMsub_followersWHEREpartner_idISNULLANDsub_followers.channel_id=channel.id
        )%s
)ASx
ORDERBYpid,cid,notif
"""%('ORpartner.idIN%s'ifpidselse'','ORchannel.idIN%s'ifcidselse'')
            params=[subtype_id,records._name,tuple(records.ids)]
            ifpids:
                params.append(tuple(pids))
            ifcids:
                params.append(tuple(cids))
            self.env.cr.execute(query,tuple(params))
            res=self.env.cr.fetchall()
        elifpidsorcids:
            params,query_pid,query_cid=[],'',''
            ifpids:
                query_pid="""
SELECTpartner.idaspid,NULL::intAScid,
    partner.activeasactive,partner.partner_shareaspshare,NULLasctype,
    users.notification_typeASnotif,
    array_agg(groups_rel.gid)FILTER(WHEREgroups_rel.gidISNOTNULL)ASgroups
FROMres_partnerpartner
    LEFTJOINres_usersusersONusers.partner_id=partner.idANDusers.active
    LEFTJOINres_groups_users_relgroups_relONgroups_rel.uid=users.id
WHEREpartner.idIN%s
GROUPBYpartner.id,users.notification_type"""
                params.append(tuple(pids))
            ifcids:
                query_cid="""
SELECTNULL::intASpid,channel.idAScid,
    TRUEasactive,NULLASpshare,channel.channel_typeASctype,
    CASEwhenchannel.email_send=TRUEthen'email'else'inbox'endASnotif,NULLASgroups
FROMmail_channelchannelWHEREchannel.idIN%s"""
                params.append(tuple(cids))
            query='UNION'.join(xforxin[query_pid,query_cid]ifx)
            query='SELECTDISTINCTON(pid,cid)*FROM(%s)ASxORDERBYpid,cid,notif'%query
            self.env.cr.execute(query,tuple(params))
            res=self.env.cr.fetchall()
        else:
            res=[]
        returnres

    def_get_subscription_data(self,doc_data,pids,cids,include_pshare=False,include_active=False):
        """Privatemethodallowingtofetchfollowerdatafromseveraldocumentsofagivenmodel.
        FollowerscanbefilteredgivenpartnerIDsandchannelIDs.

        :paramdoc_data:listofpair(res_model,res_ids)thatarethedocumentsfromwhichwe
          wanttohavesubscriptiondata;
        :parampids:optionalpartnertofilter;ifNonetakeall,otherwiselimitatetopids
        :paramcids:optionalchanneltofilter;ifNonetakeall,otherwiselimitatetocids
        :paraminclude_pshare:optionaljoininpartnertofetchtheirsharestatus
        :paraminclude_active:optionaljoininpartnertofetchtheiractiveflag

        :return:listoffollowersdatawhichisalistoftuplescontaining
          followerID,
          documentID,
          partnerID(voidifchannel_id),
          channelID(voidifpartner_id),
          followedsubtypeIDs,
          sharestatusofpartner(voididchannel_id,returnedonlyifinclude_pshareisTrue)
          activeflagstatusofpartner(voididchannel_id,returnedonlyifinclude_activeisTrue)
        """
        #basequery:fetchfollowersofgivendocuments
        where_clause='OR'.join(['fol.res_model=%sANDfol.res_idIN%s']*len(doc_data))
        where_params=list(itertools.chain.from_iterable((rm,tuple(rids))forrm,ridsindoc_data))

        #additional:filteronoptionalpids/cids
        sub_where=[]
        ifpids:
            sub_where+=["fol.partner_idIN%s"]
            where_params.append(tuple(pids))
        elifpidsisnotNone:
            sub_where+=["fol.partner_idISNULL"]
        ifcids:
            sub_where+=["fol.channel_idIN%s"]
            where_params.append(tuple(cids))
        elifcidsisnotNone:
            sub_where+=["fol.channel_idISNULL"]
        ifsub_where:
            where_clause+="AND(%s)"%"OR".join(sub_where)

        query="""
SELECTfol.id,fol.res_id,fol.partner_id,fol.channel_id,array_agg(subtype.id)%s%s
FROMmail_followersfol
%s
LEFTJOINmail_followers_mail_message_subtype_relfol_relONfol_rel.mail_followers_id=fol.id
LEFTJOINmail_message_subtypesubtypeONsubtype.id=fol_rel.mail_message_subtype_id
WHERE%s
GROUPBYfol.id%s%s"""%(
            ',partner.partner_share'ifinclude_pshareelse'',
            ',partner.active'ifinclude_activeelse'',
            'LEFTJOINres_partnerpartnerONpartner.id=fol.partner_id'if(include_pshareorinclude_active)else'',
            where_clause,
            ',partner.partner_share'ifinclude_pshareelse'',
            ',partner.active'ifinclude_activeelse''
        )
        self.env.cr.execute(query,tuple(where_params))
        returnself.env.cr.fetchall()

    #--------------------------------------------------
    #Privatetoolsmethodstogeneratenewsubscription
    #--------------------------------------------------

    def_insert_followers(self,res_model,res_ids,partner_ids,partner_subtypes,channel_ids,channel_subtypes,
                          customer_ids=None,check_existing=True,existing_policy='skip'):
        """Maininternalmethodallowingtocreateorupdatefollowersfordocuments,givena
        res_modelandthedocumentres_ids.Thismethoddoesnothandleaccessrights.Thisisthe
        roleofthecallertoensurethereisnosecuritybreach.

        :parampartner_subtypes:optionalsubtypesfornewpartnerfollowers.Ifnotgiven,default
         onesarecomputed;
        :paramchannel_subtypes:optionalsubtypesfornewchannelfollowers.Ifnotgiven,default
         onesarecomputed;
        :paramcustomer_ids:see``_add_default_followers``
        :paramcheck_existing:see``_add_followers``;
        :paramexisting_policy:see``_add_followers``;
        """
        sudo_self=self.sudo().with_context(default_partner_id=False,default_channel_id=False)
        ifnotpartner_subtypesandnotchannel_subtypes: #nosubtypes->defaultcomputation,noforce,skipexisting
            new,upd=self._add_default_followers(
                res_model,res_ids,
                partner_ids,channel_ids,
                customer_ids=customer_ids,
                check_existing=check_existing,
                existing_policy=existing_policy)
        else:
            new,upd=self._add_followers(
                res_model,res_ids,
                partner_ids,partner_subtypes,
                channel_ids,channel_subtypes,
                check_existing=check_existing,
                existing_policy=existing_policy)
        ifnew:
            sudo_self.create([
                dict(values,res_id=res_id)
                forres_id,values_listinnew.items()
                forvaluesinvalues_list
            ])
        forfol_id,valuesinupd.items():
            sudo_self.browse(fol_id).write(values)

    def_add_default_followers(self,res_model,res_ids,partner_ids,channel_ids=None,customer_ids=None,
                               check_existing=True,existing_policy='skip'):
        """Shortcutto``_add_followers``thatcomputesdefaultsubtypes.Existing
        followersareskippedastheirsubscriptionisconsideredasmoreimportant
        comparedtonewdefaultsubscription.

        :paramcustomer_ids:optionallistofpartneridsthatarecustomers.Itisusedifcomputing
         defaultsubtypeisnecessaryandallowtoavoidthecheckofpartnersbeingcustomers(no
         userorshareuser).Itisjustamatterofsavingqueriesiftheinfoisalreadyknown;
        :paramcheck_existing:see``_add_followers``;
        :paramexisting_policy:see``_add_followers``;

        :return:see``_add_followers``
        """
        ifnotpartner_idsandnotchannel_ids:
            returndict(),dict()

        default,_,external=self.env['mail.message.subtype'].default_subtypes(res_model)
        ifpartner_idsandcustomer_idsisNone:
            customer_ids=self.env['res.partner'].sudo().search([('id','in',partner_ids),('partner_share','=',True)]).ids

        c_stypes=dict.fromkeys(channel_idsor[],default.ids)
        p_stypes=dict((pid,external.idsifpidincustomer_idselsedefault.ids)forpidinpartner_ids)

        returnself._add_followers(res_model,res_ids,partner_ids,p_stypes,channel_ids,c_stypes,check_existing=check_existing,existing_policy=existing_policy)

    def_add_followers(self,res_model,res_ids,partner_ids,partner_subtypes,channel_ids,channel_subtypes,
                       check_existing=False,existing_policy='skip'):
        """Internalmethodthatgeneratesvaluestoinsertorupdatefollowers.Callershaveto
        handletheresult,forexamplebymakingavalidORMcommand,insertingorupdatingdirectly
        followerrecords,...Thismethodreturnstwomaindata

         *firstoneisadictwhichkeysareres_ids.Valueisalistofdictofvaluesvalidfor
           creatingnewfollowersfortherelatedres_id;
         *secondoneisadictwhichkeysarefollowerids.Valueisadictofvaluesvalidfor
           updatingtherelatedfollowerrecord;

        :paramcheck_existing:ifTrue,checkforexistingfollowersforgivendocumentsandhandle
        themaccordingtoexisting_policyparameter.SettingtoFalseallowstosavesomecomputation
        ifcallerissuretherearenoconflictforfollowers;
        :paramexistingpolicy:ifcheck_existing,tellswhattodowithalready-existingfollowers:

          *skip:simplyskipexistingfollowers,donottouchthem;
          *force:updateexistingwithgivensubtypesonly;
          *replace:replaceexistingwithnewsubtypes(likeforcewithoutold/newfollower);
          *update:givesanupdatedictallowingtoaddmissingsubtypes(nosubtyperemoval);
        """
        _res_ids=res_idsor[0]
        data_fols,doc_pids,doc_cids=dict(),dict((i,set())foriin_res_ids),dict((i,set())foriin_res_ids)

        ifcheck_existingandres_ids:
            forfid,rid,pid,cid,sidsinself._get_subscription_data([(res_model,res_ids)],partner_idsorNone,channel_idsorNone):
                ifexisting_policy!='force':
                    ifpid:
                        doc_pids[rid].add(pid)
                    elifcid:
                        doc_cids[rid].add(cid)
                data_fols[fid]=(rid,pid,cid,sids)

            ifexisting_policy=='force':
                self.sudo().browse(data_fols.keys()).unlink()

        new,update=dict(),dict()
        forres_idin_res_ids:
            forpartner_idinset(partner_idsor[]):
                ifpartner_idnotindoc_pids[res_id]:
                    new.setdefault(res_id,list()).append({
                        'res_model':res_model,
                        'partner_id':partner_id,
                        'subtype_ids':[(6,0,partner_subtypes[partner_id])],
                    })
                elifexisting_policyin('replace','update'):
                    fol_id,sids=next(((key,val[3])forkey,valindata_fols.items()ifval[0]==res_idandval[1]==partner_id),(False,[]))
                    new_sids=set(partner_subtypes[partner_id])-set(sids)
                    old_sids=set(sids)-set(partner_subtypes[partner_id])
                    update_cmd=[]
                    iffol_idandnew_sids:
                        update_cmd+=[(4,sid)forsidinnew_sids]
                    iffol_idandold_sidsandexisting_policy=='replace':
                        update_cmd+=[(3,sid)forsidinold_sids]
                    ifupdate_cmd:
                        update[fol_id]={'subtype_ids':update_cmd}

            forchannel_idinset(channel_idsor[]):
                ifchannel_idnotindoc_cids[res_id]:
                    new.setdefault(res_id,list()).append({
                        'res_model':res_model,
                        'channel_id':channel_id,
                        'subtype_ids':[(6,0,channel_subtypes[channel_id])],
                    })
                elifexisting_policyin('replace','update'):
                    fol_id,sids=next(((key,val[3])forkey,valindata_fols.items()ifval[0]==res_idandval[2]==channel_id),(False,[]))
                    new_sids=set(channel_subtypes[channel_id])-set(sids)
                    old_sids=set(sids)-set(channel_subtypes[channel_id])
                    update_cmd=[]
                    iffol_idandnew_sids:
                        update_cmd+=[(4,sid)forsidinnew_sids]
                    iffol_idandold_sidsandexisting_policy=='replace':
                        update_cmd+=[(3,sid)forsidinold_sids]
                    ifupdate_cmd:
                        update[fol_id]={'subtype_ids':update_cmd}

        returnnew,update
