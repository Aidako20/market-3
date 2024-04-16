flectra.define('mail/static/src/components/drop_zone/drop_zone.js',function(require){
'usestrict';

constuseShouldUpdateBasedOnProps=require('mail/static/src/component_hooks/use_should_update_based_on_props/use_should_update_based_on_props.js');

const{Component,useState}=owl;

classDropZoneextendsComponent{

    /**
     *@override
     */
    constructor(...args){
        super(...args);
        useShouldUpdateBasedOnProps();
        this.state=useState({
            /**
             *Determinewhethertheuserisdraggingfilesoverthedropzone.
             *Usefultoprovidevisualfeedbackinthatcase.
             */
            isDraggingInside:false,
        });
        /**
         *Countshowmanydragenter/leavehappenedonselfandchildren.This
         *ensuresthedropeffectstaysactivewhendraggingoverachild.
         */
        this._dragCount=0;
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Returnswhetherthegivennodeisselforachildrenofself.
     *
     *@param{Node}node
     *@returns{boolean}
     */
    contains(node){
        returnthis.el.contains(node);
    }

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Makingsurethatdraggingcontentisexternalfiles.
     *Ignoringothercontentdraggingliketext.
     *
     *@private
     *@param{DataTransfer}dataTransfer
     *@returns{boolean}
     */
    _isDragSourceExternalFile(dataTransfer){
        constdragDataType=dataTransfer.types;
        if(dragDataType.constructor===window.DOMStringList){
            returndragDataType.contains('Files');
        }
        if(dragDataType.constructor===Array){
            returndragDataType.includes('Files');
        }
        returnfalse;
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Showsavisualdropeffectwhendragginginsidethedropzone.
     *
     *@private
     *@param{DragEvent}ev
     */
    _onDragenter(ev){
        ev.preventDefault();
        if(this._dragCount===0){
            this.state.isDraggingInside=true;
        }
        this._dragCount++;
    }

    /**
     *Hidesthevisualdropeffectwhendraggingoutsidethedropzone.
     *
     *@private
     *@param{DragEvent}ev
     */
    _onDragleave(ev){
        this._dragCount--;
        if(this._dragCount===0){
            this.state.isDraggingInside=false;
        }
    }

    /**
     *Preventsdefault(fromthetemplate)inordertoreceivethedropevent.
     *Thedropeffectcursorworksonlywhensetondragover.
     *
     *@private
     *@param{DragEvent}ev
     */
    _onDragover(ev){
        ev.preventDefault();
        ev.dataTransfer.dropEffect='copy';
    }

    /**
     *Triggersthe`o-dropzone-files-dropped`eventwhennewfilesaredropped
     *onthedropzone,andthenremovesthevisualdropeffect.
     *
     *Theparentsshouldhandlethiseventtoprocessthefilesastheywish,
     *suchasuploadingthem.
     *
     *@private
     *@param{DragEvent}ev
     */
    _onDrop(ev){
        ev.preventDefault();
        if(this._isDragSourceExternalFile(ev.dataTransfer)){
            this.trigger('o-dropzone-files-dropped',{
                files:ev.dataTransfer.files,
            });
        }
        this.state.isDraggingInside=false;
    }

}

Object.assign(DropZone,{
    props:{},
    template:'mail.DropZone',
});

returnDropZone;

});
