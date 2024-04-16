#-*-coding:utf-8-*-

fromflectraimportapi,models,fields,_
fromflectra.exceptionsimportValidationError

classResCompany(models.Model):
    _inherit='res.company'

    point_of_sale_update_stock_quantities=fields.Selection([
            ('closing','Atthesessionclosing(advised)'),
            ('real','Inrealtime'),
            ],default='closing',string="Updatequantitiesinstock",
            help="Atthesessionclosing:Apickingiscreatedfortheentiresessionwhenit'sclosed\nInrealtime:Eachordersenttotheservercreateitsownpicking")

    @api.constrains('period_lock_date','fiscalyear_lock_date')
    defvalidate_period_lock_date(self):
        """Thisconstrainsmakesitimpossibletochangetheperiodlockdateif
        someopenPOSsessionexistsintoit.Withoutthat,thesePOSsessions
        wouldtriggeranerrormessagesayingthattheperiodhasbeenlockedwhen
        tryingtoclosethem.
        """
        pos_session_model=self.env['pos.session'].sudo()
        forrecordinself:
            sessions_in_period=pos_session_model.search(
                [
                    "&",
                    "&",
                    ("company_id","=",record.id),
                    ("state","!=","closed"),
                    "|",
                    ("start_at","<=",record.period_lock_date),
                    ("start_at","<=",record.fiscalyear_lock_date),
                ]
            )
            ifsessions_in_period:
                sessions_str=','.join(sessions_in_period.mapped('name'))
                raiseValidationError(_("Pleasecloseallthepointofsalesessionsinthisperiodbeforeclosingit.Opensessionsare:%s")%(sessions_str))
