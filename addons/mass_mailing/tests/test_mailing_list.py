#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportexceptions
fromflectra.addons.mass_mailing.tests.commonimportMassMailCommon
fromflectra.tests.commonimportForm,users


classTestMailingListMerge(MassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailingListMerge,cls).setUpClass()
        cls._create_mailing_list()

        cls.mailing_list_3=cls.env['mailing.list'].with_context(cls._test_context).create({
            'name':'ListC',
            'contact_ids':[
                (0,0,{'name':'Norberto','email':'norbert@example.com'}),
            ]
        })


    @users('user_marketing')
    deftest_mailing_contact_create(self):
        default_list_ids=(self.mailing_list_2|self.mailing_list_3).ids

        #simplysetdefaultlistincontext
        new=self.env['mailing.contact'].with_context(default_list_ids=default_list_ids).create([{
            'name':'Contact_%d'%x,
            'email':'contact_%d@test.example.com'%x,
        }forxinrange(0,5)])
        self.assertEqual(new.list_ids,(self.mailing_list_2|self.mailing_list_3))

        #defaultlistandsubscriptionsshouldbemerged
        new=self.env['mailing.contact'].with_context(default_list_ids=default_list_ids).create([{
            'name':'Contact_%d'%x,
            'email':'contact_%d@test.example.com'%x,
            'subscription_list_ids':[(0,0,{
                'list_id':self.mailing_list_1.id,
                'opt_out':True,
            }),(0,0,{
                'list_id':self.mailing_list_2.id,
                'opt_out':True,
            })],
        }forxinrange(0,5)])
        self.assertEqual(new.list_ids,(self.mailing_list_1|self.mailing_list_2|self.mailing_list_3))
        #shouldcorrectlytakesubscriptionopt_outvalue
        forlist_idin(self.mailing_list_1|self.mailing_list_2).ids:
            new=new.with_context(default_list_ids=[list_id])
            self.assertTrue(all(contact.opt_outforcontactinnew))
        #notopt_outfornewsubscriptionwithoutspecificcreatevalues
        forlist_idinself.mailing_list_3.ids:
            new=new.with_context(default_list_ids=[list_id])
            self.assertFalse(any(contact.opt_outforcontactinnew))

    @users('user_marketing')
    deftest_mailing_list_contact_copy_in_context_of_mailing_list(self):
        MailingContact=self.env['mailing.contact']
        contact_1=MailingContact.create({
            'name':'Sam',
            'email':'gamgee@shire.com',
            'subscription_list_ids':[(0,0,{'list_id':self.mailing_list_3.id})],
        })
        #Copythecontactwithdefault_list_idsincontext,whichshouldnotraiseanything
        contact_2=contact_1.with_context(default_list_ids=self.mailing_list_3.ids).copy()
        self.assertEqual(contact_1.list_ids,contact_2.list_ids,'Shouldcopytheexistingmailinglist(s)')

    @users('user_marketing')
    deftest_mailing_list_merge(self):
        #TESTCASE:MergeA,BintotheexistingmailinglistC
        #ThemailinglistCcontainsthesameemailaddressthan'Norbert'inlistB
        #Thistestensurethatthemailinglistsarecorrectlymergedandno
        #duplicatesareappearinginC
        merge_form=Form(self.env['mailing.list.merge'].with_context(
            active_ids=[self.mailing_list_1.id,self.mailing_list_2.id],
            active_model='mailing.list'
        ))
        merge_form.new_list_name=False
        merge_form.dest_list_id=self.mailing_list_3
        merge_form.merge_options='existing'
        merge_form.archive_src_lists=False
        result_list=merge_form.save().action_mailing_lists_merge()

        #Assertthenumberofcontactsiscorrect
        self.assertEqual(
            len(result_list.contact_ids.ids),5,
            'ThenumberofcontactsonthemailinglistCisnotequalto5')

        #Assertthere'snoduplicatedemailaddress
        self.assertEqual(
            len(list(set(result_list.contact_ids.mapped('email')))),5,
            'Duplicateshavebeenmergedintothedestinationmailinglist.Check%s'%(result_list.contact_ids.mapped('email')))

    @users('user_marketing')
    deftest_mailing_list_merge_cornercase(self):
        """Checkwronguseofmergewizard"""
        withself.assertRaises(exceptions.UserError):
            merge_form=Form(self.env['mailing.list.merge'].with_context(
                active_ids=[self.mailing_list_1.id,self.mailing_list_2.id],
            ))

        merge_form=Form(self.env['mailing.list.merge'].with_context(
            active_ids=[self.mailing_list_1.id],
            active_model='mailing.list',
            default_src_list_ids=[self.mailing_list_1.id,self.mailing_list_2.id],
            default_dest_list_id=self.mailing_list_3.id,
            default_merge_options='existing',
        ))
        merge=merge_form.save()
        self.assertEqual(merge.src_list_ids,self.mailing_list_1+self.mailing_list_2)
        self.assertEqual(merge.dest_list_id,self.mailing_list_3)
