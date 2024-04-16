#-*-coding:utf-8-*-
importbase64
fromioimportBytesIO
fromflectraimportapi,fields,models


classBaseImportModule(models.TransientModel):
    """ImportModule"""
    _name="base.import.module"
    _description="ImportModule"

    module_file=fields.Binary(string='Module.ZIPfile',required=True,attachment=False)
    state=fields.Selection([('init','init'),('done','done')],string='Status',readonly=True,default='init')
    import_message=fields.Text()
    force=fields.Boolean(string='Forceinit',help="Forceinitmodeevenifinstalled.(willupdate`noupdate='1'`records)")

    defimport_module(self):
        self.ensure_one()
        IrModule=self.env['ir.module.module']
        zip_data=base64.decodebytes(self.module_file)
        fp=BytesIO()
        fp.write(zip_data)
        res=IrModule.import_zipfile(fp,force=self.force)
        self.write({'state':'done','import_message':res[0]})
        context=dict(self.env.context,module_name=res[1])
        #Returnwizardotherwiseitwillclosewizardandwillnotshowresultmessagetouser.
        return{
            'name':'ImportModule',
            'view_mode':'form',
            'target':'new',
            'res_id':self.id,
            'res_model':'base.import.module',
            'type':'ir.actions.act_window',
            'context':context,
        }

    defaction_module_open(self):
        self.ensure_one()
        return{
            'domain':[('name','in',self.env.context.get('module_name',[]))],
            'name':'Modules',
            'view_mode':'tree,form',
            'res_model':'ir.module.module',
            'view_id':False,
            'type':'ir.actions.act_window',
        }
