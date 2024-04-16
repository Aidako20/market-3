#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importflectra.tests
fromflectra.osvimportexpression


@flectra.tests.tagged('post_install','-at_install','assets_bundle')
classBusWebTests(flectra.tests.HttpCase):

    deftest_bundle_sends_bus(self):
        """
        Teststwothings:
        -Messagesarepostedtothebuswhenassetschange
          i.e.theirhashhasbeenrecomputedanddifferfromtheattachment's
        -Theinterfacedealswiththosebusmessagesbydisplayingonenotification
        """
        db_name=self.env.registry.db_name
        bundle_xml_ids=('web.assets_common','web.assets_backend')

        domain=[]
        forbundleinbundle_xml_ids:
            domain=expression.OR([
                domain,
                [('name','ilike',bundle+'%')]
            ])
        #startfromacleanslate
        self.env['ir.attachment'].search(domain).unlink()
        self.env.registry._clear_cache()

        sendones=[]
        defpatched_sendone(self,channel,message):
            """
            ControlAPIandnumberofmessagespostedtothebus
            """
            sendones.append((channel,message))

        self.patch(type(self.env['bus.bus']),'sendone',patched_sendone)

        self.start_tour('/web',"bundle_changed_notification",login='admin',timeout=180)

        #OnesendoneforeachassetbundleandforeachCSS/JS
        self.assertEqual(len(sendones),4)
        forsentinsendones:
            channel=sent[0]
            message=sent[1]
            self.assertEqual(channel,(db_name,'bundle_changed'))
            self.assertEqual(len(message),2)
            self.assertTrue(message[0]inbundle_xml_ids)
            self.assertTrue(isinstance(message[1],str))
