#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classRestaurantFloor(models.Model):

    _name='restaurant.floor'
    _description='RestaurantFloor'

    name=fields.Char('FloorName',required=True,help='Aninternalidentificationoftherestaurantfloor')
    pos_config_id=fields.Many2one('pos.config',string='PointofSale')
    background_image=fields.Binary('BackgroundImage',help='Abackgroundimageusedtodisplayafloorlayoutinthepointofsaleinterface')
    background_color=fields.Char('BackgroundColor',help='Thebackgroundcolorofthefloorlayout,(mustbespecifiedinahtml-compatibleformat)',default='rgb(210,210,210)')
    table_ids=fields.One2many('restaurant.table','floor_id',string='Tables',help='Thelistoftablesinthisfloor')
    sequence=fields.Integer('Sequence',help='UsedtosortFloors',default=1)
    active=fields.Boolean(default=True)

    defunlink(self):
        confs=self.mapped('pos_config_id').filtered(lambdac:c.is_table_management==True)
        opened_session=self.env['pos.session'].search([('config_id','in',confs.ids),('state','!=','closed')])
        ifopened_session:
            error_msg=_("YoucannotremoveafloorthatisusedinaPoSsession,closethesession(s)first:\n")
            forfloorinself:
                forsessioninopened_session:
                    iffloorinsession.config_id.floor_ids:
                        error_msg+=_("Floor:%s-PoSConfig:%s\n")%(floor.name,session.config_id.name)
            ifconfs:
                raiseUserError(error_msg)
        returnsuper(RestaurantFloor,self).unlink()

    defwrite(self,vals):
        forfloorinself:
            iffloor.pos_config_id.has_active_sessionand(vals.get('pos_config_id')orvals.get('active')):
                raiseUserError(
                    'PleasecloseandvalidatethefollowingopenPoSSessionbeforemodifyingthisfloor.\n'
                    'Opensession:%s'%(''.join(floor.pos_config_id.mapped('name')),))
            ifvals.get('pos_config_id')andfloor.pos_config_id.idandvals.get('pos_config_id')!=floor.pos_config_id.id:
                raiseUserError('The%sisalreadyusedinanotherPosConfig.'%floor.name)
        returnsuper(RestaurantFloor,self).write(vals)


classRestaurantTable(models.Model):

    _name='restaurant.table'
    _description='RestaurantTable'

    name=fields.Char('TableName',required=True,help='Aninternalidentificationofatable')
    floor_id=fields.Many2one('restaurant.floor',string='Floor')
    shape=fields.Selection([('square','Square'),('round','Round')],string='Shape',required=True,default='square')
    position_h=fields.Float('HorizontalPosition',default=10,
        help="Thetable'shorizontalpositionfromtheleftsidetothetable'scenter,inpixels")
    position_v=fields.Float('VerticalPosition',default=10,
        help="Thetable'sverticalpositionfromthetoptothetable'scenter,inpixels")
    width=fields.Float('Width',default=50,help="Thetable'swidthinpixels")
    height=fields.Float('Height',default=50,help="Thetable'sheightinpixels")
    seats=fields.Integer('Seats',default=1,help="Thedefaultnumberofcustomerservedatthistable.")
    color=fields.Char('Color',help="Thetable'scolor,expressedasavalid'background'CSSpropertyvalue")
    active=fields.Boolean('Active',default=True,help='Iffalse,thetableisdeactivatedandwillnotbeavailableinthepointofsale')

    @api.model
    defcreate_from_ui(self,table):
        """createormodifyatablefromthepointofsaleUI.
            tablecontainsthetable'sfields.Ifitcontainsan
            id,itwillmodifytheexistingtable.Itthen
            returnstheidofthetable.
        """
        iftable.get('floor_id'):
            table['floor_id']=table['floor_id'][0]

        table_id=table.pop('id',False)
        iftable_id:
            self.browse(table_id).write(table)
        else:
            table_id=self.create(table).id
        returntable_id

    defunlink(self):
        confs=self.mapped('floor_id').mapped('pos_config_id').filtered(lambdac:c.is_table_management==True)
        opened_session=self.env['pos.session'].search([('config_id','in',confs.ids),('state','!=','closed')])
        ifopened_session:
            error_msg=_("YoucannotremoveatablethatisusedinaPoSsession,closethesession(s)first.")
            ifconfs:
                raiseUserError(error_msg)
        returnsuper(RestaurantTable,self).unlink()


classRestaurantPrinter(models.Model):

    _name='restaurant.printer'
    _description='RestaurantPrinter'

    name=fields.Char('PrinterName',required=True,default='Printer',help='Aninternalidentificationoftheprinter')
    printer_type=fields.Selection(string='PrinterType',default='iot',
        selection=[('iot','UseaprinterconnectedtotheIoTBox')])
    proxy_ip=fields.Char('ProxyIPAddress',help="TheIPAddressorhostnameofthePrinter'shardwareproxy")
    product_categories_ids=fields.Many2many('pos.category','printer_category_rel','printer_id','category_id',string='PrintedProductCategories')
