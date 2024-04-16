#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging

importrequests
fromlxmlimportetree
importre
importwerkzeug.urls

fromflectraimportapi,models
fromflectra.toolsimportmisc
fromflectra.addons.google_accountimportTIMEOUT

_logger=logging.getLogger(__name__)


classGoogleDrive(models.Model):
    _inherit='google.drive.config'

    defget_google_scope(self):
        scope=super(GoogleDrive,self).get_google_scope()
        return'%shttps://www.googleapis.com/auth/spreadsheets'%scope

    @api.model
    defwrite_config_formula(self,attachment_id,spreadsheet_key,model,domain,groupbys,view_id):
        access_token=self.get_access_token(scope='https://www.googleapis.com/auth/spreadsheets')

        formula=self._get_data_formula(model,domain,groupbys,view_id)

        url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        dbname=self._cr.dbname
        user=self.env['res.users'].browse(self.env.user.id).read(['login','password'])[0]
        username=user['login']
        password=user['password']
        ifnotpassword:
            config_formula='=oe_settings("%s";"%s")'%(url,dbname)
        else:
            config_formula='=oe_settings("%s";"%s";"%s";"%s")'%(url,dbname,username,password)
        request={
            "valueInputOption":"USER_ENTERED",
            "data":[
                {"range":"A1","values":[[formula]]},
                {"range":"O60","values":[[config_formula]]},
            ]
        }
        try:
            req=requests.post(
                'https://sheets.googleapis.com/v4/spreadsheets/%s/values:batchUpdate?%s'%(spreadsheet_key,werkzeug.urls.url_encode({'access_token':access_token})),
                data=json.dumps(request),
                headers={'content-type':'application/json','If-Match':'*'},
                timeout=TIMEOUT,
            )
        exceptIOError:
            _logger.warning("AnerroroccuredwhilewritingtheformulaontheGoogleSpreadsheet.")

        description='''
        formula:%s
        '''%formula
        ifattachment_id:
            self.env['ir.attachment'].browse(attachment_id).write({'description':description})
        returnTrue

    def_get_data_formula(self,model,domain,groupbys,view_id):
        fields=self.env[model].fields_view_get(view_id=view_id,view_type='tree')
        doc=etree.XML(fields.get('arch'))
        display_fields=[]
        fornodeindoc.xpath("//field"):
            ifnode.get('modifiers'):
                modifiers=json.loads(node.get('modifiers'))
                ifnotmodifiers.get('invisible')andnotmodifiers.get('column_invisible'):
                    display_fields.append(node.get('name'))
        fields="".join(display_fields)
        domain=domain.replace("'",r"\'").replace('"',"'").replace('True','true').replace('False','false')
        ifgroupbys:
            fields="%s%s"%(groupbys,fields)
            formula='=oe_read_group("%s";"%s";"%s";"%s")'%(model,fields,groupbys,domain)
        else:
            formula='=oe_browse("%s";"%s";"%s")'%(model,fields,domain)
        returnformula

    @api.model
    defset_spreadsheet(self,model,domain,groupbys,view_id):
        try:
            config_id=self.env['ir.model.data'].get_object_reference('google_spreadsheet','google_spreadsheet_template')[1]
        exceptValueError:
            raise
        config=self.browse(config_id)

        ifself._module_deprecated():
            return{
                'url':config.google_drive_template_url,
                'deprecated':True,
                'formula':self._get_data_formula(model,domain,groupbys,view_id),
            }

        title='Spreadsheet%s'%model
        res=self.copy_doc(False,config.google_drive_resource_id,title,model)

        mo=re.search("(key=|/d/)([A-Za-z0-9-_]+)",res['url'])
        ifmo:
            key=mo.group(2)

        self.write_config_formula(res.get('id'),key,model,domain,groupbys,view_id)
        returnres
