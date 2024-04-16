#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classBoard(models.AbstractModel):
    _name='board.board'
    _description="Board"
    _auto=False

    @api.model
    defcreate(self,vals):
        returnself

    @api.model
    deffields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        """
        Overridesormfield_view_get.
        @return:DictionaryofFields,archandtoolbar.
        """

        res=super(Board,self).fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)

        custom_view=self.env['ir.ui.view.custom'].search([('user_id','=',self.env.uid),('ref_id','=',view_id)],limit=1)
        ifcustom_view:
            res.update({'custom_view_id':custom_view.id,
                        'arch':custom_view.arch})
        res.update({
            'arch':self._arch_preprocessing(res['arch']),
            'toolbar':{'print':[],'action':[],'relate':[]}
        })
        returnres

    @api.model
    def_arch_preprocessing(self,arch):
        fromlxmlimportetree

        defremove_unauthorized_children(node):
            forchildinnode.iterchildren():
                ifchild.tag=='action'andchild.get('invisible'):
                    node.remove(child)
                else:
                    remove_unauthorized_children(child)
            returnnode

        archnode=etree.fromstring(arch)
        #addthejs_class'board'ontheflytoforcethewebclientto
        #instantiateaBoardViewinsteadofFormView
        archnode.set('js_class','board')
        returnetree.tostring(remove_unauthorized_children(archnode),pretty_print=True,encoding='unicode')
