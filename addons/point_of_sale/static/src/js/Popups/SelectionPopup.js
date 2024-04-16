flectra.define('point_of_sale.SelectionPopup',function(require){
    'usestrict';

    const{useState}=owl.hooks;
    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');

    //formerlySelectionPopupWidget
    classSelectionPopupextendsAbstractAwaitablePopup{
        /**
         *Valueofthe`item`keyoftheselectedelementintheSelection
         *Arrayisthepayloadofthispopup.
         *
         *@param{Object}props
         *@param{String}[props.confirmText='Confirm']
         *@param{String}[props.cancelText='Cancel']
         *@param{String}[props.title='Select']
         *@param{String}[props.body='']
         *@param{Array<Selection>}[props.list=[]]
         *     Selection{
         *         id:integer,
         *         label:string,
         *         isSelected:boolean,
         *         item:any,
         *     }
         */
        constructor(){
            super(...arguments);
            this.state=useState({selectedId:this.props.list.find((item)=>item.isSelected)});
        }
        selectItem(itemId){
            this.state.selectedId=itemId;
            this.confirm();
        }
        /**
         *Wesendaspayloadoftheresponsetheselecteditem.
         *
         *@override
         */
        getPayload(){
            constselected=this.props.list.find((item)=>this.state.selectedId===item.id);
            returnselected&&selected.item;
        }
    }
    SelectionPopup.template='SelectionPopup';
    SelectionPopup.defaultProps={
        confirmText:'Confirm',
        cancelText:'Cancel',
        title:'Select',
        body:'',
        list:[],
    };

    Registries.Component.add(SelectionPopup);

    returnSelectionPopup;
});
