#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxmlimportetreeasElementTree

fromflectra.httpimportController,route,request


classBoard(Controller):

    @route('/board/add_to_dashboard',type='json',auth='user')
    defadd_to_dashboard(self,action_id,context_to_save,domain,view_mode,name=''):
        #Retrievethe'MyDashboard'actionfromitsxmlid
        action=request.env.ref('board.open_board_my_dash_action').sudo()

        ifactionandaction['res_model']=='board.board'andaction['views'][0][1]=='form'andaction_id:
            #Maybeshouldcheckthecontentinsteadofmodelboard.board?
            view_id=action['views'][0][0]
            board=request.env['board.board'].fields_view_get(view_id,'form')
            ifboardand'arch'inboard:
                xml=ElementTree.fromstring(board['arch'])
                column=xml.find('./board/column')
                ifcolumnisnotNone:
                    #Wedon'twanttosaveallowed_company_ids
                    #Otherwiseondashboard,themulti-companywidgetdoesnotfiltertherecords
                    if'allowed_company_ids'incontext_to_save:
                        context_to_save.pop('allowed_company_ids')
                    new_action=ElementTree.Element('action',{
                        'name':str(action_id),
                        'string':name,
                        'view_mode':view_mode,
                        'context':str(context_to_save),
                        'domain':str(domain)
                    })
                    column.insert(0,new_action)
                    arch=ElementTree.tostring(xml,encoding='unicode')
                    request.env['ir.ui.view.custom'].create({
                        'user_id':request.session.uid,
                        'ref_id':view_id,
                        'arch':arch
                    })
                    returnTrue

        returnFalse
