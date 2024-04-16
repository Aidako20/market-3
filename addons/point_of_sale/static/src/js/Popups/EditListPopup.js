flectra.define('point_of_sale.EditListPopup',function(require){
    'usestrict';

    const{useState}=owl.hooks;
    constAbstractAwaitablePopup=require('point_of_sale.AbstractAwaitablePopup');
    constRegistries=require('point_of_sale.Registries');
    const{useAutoFocusToLast}=require('point_of_sale.custom_hooks');

    /**
     *Givenaarrayof{id,text},weshowtheuserthispopuptobeabletomodifythisgivenarray.
     *(usedtoreplacePackLotLinePopupWidget)
     *
     *TheexpectedreturnofshowPopupwhenthispopupisusedisanarrayof{_id,[id],text}.
     *  -_idistheassigneduniqueidentifierforeachitem.
     *  -idistheoriginalid.ifnotprovided,thenitmeansthattheitemisnew.
     *  -textisthemodified/unmodifiedtext.
     *
     *Example:
     *
     *```
     *  --perhapsinsideaclickhandler--
     *  //gathertheitemstoedit
     *  constnames=[{id:1,text:'Joseph'},{id:2,text:'Kaykay'}];
     *
     *  //supplytheitemstothepopupandwaitforuser'sresponse
     *  //whenuserpressed`confirm`inthepopup,thechangeshemadewillbereturnedbytheshowPopupfunction.
     *  const{confirmed,payload:newNames}=awaitthis.showPopup('EditListPopup',{
     *    title:"Canyouconfirmthisitem?",
     *    array:names})
     *
     *  //wethenconsumethenewdata.Inthisexample,itisonlylogged.
     *  if(confirmed){
     *    console.log(newNames);
     *    //theabovemightlogthefollowing:
     *    //[{_id:1,id:1,text:'JosephCaburnay'},{_id:2,id:2,'Kaykay'},{_id:3,'James'}]
     *    //Theresultshowedthattheoriginalitemwithid=1waschangedtohavetext'JosephCaburnay'from'Joseph'
     *    //Theonewithid=2didnotchange.Andanewitemwithtext='James'isadded.
     *  }
     *```
     */
    classEditListPopupextendsAbstractAwaitablePopup{
        /**
         *@param{String}titlerequiredtitleofpopup
         *@param{Array}[props.array=[]]thearrayof{id,text}tobeeditedoranarrayofstrings
         *@param{Boolean}[props.isSingleItem=false]trueifonlyallowedtoeditsingleitem(thefirstitem)
         */
        constructor(){
            super(...arguments);
            this._id=0;
            this.state=useState({array:this._initialize(this.props.array)});
            useAutoFocusToLast();
        }
        _nextId(){
            returnthis._id++;
        }
        _emptyItem(){
            return{
                text:'',
                _id:this._nextId(),
            };
        }
        _initialize(array){
            //Ifnoarrayisprovided,weinitializewithoneemptyitem.
            if(array.length===0)return[this._emptyItem()];
            //Put_idforeachitem.Itwillserveasuniqueidentifierofeachitem.
            returnarray.map((item)=>Object.assign({},{_id:this._nextId()},typeofitem==='object'?item:{'text':item}));
        }
        removeItem(event){
            constitemToRemove=event.detail;
            this.state.array.splice(
                this.state.array.findIndex(item=>item._id==itemToRemove._id),
                1
            );
            //Wekeepaminimumofoneemptyiteminthepopup.
            if(this.state.array.length===0){
                this.state.array.push(this._emptyItem());
            }
        }
        createNewItem(){
            if(this.props.isSingleItem)return;
            this.state.array.push(this._emptyItem());
        }
        /**
         *@override
         */
        getPayload(){
            return{
                newArray:this.state.array
                    .filter((item)=>item.text.trim()!=='')
                    .map((item)=>Object.assign({},item)),
            };
        }
    }
    EditListPopup.template='EditListPopup';
    EditListPopup.defaultProps={
        confirmText:'Ok',
        cancelText:'Cancel',
        array:[],
        isSingleItem:false,
    };

    Registries.Component.add(EditListPopup);

    returnEditListPopup;
});
