#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importrandom
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_

fromuuidimportuuid4

classCoupon(models.Model):
    _name='coupon.coupon'
    _description="Coupon"
    _rec_name='code'

    @api.model
    def_generate_code(self):
        """Generatea20charlongpseudo-randomstringofdigitsforbarcode
        generation.

        Adecimalserialisationislongerthanahexadecimalone*but*it
        generatesamorecompactbarcode(Code128CratherthanCode128A).

        Generate8bytes(64bits)barcodesas16bytesbarcodesarenot
        compatiblewithallscanners.
         """
        returnstr(uuid4())[:22]

    code=fields.Char(default=_generate_code,required=True,readonly=True)
    expiration_date=fields.Date('ExpirationDate',compute='_compute_expiration_date')
    state=fields.Selection([
        ('reserved','Pending'),
        ('new','Valid'),
        ('sent','Sent'),
        ('used','Used'),
        ('expired','Expired'),
        ('cancel','Cancelled')
    ],required=True,default='new')
    partner_id=fields.Many2one('res.partner',"ForCustomer")
    program_id=fields.Many2one('coupon.program',"Program")
    discount_line_product_id=fields.Many2one('product.product',related='program_id.discount_line_product_id',readonly=False,
        help='Productusedinthesalesordertoapplythediscount.')

    _sql_constraints=[
        ('unique_coupon_code','unique(code)','Thecouponcodemustbeunique!'),
    ]

    @api.depends('create_date','program_id.validity_duration')
    def_compute_expiration_date(self):
        self.expiration_date=0
        forcouponinself.filtered(lambdax:x.program_id.validity_duration>0):
            coupon.expiration_date=(coupon.create_date+relativedelta(days=coupon.program_id.validity_duration)).date()

    defaction_coupon_sent(self):
        """Openawindowtocomposeanemail,withtheediinvoicetemplate
            messageloadedbydefault
        """
        self.ensure_one()
        template=self.env.ref('coupon.mail_template_sale_coupon',False)
        compose_form=self.env.ref('mail.email_compose_message_wizard_form',False)
        ctx=dict(
            default_model='coupon.coupon',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout='mail.mail_notification_light',
            mark_coupon_as_sent=True,
            force_email=True,
        )
        return{
            'name':_('ComposeEmail'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(compose_form.id,'form')],
            'view_id':compose_form.id,
            'target':'new',
            'context':ctx,
        }

    defaction_coupon_cancel(self):
        self.state='cancel'

    defcron_expire_coupon(self):
        self._cr.execute("""
            SELECTC.idFROMCOUPON_COUPONasC
            INNERJOINCOUPON_PROGRAMasPONC.program_id=P.id
            WHEREC.STATEin('reserved','new','sent')
                ANDP.validity_duration>0
                ANDC.create_date+interval'1day'*P.validity_duration<now()""")

        expired_ids=[res[0]forresinself._cr.fetchall()]
        self.browse(expired_ids).write({'state':'expired'})
