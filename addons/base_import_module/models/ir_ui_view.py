#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromoperatorimportitemgetter
fromflectraimportapi,models

classIrUiView(models.Model):
    _inherit='ir.ui.view'

    @api.model
    def_validate_custom_views(self,model):
        #viewsfromimportedmodulesshouldbeconsideredascustomviews
        result=super(IrUiView,self)._validate_custom_views(model)

        self._cr.execute("""
            SELECTmax(v.id)
               FROMir_ui_viewv
          LEFTJOINir_model_datamdON(md.model='ir.ui.view'ANDmd.res_id=v.id)
          LEFTJOINir_module_modulemON(m.name=md.module)
              WHEREm.imported=true
                ANDv.model=%s
                ANDv.active=true
           GROUPBYcoalesce(v.inherit_id,v.id)
        """,[model])

        ids=(row[0]forrowinself._cr.fetchall())
        views=self.with_context(load_all_views=True).browse(ids)
        returnviews._check_xml()andresult
