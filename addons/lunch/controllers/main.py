#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,http,fields
fromflectra.exceptionsimportAccessError
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.toolsimportfloat_round,float_repr


classLunchController(http.Controller):
    @http.route('/lunch/infos',type='json',auth='user')
    definfos(self,user_id=None):
        self._check_user_impersonification(user_id)
        user=request.env['res.users'].browse(user_id)ifuser_idelserequest.env.user

        infos=self._make_infos(user,order=False)

        lines=self._get_current_lines(user.id)
        iflines:
            lines=[{'id':line.id,
                      'product':(line.product_id.id,line.product_id.name,float_repr(float_round(line.price,2),2)),
                      'toppings':[(topping.name,float_repr(float_round(topping.price,2),2))
                                   fortoppinginline.topping_ids_1|line.topping_ids_2|line.topping_ids_3],
                      'quantity':line.quantity,
                      'price':line.price,
                      'state':line.state,#Onlyusedfor_get_state
                      'note':line.note}forlineinlines]
            raw_state,state=self._get_state(lines)
            infos.update({
                'total':float_repr(float_round(sum(line['price']forlineinlines),2),2),
                'raw_state':raw_state,
                'state':state,
                'lines':lines,
            })
        returninfos

    @http.route('/lunch/trash',type='json',auth='user')
    deftrash(self,user_id=None):
        self._check_user_impersonification(user_id)
        user=request.env['res.users'].browse(user_id)ifuser_idelserequest.env.user

        lines=self._get_current_lines(user.id)
        lines.action_cancel()
        lines.unlink()

    @http.route('/lunch/pay',type='json',auth='user')
    defpay(self,user_id=None):
        self._check_user_impersonification(user_id)
        user=request.env['res.users'].browse(user_id)ifuser_idelserequest.env.user

        lines=self._get_current_lines(user.id)
        iflines:
            lines=lines.filtered(lambdaline:line.state=='new')

            lines.action_order()
            returnTrue

        returnFalse

    @http.route('/lunch/payment_message',type='json',auth='user')
    defpayment_message(self):
        return{'message':request.env['ir.qweb']._render('lunch.lunch_payment_dialog',{})}

    @http.route('/lunch/user_location_set',type='json',auth='user')
    defset_user_location(self,location_id=None,user_id=None):
        self._check_user_impersonification(user_id)
        user=request.env['res.users'].browse(user_id)ifuser_idelserequest.env.user

        user.sudo().last_lunch_location_id=request.env['lunch.location'].browse(location_id)
        returnTrue

    @http.route('/lunch/user_location_get',type='json',auth='user')
    defget_user_location(self,user_id=None):
        self._check_user_impersonification(user_id)
        user=request.env['res.users'].browse(user_id)ifuser_idelserequest.env.user

        user_location=user.last_lunch_location_id
        has_multi_company_access=notuser_location.company_idoruser_location.company_id.idinrequest._context.get('allowed_company_ids',request.env.company.ids)

        ifnotuser_locationornothas_multi_company_access:
            returnrequest.env['lunch.location'].search([],limit=1).id
        returnuser_location.id

    def_make_infos(self,user,**kwargs):
        res=dict(kwargs)

        is_manager=request.env.user.has_group('lunch.group_lunch_manager')

        currency=user.company_id.currency_id

        res.update({
            'username':user.sudo().name,
            'userimage':'/web/image?model=res.users&id=%s&field=image_128'%user.id,
            'wallet':request.env['lunch.cashmove'].get_wallet_balance(user,False),
            'is_manager':is_manager,
            'locations':request.env['lunch.location'].search_read([],['name']),
            'currency':{'symbol':currency.symbol,'position':currency.position},
        })

        user_location=user.last_lunch_location_id
        has_multi_company_access=notuser_location.company_idoruser_location.company_id.idinrequest._context.get('allowed_company_ids',request.env.company.ids)

        ifnotuser_locationornothas_multi_company_access:
            user.last_lunch_location_id=user_location=request.env['lunch.location'].search([],limit=1)

        alert_domain=expression.AND([
            [('available_today','=',True)],
            [('location_ids','in',user_location.id)],
            [('mode','=','alert')],
        ])

        res.update({
            'user_location':(user_location.id,user_location.name),
            'alerts':request.env['lunch.alert'].search_read(alert_domain,['message']),
        })

        returnres

    def_check_user_impersonification(self,user_id=None):
        if(user_idandrequest.env.uid!=user_idandnotrequest.env.user.has_group('lunch.group_lunch_manager')):
            raiseAccessError(_('Youaretryingtoimpersonateanotheruser,butthiscanonlybedonebyalunchmanager'))

    def_get_current_lines(self,user_id):
        returnrequest.env['lunch.order'].search([('user_id','=',user_id),('date','=',fields.Date.today()),('state','!=','cancelled')])

    def_get_state(self,lines):
        """
            Thismethodreturnstheloweststateofthelistoflines

            eg:[confirmed,confirmed,new]willreturn('new','ToOrder')
        """
        states_to_int={'new':0,'ordered':1,'confirmed':2,'cancelled':3}
        int_to_states=['new','ordered','confirmed','cancelled']
        translated_states=dict(request.env['lunch.order']._fields['state']._description_selection(request.env))

        state=int_to_states[min(states_to_int[line['state']]forlineinlines)]

        return(state,translated_states[state])
