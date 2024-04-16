flectra.define('mail/static/src/components/emojis_popover/emojis_popover.js',function(require){
'usestrict';

constemojis=require('mail.emojis');
constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');
constuseUpdate=require('mail/static/src/component_hooks/use_update/use_update.js');

const{Component}=owl;

classEmojisPopoverextendsComponent{

    /**
     *@param{...any}args
     */
    constructor(...args){
        super(...args);
        this.emojis=emojis;
        useShouldUpdateBasedOnProps();
        useUpdate({func:()=>this._update()});
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _update(){
        this.trigger('o-popover-compute');
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    close(){
        this.trigger('o-popover-close');
    }

    /**
     *Returnswhetherthegivennodeisselforachildrenofself.
     *
     *@param{Node}node
     *@returns{boolean}
     */
    contains(node){
        if(!this.el){
            returnfalse;
        }
        returnthis.el.contains(node);
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickEmoji(ev){
        this.close();
        this.trigger('o-emoji-selection',{
            unicode:ev.currentTarget.dataset.unicode,
        });
    }

}

Object.assign(EmojisPopover,{
    props:{},
    template:'mail.EmojisPopover',
});

returnEmojisPopover;

});
