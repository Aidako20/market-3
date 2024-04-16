#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.testsimportcommon
fromflectra.testsimporttagged,users


@tagged('mail_render')
classTestMailRender(common.MailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestMailRender,cls).setUpClass()

        #activatemultilanguagesupport
        cls.env['res.lang']._activate_lang('fr_FR')
        cls.user_admin.write({'lang':'en_US'})

        #testrecords
        cls.render_object=cls.env['res.partner'].create({
            'name':'TestRecord',
            'lang':'en_US',
        })
        cls.render_object_fr=cls.env['res.partner'].create({
            'name':'ElementdeTest',
            'lang':'fr_FR',
        })

        #somejinjatemplates
        cls.base_jinja_bits=[
            '<p>Hello</p>',
            '<p>Hello${object.name}</p>',
            """<p>
%setenglish=object.lang=='en_US'
%ifenglish
    <span>EnglishSpeaker</span>
%else
    <span>OtherSpeaker</span>
%endif
</p>"""
        ]
        cls.base_jinja_bits_fr=[
            '<p>Bonjour</p>',
            '<p>Bonjour${object.name}</p>',
            """<p>
%setenglish=object.lang=='en_US'
%ifenglish
    <span>NarrateurAnglais</span>
%else
    <span>AutreNarrateur</span>
%endif
</p>"""
        ]

        #someqwebtemplatesandtheirxmlids
        cls.base_qweb_templates=cls.env['ir.ui.view'].create([
            {'name':'TestRender','type':'qweb',
             'arch':'<p>Hello</p>',
            },
            {'name':'TestRender2','type':'qweb',
             'arch':'<p>Hello<tt-esc="object.name"/></p>',
            },
            {'name':'TestRender3','type':'qweb',
             'arch':"""<p>
    <spant-if="object.lang=='en_US'">EnglishSpeaker</span>
    <spant-else="">OtherSpeaker</span>
</p>""",
            },
        ])
        cls.base_qweb_templates_data=cls.env['ir.model.data'].create([
            {'name':template.name,'module':'mail',
             'model':template._name,'res_id':template.id,
            }fortemplateincls.base_qweb_templates
        ])
        cls.base_qweb_templates_xmlids=[
            model_data.complete_name
            formodel_dataincls.base_qweb_templates_data
        ]

        #renderresult
        cls.base_rendered=[
            '<p>Hello</p>',
            '<p>Hello%s</p>'%cls.render_object.name,
            """<p>
    <span>EnglishSpeaker</span>
</p>"""
        ]
        cls.base_rendered_fr=[
            '<p>Bonjour</p>',
            '<p>Bonjour%s</p>'%cls.render_object_fr.name,
            """<p>
    <span>AutreNarrateur</span>
</p>"""
        ]

        #linktomailtemplate
        cls.test_template_jinja=cls.env['mail.template'].create({
            'name':'TestTemplate',
            'subject':cls.base_jinja_bits[0],
            'body_html':cls.base_jinja_bits[1],
            'model_id':cls.env['ir.model']._get('res.partner').id,
            'lang':'${object.lang}'
        })

        #sometranslations
        cls.env['ir.translation'].create({
            'type':'model',
            'name':'mail.template,subject',
            'lang':'fr_FR',
            'res_id':cls.test_template_jinja.id,
            'src':cls.test_template_jinja.subject,
            'value':cls.base_jinja_bits_fr[0],
        })
        cls.env['ir.translation'].create({
            'type':'model',
            'name':'mail.template,body_html',
            'lang':'fr_FR',
            'res_id':cls.test_template_jinja.id,
            'src':cls.test_template_jinja.body_html,
            'value':cls.base_jinja_bits_fr[1],
        })
        cls.env['ir.model.data'].create({
            'name':'test_template_xmlid',
            'module':'mail',
            'model':cls.test_template_jinja._name,
            'res_id':cls.test_template_jinja.id,
        })

    @users('employee')
    deftest_render_jinja(self):
        source="""<p>
%setline_statement_variable=3
<span>Wehave${line_statement_variable}cookiesinstock</span>
<span>Wehave<%setblock_variable=4%>${block_variable}cookiesinstock</span>
</p>"""
        partner=self.env['res.partner'].browse(self.render_object.ids)
        result=self.env['mail.render.mixin']._render_template(
            source,
            partner._name,
            partner.ids,
            engine='jinja',
        )[partner.id]
        self.assertEqual(result,"""<p>
<span>Wehave3cookiesinstock</span>
<span>Wehave4cookiesinstock</span>
</p>""")

    @users('employee')
    deftest_render_mail_template_jinja(self):
        template=self.env['mail.template'].browse(self.test_template_jinja.ids)
        partner=self.env['res.partner'].browse(self.render_object.ids)
        forfname,expectedinzip(['subject','body_html'],self.base_rendered):
            rendered=template._render_field(
                fname,
                partner.ids,
                compute_lang=True
            )[partner.id]
            self.assertEqual(rendered,expected)

        partner=self.env['res.partner'].browse(self.render_object_fr.ids)
        forfname,expectedinzip(['subject','body_html'],self.base_rendered_fr):
            rendered=template._render_field(
                fname,
                partner.ids,
                compute_lang=True
            )[partner.id]
            self.assertEqual(rendered,expected)

    @users('employee')
    deftest_render_template_jinja(self):
        partner=self.env['res.partner'].browse(self.render_object.ids)
        forsource,expectedinzip(self.base_jinja_bits,self.base_rendered):
            rendered=self.env['mail.render.mixin']._render_template(
                source,
                partner._name,
                partner.ids,
                engine='jinja',
            )[partner.id]
            self.assertEqual(rendered,expected)

    @users('employee')
    deftest_render_template_qweb(self):
        partner=self.env['res.partner'].browse(self.render_object.ids)
        forsource,expectedinzip(self.base_qweb_templates_xmlids,self.base_rendered):
            rendered=self.env['mail.render.mixin']._render_template(
                source,
                partner._name,
                partner.ids,
                engine='qweb',
            )[partner.id].decode()
            self.assertEqual(rendered,expected)
