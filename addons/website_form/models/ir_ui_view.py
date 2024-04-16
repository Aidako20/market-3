#-*-coding:utf-8-*-
fromlxmlimportetree

fromflectraimportmodels
fromflectra.tools.miscimporthmac


classView(models.Model):

    _inherit="ir.ui.view"

    defread_combined(self,fields=None):
        root=super(View,self).read_combined(fields)
        ifself.type!="qweb"or'/website_form/'notinroot['arch']: #Performancerelatedcheck,reducetheamountofoperationforunrelatedviews
            returnroot
        root_node=etree.fromstring(root['arch'])
        nodes=root_node.xpath('.//form[contains(@action,"/website_form/")]')
        forforminnodes:
            existing_hash_node=form.find('.//input[@type="hidden"][@name="website_form_signature"]')
            ifexisting_hash_nodeisnotNone:
                existing_hash_node.getparent().remove(existing_hash_node)
            input_nodes=form.xpath('.//input[contains(@name,"email_")]')
            form_values={input_node.attrib['name']:input_nodeforinput_nodeininput_nodes}
            #ifthisformdoesnotsendanemail,ignore.Butatthisstage,
            #thevalueofemail_tocanstillbeNoneincaseofdefaultvalue
            if'email_to'notinform_values.keys():
                continue
            elifnotform_values['email_to'].attrib.get('value'):
                form_values['email_to'].attrib['value']=self.env.company.emailor''
            has_cc={'email_cc','email_bcc'}&form_values.keys()
            value=form_values['email_to'].attrib['value']+(':email_cc'ifhas_ccelse'')
            hash_value=hmac(self.sudo().env,'website_form_signature',value)
            hash_node='<inputtype="hidden"class="form-controls_website_form_inputs_website_form_custom"name="website_form_signature"value=""/>'
            ifhas_cc:
                hash_value+=':email_cc'
            form_values['email_to'].addnext(etree.fromstring(hash_node))
            form_values['email_to'].getnext().attrib['value']=hash_value
        root['arch']=etree.tostring(root_node)
        returnroot
