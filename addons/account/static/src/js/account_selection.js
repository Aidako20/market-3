flectra.define('account.hierarchy.selection',function(require){
"usestrict";

    varcore=require('web.core');
    varrelational_fields=require('web.relational_fields');
    var_t=core._t;
    varregistry=require('web.field_registry');


    varFieldSelection=relational_fields.FieldSelection;

    varqweb=core.qweb;

    varHierarchySelection=FieldSelection.extend({
        _renderEdit:function(){
            varself=this;
            varprom=Promise.resolve()
            if(!self.hierarchy_groups){
                prom=this._rpc({
                    model:'account.account.type',
                    method:'search_read',
                    kwargs:{
                        domain:[],
                        fields:['id','internal_group','display_name'],
                    },
                }).then(function(arg){
                    self.values=_.map(arg,v=>[v['id'],v['display_name']])
                    self.hierarchy_groups=[
                        {
                            'name':_t('BalanceSheet'),
                            'children':[
                                {'name':_t('Assets'),'ids':_.map(_.filter(arg,v=>v['internal_group']=='asset'),v=>v['id'])},
                                {'name':_t('Liabilities'),'ids':_.map(_.filter(arg,v=>v['internal_group']=='liability'),v=>v['id'])},
                                {'name':_t('Equity'),'ids':_.map(_.filter(arg,v=>v['internal_group']=='equity'),v=>v['id'])},
                            ],
                        },
                        {
                            'name':_t('Profit&Loss'),
                            'children':[
                                {'name':_t('Income'),'ids':_.map(_.filter(arg,v=>v['internal_group']=='income'),v=>v['id'])},
                                {'name':_t('Expense'),'ids':_.map(_.filter(arg,v=>v['internal_group']=='expense'),v=>v['id'])},
                            ],
                        },
                        {'name':_t('Other'),'ids':_.map(_.filter(arg,v=>!['asset','liability','equity','income','expense'].includes(v['internal_group'])),v=>v['id'])},
                    ]
                });
            }

            Promise.resolve(prom).then(function(){
                self.$el.empty();
                self._addHierarchy(self.$el,self.hierarchy_groups,0);
                varvalue=self.value;
                if(self.field.type==='many2one'&&value){
                    value=value.data.id;
                }
                self.$el.val(JSON.stringify(value));
            });
        },
        _addHierarchy:function(el,group,level){
            varself=this;
            _.each(group,function(item){
                varoptgroup=$('<optgroup/>').attr(({
                    'label':$('<div/>').html('&nbsp;'.repeat(6*level)+item['name']).text(),
                }))
                _.each(item['ids'],function(id){
                    varvalue=_.find(self.values,v=>v[0]==id)
                    optgroup.append($('<option/>',{
                        value:JSON.stringify(value[0]),
                        text:value[1],
                    }));
                })
                el.append(optgroup)
                if(item['children']){
                    self._addHierarchy(el,item['children'],level+1);
                }
            })
        }
    });
    registry.add("account_hierarchy_selection",HierarchySelection);
});
