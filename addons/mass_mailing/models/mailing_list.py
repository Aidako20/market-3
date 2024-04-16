#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,fields,models
fromflectra.exceptionsimportUserError


classMassMailingList(models.Model):
    """Modelofacontactlist."""
    _name='mailing.list'
    _order='name'
    _description='MailingList'

    name=fields.Char(string='MailingList',required=True)
    active=fields.Boolean(default=True)
    contact_nbr=fields.Integer(compute="_compute_contact_nbr",string='NumberofContacts')
    contact_ids=fields.Many2many(
        'mailing.contact','mailing_contact_list_rel','list_id','contact_id',
        string='MailingLists')
    subscription_ids=fields.One2many(
        'mailing.contact.subscription','list_id',string='SubscriptionInformation',
        depends=['contact_ids'])
    is_public=fields.Boolean(default=True,help="Themailinglistcanbeaccessiblebyrecipientintheunsubscription"
                                                  "pagetoallowshimtoupdatehissubscriptionpreferences.")

    #Computenumberofcontactsnonopt-out,nonblacklistedandvalidemailrecipientforamailinglist
    def_compute_contact_nbr(self):
        ifself.ids:
            self.env.cr.execute('''
                select
                    list_id,count(*)
                from
                    mailing_contact_list_relr
                    leftjoinmailing_contactcon(r.contact_id=c.id)
                    leftjoinmail_blacklistblonc.email_normalized=bl.emailandbl.active
                where
                    list_idin%s
                    ANDCOALESCE(r.opt_out,FALSE)=FALSE
                    ANDc.email_normalizedISNOTNULL
                    ANDbl.idISNULL
                groupby
                    list_id
            ''',(tuple(self.ids),))
            data=dict(self.env.cr.fetchall())
            formailing_listinself:
                mailing_list.contact_nbr=data.get(mailing_list._origin.id,0)
        else:
            self.contact_nbr=0

    defwrite(self,vals):
        #Preventarchivingusedmailinglist
        if'active'invalsandnotvals.get('active'):
            mass_mailings=self.env['mailing.mailing'].search_count([
                ('state','!=','done'),
                ('contact_list_ids','in',self.ids),
            ])

            ifmass_mailings>0:
                raiseUserError(_("Atleastoneofthemailinglistyouaretryingtoarchiveisusedinanongoingmailingcampaign."))

        returnsuper(MassMailingList,self).write(vals)

    defname_get(self):
        return[(list.id,"%s(%s)"%(list.name,list.contact_nbr))forlistinself]

    defaction_view_contacts(self):
        action=self.env["ir.actions.actions"]._for_xml_id("mass_mailing.action_view_mass_mailing_contacts")
        action['domain']=[('list_ids','in',self.ids)]
        context=dict(self.env.context,search_default_filter_valid_email_recipient=1,default_list_ids=self.ids)
        action['context']=context
        returnaction

    defaction_merge(self,src_lists,archive):
        """
            Insertallthecontactfromthemailinglists'src_lists'tothe
            mailinglistin'self'.Possibilitytoarchivethemailinglists
            'src_lists'afterthemergeexceptthedestinationmailinglist'self'.
        """
        #ExplationoftheSQLquerywithanexample.Therearethefollowinglists
        #A(id=4):yti@flectrahq.com;yti@example.com
        #B(id=5):yti@flectrahq.com;yti@openerp.com
        #C(id=6):nothing
        #TomergethemailinglistsAandBintoC,webuildtheviewstthatlooks
        #likethiswithourexample:
        #
        # contact_id|          email          |row_number| list_id|
        #------------+---------------------------+------------------------
        #          4|yti@flectrahq.com             |         1|       4|
        #          6|yti@flectrahq.com             |         2|       5|
        #          5|yti@example.com          |         1|       4|
        #          7|yti@openerp.com          |         1|       5|
        #
        #Therow_columniskindofanoccurencecounterfortheemailaddress.
        #ThenwecreatetheMany2manyrelationbetweenthedestinationlistandthecontacts
        #whileavoidingtoinsertanexistingemailaddress(ifthedestinationisinthesource
        #forexample)
        self.ensure_one()
        #Putdestinationissourceslistsifnotalreadythecase
        src_lists|=self
        self.env['mailing.contact'].flush(['email','email_normalized'])
        self.env['mailing.contact.subscription'].flush(['contact_id','opt_out','list_id'])
        self.env.cr.execute("""
            INSERTINTOmailing_contact_list_rel(contact_id,list_id)
            SELECTst.contact_idAScontact_id,%sASlist_id
            FROM
                (
                SELECT
                    contact.idAScontact_id,
                    contact.emailASemail,
                    list.idASlist_id,
                    row_number()OVER(PARTITIONBYemailORDERBYemail)ASrn
                FROM
                    mailing_contactcontact,
                    mailing_contact_list_relcontact_list_rel,
                    mailing_listlist
                WHEREcontact.id=contact_list_rel.contact_id
                ANDCOALESCE(contact_list_rel.opt_out,FALSE)=FALSE
                ANDcontact.email_normalizedNOTIN(selectemailfrommail_blacklistwhereactive=TRUE)
                ANDlist.id=contact_list_rel.list_id
                ANDlist.idIN%s
                ANDNOTEXISTS
                    (
                    SELECT1
                    FROM
                        mailing_contactcontact2,
                        mailing_contact_list_relcontact_list_rel2
                    WHEREcontact2.email=contact.email
                    ANDcontact_list_rel2.contact_id=contact2.id
                    ANDcontact_list_rel2.list_id=%s
                    )
                )st
            WHEREst.rn=1;""",(self.id,tuple(src_lists.ids),self.id))
        self.flush()
        self.invalidate_cache()
        ifarchive:
            (src_lists-self).action_archive()

    defclose_dialog(self):
        return{'type':'ir.actions.act_window_close'}
