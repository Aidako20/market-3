flectra.define('account.ShowGroupedList',function(require){
"usestrict";

const{Component}=owl;
const{useState}=owl.hooks;
constAbstractFieldOwl=require('web.AbstractFieldOwl');
constfield_registry=require('web.field_registry_owl');

classListItemextendsComponent{}
ListItem.template='account.GroupedItemTemplate';
ListItem.props=["item_vals","options"];

classListGroupextendsComponent{}
ListGroup.template='account.GroupedItemsTemplate';
ListGroup.components={ListItem}
ListGroup.props=["group_vals","options"];


classShowGroupedListextendsAbstractFieldOwl{
    constructor(...args){
        super(...args);
        this.data=this.value?JSON.parse(this.value):{
            groups_vals:[],
            options:{
                discarded_number:'',
                columns:[],
            },
        };
    }
    asyncwillUpdateProps(nextProps){
        awaitsuper.willUpdateProps(nextProps);
        Object.assign(this.data,JSON.parse(this.value));
    }
}
ShowGroupedList.template='account.GroupedListTemplate';
ShowGroupedList.components={ListGroup}

field_registry.add('grouped_view_widget',ShowGroupedList);
returnShowGroupedList;
});
