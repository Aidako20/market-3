#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importuuid
fromwerkzeug.urlsimporturl_join

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classAdyenAccount(models.Model):
    _inherit='adyen.account'

    store_ids=fields.One2many('adyen.store','adyen_account_id')
    terminal_ids=fields.One2many('adyen.terminal','adyen_account_id')

    @api.model
    def_sync_adyen_cron(self):
        self.env['adyen.terminal']._sync_adyen_terminals()
        super(AdyenAccount,self)._sync_adyen_cron()

    defaction_order_terminal(self):
        ifnotself.store_ids:
            raiseValidationError(_('Pleasecreateastorefirst.'))

        store_uuids=','.join(self.store_ids.mapped('store_uuid'))
        onboarding_url=self.env['ir.config_parameter'].sudo().get_param('adyen_platforms.onboarding_url')
        return{
            'type':'ir.actions.act_url',
            'target':'new',
            'url':url_join(onboarding_url,'order_terminals?store_uuids=%s'%store_uuids),
        }


classAdyenStore(models.Model):
    _name='adyen.store'
    _inherit=['adyen.address.mixin']
    _description='AdyenforPlatformsStore'

    adyen_account_id=fields.Many2one('adyen.account',ondelete='cascade')
    store_reference=fields.Char('Reference',default=lambdaself:uuid.uuid4().hex)
    store_uuid=fields.Char('UUID',readonly=True)#GivenbyAdyen
    name=fields.Char('Name',required=True)
    phone_number=fields.Char('PhoneNumber',required=True)
    terminal_ids=fields.One2many('adyen.terminal','store_id',string='PaymentTerminals',readonly=True)

    @api.model
    defcreate(self,values):
        adyen_store_id=super(AdyenStore,self).create(values)
        response=adyen_store_id.adyen_account_id._adyen_rpc('create_store',adyen_store_id._format_data())
        stores=response['accountHolderDetails']['storeDetails']
        created_store=next(storeforstoreinstoresifstore['storeReference']==adyen_store_id.store_reference)
        adyen_store_id.with_context(update_from_adyen=True).sudo().write({
            'store_uuid':created_store['store'],
        })
        returnadyen_store_id

    defunlink(self):
        forstore_idinself:
            store_id.adyen_account_id._adyen_rpc('close_stores',{
                'accountHolderCode':store_id.adyen_account_id.account_holder_code,
                'stores':[store_id.store_uuid],
            })
        returnsuper(AdyenStore,self).unlink()

    def_format_data(self):
        return{
            'accountHolderCode':self.adyen_account_id.account_holder_code,
            'accountHolderDetails':{
                'storeDetails':[{
                    'storeReference':self.store_reference,
                    'storeName':self.name,
                    'merchantCategoryCode':'7999',
                    'address':{
                        'city':self.city,
                        'country':self.country_id.code,
                        'houseNumberOrName':self.house_number_or_name,
                        'postalCode':self.zip,
                        'stateOrProvince':self.state_id.codeorNone,
                        'street':self.street,
                    },
                    'fullPhoneNumber':self.phone_number,
                }],
            }
        }


classAdyenTerminal(models.Model):
    _name='adyen.terminal'
    _description='AdyenforPlatformsTerminal'
    _rec_name='terminal_uuid'

    adyen_account_id=fields.Many2one('adyen.account',ondelete='cascade')
    store_id=fields.Many2one('adyen.store')
    terminal_uuid=fields.Char('TerminalID')

    @api.model
    def_sync_adyen_terminals(self):
        foradyen_store_idinself.env['adyen.store'].search([]):
            response=adyen_store_id.adyen_account_id._adyen_rpc('connected_terminals',{
                'store':adyen_store_id.store_uuid,
            })
            terminals_in_db=set(self.search([('store_id','=',adyen_store_id.id)]).mapped('terminal_uuid'))

            #Addedterminals
            forterminalinset(response.get('uniqueTerminalIds'))-terminals_in_db:
                self.sudo().create({
                    'adyen_account_id':adyen_store_id.adyen_account_id.id,
                    'store_id':adyen_store_id.id,
                    'terminal_uuid':terminal,
                })
